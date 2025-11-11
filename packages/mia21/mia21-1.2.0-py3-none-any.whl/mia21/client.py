"""Main Mia21 client implementation."""

import requests
import json
import uuid
import base64
from enum import Enum
from typing import Optional, List, Generator, Dict, Any
from .models import ChatMessage, Space, InitializeResponse, ChatResponse, Tool, ToolCall, StreamEvent
from .exceptions import Mia21Error, ChatNotInitializedError, APIError


class ResponseMode(str, Enum):
    """Response mode for chat requests"""
    TEXT = "text"
    STREAM_TEXT = "stream_text"
    STREAM_VOICE = "stream_voice"
    STREAM_VOICE_ONLY = "stream_voice_only"


class VoiceConfig:
    """Configuration for voice output"""
    
    def __init__(
        self,
        enabled: bool = True,
        voice_id: str = "P7x743VjyZEOihNNygQ9",
        elevenlabs_api_key: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ):
        """
        Initialize voice configuration.
        
        Args:
            enabled: Enable voice output
            voice_id: ElevenLabs voice ID
            elevenlabs_api_key: Customer's ElevenLabs API key (BYOK)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
        """
        self.enabled = enabled
        self.voice_id = voice_id
        self.elevenlabs_api_key = elevenlabs_api_key
        self.stability = stability
        self.similarity_boost = similarity_boost
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API requests"""
        return {
            "enabled": self.enabled,
            "voice_id": self.voice_id,
            "elevenlabs_api_key": self.elevenlabs_api_key,
            "stability": self.stability,
            "similarity_boost": self.similarity_boost
        }


class Mia21Client:
    """
    Mia21 Chat API Client
    
    Example:
        >>> from mia21 import Mia21Client
        >>> client = Mia21Client(api_key="your-api-key")
        >>> client.initialize()
        >>> response = client.chat("Hello!")
        >>> print(response.message)
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.mia21.com",
        user_id: Optional[str] = None,
        timeout: int = 90,
        customer_llm_key: Optional[str] = None
    ):
        """
        Initialize Mia21 client.
        
        Args:
            api_key: Your Mia21 API key (optional if using BYOK)
            base_url: API base URL (default: production)
            user_id: Unique user identifier (auto-generated if not provided)
            timeout: Request timeout in seconds (default: 90)
            customer_llm_key: Your LLM API key for BYOK (OpenAI or Gemini)
        """
        self.api_key = api_key
        self.customer_llm_key = customer_llm_key
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.user_id = user_id or str(uuid.uuid4())
        self.timeout = timeout
        self.current_space = None
        self._session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key
        self._session.headers.update(headers)
    
    def list_spaces(self) -> List[Space]:
        """
        List all available spaces.
        
        Returns:
            List of Space objects
            
        Example:
            >>> spaces = client.list_spaces()
            >>> for space in spaces:
            ...     print(f"{space.id}: {space.name}")
        """
        try:
            response = self._session.post(
                f"{self.api_url}/list_spaces",
                json={"app_id": self.user_id},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return [Space(**s) for s in data.get("spaces", [])]
        except requests.RequestException as e:
            raise APIError(f"Failed to list spaces: {e}")
    
    def initialize(
        self,
        space_id: str = "dr_panda",
        bot_id: Optional[str] = None,
        llm_type: str = "openai",
        user_name: Optional[str] = None,
        language: Optional[str] = None,
        generate_first_message: bool = True,
        incognito_mode: bool = False,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None
    ) -> InitializeResponse:
        """
        Initialize a chat session with a bot.
        
        Args:
            space_id: Space to use (default: "dr_panda")
            bot_id: Bot ID within the space (uses default bot if not specified)
            llm_type: "openai" or "gemini"
            user_name: User's display name
            language: Force language (e.g., "es", "de")
            generate_first_message: Generate AI greeting
            incognito_mode: Privacy mode (no data saved)
            customer_llm_key: Your LLM API key for BYOK (overrides instance key)
            space_config: Complete space configuration (for external/custom spaces)
            
        Returns:
            InitializeResponse with first message
            
        Example:
            >>> # Initialize with specific bot
            >>> response = client.initialize(
            ...     space_id="customer-support",
            ...     bot_id="sarah",
            ...     llm_type="openai",
            ...     customer_llm_key="your-openai-key"
            ... )
            >>> print(response.message)
            
            >>> # Initialize with default bot (bot_id omitted)
            >>> response = client.initialize(
            ...     space_id="customer-support",
            ...     llm_type="openai"
            ... )
        """
        try:
            payload = {
                "app_id": self.user_id,
                "space_id": space_id,
                "llm_type": llm_type,
                "user_name": user_name,
                "language": language,
                "generate_first_message": generate_first_message,
                "incognito_mode": incognito_mode
            }
            
            # Add bot_id if provided
            if bot_id:
                payload["bot_id"] = bot_id
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided (for external spaces)
            if space_config:
                payload["space_config"] = space_config
            
            response = self._session.post(
                f"{self.api_url}/initialize_chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.current_space = space_id
            return InitializeResponse(**data)
        except requests.RequestException as e:
            raise APIError(f"Failed to initialize chat: {e}")
    
    def chat(
        self,
        message: str,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None,
        llm_type: Optional[str] = None
    ) -> ChatResponse:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            space_id: Which space to chat with (uses current if not specified)
            bot_id: Which bot to chat with (uses default if not specified)
            temperature: Override temperature (0.0-2.0)
            max_tokens: Override max tokens
            customer_llm_key: Your LLM API key for BYOK (overrides instance key)
            space_config: Complete space configuration (for external spaces)
            llm_type: LLM type to use (overrides default)
            
        Returns:
            ChatResponse with AI message and tool_calls (if any)
            
        Example:
            >>> response = client.chat("I'm feeling anxious today", bot_id="sarah")
            >>> print(response.message)
            >>> if response.tool_calls:
            ...     print(f"Functions triggered: {[tc['name'] for tc in response.tool_calls]}")
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        try:
            payload = {
                "app_id": self.user_id,
                "space_id": space_id or self.current_space,
                "messages": [{"role": "user", "content": message}],
                "llm_type": llm_type or "openai",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Add bot_id if provided
            if bot_id:
                payload["bot_id"] = bot_id
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided
            if space_config:
                payload["space_config"] = space_config
            
            response = self._session.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return ChatResponse(**data)
        except requests.RequestException as e:
            raise APIError(f"Failed to send message: {e}")
    
    def stream_chat(
        self,
        message: str,
        space_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None,
        llm_type: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the response in real-time.
        
        Args:
            message: User message
            space_id: Which space to chat with
            temperature: Override temperature
            max_tokens: Override max tokens
            customer_llm_key: Your LLM API key for BYOK
            space_config: Complete space configuration (for external spaces)
            llm_type: LLM type to use
            
        Yields:
            Text chunks as they arrive
            
        Example:
            >>> for chunk in client.stream_chat("Tell me a story"):
            ...     print(chunk, end='', flush=True)
            
            >>> # With custom space
            >>> for chunk in client.stream_chat(
            ...     "Hello!",
            ...     space_config={
            ...         "space_id": "my_bot",
            ...         "prompt": "You are helpful",
            ...         "llm_identifier": "gemini-2.5-flash",
            ...         "temperature": 0.7,
            ...         "max_tokens": 1000
            ...     },
            ...     llm_type="gemini",
            ...     customer_llm_key="your-gemini-key"
            ... ):
            ...     print(chunk, end='', flush=True)
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        try:
            payload = {
                "app_id": self.user_id,
                "space_id": space_id or self.current_space,
                "messages": [{"role": "user", "content": message}],
                "llm_type": llm_type or "openai",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided
            if space_config:
                payload["space_config"] = space_config
            
            response = self._session.post(
                f"{self.api_url}/chat/stream",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data = json.loads(line_text[6:])
                        
                        # Handle errors (skip function_call conversion errors)
                        if 'error' in data and data['error']:
                            error_msg = data['error']
                            if 'function_call' not in error_msg and 'convert' not in error_msg.lower():
                                raise APIError(f"Streaming error: {error_msg}")
                        
                        # Handle function calls (logged but not yielded)
                        if data.get('type') == 'function_call':
                            # Function calls execute silently in background
                            continue
                        
                        # Handle text content
                        if 'content' in data:
                            yield data['content']
                        
                        # Handle completion
                        if data.get('done'):
                            # Log any tool calls that were triggered
                            if data.get('tool_calls'):
                                import logging
                                logging.info(f"Functions triggered: {[tc['name'] for tc in data['tool_calls']]}")
                            break
        except requests.RequestException as e:
            raise APIError(f"Failed to stream message: {e}")
    
    def chat_stream_v2(
        self,
        messages: List[Dict[str, str]],
        response_mode: ResponseMode = ResponseMode.STREAM_TEXT,
        voice_config: Optional[VoiceConfig] = None,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        llm_type: str = "openai",
        customer_llm_key: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Send chat with enhanced response modes including voice (v2 endpoint).
        
        Args:
            messages: Message history [{"role": "user", "content": "..."}]
            response_mode: Response mode (TEXT, STREAM_TEXT, STREAM_VOICE, STREAM_VOICE_ONLY)
            voice_config: Voice configuration for voice modes (required if using voice)
            space_id: Optional space ID
            bot_id: Optional bot ID
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            llm_type: LLM type ("openai" or "gemini")
            customer_llm_key: Your LLM API key for BYOK
            tools: List of tool definitions in OpenAI format (optional)
            tool_choice: Control tool usage: "auto", "none", or {"type": "function", "function": {"name": "..."}}
            
        Yields:
            Dict with:
                - type: "text" | "audio" | "tool_call" | "text_complete" | "done" | "error"
                - data: Content (string for text, dict for audio/tool_call)
                
        Examples:
            >>> # Simple text streaming
            >>> for event in client.chat_stream_v2(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     response_mode=ResponseMode.STREAM_TEXT
            ... ):
            ...     if event["type"] == "text":
            ...         print(event["data"], end="", flush=True)
            
            >>> # Voice streaming
            >>> from mia21 import ResponseMode, VoiceConfig
            >>> 
            >>> for event in client.chat_stream_v2(
            ...     messages=[{"role": "user", "content": "Tell me a joke"}],
            ...     response_mode=ResponseMode.STREAM_VOICE,
            ...     voice_config=VoiceConfig(
            ...         enabled=True,
            ...         elevenlabs_api_key="sk_..."
            ...     )
            ... ):
            ...     if event["type"] == "text":
            ...         print(event["data"], end="", flush=True)
            ...     elif event["type"] == "audio":
            ...         # Decode and play audio
            ...         audio_b64 = event["data"]["audio"]
            ...         audio_bytes = base64.b64decode(audio_b64)
            ...         # Save or play audio_bytes
        """
        payload = {
            "app_id": self.user_id,
            "messages": messages,
            "llm_type": llm_type,
            "response_mode": response_mode.value
        }
        
        # Optional parameters
        if space_id:
            payload["space_id"] = space_id
        if bot_id:
            payload["bot_id"] = bot_id
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if customer_llm_key or self.customer_llm_key:
            payload["customer_llm_key"] = customer_llm_key or self.customer_llm_key
        if voice_config:
            payload["voice_config"] = voice_config.to_dict()
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
        
        # For non-streaming mode (TEXT), use regular POST
        if response_mode == ResponseMode.TEXT:
            response = self._session.post(
                f"{self.api_url}/chat/stream-v2",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}", response.text)
            
            result = response.json()
            yield {"type": "done", "data": result}
            return
        
        # For streaming modes, use SSE
        try:
            response = self._session.post(
                f"{self.api_url}/chat/stream-v2",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}", response.text)
            
            # Process SSE stream
            current_event = None
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                
                # Event type
                if line.startswith("event: "):
                    current_event = line[7:].strip()
                    
                    # Handle simple events
                    if current_event == "text_complete":
                        yield {"type": "text_complete", "data": None}
                        current_event = None
                    elif current_event == "done":
                        yield {"type": "done", "data": None}
                        break
                    elif current_event == "error":
                        yield {"type": "error", "data": "Stream error"}
                        current_event = None
                    continue
                
                # Data line
                if line.startswith("data: "):
                    data_content = line[6:]
                    
                    # Handle [DONE] marker
                    if data_content == "[DONE]":
                        continue
                    
                    # Try to parse as JSON
                    if data_content.startswith("{"):
                        try:
                            data_json = json.loads(data_content)
                            
                            # Tool call event
                            if current_event == "tool_call" or data_json.get("type") == "tool_call":
                                yield {"type": "tool_call", "data": data_json}
                                current_event = None
                            # Audio chunk
                            elif "audio" in data_json:
                                yield {"type": "audio", "data": data_json}
                            # Error
                            elif "error" in data_json:
                                yield {"type": "error", "data": data_json["error"]}
                        except json.JSONDecodeError:
                            # Not valid JSON, treat as text
                            yield {"type": "text", "data": data_content}
                    else:
                        # Plain text chunk
                        yield {"type": "text", "data": data_content}
        
        except Exception as e:
            raise Mia21Error(f"Streaming failed: {str(e)}")
    
    def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Optional language code (e.g., 'en', 'es'). Auto-detect if None
            prompt: Optional context to guide transcription
            response_format: Response format (json, verbose_json, text, srt, vtt)
            temperature: Sampling temperature (0.0 - 1.0)
            openai_api_key: Your OpenAI API key (BYOK)
            
        Returns:
            Dict with transcription results
            
        Example:
            >>> result = client.transcribe_audio("recording.mp3", language="en")
            >>> print(result["text"])
            "Hello, this is a test"
        """
        try:
            url = f"{self.api_url}/stt/transcribe"
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'response_format': response_format,
                    'temperature': temperature
                }
                
                if language:
                    data['language'] = language
                if prompt:
                    data['prompt'] = prompt
                if openai_api_key:
                    data['openai_api_key'] = openai_api_key
                
                response = self._session.post(url, files=files, data=data, timeout=60)
                
                if response.status_code != 200:
                    raise APIError(f"Transcription failed: {response.status_code}", response.text)
                
                return response.json()
        
        except Exception as e:
            raise Mia21Error(f"Failed to transcribe audio: {str(e)}")
    
    def translate_audio(
        self,
        audio_file_path: str,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate audio in any language to English using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file
            prompt: Optional context to guide translation
            response_format: Response format (json, verbose_json, text, srt, vtt)
            temperature: Sampling temperature (0.0 - 1.0)
            openai_api_key: Your OpenAI API key (BYOK)
            
        Returns:
            Dict with translation results (always in English)
            
        Example:
            >>> result = client.translate_audio("spanish_audio.mp3")
            >>> print(result["text"])
            "Hello, how are you?"
        """
        try:
            url = f"{self.api_url}/stt/translate"
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'response_format': response_format,
                    'temperature': temperature
                }
                
                if prompt:
                    data['prompt'] = prompt
                if openai_api_key:
                    data['openai_api_key'] = openai_api_key
                
                response = self._session.post(url, files=files, data=data, timeout=60)
                
                if response.status_code != 200:
                    raise APIError(f"Translation failed: {response.status_code}", response.text)
                
                return response.json()
        
        except Exception as e:
            raise Mia21Error(f"Failed to translate audio: {str(e)}")

    def close(self, space_id: Optional[str] = None):
        """
        Close chat session and save conversation.
        
        Args:
            space_id: Which space to close (current if not specified)
            
        Example:
            >>> client.close()
        """
        try:
            response = self._session.post(
                f"{self.api_url}/close_chat",
                json={
                    "app_id": self.user_id,
                    "space_id": space_id or self.current_space
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to close chat: {e}")
    
    # Bot Management Methods
    
    def create_bot(
        self,
        space_id: str,
        bot_id: str,
        name: str,
        voice_id: str,
        additional_prompt: str = "",
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new bot within a space.
        
        Args:
            space_id: Space ID to create bot in
            bot_id: Unique bot identifier (e.g., "sarah", "alex")
            name: Display name for the bot
            voice_id: ElevenLabs voice ID
            additional_prompt: Additional prompt that adds to space's base_prompt
            is_default: Whether this is the default bot for the space
            
        Returns:
            Bot object with all details
            
        Example:
            >>> bot = client.create_bot(
            ...     space_id="customer-support",
            ...     bot_id="sarah",
            ...     name="Sarah",
            ...     voice_id="rachel_voice_id",
            ...     additional_prompt="You are warm and empathetic.",
            ...     is_default=True
            ... )
            >>> print(f"Created bot: {bot['name']}")
        """
        try:
            payload = {
                "bot_id": bot_id,
                "name": name,
                "voice_id": voice_id,
                "additional_prompt": additional_prompt,
                "is_default": is_default
            }
            
            response = self._session.post(
                f"{self.api_url}/customers/spaces/{space_id}/bots",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to create bot: {e}")
    
    def list_bots(self, space_id: str) -> List[Dict[str, Any]]:
        """
        List all bots in a space.
        
        Args:
            space_id: Space ID to list bots from
            
        Returns:
            List of bot objects
            
        Example:
            >>> bots = client.list_bots("customer-support")
            >>> for bot in bots:
            ...     print(f"{bot['name']} ({bot['bot_id']})")
        """
        try:
            response = self._session.get(
                f"{self.api_url}/customers/spaces/{space_id}/bots",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to list bots: {e}")
    
    def get_bot(self, space_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Get a specific bot.
        
        Args:
            space_id: Space ID
            bot_id: Bot ID
            
        Returns:
            Bot object
            
        Example:
            >>> bot = client.get_bot("customer-support", "sarah")
            >>> print(f"Voice: {bot['voice_id']}")
        """
        try:
            response = self._session.get(
                f"{self.api_url}/customers/spaces/{space_id}/bots/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to get bot: {e}")
    
    def update_bot(
        self,
        space_id: str,
        bot_id: str,
        name: Optional[str] = None,
        voice_id: Optional[str] = None,
        additional_prompt: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a bot.
        
        Args:
            space_id: Space ID
            bot_id: Bot ID to update
            name: New name (optional)
            voice_id: New voice ID (optional)
            additional_prompt: New additional prompt (optional)
            is_default: Set as default bot (optional)
            
        Returns:
            Updated bot object
            
        Example:
            >>> updated = client.update_bot(
            ...     space_id="customer-support",
            ...     bot_id="sarah",
            ...     voice_id="new_voice_id",
            ...     is_default=True
            ... )
        """
        try:
            payload = {}
            if name is not None:
                payload["name"] = name
            if voice_id is not None:
                payload["voice_id"] = voice_id
            if additional_prompt is not None:
                payload["additional_prompt"] = additional_prompt
            if is_default is not None:
                payload["is_default"] = is_default
            
            response = self._session.put(
                f"{self.api_url}/customers/spaces/{space_id}/bots/{bot_id}",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to update bot: {e}")
    
    def delete_bot(self, space_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Delete a bot.
        
        Args:
            space_id: Space ID
            bot_id: Bot ID to delete
            
        Returns:
            Success response
            
        Note:
            Cannot delete the last bot in a space (minimum 1 bot required)
            
        Example:
            >>> result = client.delete_bot("customer-support", "old-bot")
            >>> print(result['message'])
        """
        try:
            response = self._session.delete(
                f"{self.api_url}/customers/spaces/{space_id}/bots/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to delete bot: {e}")
    
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

