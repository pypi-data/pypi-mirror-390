"""
Files API - Upload and manage files
"""

from typing import BinaryIO, Dict, Any, List, Optional


class Files:
    """Files API resource"""
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        file: BinaryIO,
        purpose: str,
    ) -> Dict[str, Any]:
        """
        Upload a file for use with other API endpoints
        
        Args:
            file: File object to upload
            purpose: Purpose of the file (e.g., "fine-tune", "assistants")
            
        Returns:
            File object with id, filename, purpose, etc.
        """
        files = {
            "file": file,
        }
        data = {
            "purpose": purpose,
        }
        
        # For multipart/form-data, we need to send purpose as form field
        return self.client._request(
            "POST",
            "/files",
            files=files,
            data=data,
        )
    
    def list(self, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        List all uploaded files
        
        Args:
            purpose: Filter by purpose
            
        Returns:
            List of file objects
        """
        params = {}
        if purpose:
            params["purpose"] = purpose
        
        return self.client._request("GET", "/files", params=params)
    
    def retrieve(self, file_id: str) -> Dict[str, Any]:
        """
        Retrieve information about a specific file
        
        Args:
            file_id: File ID
            
        Returns:
            File object
        """
        return self.client._request("GET", f"/files/{file_id}")
    
    def delete(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file
        
        Args:
            file_id: File ID to delete
            
        Returns:
            Deletion status
        """
        return self.client._request("DELETE", f"/files/{file_id}")
    
    def content(self, file_id: str) -> bytes:
        """
        Retrieve file content
        
        Args:
            file_id: File ID
            
        Returns:
            File content as bytes
        """
        import requests
        url = f"{self.client.base_url}/files/{file_id}/content"
        headers = self.client._get_headers()
        
        response = requests.get(url, headers=headers, timeout=self.client.timeout)
        response.raise_for_status()
        return response.content
