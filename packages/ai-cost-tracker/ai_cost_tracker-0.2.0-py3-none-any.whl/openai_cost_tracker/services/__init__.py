"""Services module for OpenAI Cost Tracker"""

from .cost_tracker import CostTracker, get_tracker, PRICING, APIUsageRecord
from .openai_scanner import OpenAIScanner, OpenAIUsage
from .universal_tracker import UniversalCostTracker, UniversalTrackerAPI, SUPPORTED_PROVIDERS
from .system_scanner import SystemWideScanner, SystemAIUsage

# Email configuration
try:
    from .email_config import EmailConfigManager, EmailProvider, SMTPProvider, SendGridProvider, MailgunProvider
    EMAIL_CONFIG_AVAILABLE = True
except ImportError:
    EMAIL_CONFIG_AVAILABLE = False

# Auto-tracking imports
try:
    from .auto_interceptor import auto_patch_all, init_auto_tracking, patch_openai, patch_anthropic
    AUTO_TRACKING_AVAILABLE = True
except ImportError:
    AUTO_TRACKING_AVAILABLE = False

try:
    from .zero_config_tracker import *
    ZERO_CONFIG_AVAILABLE = True
except ImportError:
    ZERO_CONFIG_AVAILABLE = False

__all__ = [
    "CostTracker",
    "get_tracker",
    "PRICING",
    "APIUsageRecord",
    "OpenAIScanner",
    "OpenAIUsage",
    "UniversalCostTracker",
    "UniversalTrackerAPI",
    "SUPPORTED_PROVIDERS",
    "SystemWideScanner",
    "SystemAIUsage",
]

if EMAIL_CONFIG_AVAILABLE:
    __all__.extend([
        "EmailConfigManager",
        "EmailProvider",
        "SMTPProvider",
        "SendGridProvider",
        "MailgunProvider",
    ])

if AUTO_TRACKING_AVAILABLE:
    __all__.extend([
        "auto_patch_all",
        "init_auto_tracking",
        "patch_openai",
        "patch_anthropic",
    ])
