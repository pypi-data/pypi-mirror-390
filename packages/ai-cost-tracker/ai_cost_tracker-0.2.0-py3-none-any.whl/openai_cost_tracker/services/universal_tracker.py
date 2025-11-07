#!/usr/bin/env python3
"""
Universal AI Cost Tracker API Server
REST API that accepts tracking data from ANY language/framework
Works as a daemon service that monitors system-wide AI API usage
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from threading import Lock
import hashlib

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Fallback - will use FastAPI if Flask not available
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        FASTAPI_AVAILABLE = True
    except ImportError:
        FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

# Supported AI Providers
SUPPORTED_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "api_key_patterns": [r"sk-[a-zA-Z0-9]{20,}", r"OPENAI_API_KEY"],
        "endpoints": ["api.openai.com", "api.openai.com/v1"],
    },
    "perplexity": {
        "name": "Perplexity AI",
        "api_key_patterns": [r"pplx-[a-zA-Z0-9]{20,}", r"PERPLEXITY_API_KEY"],
        "endpoints": ["api.perplexity.ai"],
    },
    "grok": {
        "name": "Grok (xAI)",
        "api_key_patterns": [r"xai-[a-zA-Z0-9]{20,}", r"GROK_API_KEY", r"XAI_API_KEY"],
        "endpoints": ["api.x.ai"],
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "api_key_patterns": [r"sk-ant-[a-zA-Z0-9-]{20,}", r"ANTHROPIC_API_KEY"],
        "endpoints": ["api.anthropic.com"],
    },
    "google": {
        "name": "Google AI",
        "api_key_patterns": [r"AIza[0-9A-Za-z-_]{35}", r"GOOGLE_AI_API_KEY", r"GEMINI_API_KEY"],
        "endpoints": ["generativelanguage.googleapis.com", "ai.google.dev"],
    },
    "cohere": {
        "name": "Cohere",
        "api_key_patterns": [r"co-[a-zA-Z0-9]{20,}", r"COHERE_API_KEY"],
        "endpoints": ["api.cohere.ai"],
    },
    "mistral": {
        "name": "Mistral AI",
        "api_key_patterns": [r"mistral-[a-zA-Z0-9]{20,}", r"MISTRAL_API_KEY"],
        "endpoints": ["api.mistral.ai"],
    },
}


@dataclass
class UniversalUsageRecord:
    """Universal record for any AI provider"""
    timestamp: str
    provider: str  # openai, perplexity, grok, etc.
    service_name: str
    language: str  # python, javascript, nodejs, etc.
    framework: Optional[str]  # flask, react, express, etc.
    api_key_hash: str
    api_type: str  # chat, completion, image, video, embedding, etc.
    model: str
    operation: str
    cost_usd: float
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    request_size: Optional[int] = None  # bytes
    response_size: Optional[int] = None  # bytes
    duration_ms: Optional[int] = None
    video_seconds: Optional[float] = None
    image_size: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    resource_id: Optional[str] = None  # video_id, image_id, etc.
    success: bool = True
    error_message: Optional[str] = None
    process_id: Optional[int] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None


class UniversalCostTracker:
    """Universal cost tracker that accepts data from any source"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize universal tracker"""
        if db_path is None:
            import os
            default_dir = Path.home() / ".ai_cost_tracker"
            if not os.access(Path.home(), os.W_OK):
                default_dir = Path.cwd() / ".ai_cost_tracker"
            db_path = default_dir / "universal_usage.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database with universal schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS universal_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    language TEXT,
                    framework TEXT,
                    api_key_hash TEXT NOT NULL,
                    api_type TEXT NOT NULL,
                    model TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    cost_usd REAL NOT NULL,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    request_size INTEGER,
                    response_size INTEGER,
                    duration_ms INTEGER,
                    video_seconds REAL,
                    image_size TEXT,
                    request_data TEXT,
                    response_data TEXT,
                    resource_id TEXT,
                    success INTEGER NOT NULL,
                    error_message TEXT,
                    process_id INTEGER,
                    client_ip TEXT,
                    user_agent TEXT
                )
            """)
            
            # Create indices
            for idx in ["timestamp", "provider", "service_name", "language", "api_key_hash", "api_type"]:
                conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{idx} ON universal_usage({idx})
                """)
            conn.commit()
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for identification"""
        if not api_key:
            return "unknown"
        hash_obj = hashlib.sha256(api_key.encode())
        return hash_obj.hexdigest()[:16]
    
    def _detect_provider(self, api_key: str) -> str:
        """Detect AI provider from API key"""
        api_key = api_key or ""
        for provider, info in SUPPORTED_PROVIDERS.items():
            for pattern in info["api_key_patterns"]:
                import re
                if re.search(pattern, api_key, re.IGNORECASE):
                    return provider
        return "unknown"
    
    def log_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log usage from any source (REST API call)"""
        try:
            # Extract data
            provider = data.get("provider", "unknown")
            api_key = data.get("api_key", "")
            
            # Auto-detect provider if not specified
            if provider == "unknown" and api_key:
                provider = self._detect_provider(api_key)
            
            api_key_hash = self._hash_api_key(api_key)
            
            record = UniversalUsageRecord(
                timestamp=datetime.utcnow().isoformat(),
                provider=provider,
                service_name=data.get("service_name", "unknown"),
                language=data.get("language", "unknown"),
                framework=data.get("framework"),
                api_key_hash=api_key_hash,
                api_type=data.get("api_type", "unknown"),
                model=data.get("model", "unknown"),
                operation=data.get("operation", "call"),
                cost_usd=float(data.get("cost_usd", 0.0)),
                tokens_input=data.get("tokens_input"),
                tokens_output=data.get("tokens_output"),
                request_size=data.get("request_size"),
                response_size=data.get("response_size"),
                duration_ms=data.get("duration_ms"),
                video_seconds=data.get("video_seconds"),
                image_size=data.get("image_size"),
                request_data=json.dumps(data.get("request_data")) if data.get("request_data") else None,
                response_data=json.dumps(self._sanitize_response(data.get("response_data"))) if data.get("response_data") else None,
                resource_id=data.get("resource_id"),
                success=data.get("success", True),
                error_message=data.get("error_message"),
                process_id=data.get("process_id"),
                client_ip=data.get("client_ip"),
                user_agent=data.get("user_agent"),
            )
            
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO universal_usage (
                            timestamp, provider, service_name, language, framework,
                            api_key_hash, api_type, model, operation, cost_usd,
                            tokens_input, tokens_output, request_size, response_size,
                            duration_ms, video_seconds, image_size, request_data,
                            response_data, resource_id, success, error_message,
                            process_id, client_ip, user_agent
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.timestamp, record.provider, record.service_name,
                        record.language, record.framework, record.api_key_hash,
                        record.api_type, record.model, record.operation, record.cost_usd,
                        record.tokens_input, record.tokens_output, record.request_size,
                        record.response_size, record.duration_ms, record.video_seconds,
                        record.image_size, record.request_data, record.response_data,
                        record.resource_id, 1 if record.success else 0,
                        record.error_message, record.process_id, record.client_ip,
                        record.user_agent
                    ))
                    conn.commit()
            
            logger.info(f"💰 Tracked {provider}/{record.api_type} - ${record.cost_usd:.4f} - {record.service_name}")
            
            return {"success": True, "id": record.api_key_hash}
            
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
            return {"success": False, "error": str(e)}
    
    def _sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data"""
        if not response:
            return {}
        sanitized = {}
        for key in ["id", "status", "model", "created_at"]:
            if key in response:
                sanitized[key] = str(response[key])[:500]
        return sanitized
    
    def get_summary(self, **filters) -> Dict[str, Any]:
        """Get usage summary with filters"""
        query = "SELECT * FROM universal_usage WHERE 1=1"
        params = []
        
        for key, value in filters.items():
            if value:
                query += f" AND {key} = ?"
                params.append(value)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        total_cost = sum(row["cost_usd"] for row in rows)
        total_calls = len(rows)
        
        by_provider = {}
        by_language = {}
        by_service = {}
        by_api_key = {}
        
        for row in rows:
            provider = row["provider"]
            language = row["language"] or "unknown"
            service = row["service_name"]
            api_key = row["api_key_hash"] or "unknown"
            
            by_provider[provider] = by_provider.get(provider, {"cost": 0, "calls": 0})
            by_provider[provider]["cost"] += row["cost_usd"]
            by_provider[provider]["calls"] += 1
            
            by_language[language] = by_language.get(language, {"cost": 0, "calls": 0})
            by_language[language]["cost"] += row["cost_usd"]
            by_language[language]["calls"] += 1
            
            by_service[service] = by_service.get(service, {"cost": 0, "calls": 0})
            by_service[service]["cost"] += row["cost_usd"]
            by_service[service]["calls"] += 1
            
            by_api_key[api_key] = by_api_key.get(api_key, {"cost": 0, "calls": 0, "services": set()})
            by_api_key[api_key]["cost"] += row["cost_usd"]
            by_api_key[api_key]["calls"] += 1
            by_api_key[api_key]["services"].add(service)
        
        # Convert sets to lists
        for key_data in by_api_key.values():
            key_data["services"] = list(key_data["services"])
        
        return {
            "total_cost_usd": total_cost,
            "total_calls": total_calls,
            "by_provider": by_provider,
            "by_language": by_language,
            "by_service": by_service,
            "by_api_key": by_api_key,
            "records": [dict(row) for row in rows]
        }


class UniversalTrackerAPI:
    """REST API server for universal tracking"""
    
    def __init__(self, port: int = 8888, host: str = "0.0.0.0"):
        self.tracker = UniversalCostTracker()
        self.port = port
        self.host = host
        
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_flask_routes()
        elif FASTAPI_AVAILABLE:
            self.app = FastAPI()
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            self._setup_fastapi_routes()
        else:
            raise ImportError("Neither Flask nor FastAPI available. Install one: pip install flask or pip install fastapi")
    
    def _setup_flask_routes(self):
        """Setup Flask routes"""
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy", "service": "universal-ai-tracker"})
        
        @self.app.route("/api/track", methods=["POST"])
        def track():
            data = request.json
            result = self.tracker.log_usage(data)
            return jsonify(result)
        
        @self.app.route("/api/summary", methods=["GET"])
        def summary():
            filters = {
                "provider": request.args.get("provider"),
                "language": request.args.get("language"),
                "service_name": request.args.get("service"),
                "api_key_hash": request.args.get("api_key"),
            }
            result = self.tracker.get_summary(**{k: v for k, v in filters.items() if v})
            return jsonify(result)
    
    def _setup_fastapi_routes(self):
        """Setup FastAPI routes"""
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "service": "universal-ai-tracker"}
        
        @self.app.post("/api/track")
        async def track(data: dict):
            result = self.tracker.log_usage(data)
            return result
        
        @self.app.get("/api/summary")
        async def summary(
            provider: Optional[str] = None,
            language: Optional[str] = None,
            service: Optional[str] = None,
            api_key: Optional[str] = None
        ):
            filters = {
                "provider": provider,
                "language": language,
                "service_name": service,
                "api_key_hash": api_key,
            }
            result = self.tracker.get_summary(**{k: v for k, v in filters.items() if v})
            return result
    
    def run(self):
        """Run the API server"""
        if FLASK_AVAILABLE:
            self.app.run(host=self.host, port=self.port, debug=False)
        elif FASTAPI_AVAILABLE:
            import uvicorn
            uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api = UniversalTrackerAPI(port=8888)
    logger.info(f"🚀 Universal AI Tracker API starting on {api.host}:{api.port}")
    logger.info("📡 Accepting tracking requests from any language/framework")
    api.run()

