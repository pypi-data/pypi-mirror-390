"""Tools adapter for creating ARC Protocol handoff tools for LangChain.

This module provides functionality to create handoff tools that enable communication
between LangChain agents and ARC Protocol agents.
"""

import asyncio
import re
import uuid
from typing import Any, Dict, List, Optional, Union, cast

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from arc import Client as ARCClient
from arc.models import Message, Part, Role, TaskObject, TaskStatus

# Constants
WHITESPACE_RE = re.compile(r"\s+")
METADATA_KEY_HANDOFF_DESTINATION = "__handoff_destination"
METADATA_KEY_IS_HANDOFF_BACK = "__is_handoff_back"


def _normalize_agent_name(agent_name: str) -> str:
    """Normalize an agent name to be used inside the tool name."""
    return WHITESPACE_RE.sub("_", agent_name.strip()).lower()


class AgentInfo(BaseModel):
    """Information about an ARC agent."""
    
    id: str = Field(..., description="Agent ID used for ARC Protocol communication")
    name: str = Field(..., description="Human-readable name of the agent")
    url: str = Field(..., description="ARC endpoint URL for the agent")
    description: Optional[str] = Field(None, description="Description of the agent's capabilities")


class HandoffToolParams(BaseModel):
    """Parameters for handoff tool."""
    
    message: str = Field(
        ..., 
        description="Message to send to the target agent"
    )


def create_arc_handoff_tool(
    agent_info: AgentInfo,
    arc_client: ARCClient,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> BaseTool:
    """Create a tool that can handoff control to an ARC Protocol agent.
    
    Args:
        agent_info: Information about the target agent
        arc_client: ARC client for communication
        name: Optional name of the tool to use for the handoff.
            If not provided, the tool name will be `transfer_to_<agent_name>`.
        description: Optional description for the handoff tool.
            If not provided, the description will be `Ask agent <agent_name> for help`.
            
    Returns:
        A LangChain tool that handles handoff to the ARC agent
    """
    if name is None:
        name = f"transfer_to_{_normalize_agent_name(agent_info.name)}"
    
    if description is None:
        description = f"Ask agent '{agent_info.name}' for help"
    
    async def _handoff_to_agent(message: str) -> str:
        """Handle the handoff to an ARC agent.
        
        Args:
            message: Message to send to the target agent
            
        Returns:
            Response from the target agent
        """
        try:
            # Create a message for the ARC Protocol
            arc_message = {
                "role": "user",
                "parts": [{"type": "TextPart", "content": message}]
            }
            
            # Create a task with the target agent
            response = await arc_client.task.create(
                target_agent=agent_info.id,
                initial_message=arc_message
            )
            
            # Get the task ID from the response
            task_result = response.get("result", {})
            if not task_result or task_result.get("type") != "task":
                return f"Error: Unexpected response format from agent {agent_info.name}"
                
            task = task_result.get("task", {})
            task_id = task.get("taskId")
            
            if not task_id:
                return f"Error: Failed to create task with agent {agent_info.name}"
            
            # Wait for the task to complete
            max_attempts = 10
            attempt = 0
            task_status = task.get("status", "SUBMITTED")
            
            while task_status not in ["COMPLETED", "FAILED", "CANCELED"] and attempt < max_attempts:
                await asyncio.sleep(1)  # Wait before checking status
                attempt += 1
                
                # Get task status
                info_response = await arc_client.task.info(
                    target_agent=agent_info.id,
                    task_id=task_id
                )
                
                task_info = info_response.get("result", {}).get("task", {})
                task_status = task_info.get("status", task_status)
                
                if task_status == "COMPLETED":
                    # Get the last message from the agent
                    messages = task_info.get("messages", [])
                    if messages:
                        agent_messages = [m for m in messages if m.get("role") == "agent"]
                        if agent_messages:
                            last_message = agent_messages[-1]
                            parts = last_message.get("parts", [])
                            content_parts = [p.get("content", "") for p in parts if p.get("type") == "TextPart"]
                            return " ".join(content_parts)
                    
                    return f"Task completed by {agent_info.name}, but no response message was found."
                
                elif task_status == "FAILED":
                    return f"Task failed: {task_info.get('reason', 'Unknown error')}"
                
                elif task_status == "CANCELED":
                    return f"Task was canceled: {task_info.get('reason', 'No reason provided')}"
            
            if attempt >= max_attempts:
                return f"Timeout waiting for response from {agent_info.name}"
            
            return f"Unexpected error communicating with {agent_info.name}"
            
        except Exception as e:
            return f"Error during handoff to {agent_info.name}: {str(e)}"
    
    return StructuredTool(
        name=name,
        description=description,
        args_schema=HandoffToolParams,
        func=lambda **kwargs: asyncio.run(_handoff_to_agent(kwargs.get("message", ""))),
        coroutine=_handoff_to_agent,
        return_direct=False,
        metadata={METADATA_KEY_HANDOFF_DESTINATION: agent_info.id}
    )


async def load_arc_handoff_tools(
    agent_ids: List[str],
    ledger_url: str,
    arc_client: ARCClient,
) -> List[BaseTool]:
    """Load handoff tools for ARC Protocol agents.
    
    Args:
        agent_ids: List of agent IDs to create tools for
        ledger_url: URL of the ARC Ledger for retrieving agent information
        arc_client: ARC client for communication
        
    Returns:
        List of LangChain tools for handoff to ARC agents
    """
    tools = []
    
    # Create a temporary client to fetch agent information
    async with ARCClient(endpoint=ledger_url) as ledger_client:
        for agent_id in agent_ids:
            try:
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
                if result and result.get("type") == "task":
                    task = result.get("task", {})
                    artifacts = task.get("artifacts", [])
                    
                    # Find the agent info artifact
                    for artifact in artifacts:
                        parts = artifact.get("parts", [])
                        for part in parts:
                            if part.get("type") == "DataPart":
                                agent_data = part.get("content", {})
                                if agent_data and isinstance(agent_data, dict):
                                    # Create agent info object
                                    agent_info = AgentInfo(
                                        id=agent_id,
                                        name=agent_data.get("name", agent_id),
                                        url=agent_data.get("url", ""),
                                        description=agent_data.get("description", "")
                                    )
                                    
                                    # Create and add the handoff tool
                                    tool = create_arc_handoff_tool(agent_info, arc_client)
                                    tools.append(tool)
                                    break
            
            except Exception as e:
                print(f"Error loading agent {agent_id}: {str(e)}")
                continue
    
    return tools


def convert_langchain_message_to_arc(message: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a LangChain message to ARC Protocol format.
    
    Args:
        message: LangChain message
        
    Returns:
        ARC Protocol message
    """
    role = "user"
    if message.get("type") == "ai":
        role = "agent"
    elif message.get("type") == "system":
        role = "system"
    
    content = message.get("content", "")
    
    # Create ARC message
    arc_message = {
        "role": role,
        "parts": [{"type": "TextPart", "content": content}]
    }
    
    return arc_message


def convert_arc_message_to_langchain(message: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an ARC Protocol message to LangChain format.
    
    Args:
        message: ARC Protocol message
        
    Returns:
        LangChain message
    """
    role = message.get("role", "user")
    
    # Map ARC roles to LangChain types
    message_type = "human"
    if role == "agent":
        message_type = "ai"
    elif role == "system":
        message_type = "system"
    
    # Extract content from parts
    content = ""
    parts = message.get("parts", [])
    for part in parts:
        if part.get("type") == "TextPart":
            content += part.get("content", "")
    
    # Create LangChain message
    lc_message = {
        "type": message_type,
        "content": content
    }
    
    return lc_message
