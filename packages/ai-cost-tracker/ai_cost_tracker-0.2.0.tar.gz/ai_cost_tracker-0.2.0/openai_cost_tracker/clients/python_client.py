"""
Python Client SDK for Universal AI Cost Tracker
Use this in any Python project to track AI API calls
"""

import os
import time
import requests
import hashlib
from typing import Optional, Dict, Any
from functools import wraps

DEFAULT_TRACKER_URL = os.getenv("AI_TRACKER_URL", "http://localhost:8888")


class AITrackerClient:
    """Python client for universal AI cost tracker"""
    
    def __init__(self, tracker_url: str = DEFAULT_TRACKER_URL, service_name: Optional[str] = None):
        self.tracker_url = tracker_url
        self.service_name = service_name or self._detect_service_name()
        self.session = requests.Session()
    
    def _detect_service_name(self) -> str:
        """Auto-detect service name"""
        import sys
        return os.path.basename(sys.argv[0]) if sys.argv else "python_script"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key"""
        if not api_key:
            return "unknown"
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    def track_call(
        self,
        provider: str,
        api_key: str,
        api_type: str,
        model: str,
        operation: str,
        cost_usd: float,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Track an AI API call"""
        try:
            data = {
                "provider": provider,
                "api_key": api_key,
                "service_name": self.service_name,
                "language": "python",
                "api_type": api_type,
                "model": model,
                "operation": operation,
                "cost_usd": cost_usd,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "process_id": os.getpid(),
                **kwargs
            }
            
            response = self.session.post(
                f"{self.tracker_url}/api/track",
                json=data,
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            # Fail silently - don't break user's code
            return False
    
    def track_openai(self, response, model: str, api_key: str, cost_calculator=None):
        """Track OpenAI API call"""
        usage = getattr(response, 'usage', None)
        tokens_input = getattr(usage, 'prompt_tokens', 0) if usage else 0
        tokens_output = getattr(usage, 'completion_tokens', 0) if usage else 0
        
        if cost_calculator:
            cost = cost_calculator(model, tokens_input, tokens_output)
        else:
            # Default OpenAI pricing
            cost = (tokens_input / 1_000_000 * 2.50) + (tokens_output / 1_000_000 * 10.00)
        
        return self.track_call(
            provider="openai",
            api_key=api_key,
            api_type="chat",
            model=model,
            operation="create",
            cost_usd=cost,
            tokens_input=tokens_input,
            tokens_output=tokens_output
        )


# Decorator for automatic tracking
def track_ai_calls(provider: str, cost_calculator=None):
    """Decorator to automatically track AI API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = AITrackerClient()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Extract API key from kwargs or env
                api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY") or ""
                
                # Try to extract cost from result
                cost = 0.0
                if hasattr(result, 'usage'):
                    # OpenAI-style response
                    usage = result.usage
                    if cost_calculator:
                        cost = cost_calculator(result.model, usage.prompt_tokens, usage.completion_tokens)
                
                client.track_call(
                    provider=provider,
                    api_key=api_key,
                    api_type="unknown",
                    model=kwargs.get("model", "unknown"),
                    operation=func.__name__,
                    cost_usd=cost,
                    duration_ms=duration_ms
                )
                
                return result
            except Exception as e:
                # Track failed call
                client.track_call(
                    provider=provider,
                    api_key=kwargs.get("api_key", ""),
                    api_type="unknown",
                    model=kwargs.get("model", "unknown"),
                    operation=func.__name__,
                    cost_usd=0.0,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator


# Usage example:
"""
from openai_cost_tracker.clients.python_client import AITrackerClient, track_ai_calls
from openai import OpenAI

client = OpenAI()
tracker = AITrackerClient()

# Manual tracking
response = client.chat.completions.create(model="gpt-4", messages=[...])
tracker.track_openai(response, model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

# Automatic tracking with decorator
@track_ai_calls(provider="openai")
def my_ai_function():
    return client.chat.completions.create(...)
"""

