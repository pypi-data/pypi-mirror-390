# gptquery/core/client.py
"""
TODO
[ ] REMOVE the default_model architecture and make it such that it forces to provide a model.  
    Anyways, defualts are handled at `prompt_fucntion()` entry point.
"""

import requests
import time
import random
from typing import Optional, Dict, Any

class ModelValidationError(Exception):
    """Raised when an invalid model is specified."""
    pass

class APIError(Exception):
    """General API error."""
    pass

class RateLimitError(Exception):
    """Rate limit exceeded error."""
    pass

class AuthenticationError(Exception):
    """Invalid API key error."""
    pass

class GPTClient:
    """Multi-provider GPT API client with model validation and configurable retry logic."""
    # Provider configurations
    PROVIDER_CONFIGS = {
        "openai": {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "models": [
                "gpt-5","gpt-5-2025-08-07",
                "gpt-5-mini","gpt-5-mini-2025-08-07",
                "gpt-5-nano","gpt-5-nano-2025-08-07",
                "gpt-4.1","gpt-4.1-2025-04-14",
                "gpt-4o", "gpt-4o-audio", "chatgpt-4o",
                "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o-mini", 
                "o3", "o3-mini", "o4-mini",
                "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
            ],
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "user_agent": "GPT-Query-OpenAI-Client"
        },
        "perplexity": {
            "api_url": "https://api.perplexity.ai/chat/completions",
            "models": [
                "sonar", "sonar-pro",
                "sonar-reasoning", "sonar-reasoning-pro", 
                "sonar-deep-research",
                "sonar-small", "sonar-medium",
                "llama-3.1-sonar-large-128k-online", 
                "llama-3.1-sonar-small-128k-online",
                "llama-3.1-sonar-huge-128k-online",
                "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"
            ],
            "auth_header": "Authorization", 
            "auth_prefix": "Bearer ",
            "user_agent": "GPT-Query-Perplexity-Client"
        },
        "claude": {
            "api_url": "https://api.anthropic.com/v1/messages",
            "models": [
                'claude-haiku-4-5-20251001',
                'claude-sonnet-4-5-20250929',
                'claude-opus-4-1-20250805',
                'claude-opus-4-20250514',
                'claude-sonnet-4-20250514',
                'claude-3-7-sonnet-20250219',
                'claude-3-5-haiku-20241022',
                'claude-3-haiku-20240307',
                'claude-3-opus-20240229',
                "claude-3-5-sonnet-20241022", 
                "claude-3-5-haiku-20241022", 
                "claude-3-opus-20240229", 
                "claude-3-sonnet-20240229"
            ],
            "auth_header": "x-api-key",
            "auth_prefix": "",
            "user_agent": "GPT-Query-Claude-Client"
        }
    }
    
    def __init__(self, api_key: str, default_model: str = "gpt-4.1-mini", provider: str = "openai"):
        """Initialize multi-provider GPT client."""
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key is required")
            
        if provider not in self.PROVIDER_CONFIGS:
            available = list(self.PROVIDER_CONFIGS.keys())
            raise ValueError(f"Unsupported provider: {provider}. Available: {available}")
        
        self.provider = provider
        self.api_key = api_key
        
        # SET provider-specific configuration
        config = self.PROVIDER_CONFIGS[provider]
        self.api_url = config["api_url"]
        self.AVAILABLE_MODELS = config["models"]
        self.auth_header = config["auth_header"]
        self.auth_prefix = config["auth_prefix"] 
        self.user_agent = config["user_agent"]
        
        # Set default model (with provider-specific fallback)
        if provider == "perplexity" and default_model == "gpt-4.1-mini":
            self.default_model = "sonar-pro"
        elif provider == "claude" and default_model == "gpt-4.1-mini":
            self.default_model = "claude-3-5-sonnet-20241022"
        else:
            self.default_model = default_model
        
        # Validate default model
        if self.default_model not in self.AVAILABLE_MODELS:
            self._handle_invalid_default_model()

    def extract(self, text: str, prompt: str, model: Optional[str] = None, 
                max_tokens: int = 5000, temperature: float = 0.0, top_p: float = 1.0,
                frequency_penalty: float = 0.0, presence_penalty: float = 0.0, 
                timeout: int = 60, max_retries: int = 3) -> str:
        """Extract information using GPT with provider-agnostic interface."""
        
        model = model or self.default_model
        self._validate_model(model)
        
        if not text or not prompt:
            raise APIError("Both text and prompt are required")
        
        # Route to provider-specific implementation
        if self.provider in ["openai", "perplexity"]:
            return self._extract_openai_format(text, prompt, model, timeout, max_retries, 
                                             max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
        elif self.provider == "claude":
            return self._extract_claude_format(text, prompt, model, timeout, max_retries, max_tokens, temperature)
        else:
            raise APIError(f"Unsupported provider routing: {self.provider}")

    def _extract_openai_format(self, text: str, prompt: str, model: str, timeout: int, max_retries: int,
                              max_tokens: int, temperature: float, top_p: float, 
                              frequency_penalty: float, presence_penalty: float) -> str:
        """Handle OpenAI/Perplexity compatible format"""
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        headers = {
            self.auth_header: f"{self.auth_prefix}{self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent
        }
        
        return self._make_request(payload, headers, timeout, max_retries)

    def _extract_claude_format(self, text: str, prompt: str, model: str, timeout: int, max_retries: int,
                              max_tokens: int, temperature: float) -> str:
        """Handle Claude-specific format"""
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": f"{prompt}\n\nText: {text}"}
            ]
        }
        
        headers = {
            self.auth_header: self.api_key,
            "Content-Type": "application/json", 
            "anthropic-version": "2023-06-01",
            "User-Agent": self.user_agent
        }
        
        return self._make_request(payload, headers, timeout, max_retries)

    def _make_request(self, payload: dict, headers: dict, timeout: int, max_retries: int) -> str:
        """Unified request handling for all providers"""
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=timeout)
                
                if response.status_code == 200:
                    response_data = response.json()
                    return self._extract_content(response_data)
                elif response.status_code == 401:
                    raise AuthenticationError(f"Invalid API key for {self.provider}")
                elif response.status_code == 429:
                    if attempt < max_retries:
                        wait_time = self._calculate_backoff(attempt)
                        print(f"Rate limited by {self.provider}, waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError(f"Rate limit exceeded for {self.provider}")
                elif response.status_code == 400:
                    error_detail = self._extract_error_detail(response)
                    raise APIError(f"Bad request to {self.provider}: {error_detail}")
                else:
                    raise APIError(f"{self.provider} HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Request timeout to {self.provider}")
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Connection error to {self.provider}")
            except requests.exceptions.RequestException as e:
                raise APIError(f"Request to {self.provider} failed: {str(e)}")
        
        raise APIError("Unexpected error in retry logic")

    def _validate_model(self, model: str) -> None:
        """Validate model for current provider."""
        if model not in self.AVAILABLE_MODELS:
            suggestions = [m for m in self.AVAILABLE_MODELS if model.lower() in m.lower()]
            error_msg = f"Invalid model '{model}' for provider '{self.provider}'"
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions[:3])}?"
            error_msg += f"\nAvailable {self.provider} models:\n" + "\n".join(f"- {model}" for model in self.AVAILABLE_MODELS)
            raise ModelValidationError(error_msg)

    def _handle_invalid_default_model(self):
        """Handle invalid default model."""
        suggestions = [m for m in self.AVAILABLE_MODELS if self.default_model.lower() in m.lower()]
        error_msg = f"Invalid default model '{self.default_model}' for provider '{self.provider}'"
        if suggestions:
            error_msg += f". Did you mean: {', '.join(suggestions[:3])}?"
        error_msg += f"\nAvailable {self.provider} models:\n" + "\n".join(f"- {model}" for model in self.AVAILABLE_MODELS)
        raise ModelValidationError(error_msg)

    def _extract_content(self, response_data: Dict[str, Any]) -> str:
        """Extract content from API response (handles both OpenAI and Claude formats)."""
        try:
            # Claude format
            if self.provider == "claude":
                if "content" in response_data and len(response_data["content"]) > 0:
                    return response_data["content"][0]["text"]
                else:
                    raise APIError(f"Unexpected Claude response structure: {response_data}")
            
            # OpenAI/Perplexity format
            else:
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    else:
                        raise APIError(f"Unexpected {self.provider} response: missing message content")
                else:
                    raise APIError(f"Unexpected {self.provider} response: no choices")
                    
        except (KeyError, IndexError, TypeError) as e:
            raise APIError(f"Failed to parse {self.provider} response: {str(e)}")

    def _extract_error_detail(self, response: requests.Response) -> str:
        """Extract error details from failed response."""
        try:
            error_data = response.json()
            if "error" in error_data and "message" in error_data["error"]:
                return error_data["error"]["message"]
            else:
                return response.text
        except:  # noqa: E722
            return response.text

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter."""
        base_delay = 2 ** attempt
        jitter = random.uniform(0.1, 0.5)
        return base_delay + jitter

    def get_available_models(self) -> list:
        """Return available models for current provider."""
        return self.AVAILABLE_MODELS.copy()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Return current provider configuration info."""
        return {
            "provider": self.provider,
            "api_url": self.api_url,
            "default_model": self.default_model,
            "available_models": self.AVAILABLE_MODELS.copy()
        }
