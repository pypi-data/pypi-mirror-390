"""
Mia21 Portal Client - For use with portal backend API.

This client works with the customer portal backend which handles
BYOK (Bring Your Own Key) automatically using stored customer credentials.
"""

import requests
import json
import uuid
from typing import Optional, List, Generator, Dict, Any
from .models import ChatMessage, Space, InitializeResponse, ChatResponse
from .exceptions import Mia21Error, ChatNotInitializedError, APIError


class Mia21PortalClient:
    """
    Mia21 Portal API Client (for portal backend with automatic BYOK)
    
    This client is designed for customers who have registered at app.mia21.com
    and want to use their stored LLM keys automatically.
    
    Example:
        >>> from mia21 import Mia21PortalClient
        >>> client = Mia21PortalClient(api_key="mia_sk_cust_...")
        >>> client.initialize(space_id="my-space")
        >>> response = client.chat("Hello!")
        >>> print(response.message)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://mia-app-backend-795279012747.us-central1.run.app",
        timeout: int = 90
    ):
        """
        Initialize Mia21 Portal client.
        
        Args:
            api_key: Your Mia customer API key (from app.mia21.com)
            base_url: Portal backend URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1/chat"
        self.timeout = timeout
        self.user_id = str(uuid.uuid4())  # Generate unique end-user ID
        self.current_space = None
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": api_key
        })
    
    def initialize(
        self,
        space_id: str,
        user_name: Optional[str] = None,
        llm_type: str = "openai",
        generate_first_message: bool = True,
        user_id: Optional[str] = None
    ) -> InitializeResponse:
        """
        Initialize a chat session.
        
        Args:
            space_id: Space ID to use
            user_name: End-user's display name
            llm_type: LLM type (openai/gemini) - uses your stored key
            generate_first_message: Whether to generate AI greeting
            user_id: Optional custom user_id (auto-generated if not provided)
            
        Returns:
            InitializeResponse with first message
        """
        if user_id:
            self.user_id = user_id
            
        try:
            payload = {
                "user_id": self.user_id,
                "space_id": space_id,
                "user_name": user_name or "User",
                "llm_type": llm_type,
                "generate_first_message": generate_first_message
            }
            
            response = self._session.post(
                f"{self.api_url}/initialize",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.current_space = data.get("space_id", space_id)
            
            return InitializeResponse(
                user_id=data.get("user_id", self.user_id),
                space_id=self.current_space,
                message=data.get("first_message"),
                is_new_user=data.get("is_new_user", True)
            )
        except requests.RequestException as e:
            raise APIError(f"Failed to initialize chat: {e}")
    
    def chat(
        self,
        message: str,
        space_id: Optional[str] = None,
        llm_type: Optional[str] = None
    ) -> ChatResponse:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            space_id: Which space to chat with (uses current if not specified)
            llm_type: LLM type (uses initialization default if not specified)
            
        Returns:
            ChatResponse with AI message
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        try:
            payload = {
                "user_id": self.user_id,
                "message": message,
                "space_id": space_id or self.current_space
            }
            
            if llm_type:
                payload["llm_type"] = llm_type
            
            response = self._session.post(
                f"{self.api_url}/message",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return ChatResponse(
                message=data.get("response", ""),
                user_id=data.get("user_id", self.user_id),
                space_id=data.get("space_id", self.current_space),
                llm_type=data.get("llm_type", "openai"),
                tool_calls=[]  # Portal backend doesn't expose tool calls
            )
        except requests.RequestException as e:
            raise APIError(f"Failed to send message: {e}")
    
    def close(self, space_id: Optional[str] = None):
        """
        Close chat session.
        
        Args:
            space_id: Which space to close (current if not specified)
        """
        try:
            response = self._session.post(
                f"{self.api_url}/close",
                json={
                    "user_id": self.user_id,
                    "space_id": space_id or self.current_space
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to close chat: {e}")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close on context exit."""
        if self.current_space:
            try:
                self.close()
            except:
                pass

