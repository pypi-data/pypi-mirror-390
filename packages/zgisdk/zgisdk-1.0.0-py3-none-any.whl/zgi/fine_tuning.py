"""
Fine-tuning API - Create and manage fine-tuning jobs
"""

from typing import Dict, Any, Optional, List


class FineTuningJobs:
    """Fine-tuning jobs API"""
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        training_file: str,
        model: str,
        validation_file: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        suffix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a fine-tuning job
        
        Args:
            training_file: File ID of training data
            model: Base model to fine-tune
            validation_file: File ID of validation data (optional)
            hyperparameters: Hyperparameters for fine-tuning
            suffix: Custom suffix for fine-tuned model name
            
        Returns:
            Fine-tuning job object
        """
        data = {
            "training_file": training_file,
            "model": model,
        }
        
        if validation_file:
            data["validation_file"] = validation_file
        if hyperparameters:
            data["hyperparameters"] = hyperparameters
        if suffix:
            data["suffix"] = suffix
        
        return self.client._request("POST", "/fine_tuning/jobs", data=data)
    
    def list(self, limit: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """
        List fine-tuning jobs
        
        Args:
            limit: Number of jobs to return
            after: Cursor for pagination
            
        Returns:
            List of fine-tuning jobs
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        
        return self.client._request("GET", "/fine_tuning/jobs", params=params)
    
    def retrieve(self, job_id: str) -> Dict[str, Any]:
        """
        Retrieve fine-tuning job details
        
        Args:
            job_id: Fine-tuning job ID
            
        Returns:
            Fine-tuning job object
        """
        return self.client._request("GET", f"/fine_tuning/jobs/{job_id}")
    
    def cancel(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a fine-tuning job
        
        Args:
            job_id: Fine-tuning job ID
            
        Returns:
            Updated job object
        """
        return self.client._request("POST", f"/fine_tuning/jobs/{job_id}/cancel")
    
    def list_events(
        self,
        job_id: str,
        limit: int = 20,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List events for a fine-tuning job
        
        Args:
            job_id: Fine-tuning job ID
            limit: Number of events to return
            after: Cursor for pagination
            
        Returns:
            List of events
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        
        return self.client._request(
            "GET",
            f"/fine_tuning/jobs/{job_id}/events",
            params=params,
        )


class FineTuning:
    """Fine-tuning API resource"""
    
    def __init__(self, client):
        self.jobs = FineTuningJobs(client)
