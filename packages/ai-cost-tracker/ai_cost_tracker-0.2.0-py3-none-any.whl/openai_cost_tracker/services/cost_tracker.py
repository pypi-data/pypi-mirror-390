"""
OpenAI API Cost Tracking System
Tracks all OpenAI API calls, calculates costs, and logs usage across all services.
"""

import json
import sqlite3
import hashlib
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from threading import Lock
import time

logger = logging.getLogger(__name__)

# OpenAI Pricing (as of 2024-2025 - update as needed)
PRICING = {
    "sora-2": {
        # Sora 2 pricing per second of video
        "per_second": 0.015,  # $0.015 per second of generated video
        "min_cost": 0.05,  # Minimum cost per video
    },
    "gpt-image-1": {
        # DALL-E 3 / gpt-image-1 pricing
        "1024x1024": 0.04,  # $0.040 per image
        "1792x1024": 0.08,  # $0.080 per image (landscape)
        "1024x1792": 0.08,  # $0.080 per image (portrait)
        "1024x1024_hd": 0.08,  # HD quality
    },
    "dall-e-3": {
        "1024x1024": 0.04,
        "1792x1024": 0.08,
        "1024x1792": 0.08,
        "1024x1024_hd": 0.08,
    },
    "dall-e-2": {
        "256x256": 0.016,
        "512x512": 0.018,
        "1024x1024": 0.02,
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,  # $2.50 per 1M tokens
        "output": 10.00 / 1_000_000,  # $10.00 per 1M tokens
    },
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,  # $0.15 per 1M tokens
        "output": 0.600 / 1_000_000,  # $0.60 per 1M tokens
    },
    "gpt-4": {
        "input": 30.00 / 1_000_000,  # $30 per 1M tokens
        "output": 60.00 / 1_000_000,  # $60 per 1M tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.50 / 1_000_000,  # $0.50 per 1M tokens
        "output": 1.50 / 1_000_000,  # $1.50 per 1M tokens
    },
}

# Default quality mapping for images
DEFAULT_IMAGE_QUALITY = {
    "standard": "",
    "hd": "_hd",
}


@dataclass
class APIUsageRecord:
    """Record of a single API usage"""
    timestamp: str
    service_name: str  # e.g., "automation_service_v2", "email_watcher"
    api_key_hash: str  # SHA256 hash of API key (first 8 chars)
    api_type: str  # "video", "image", "chat", "embedding"
    model: str
    operation: str  # "create", "generate", "retrieve", etc.
    cost_usd: float
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    video_seconds: Optional[float] = None
    image_size: Optional[str] = None
    image_quality: Optional[str] = None
    request_data: Optional[str] = None  # JSON string of request (sanitized)
    response_data: Optional[str] = None  # JSON string of response (sanitized)
    video_id: Optional[str] = None
    image_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    process_id: Optional[int] = None
    user: Optional[str] = None


class CostTracker:
    """Centralized cost tracking system for OpenAI API calls"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize cost tracker with database path"""
        if db_path is None:
            # Default to user's home directory or current directory
            import os
            default_dir = Path.home() / ".openai_cost_tracker"
            if not os.access(Path.home(), os.W_OK):
                # Fallback to current directory if home is not writable
                default_dir = Path.cwd() / ".openai_cost_tracker"
            db_path = default_dir / "openai_usage.db"
        else:
            db_path = Path(db_path)
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    api_key_hash TEXT NOT NULL,
                    api_type TEXT NOT NULL,
                    model TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    cost_usd REAL NOT NULL,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    video_seconds REAL,
                    image_size TEXT,
                    image_quality TEXT,
                    request_data TEXT,
                    response_data TEXT,
                    video_id TEXT,
                    image_id TEXT,
                    success INTEGER NOT NULL,
                    error_message TEXT,
                    process_id INTEGER,
                    user TEXT
                )
            """)
            
            # Create indices for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON api_usage(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_service ON api_usage(service_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_key_hash ON api_usage(api_key_hash)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_type ON api_usage(api_type)
            """)
            conn.commit()
    
    def _hash_api_key(self, api_key: str) -> str:
        """Create a hash of API key for identification (first 8 chars of hash)"""
        if not api_key:
            return "unknown"
        hash_obj = hashlib.sha256(api_key.encode())
        return hash_obj.hexdigest()[:16]  # First 16 chars for identification
    
    def _get_service_name(self) -> str:
        """Detect service name from process/environment"""
        import sys
        import os
        
        # Check process name
        proc_name = os.path.basename(sys.argv[0]) if sys.argv else "unknown"
        
        # Check environment variables
        if os.getenv("INSTAGRAM_ACCOUNT"):
            account = os.getenv("INSTAGRAM_ACCOUNT")
            if "automation" in proc_name.lower():
                return f"automation_service_v2_{account}"
        
        if "email" in proc_name.lower() or "watcher" in proc_name.lower():
            return "email_watcher_service"
        
        if "uvicorn" in proc_name or "backend" in proc_name:
            return "backend_api_server"
        
        # Fallback to script name
        return proc_name.replace(".py", "").replace("_", " ")
    
    def calculate_video_cost(self, model: str, seconds: float) -> float:
        """Calculate cost for video generation"""
        if model not in PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = "sora-2"
        
        pricing = PRICING.get(model, PRICING["sora-2"])
        cost = seconds * pricing.get("per_second", 0.015)
        return max(cost, pricing.get("min_cost", 0.05))
    
    def calculate_image_cost(self, model: str, size: str, quality: str = "standard") -> float:
        """Calculate cost for image generation"""
        if model not in PRICING:
            logger.warning(f"Unknown image model {model}, using default")
            model = "gpt-image-1"
        
        pricing = PRICING.get(model, PRICING["gpt-image-1"])
        
        # Map quality to size key
        size_key = size
        if quality == "hd" and size == "1024x1024":
            size_key = "1024x1024_hd"
        
        cost = pricing.get(size_key, pricing.get("1024x1024", 0.04))
        return cost
    
    def calculate_chat_cost(self, model: str, tokens_input: int, tokens_output: int) -> float:
        """Calculate cost for chat/completion API"""
        if model not in PRICING:
            logger.warning(f"Unknown chat model {model}")
            return 0.0
        
        pricing = PRICING[model]
        input_cost = (tokens_input / 1_000_000) * pricing.get("input", 0)
        output_cost = (tokens_output / 1_000_000) * pricing.get("output", 0)
        return input_cost + output_cost
    
    def log_api_call(
        self,
        api_key: str,
        api_type: str,
        model: str,
        operation: str,
        cost: float,
        service_name: Optional[str] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        video_seconds: Optional[float] = None,
        image_size: Optional[str] = None,
        image_quality: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        video_id: Optional[str] = None,
        image_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        user: Optional[str] = None
    ):
        """Log an API call to the database"""
        if service_name is None:
            service_name = self._get_service_name()
        
        api_key_hash = self._hash_api_key(api_key)
        
        record = APIUsageRecord(
            timestamp=datetime.utcnow().isoformat(),
            service_name=service_name,
            api_key_hash=api_key_hash,
            api_type=api_type,
            model=model,
            operation=operation,
            cost_usd=cost,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            video_seconds=video_seconds,
            image_size=image_size,
            image_quality=image_quality,
            request_data=json.dumps(request_data) if request_data else None,
            response_data=json.dumps(self._sanitize_response(response_data)) if response_data else None,
            video_id=video_id,
            image_id=image_id,
            success=success,
            error_message=error_message,
            process_id=os.getpid(),
            user=user
        )
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO api_usage (
                            timestamp, service_name, api_key_hash, api_type, model, operation,
                            cost_usd, tokens_input, tokens_output, video_seconds, image_size,
                            image_quality, request_data, response_data, video_id, image_id,
                            success, error_message, process_id, user
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.timestamp, record.service_name, record.api_key_hash,
                        record.api_type, record.model, record.operation, record.cost_usd,
                        record.tokens_input, record.tokens_output, record.video_seconds,
                        record.image_size, record.image_quality, record.request_data,
                        record.response_data, record.video_id, record.image_id,
                        1 if record.success else 0, record.error_message,
                        record.process_id, record.user
                    ))
                    conn.commit()
                    
                logger.info(f"💰 Tracked API call: {api_type}/{model} - ${cost:.4f} - {service_name}")
            except Exception as e:
                logger.error(f"Failed to log API call: {e}")
    
    def _sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data (remove sensitive info, limit size)"""
        if not response:
            return {}
        
        sanitized = {}
        # Keep only relevant fields, limit data size
        for key in ["id", "status", "model", "created_at", "size", "seconds", "progress"]:
            if key in response:
                sanitized[key] = str(response[key])[:500]  # Limit field size
        
        return sanitized
    
    def get_usage_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service_name: Optional[str] = None,
        api_key_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage summary with filtering"""
        query = "SELECT * FROM api_usage WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if service_name:
            query += " AND service_name = ?"
            params.append(service_name)
        
        if api_key_hash:
            query += " AND api_key_hash = ?"
            params.append(api_key_hash)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        total_cost = sum(row["cost_usd"] for row in rows)
        total_calls = len(rows)
        
        by_service = {}
        by_api_type = {}
        by_model = {}
        by_api_key = {}
        by_process = {}
        
        # Token statistics
        total_tokens_input = 0
        total_tokens_output = 0
        
        for row in rows:
            service = row["service_name"]
            api_type = row["api_type"]
            model = row["model"]
            api_key = row["api_key_hash"] or "unknown"
            process_id = row["process_id"]
            
            by_service[service] = by_service.get(service, {"cost": 0, "calls": 0, "tokens_input": 0, "tokens_output": 0})
            by_service[service]["cost"] += row["cost_usd"]
            by_service[service]["calls"] += 1
            by_service[service]["tokens_input"] += row["tokens_input"] or 0
            by_service[service]["tokens_output"] += row["tokens_output"] or 0
            
            by_api_type[api_type] = by_api_type.get(api_type, {"cost": 0, "calls": 0})
            by_api_type[api_type]["cost"] += row["cost_usd"]
            by_api_type[api_type]["calls"] += 1
            
            by_model[model] = by_model.get(model, {"cost": 0, "calls": 0})
            by_model[model]["cost"] += row["cost_usd"]
            by_model[model]["calls"] += 1
            
            by_api_key[api_key] = by_api_key.get(api_key, {"cost": 0, "calls": 0, "services": set()})
            by_api_key[api_key]["cost"] += row["cost_usd"]
            by_api_key[api_key]["calls"] += 1
            by_api_key[api_key]["services"].add(service)
            
            if process_id:
                by_process[process_id] = by_process.get(process_id, {"cost": 0, "calls": 0, "service": service})
                by_process[process_id]["cost"] += row["cost_usd"]
                by_process[process_id]["calls"] += 1
            
            total_tokens_input += row["tokens_input"] or 0
            total_tokens_output += row["tokens_output"] or 0
        
        # Convert sets to lists for JSON serialization
        for key_data in by_api_key.values():
            key_data["services"] = list(key_data["services"])
        
        return {
            "total_cost_usd": total_cost,
            "total_calls": total_calls,
            "total_tokens_input": total_tokens_input,
            "total_tokens_output": total_tokens_output,
            "by_service": by_service,
            "by_api_type": by_api_type,
            "by_model": by_model,
            "by_api_key": by_api_key,
            "by_process": by_process,
            "records": [dict(row) for row in rows]
        }
    
    def get_recent_calls(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent API calls"""
        query = "SELECT * FROM api_usage ORDER BY timestamp DESC LIMIT ?"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (limit,))
            rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


# Global tracker instance
_global_tracker: Optional[CostTracker] = None

def get_tracker() -> CostTracker:
    """Get or create global cost tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker

