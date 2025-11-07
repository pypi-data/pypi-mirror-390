#!/usr/bin/env python3
"""
Zero-Configuration Automatic Tracking
Just import this module - no code changes needed!
Works by monkey-patching libraries at import time
"""

import os
import sys

# Set environment variable to enable auto-tracking
os.environ.setdefault("AI_AUTO_TRACK", "1")

# Import auto-interceptor (will auto-patch on import)
from .auto_interceptor import auto_patch_all, init_auto_tracking

# Initialize tracking
init_auto_tracking()

# Auto-patch all libraries
auto_patch_all()

# Success message (only if verbose mode is enabled)
if os.getenv("OPENAI_COST_TRACKER_VERBOSE", "0").lower() in ("1", "true", "yes"):
    print("✅ Zero-config AI tracking enabled!")
    print("   All OpenAI/Anthropic/etc. calls are now automatically tracked")
    print("   No code changes needed in your existing files!")


# Usage:
"""
# Just add ONE line at the top of your main file:
import openai_cost_tracker.services.zero_config_tracker

# That's it! All AI calls are now tracked automatically.
# Works with:
# - OpenAI
# - Anthropic
# - Any library we've patched

# No need to modify any other files!
"""

