"""
LangChain adaptor for ARC Protocol.

This module provides the ARCLangChainAdaptor class for integrating ARC Protocol
with LangChain agents and workflows.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import BaseTool

from arc import Client as ARCClient

from ..base import BaseAdaptor
from .tools import create_arc_handoff_tool, load_arc_handoff_tools, AgentInfo


class ARCLangChainAdaptor(BaseAdaptor):
    """
    Adaptor for integrating ARC Protocol with LangChain.
    
    This adaptor enables LangChain agents to communicate with ARC Protocol agents
    through handoff tools.
    """
    
    def __init__(
        self,
        arc_endpoint: str,
        ledger_url: str,
        agent_ids: List[str],
        token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the ARCLangChainAdaptor.
        
        Args:
            arc_endpoint: ARC Protocol endpoint URL
            ledger_url: URL of the ARC Ledger for retrieving agent information
            agent_ids: List of agent IDs to create tools for
            token: Optional OAuth2 bearer token for authentication
            config: Optional additional configuration
        """
        # Set attributes before calling super().__init__ to avoid validation errors
        self.arc_endpoint = arc_endpoint
        self.ledger_url = ledger_url
        self.agent_ids = agent_ids
        self.token = token
        self.arc_client = ARCClient(endpoint=arc_endpoint, token=token)
        self.tools: List[BaseTool] = []
        
        # Now call super().__init__ with config
        super().__init__(config or {})
    
    def _validate_config(self) -> None:
        """
        Validate the adaptor configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.arc_endpoint:
            raise ValueError("ARC endpoint URL is required")
        
        if not self.ledger_url:
            raise ValueError("ARC Ledger URL is required")
        
        if not self.agent_ids:
            raise ValueError("At least one agent ID is required")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an ARC request and return the response.
        
        Args:
            request: ARC request object
            
        Returns:
            ARC response object
        """
        method = request.get("method")
        target_agent = request.get("targetAgent")
        params = request.get("params", {})
        
        response = await self.arc_client.send_request(
            method=method,
            target_agent=target_agent,
            params=params
        )
        
        return response
    
    async def translate_to_native(self, arc_request: Dict[str, Any]) -> Any:
        """
        Translate an ARC request to the native format of LangChain.
        
        Args:
            arc_request: ARC request object
            
        Returns:
            Request in LangChain format
        """
        # This is a simplified implementation
        # In a real-world scenario, you would need to map ARC request fields to LangChain format
        method = arc_request.get("method")
        params = arc_request.get("params", {})
        
        if method == "task.create":
            initial_message = params.get("initialMessage", {})
            content = ""
            
            # Extract content from message parts
            for part in initial_message.get("parts", []):
                if part.get("type") == "TextPart":
                    content += part.get("content", "")
            
            return {
                "type": "human",
                "content": content
            }
        
        return arc_request
    
    async def translate_from_native(self, native_response: Any) -> Dict[str, Any]:
        """
        Translate a native response from LangChain to an ARC response.
        
        Args:
            native_response: Response from LangChain
            
        Returns:
            ARC response object
        """
        # This is a simplified implementation
        # In a real-world scenario, you would need to map LangChain response fields to ARC format
        if isinstance(native_response, dict):
            if "content" in native_response:
                return {
                    "arc": "1.0",
                    "id": "response_id",
                    "responseAgent": "langchain_agent",
                    "targetAgent": "requesting_agent",
                    "result": {
                        "type": "task",
                        "task": {
                            "taskId": "task_id",
                            "status": "COMPLETED",
                            "messages": [
                                {
                                    "role": "agent",
                                    "parts": [
                                        {
                                            "type": "TextPart",
                                            "content": native_response["content"]
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "error": None
                }
        
        return {
            "arc": "1.0",
            "id": "response_id",
            "responseAgent": "langchain_agent",
            "targetAgent": "requesting_agent",
            "result": {
                "success": True,
                "message": str(native_response)
            },
            "error": None
        }
    
    async def load_tools(self) -> List[BaseTool]:
        """
        Load handoff tools for ARC Protocol agents.
        
        Returns:
            List of LangChain tools for handoff to ARC agents
        """
        self.tools = await load_arc_handoff_tools(
            agent_ids=self.agent_ids,
            ledger_url=self.ledger_url,
            arc_client=self.arc_client
        )
        return self.tools
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get the loaded handoff tools.
        
        Returns:
            List of LangChain tools for handoff to ARC agents
        """
        if not self.tools:
            # Load tools synchronously if they haven't been loaded yet
            self.tools = asyncio.run(self.load_tools())
        return self.tools
    
    async def create_handoff_tool(self, agent_info: AgentInfo) -> BaseTool:
        """
        Create a handoff tool for an ARC Protocol agent.
        
        Args:
            agent_info: Information about the target agent
            
        Returns:
            A LangChain tool for handoff to the ARC agent
        """
        return create_arc_handoff_tool(
            agent_info=agent_info,
            arc_client=self.arc_client
        )
    
    async def close(self):
        """Close the ARC client and release resources."""
        await self.arc_client.close()
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()