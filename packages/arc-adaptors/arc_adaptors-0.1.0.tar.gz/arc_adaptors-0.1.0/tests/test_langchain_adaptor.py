"""
Tests for the LangChain adaptor.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from arc_adaptors.langchain import ARCLangChainAdaptor
from arc_adaptors.langchain.tools import AgentInfo, create_arc_handoff_tool


class TestARCLangChainAdaptor:
    """Tests for the ARCLangChainAdaptor class."""
    
    @pytest.fixture
    def mock_arc_client(self):
        """Create a mock ARC client."""
        mock_client = AsyncMock()
        mock_client.task.create = AsyncMock()
        mock_client.task.info = AsyncMock()
        mock_client.send_request = AsyncMock()
        mock_client.close = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def adaptor(self, mock_arc_client):
        """Create an adaptor instance with a mock client."""
        with patch("arc_adaptors.langchain.adaptor.ARCClient", return_value=mock_arc_client):
            adaptor = ARCLangChainAdaptor(
                arc_endpoint="https://api.example.com/arc",
                ledger_url="https://ledger.example.com/arc",
                agent_ids=["math-agent", "weather-agent"]
            )
            yield adaptor
    
    def test_validate_config_valid(self, adaptor):
        """Test that valid configuration passes validation."""
        adaptor._validate_config()  # Should not raise an exception
    
    def test_validate_config_invalid(self):
        """Test that invalid configuration raises an exception."""
        # Missing arc_endpoint
        with pytest.raises(ValueError):
            with patch("arc_adaptors.langchain.adaptor.ARCClient", return_value=AsyncMock()):
                ARCLangChainAdaptor(
                    arc_endpoint="",
                    ledger_url="https://ledger.example.com/arc",
                    agent_ids=["math-agent"]
                )
        
        # Missing ledger_url
        with pytest.raises(ValueError):
            with patch("arc_adaptors.langchain.adaptor.ARCClient", return_value=AsyncMock()):
                ARCLangChainAdaptor(
                    arc_endpoint="https://api.example.com/arc",
                    ledger_url="",
                    agent_ids=["math-agent"]
                )
        
        # Missing agent_ids
        with pytest.raises(ValueError):
            with patch("arc_adaptors.langchain.adaptor.ARCClient", return_value=AsyncMock()):
                ARCLangChainAdaptor(
                    arc_endpoint="https://api.example.com/arc",
                    ledger_url="https://ledger.example.com/arc",
                    agent_ids=[]
                )
    
    @pytest.mark.asyncio
    async def test_process_request(self, adaptor, mock_arc_client):
        """Test processing an ARC request."""
        # Set up mock response
        mock_response = {
            "arc": "1.0",
            "id": "response_id",
            "responseAgent": "math-agent",
            "targetAgent": "requester",
            "result": {"success": True}
        }
        mock_arc_client.send_request.return_value = mock_response
        
        # Create request
        request = {
            "method": "task.create",
            "targetAgent": "math-agent",
            "params": {"initialMessage": {"role": "user", "parts": [{"type": "TextPart", "content": "Calculate 2+2"}]}}
        }
        
        # Process request
        response = await adaptor.process_request(request)
        
        # Check that the client was called correctly
        mock_arc_client.send_request.assert_called_once_with(
            method="task.create",
            target_agent="math-agent",
            params={"initialMessage": {"role": "user", "parts": [{"type": "TextPart", "content": "Calculate 2+2"}]}}
        )
        
        # Check response
        assert response == mock_response
    
    @pytest.mark.asyncio
    async def test_translate_to_native(self, adaptor):
        """Test translating an ARC request to LangChain format."""
        # Create ARC request
        arc_request = {
            "method": "task.create",
            "params": {
                "initialMessage": {
                    "role": "user",
                    "parts": [{"type": "TextPart", "content": "Calculate 2+2"}]
                }
            }
        }
        
        # Translate to LangChain format
        lc_request = await adaptor.translate_to_native(arc_request)
        
        # Check result
        assert lc_request == {"type": "human", "content": "Calculate 2+2"}
    
    @pytest.mark.asyncio
    async def test_translate_from_native(self, adaptor):
        """Test translating a LangChain response to ARC format."""
        # Create LangChain response
        lc_response = {"type": "ai", "content": "The answer is 4"}
        
        # Translate to ARC format
        arc_response = await adaptor.translate_from_native(lc_response)
        
        # Check result
        assert arc_response["arc"] == "1.0"
        assert arc_response["result"]["type"] == "task"
        assert arc_response["result"]["task"]["messages"][0]["parts"][0]["content"] == "The answer is 4"
    
    @pytest.mark.asyncio
    async def test_load_tools(self, adaptor):
        """Test loading handoff tools."""
        # Create mock tools
        mock_tool1 = MagicMock()
        mock_tool1.name = "transfer_to_math_expert"
        
        mock_tool2 = MagicMock()
        mock_tool2.name = "transfer_to_weather_expert"
        
        mock_tools = [mock_tool1, mock_tool2]
        
        # Mock the load_arc_handoff_tools function
        with patch("arc_adaptors.langchain.adaptor.load_arc_handoff_tools", return_value=mock_tools) as mock_load:
            # Load tools
            tools = await adaptor.load_tools()
            
            # Check that the function was called correctly
            mock_load.assert_called_once_with(
                agent_ids=adaptor.agent_ids,
                ledger_url=adaptor.ledger_url,
                arc_client=adaptor.arc_client
            )
            
            # Check that the tools were returned
            assert len(tools) == 2
            assert tools[0].name == "transfer_to_math_expert"
            assert tools[1].name == "transfer_to_weather_expert"


class TestHandoffTools:
    """Tests for the handoff tools."""
    
    @pytest.mark.asyncio
    async def test_create_arc_handoff_tool(self):
        """Test creating a handoff tool."""
        # Create agent info
        agent_info = AgentInfo(
            id="math-agent",
            name="Math Expert",
            url="https://api.example.com/arc/math",
            description="Expert in mathematics"
        )
        
        # Create mock client
        mock_client = AsyncMock()
        
        # Set up mock response for task.create
        task_create_response = {
            "result": {
                "type": "task",
                "task": {
                    "taskId": "task-123",
                    "status": "SUBMITTED"
                }
            }
        }
        mock_client.task.create.return_value = task_create_response
        
        # Set up mock response for task.info
        task_info_response = {
            "result": {
                "type": "task",
                "task": {
                    "taskId": "task-123",
                    "status": "COMPLETED",
                    "messages": [
                        {
                            "role": "agent",
                            "parts": [{"type": "TextPart", "content": "The answer is 4"}]
                        }
                    ]
                }
            }
        }
        mock_client.task.info.return_value = task_info_response
        
        # Create handoff tool
        tool = create_arc_handoff_tool(agent_info, mock_client)
        
        # Check tool properties
        assert tool.name == "transfer_to_math_expert"
        assert "Ask agent 'Math Expert' for help" in tool.description
        
        # Test the coroutine directly instead of using the func property
        result = await tool.coroutine("Calculate 2+2")
        
        # Check that the client was called correctly
        mock_client.task.create.assert_called_once()
        mock_client.task.info.assert_called_once()
        
        # Check result
        assert "The answer is 4" in result