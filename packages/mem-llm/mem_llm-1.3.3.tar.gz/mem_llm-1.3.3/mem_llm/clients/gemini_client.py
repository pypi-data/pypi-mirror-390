"""
Google Gemini LLM Client
=========================

Client for Google Gemini API (cloud service).

Features:
- Gemini 1.5 Pro, Flash, etc.
- Fast and powerful
- Large context window (up to 2M tokens)
- Multimodal support (text, images, video)

Setup:
1. Get API key from: https://makersuite.google.com/app/apikey
2. Set environment variable: export GEMINI_API_KEY="your-key"
   Or pass api_key parameter to constructor

Models:
- gemini-1.5-pro: Most capable model
- gemini-1.5-flash: Fastest model
- gemini-pro: Standard model

Author: C. Emre Karataş
Version: 1.3.0
"""

import requests
import time
import os
import json
from typing import List, Dict, Optional, Iterator
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_llm_client import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """
    Google Gemini API client implementation
    
    Supports Gemini models via Google AI Studio API.
    Requires API key from Google AI Studio.
    
    Usage:
        # Option 1: Using environment variable
        export GEMINI_API_KEY="your-api-key"
        client = GeminiClient(model="gemini-2.5-flash")
        
        # Option 2: Direct API key
        client = GeminiClient(
            model="gemini-2.5-flash",
            api_key="your-api-key"
        )
        
        response = client.chat([{"role": "user", "content": "Hello!"}])
    """
    
    # Available Gemini models
    MODELS = {
        'gemini-2.5-flash': 'Latest Gemini 2.5 Flash model (recommended)'
    }
    
    def __init__(self, 
                 model: str = "gemini-2.5-flash",
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize Gemini client
        
        Args:
            model: Gemini model name (default: gemini-2.5-flash)
            api_key: Google AI API key (if None, reads from GEMINI_API_KEY env var)
            **kwargs: Additional configuration
        
        Raises:
            ValueError: If API key is not provided
        """
        super().__init__(model=model, **kwargs)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. "
                "Set GEMINI_API_KEY environment variable or pass api_key parameter. "
                "Get key from: https://makersuite.google.com/app/apikey"
            )
        
        # API endpoints
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.chat_url = f"{self.base_url}/models/{self.model}:generateContent"
        self.stream_url = f"{self.base_url}/models/{self.model}:streamGenerateContent"
        
        # Add API key to URLs
        self.chat_url += f"?key={self.api_key}"
        self.stream_url += f"?key={self.api_key}"
        
        self.logger.debug(f"Initialized Gemini client with model: {model}")
    
    def check_connection(self) -> bool:
        """
        Check if Gemini API is accessible
        
        Returns:
            True if API is available
        """
        try:
            # Send a minimal test request
            test_payload = {
                "contents": [{
                    "parts": [{"text": "Hi"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            
            response = requests.post(
                self.chat_url,
                json=test_payload,
                timeout=10
            )
            
            # 200 = success, 400 might be rate limit or quota (but API is working)
            return response.status_code in [200, 400, 429]
            
        except Exception as e:
            self.logger.debug(f"Gemini connection check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List available Gemini models
        
        Returns:
            List of model identifiers
        """
        return list(self.MODELS.keys())
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             temperature: float = 0.7, 
             max_tokens: int = 2000,
             **kwargs) -> str:
        """
        Send chat request to Gemini API
        
        Args:
            messages: Message history in OpenAI format
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional Gemini-specific parameters
                     - top_p: Nucleus sampling (0.0-1.0)
                     - top_k: Top-K sampling
                     - safety_settings: Safety filter settings
            
        Returns:
            Model response text
            
        Raises:
            ConnectionError: If cannot connect to Gemini API
            ValueError: If invalid parameters or API key
        """
        # Validate messages
        self._validate_messages(messages)
        
        # Convert OpenAI format to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        # Build Gemini payload
        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40)
            }
        }
        
        # Add safety settings if provided
        if "safety_settings" in kwargs:
            payload["safetySettings"] = kwargs["safety_settings"]
        
        # Send request with retry logic
        max_retries = kwargs.get("max_retries", 3)
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.chat_url,
                    json=payload,
                    timeout=kwargs.get("timeout", 60)
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extract content from Gemini format
                    candidates = response_data.get('candidates', [])
                    if not candidates:
                        self.logger.warning("No candidates in Gemini response")
                        if attempt < max_retries - 1:
                            time.sleep(1.0 * (2 ** attempt))
                            continue
                        return ""
                    
                    # Get the first candidate's content
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    
                    if not parts:
                        self.logger.warning("No parts in Gemini response")
                        if attempt < max_retries - 1:
                            time.sleep(1.0 * (2 ** attempt))
                            continue
                        return ""
                    
                    # Combine all text parts
                    text_parts = [part.get('text', '') for part in parts if 'text' in part]
                    result = ' '.join(text_parts).strip()
                    
                    if not result:
                        self.logger.warning("Empty content in Gemini response")
                        if attempt < max_retries - 1:
                            time.sleep(1.0 * (2 ** attempt))
                            continue
                    
                    # Log usage metadata if available
                    usage_metadata = response_data.get('usageMetadata', {})
                    if usage_metadata:
                        self.logger.debug(
                            f"Gemini usage - "
                            f"prompt: {usage_metadata.get('promptTokenCount', 0)} tokens, "
                            f"response: {usage_metadata.get('candidatesTokenCount', 0)} tokens, "
                            f"total: {usage_metadata.get('totalTokenCount', 0)} tokens"
                        )
                    
                    # Check for safety ratings/blocks
                    finish_reason = candidates[0].get('finishReason', '')
                    if finish_reason == 'SAFETY':
                        self.logger.warning("Response blocked by Gemini safety filters")
                        safety_ratings = candidates[0].get('safetyRatings', [])
                        self.logger.debug(f"Safety ratings: {safety_ratings}")
                    
                    return result
                
                elif response.status_code == 400:
                    # Bad request - likely API key or parameter issue
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    self.logger.error(f"Gemini API error (400): {error_msg}")
                    
                    if "API_KEY" in error_msg.upper():
                        raise ValueError(f"Invalid Gemini API key. Get key from: https://makersuite.google.com/app/apikey")
                    
                    raise ValueError(f"Gemini API error: {error_msg}")
                
                elif response.status_code == 429:
                    # Rate limit - retry with exponential backoff
                    self.logger.warning(f"Gemini rate limit hit (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = min(30, 2.0 * (2 ** attempt))
                        time.sleep(wait_time)
                        continue
                    raise ConnectionError("Gemini API rate limit exceeded. Please try again later.")
                
                elif response.status_code == 403:
                    # Permission denied - quota or billing issue
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    raise ValueError(f"Gemini API permission denied: {error_msg}")
                
                else:
                    # Other errors
                    error_msg = f"Gemini API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('error', {}).get('message', response.text)
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                    
                    self.logger.error(error_msg)
                    
                    if attempt < max_retries - 1:
                        time.sleep(1.0 * (2 ** attempt))
                        continue
                    raise ConnectionError(error_msg)
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Gemini request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2.0 * (2 ** attempt))
                    continue
                raise ConnectionError("Gemini API request timeout. Please try again.")
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Cannot connect to Gemini API (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (2 ** attempt))
                    continue
                raise ConnectionError("Cannot connect to Gemini API. Check your internet connection.") from e
                
            except (ValueError, ConnectionError):
                # Re-raise our custom exceptions
                raise
                
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (2 ** attempt))
                    continue
                raise
        
        raise ConnectionError("Failed to get response after maximum retries")
    
    def chat_stream(self, 
                    messages: List[Dict[str, str]], 
                    temperature: float = 0.7, 
                    max_tokens: int = 2000,
                    **kwargs) -> Iterator[str]:
        """
        Send chat request to Gemini API with streaming response
        
        Args:
            messages: Message history in OpenAI format
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional Gemini-specific parameters
            
        Yields:
            Response text chunks as they arrive
            
        Raises:
            ConnectionError: If cannot connect to Gemini API
            ValueError: If invalid parameters or API key
        """
        # Validate messages
        self._validate_messages(messages)
        
        # Convert OpenAI format to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        # Build Gemini payload
        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40)
            }
        }
        
        # Add safety settings if provided
        if "safety_settings" in kwargs:
            payload["safetySettings"] = kwargs["safety_settings"]
        
        try:
            response = requests.post(
                self.stream_url,  # Use streaming endpoint
                json=payload,
                stream=True,  # Enable streaming
                timeout=kwargs.get("timeout", 60)
            )
            
            if response.status_code == 200:
                # Process Gemini streaming response
                # Gemini returns JSON objects separated by newlines
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line.decode('utf-8'))
                            
                            # Extract content from Gemini format
                            candidates = chunk_data.get('candidates', [])
                            if candidates:
                                content = candidates[0].get('content', {})
                                parts = content.get('parts', [])
                                
                                # Combine all text parts in this chunk
                                for part in parts:
                                    if 'text' in part:
                                        yield part['text']
                                        
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Failed to parse Gemini streaming chunk: {e}")
                            continue
            
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
                if "API_KEY" in error_msg.upper():
                    raise ValueError(f"Invalid Gemini API key. Get key from: https://makersuite.google.com/app/apikey")
                raise ValueError(f"Gemini API error: {error_msg}")
            
            elif response.status_code == 429:
                raise ConnectionError("Gemini API rate limit exceeded. Please try again later.")
            
            elif response.status_code == 403:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
                raise ValueError(f"Gemini API permission denied: {error_msg}")
            
            else:
                error_msg = f"Gemini API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('error', {}).get('message', response.text)
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                raise ConnectionError(error_msg)
                
        except requests.exceptions.Timeout:
            raise ConnectionError("Gemini API request timeout. Please try again.")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("Cannot connect to Gemini API. Check your internet connection.") from e
        except (ValueError, ConnectionError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in streaming: {e}")
            raise
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """
        Convert OpenAI message format to Gemini format
        
        OpenAI format: [{"role": "user/assistant/system", "content": "..."}]
        Gemini format: [{"role": "user/model", "parts": [{"text": "..."}]}]
        
        Args:
            messages: Messages in OpenAI format
            
        Returns:
            Messages in Gemini format
        """
        gemini_messages = []
        system_prompt = None
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '').strip()
            
            if not content:
                continue
            
            # Handle system messages (Gemini doesn't have system role)
            if role == 'system':
                # Prepend system prompt to first user message
                system_prompt = content
                continue
            
            # Convert role: assistant -> model
            gemini_role = 'model' if role == 'assistant' else 'user'
            
            # Build Gemini message
            gemini_msg = {
                "role": gemini_role,
                "parts": [{"text": content}]
            }
            
            # If this is the first user message and we have a system prompt,
            # prepend system prompt to the content
            if gemini_role == 'user' and system_prompt and not gemini_messages:
                gemini_msg["parts"][0]["text"] = f"{system_prompt}\n\n{content}"
                system_prompt = None  # Only use once
            
            gemini_messages.append(gemini_msg)
        
        return gemini_messages
    
    def get_info(self) -> Dict:
        """
        Get comprehensive client information
        
        Returns:
            Dictionary with client metadata
        """
        base_info = super().get_info()
        
        # Add Gemini-specific info
        base_info['api_status'] = 'configured' if self.api_key else 'missing_key'
        base_info['model_description'] = self.MODELS.get(self.model, 'Unknown model')
        base_info['available_models'] = self.list_models()
        
        return base_info

