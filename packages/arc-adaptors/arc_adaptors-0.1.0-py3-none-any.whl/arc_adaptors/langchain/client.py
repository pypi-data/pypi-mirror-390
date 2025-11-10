"""
ARC client wrapper for LangChain integration.

This module provides a wrapper around the ARC client to simplify integration
with LangChain agents and workflows.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncIterator

from arc import Client as ARCClient

from .tools import AgentInfo


class ARCClientWrapper:
    """
    Wrapper around the ARC client for LangChain integration.
    
    This wrapper simplifies the process of connecting to multiple ARC agents
    and managing connections.
    """
    
    def __init__(
        self,
        connections: Dict[str, Dict[str, Any]],
        token: Optional[str] = None
    ):
        """
        Initialize the ARCClientWrapper.
        
        Args:
            connections: A dictionary mapping agent IDs to connection configurations
            token: Optional OAuth2 bearer token for authentication
        """
        self.connections = connections
        self.token = token
        self.clients: Dict[str, ARCClient] = {}
    
    @asynccontextmanager
    async def session(self, agent_id: str) -> AsyncIterator[ARCClient]:
        """
        Create a session with an ARC agent.
        
        Args:
            agent_id: ID of the agent to connect to
            
        Yields:
            An initialized ARCClient for the specified agent
            
        Raises:
            ValueError: If the agent ID is not found in the connections
        """
        if agent_id not in self.connections:
            raise ValueError(f"Agent {agent_id} not found in connections")
        
        connection = self.connections[agent_id]
        endpoint = connection.get("url")
        
        if not endpoint:
            raise ValueError(f"URL not provided for agent {agent_id}")
        
        client = ARCClient(endpoint=endpoint, token=self.token)
        
        try:
            yield client
        finally:
            await client.close()
    
    async def get_agent_info(self, agent_id: str, ledger_url: str) -> AgentInfo:
        """
        Get information about an ARC agent from the ledger.
        
        Args:
            agent_id: ID of the agent to get information for
            ledger_url: URL of the ARC Ledger
            
        Returns:
            Information about the agent
            
        Raises:
            ValueError: If the agent information cannot be retrieved
        """
        async with ARCClient(endpoint=ledger_url, token=self.token) as ledger_client:
            # Fetch agent information from the ledger
            response = await ledger_client.task.create(
                target_agent="ledger",
                initial_message={
                    "role": "user",
                    "parts": [{"type": "TextPart", "content": f"Get agent info for {agent_id}"}]
                },
                metadata={"agent_id": agent_id}
            )
            
            # Extract agent information from the response
            result = response.get("result", {})
            if not result or result.get("type") != "task":
                raise ValueError(f"Failed to get information for agent {agent_id}")
            
            task = result.get("task", {})
            artifacts = task.get("artifacts", [])
            
            # Find the agent info artifact
            for artifact in artifacts:
                parts = artifact.get("parts", [])
                for part in parts:
                    if part.get("type") == "DataPart":
                        agent_data = part.get("content", {})
                        if agent_data and isinstance(agent_data, dict):
                            return AgentInfo(
                                id=agent_id,
                                name=agent_data.get("name", agent_id),
                                url=agent_data.get("url", ""),
                                description=agent_data.get("description", "")
                            )
            
            raise ValueError(f"No information found for agent {agent_id}")
    
    async def get_all_agent_info(self, agent_ids: List[str], ledger_url: str) -> List[AgentInfo]:
        """
        Get information about multiple ARC agents.
        
        Args:
            agent_ids: List of agent IDs to get information for
            ledger_url: URL of the ARC Ledger
            
        Returns:
            List of agent information objects
        """
        agent_info_list = []
        
        for agent_id in agent_ids:
            try:
                agent_info = await self.get_agent_info(agent_id, ledger_url)
                agent_info_list.append(agent_info)
            except Exception as e:
                print(f"Error getting information for agent {agent_id}: {str(e)}")
        
        return agent_info_list
