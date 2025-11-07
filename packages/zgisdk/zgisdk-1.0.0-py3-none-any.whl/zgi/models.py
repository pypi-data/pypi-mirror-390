"""
Models API - List and retrieve model information
"""

from typing import Dict, Any


class Models:
    """Models API resource"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> Dict[str, Any]:
        """
        List all available models
        
        Returns:
            List of model objects
        """
        return self.client._request("GET", "/models")
    
    def retrieve(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve information about a specific model
        
        Args:
            model_id: Model ID (e.g., "gpt-4")
            
        Returns:
            Model object with details
        """
        return self.client._request("GET", f"/models/{model_id}")
