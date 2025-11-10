"""
Base adaptor class for ARC Protocol integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List


class BaseAdaptor(ABC):
    """
    Base class for all ARC Protocol adaptors.
    
    Adaptors provide integration between the ARC Protocol and various AI services,
    frameworks, or tools. They handle the translation between ARC's communication
    format and the target system's API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adaptor with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the adaptor configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an ARC request and return the response.
        
        Args:
            request: ARC request object
            
        Returns:
            ARC response object
        """
        pass
    
    @abstractmethod
    async def translate_to_native(self, arc_request: Dict[str, Any]) -> Any:
        """
        Translate an ARC request to the native format of the target system.
        
        Args:
            arc_request: ARC request object
            
        Returns:
            Request in the native format of the target system
        """
        pass
    
    @abstractmethod
    async def translate_from_native(self, native_response: Any) -> Dict[str, Any]:
        """
        Translate a native response from the target system to an ARC response.
        
        Args:
            native_response: Response from the target system
            
        Returns:
            ARC response object
        """
        pass
