#!/usr/bin/env python3
"""
Automatic Interceptor for AI API Calls
Monkey-patches common libraries to automatically track without code changes
"""

import os
import sys
import importlib
import functools
import logging

logger = logging.getLogger(__name__)

# Global tracker instance (set via init)
_tracker = None


def init_auto_tracking():
    """Initialize automatic tracking - call this once at startup"""
    global _tracker
    
    if _tracker is None:
        try:
            from .cost_tracker import get_tracker
            _tracker = get_tracker()
            logger.debug("✅ Auto-tracking initialized with local CostTracker")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize auto-tracking: {e}")
            return False
    return True


def _track_call(func, provider, *args, **kwargs):
    """Track an API call automatically"""
    if not _tracker:
        init_auto_tracking()
    
    if not _tracker:
        return func(*args, **kwargs)
    
    import time
    start_time = time.time()
    
    try:
        result = func(*args, **kwargs)
        
        # Extract API key
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY") or ""
        
        # Determine API type and model
        api_type = "chat"
        model = kwargs.get("model", "gpt-3.5-turbo")
        
        # Try to extract cost/tokens from result
        cost = 0.0
        tokens_input = None
        tokens_output = None
        
        if hasattr(result, 'usage'):
            # OpenAI-style response
            usage = result.usage
            tokens_input = getattr(usage, 'prompt_tokens', 0)
            tokens_output = getattr(usage, 'completion_tokens', 0)
            # Calculate cost using CostTracker
            cost = _tracker.calculate_chat_cost(model, tokens_input or 0, tokens_output or 0)
        elif hasattr(result, 'created') and hasattr(result, 'data'):
            # Image generation response
            api_type = "image"
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")
            cost = _tracker.calculate_image_cost(model, size, quality)
        
        # Track the call
        try:
            _tracker.log_api_call(
                api_key=api_key,
                api_type=api_type,
                model=model,
                operation=func.__name__,
                cost=cost,
                tokens_input=tokens_input,
                tokens_output=tokens_output
            )
        except Exception as e:
            logger.debug(f"Failed to log API call: {e}")
        
        return result
    except Exception as e:
        # Track failed call
        if _tracker:
            try:
                _tracker.log_api_call(
                    api_key=kwargs.get("api_key", "") or os.getenv("OPENAI_API_KEY", ""),
                    api_type="unknown",
                    model=kwargs.get("model", "unknown"),
                    operation=func.__name__,
                    cost=0.0,
                    success=False,
                    error_message=str(e)[:500]
                )
            except Exception:
                pass  # Don't break user's code
        raise


def patch_openai():
    """Automatically patch OpenAI library"""
    try:
        import openai
        
        # Patch the OpenAI class's chat.completions.create method
        # We need to patch at the class level so it works for all instances
        original_class = openai.OpenAI
        
        # Store original if not already stored
        if not hasattr(original_class, '_original_init'):
            original_class._original_init = original_class.__init__
            
            def patched_init(self, *args, **kwargs):
                # Call original init
                original_class._original_init(self, *args, **kwargs)
                
                # Patch the chat.completions.create method on this instance
                if hasattr(self, 'chat') and hasattr(self.chat, 'completions'):
                    if not hasattr(self.chat.completions, '_original_create'):
                        self.chat.completions._original_create = self.chat.completions.create
                    
                    @functools.wraps(self.chat.completions._original_create)
                    def patched_create(*args, **kwargs):
                        return _track_call(self.chat.completions._original_create, "openai", *args, **kwargs)
                    
                    self.chat.completions.create = patched_create
                
                # Patch images.generate
                if hasattr(self, 'images') and hasattr(self.images, 'generate'):
                    if not hasattr(self.images, '_original_generate'):
                        self.images._original_generate = self.images.generate
                    
                    @functools.wraps(self.images._original_generate)
                    def patched_generate(*args, **kwargs):
                        return _track_call(self.images._original_generate, "openai", *args, **kwargs)
                    
                    self.images.generate = patched_generate
            
            original_class.__init__ = patched_init
        
        # Patch AsyncOpenAI similarly
        if hasattr(openai, 'AsyncOpenAI'):
            async_original_class = openai.AsyncOpenAI
            if not hasattr(async_original_class, '_original_init'):
                async_original_class._original_init = async_original_class.__init__
                
                def patched_async_init(self, *args, **kwargs):
                    # Call original init (AsyncOpenAI.__init__ is not async)
                    async_original_class._original_init(self, *args, **kwargs)
                    
                    # Patch methods after init
                    if hasattr(self, 'chat') and hasattr(self.chat, 'completions'):
                        if not hasattr(self.chat.completions, '_original_create'):
                            self.chat.completions._original_create = self.chat.completions.create
                        
                        @functools.wraps(self.chat.completions._original_create)
                        async def patched_async_create(*args, **kwargs):
                            result = await self.chat.completions._original_create(*args, **kwargs)
                            # Track after the call
                            if _tracker:
                                try:
                                    api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY") or ""
                                    model = kwargs.get("model", "gpt-3.5-turbo")
                                    if hasattr(result, 'usage'):
                                        usage = result.usage
                                        tokens_input = getattr(usage, 'prompt_tokens', 0)
                                        tokens_output = getattr(usage, 'completion_tokens', 0)
                                        cost = _tracker.calculate_chat_cost(model, tokens_input, tokens_output)
                                        _tracker.log_api_call(
                                            api_key=api_key,
                                            api_type="chat",
                                            model=model,
                                            operation="create",
                                            cost=cost,
                                            tokens_input=tokens_input,
                                            tokens_output=tokens_output
                                        )
                                except Exception:
                                    pass
                            return result
                        
                        self.chat.completions.create = patched_async_create
                
                async_original_class.__init__ = patched_async_init
        
        logger.debug("✅ OpenAI library auto-patched")
        return True
    except Exception as e:
        logger.debug(f"Failed to patch OpenAI: {e}")
        return False


def patch_anthropic():
    """Automatically patch Anthropic library"""
    try:
        import anthropic
        
        if not hasattr(anthropic.Anthropic.messages, '_original_create'):
            anthropic.Anthropic.messages._original_create = anthropic.Anthropic.messages.create
        
        @functools.wraps(anthropic.Anthropic.messages._original_create)
        def patched_create(self, *args, **kwargs):
            return _track_call(anthropic.Anthropic.messages._original_create, "anthropic", self, *args, **kwargs)
        
        anthropic.Anthropic.messages.create = patched_create
        
        logger.debug("✅ Anthropic library auto-patched")
        return True
    except Exception as e:
        logger.debug(f"Failed to patch Anthropic: {e}")
        return False


def auto_patch_all():
    """Auto-patch all supported libraries"""
    init_auto_tracking()
    patch_openai()
    patch_anthropic()
    # Add more providers as needed


# Don't auto-patch on import - let zero_config_tracker handle it
# This prevents double-patching when imported multiple times


# Usage: Just import this module and it works!
"""
# In your main.py or __init__.py, just add:
import openai_cost_tracker.services.auto_interceptor

# That's it! All OpenAI calls are now tracked automatically
# No need to modify any other files!
"""

