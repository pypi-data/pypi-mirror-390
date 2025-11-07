"""
Chat API - OpenAI-compatible chat completions
"""

from typing import List, Dict, Any, Optional, Union


class ChatCompletions:
    """Chat completions API"""
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion
        
        Args:
            model: Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: List of message objects with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stream: Whether to stream responses
            stop: Stop sequences
            max_tokens: Maximum tokens to generate
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            logit_bias: Token bias dictionary
            user: Unique user identifier
            
        Returns:
            Chat completion response
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        
        if stop is not None:
            data["stop"] = stop
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if logit_bias is not None:
            data["logit_bias"] = logit_bias
        if user is not None:
            data["user"] = user
        
        # Add any additional kwargs
        data.update(kwargs)
        
        return self.client._request("POST", "/chat/completions", data=data)


class Chat:
    """Chat API resource"""
    
    def __init__(self, client):
        self.completions = ChatCompletions(client)
