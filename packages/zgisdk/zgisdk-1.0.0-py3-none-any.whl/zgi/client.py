"""
ZGI Client - OpenAI-compatible API client
"""

import os
import requests
from typing import Optional, Dict, Any, List, Union
from .chat import Chat
from .files import Files
from .models import Models
from .fine_tuning import FineTuning


class ZGI:
    """
    ZGI API Client - OpenAI-compatible interface
    
    Usage:
        from zgi import ZGI
        
        client = ZGI(api_key="your-api-key")
        
        # Chat completions
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        
        # File upload
        file = client.files.create(
            file=open("data.jsonl", "rb"),
            purpose="fine-tune"
        )
        
        # Fine-tuning
        job = client.fine_tuning.jobs.create(
            training_file=file.id,
            model="gpt-3.5-turbo"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize ZGI client
        
        Args:
            api_key: Your ZGI API key (or set ZGI_API_KEY environment variable)
            base_url: Base URL for API requests (default: https://api.zgi.ai/v1)
            organization: Organization ID (optional)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("ZGI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set it via api_key parameter or ZGI_API_KEY environment variable."
            )
        
        self.base_url = base_url or os.getenv("ZGI_BASE_URL", "https://api.zgi.ai/v1")
        self.organization = organization or os.getenv("ZGI_ORGANIZATION")
        self.timeout = timeout
        
        # Initialize API resources
        self.chat = Chat(self)
        self.files = Files(self)
        self.models = Models(self)
        self.fine_tuning = FineTuning(self)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            data: JSON data to send
            files: Files to upload
            params: URL query parameters
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        # Remove Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not files else None,
                files=files,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
