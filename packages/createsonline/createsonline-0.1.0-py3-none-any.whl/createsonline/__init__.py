# createsonline/__init__.py
"""
CREATESONLINE - The AI-Native Web Framework

Build Intelligence Into Everything

A pure AI-native framework for building intelligent applications.
Zero external dependencies - works with just Python 3.9+
"""

# Read version from VERSION file
def _get_version():
    """Get version from VERSION file"""
    from pathlib import Path
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return '0.1.0'  # fallback version

__version__ = _get_version()
__framework_name__ = 'CREATESONLINE'
__tagline__ = 'Build Intelligence Into Everything'
__author__ = 'Ahmed Hassan'
__license__ = 'MIT'

# System requirements check
import sys
if sys.version_info < (3, 9):
    raise RuntimeError(f"CREATESONLINE requires Python 3.9+. Current: {sys.version}")

# Core framework imports (always available)
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union

# Setup logging
logger = logging.getLogger("createsonline")


class CreatesonlineInternalApp:
    """
    Pure CREATESONLINE core application - ZERO external dependencies
    
    This is the internal implementation that works with just Python stdlib.
    Provides full AI-native framework capabilities without any external packages.
    """
    
    def __init__(
        self,
        title: str = "CREATESONLINE Application",
        description: str = "AI-powered application built with CREATESONLINE",
        version: str = "1.0.0",
        ai_config: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        **kwargs
    ):
        # Core application metadata
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.ai_config = ai_config or {}
        
        # Internal routing system
        self.routes = {}
        self.middleware = []
        self.startup_handlers = []
        self.shutdown_handlers = []
        
        # AI-native features (internal implementations)
        self.ai_enabled = True
        self.ai_features = []
        self.ai_services = CreatesonlineInternalAI()
        
        # Setup framework routes
        self._setup_framework_routes()
        
        logger.info(f"CREATESONLINE v{__version__} initialized (Internal Core)")
        logger.info(f"âœ¨ {self.title} - AI-Native Framework Ready")
    
    def _setup_framework_routes(self):
        """Setup built-in CREATESONLINE framework routes - fallback implementation"""
        
        @self.get("/health")
        async def health_check(request):
            return {
                "status": "healthy",
                "framework": "CREATESONLINE",
                "version": __version__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ========================================
    # PURE ASGI IMPLEMENTATION
    # ========================================
    
    async def __call__(self, scope, receive, send):
        """Pure ASGI interface - no external dependencies"""
        
        if scope['type'] == 'http':
            await self._handle_http(scope, receive, send)
        elif scope['type'] == 'websocket':
            await self._handle_websocket(scope, receive, send)
    
    async def _handle_http(self, scope, receive, send):
        """Handle HTTP requests with internal router"""
        
        path = scope['path']
        method = scope['method']
        route_key = f"{method}:{path}"
        
        # Create internal request object
        request = CreatesonlineInternalRequest(scope, receive)
        
        try:
            # Find matching route
            if route_key in self.routes:
                handler = self.routes[route_key]
                response_data = await handler(request)
                status = 200
            else:
                # 404 handler
                response_data = {
                    "error": "Not Found",
                    "path": path,
                    "method": method,
                    "framework": "CREATESONLINE",
                    "available_routes": list(self.routes.keys())
                }
                status = 404
            
            # Send response
            if isinstance(response_data, dict):
                await self._send_json_response(send, response_data, status=status)
            else:
                await self._send_text_response(send, str(response_data))
                
        except Exception as e:
            # Error handling - log the full traceback
            logger.exception(f"Request handling error for {method} {path}")
            error_data = {
                "error": "Internal Server Error",
                "message": str(e) if self.debug else "Something went wrong",
                "framework": "CREATESONLINE"
            }
            await self._send_json_response(send, error_data, status=500)
    
    async def _handle_websocket(self, scope, receive, send):
        """Handle WebSocket connections with security measures"""
        # Basic WebSocket support
        await send({'type': 'websocket.accept'})
        
        message_count = 0
        max_messages = 100  # Rate limiting
        
        while True:
            message = await receive()
            if message['type'] == 'websocket.disconnect':
                break
            elif message['type'] == 'websocket.receive':
                # Rate limiting
                message_count += 1
                if message_count > max_messages:
                    logger.warning("WebSocket rate limit exceeded")
                    await send({'type': 'websocket.close', 'code': 1008})
                    break
                
                # Sanitize input - don't echo raw user content
                user_text = message.get('text', '')
                if user_text:
                    # Basic sanitization - truncate and log
                    sanitized_text = user_text[:100]  # Limit length
                    logger.info(f"WebSocket message received (length: {len(user_text)})")
                else:
                    sanitized_text = ''
                
                # Send safe response without echoing raw input
                await send({
                    'type': 'websocket.send',
                    'text': json.dumps({
                        "framework": "CREATESONLINE",
                        "message": "WebSocket message processed",
                        "message_count": message_count,
                        "received_length": len(user_text)
                    })
                })
    
    async def _send_json_response(self, send, data, status=200):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2 if self.debug else None).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'content-length', str(len(response_body)).encode()],
                [b'x-framework', b'CREATESONLINE'],
                [b'x-version', __version__.encode()],
            ],
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })
    
    async def _send_text_response(self, send, text, status=200):
        """Send plain text or HTML response"""
        response_body = text.encode('utf-8')
        
        # Detect if it's HTML
        content_type = b'text/html; charset=utf-8' if text.strip().startswith('<!DOCTYPE') or text.strip().startswith('<html') else b'text/plain'
        
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', content_type],
                [b'content-length', str(len(response_body)).encode()],
                [b'x-framework', b'CREATESONLINE'],
            ],
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })
    
    # ========================================
    # ROUTING DECORATORS (DJANGO/FASTAPI STYLE)
    # ========================================
    
    def get(self, path: str):
        """GET route decorator"""
        def decorator(func):
            self.routes[f"GET:{path}"] = func
            return func
        return decorator
    
    def post(self, path: str):
        """POST route decorator"""
        def decorator(func):
            self.routes[f"POST:{path}"] = func
            return func
        return decorator
    
    def put(self, path: str):
        """PUT route decorator"""
        def decorator(func):
            self.routes[f"PUT:{path}"] = func
            return func
        return decorator
    
    def delete(self, path: str):
        """DELETE route decorator"""
        def decorator(func):
            self.routes[f"DELETE:{path}"] = func
            return func
        return decorator
    
    def route(self, path: str, methods: List[str] = None):
        """Multi-method route decorator"""
        if methods is None:
            methods = ["GET"]
        
        def decorator(func):
            for method in methods:
                self.routes[f"{method.upper()}:{path}"] = func
            return func
        return decorator
    
    # ========================================
    # AI-NATIVE FEATURES
    # ========================================
    
    def enable_ai_features(self, features: List[str]):
        """Enable AI features in CREATESONLINE application"""
        for feature in features:
            if feature not in self.ai_features:
                self.ai_features.append(feature)
                logger.info(f"AI Feature enabled: {feature}")
        return self
    
    # ========================================
    # LIFECYCLE EVENTS
    # ========================================
    
    def on_startup(self, func: Callable):
        """Register startup handler"""
        self.startup_handlers.append(func)
        return func
    
    def on_shutdown(self, func: Callable):
        """Register shutdown handler"""
        self.shutdown_handlers.append(func)
        return func
    
    # ========================================
    # SERVER RUNNER - PURE INDEPENDENCE
    # ========================================
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """
        Run the application using CREATESONLINE's internal pure Python server
        
        NO EXTERNAL DEPENDENCIES - 100% Pure Python Implementation
        
        Args:
            host: Host to bind to (default: 127.0.0.1)
            port: Port to listen on (default: 8000)
        """
        from .server import run_server
        
        
        
        logger.info("Starting CREATESONLINE Pure Python Server")
        logger.info(f"Framework: CREATESONLINE v{__version__}")
        logger.info("Pure Independence: Zero external web dependencies")
        run_server(self, host=host, port=port)


class CreatesonlineInternalRequest:
    """Internal request object - no external dependencies"""
    
    def __init__(self, scope, receive):
        self.scope = scope
        self.receive = receive
        self.path = scope['path']
        self.method = scope['method']
        self.headers = dict(scope.get('headers', []))
        self.query_params = self._parse_query_string(scope.get('query_string', b''))
        self.path_params = scope.get('path_params', {})
    
    def _parse_query_string(self, query_string):
        """Parse query string into dict"""
        if not query_string:
            return {}
        
        params = {}
        for pair in query_string.decode().split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
        return params
    
    async def json(self):
        """Parse JSON body"""
        body = await self._get_body()
        return json.loads(body.decode())
    
    async def _get_body(self):
        """Get request body"""
        body = b''
        while True:
            message = await self.receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body


class CreatesonlineInternalAI:
    """Internal AI services - no external dependencies"""
    
    def __init__(self):
        self.cache = {}
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using internal algorithms"""
        
        # Simple rule-based text generation
        templates = {
            "hello": "Hello! Welcome to CREATESONLINE - the AI-Native framework.",
            "describe": f"CREATESONLINE is an innovative AI-native web framework that builds intelligence into everything.",
            "explain": f"This framework provides built-in AI capabilities without external dependencies.",
            "summarize": f"Summary: {prompt[:100]}...",
        }
        
        prompt_lower = prompt.lower()
        for key, template in templates.items():
            if key in prompt_lower:
                return template
        
        return f"CREATESONLINE AI Response: Generated content for '{prompt[:50]}...'"
    
    def get_embedding(self, text: str, dimensions: int = 128) -> List[float]:
        """Generate consistent hash-based embeddings"""
        
        # Create deterministic embedding using hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(dimensions):
            byte_index = i % len(hash_bytes)
            # Normalize to [-0.5, 0.5] range
            value = (hash_bytes[byte_index] / 255.0) - 0.5
            embedding.append(value)
        
        return embedding
    
    def similarity_search(self, query_embedding: List[float], documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """Perform similarity search using cosine similarity"""
        
        results = []
        for doc in documents:
            if 'embedding' in doc:
                similarity = self._cosine_similarity(query_embedding, doc['embedding'])
                results.append({
                    'document': doc,
                    'similarity': similarity
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


# ========================================
# MAIN FRAMEWORK API
# ========================================

def create_app(
    title: str = "CREATESONLINE Application",
    description: str = "AI-powered application built with CREATESONLINE",
    version: str = "1.0.0",
    ai_config: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    **kwargs
) -> Union[Any, 'CreatesonlineInternalApp']:
    """
    Create a CREATESONLINE application instance
    
    This function tries to use the full-featured app first, but falls back
    to the internal core implementation if dependencies are missing.
    
    Args:
        title: Application title
        description: Application description
        version: Application version
        ai_config: AI configuration dictionary
        debug: Enable debug mode
        **kwargs: Additional configuration options
    
    Returns:
        CREATESONLINE application instance (full-featured or internal core)
        
    Example:
        ```python
        from createsonline import create_app
        
        app = create_app(
            title="My AI App",
            description="Intelligent application",
            ai_config={
                "enable_smart_fields": True,
                "default_llm": "internal"
            }
        )
        
        @app.get("/")
        async def home(request):
            return {"message": "Hello from CREATESONLINE!"}
        ```
    """
    
    # TRY: Use full-featured CREATESONLINE app if dependencies available
    try:
        from createsonline.config.app import CreatesonlineApp
        logger.info("ðŸš€ Loading full-featured CREATESONLINE...")
        return CreatesonlineApp(
            title=title,
            description=description,
            version=version,
            ai_config=ai_config or {},
            debug=debug,
            **kwargs
        )
    
    except ImportError as e:
        # FALLBACK: Use internal core implementation
        logger.warning(f"ðŸ”„ External dependencies missing ({e})")
        logger.info("âœ… Using CREATESONLINE Internal Core - Zero Dependencies")
        return CreatesonlineInternalApp(
            title=title,
            description=description,
            version=version,
            ai_config=ai_config or {},
            debug=debug,
            **kwargs
        )


# Framework information functions
def get_version() -> str:
    """Get CREATESONLINE framework version"""
    return __version__


def get_framework_info() -> Dict[str, Any]:
    """Get comprehensive framework information"""
    return {
        "name": __framework_name__,
        "version": __version__,
        "tagline": __tagline__,
        "author": __author__,
        "license": __license__,
        "python_requires": ">=3.9",
        "mode": "independent_core",
        "homepage": "https://createsonline.com",
        "repository": "https://github.com/meahmedh/createsonline",
        "features": [
            "Pure AI-Native Architecture",
            "Zero External Dependencies",
            "Built-in Admin Interface",
            "User Management System",
            "AI-Enhanced Fields",
            "Internal Template System",
            "Mock AI Services",
            "Pure ASGI Implementation"
        ],
        "ai_capabilities": [
            "Hash-based embeddings",
            "Rule-based text generation",
            "Similarity search",
            "Internal ML algorithms",
            "AI field types"
        ]
    }


# Public API exports
__all__ = [
    'create_app',
    'CreatesonlineInternalApp',
    'CreatesonlineInternalAI',
    '__version__',
    'get_version',
    'get_framework_info',
    'run_server'  # Pure Python server
]

# Import server for convenience
from .server import run_server

def get_framework_banner():
    """Generate framework banner based on loaded implementation"""
    # Check if full-featured app is available
    try:
        from createsonline.config.app import CreatesonlineApp
        mode = "Full Featured"
    except ImportError:
        mode = "Internal Core"
    
    return f"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                        CREATESONLINE                         â•‘
â•‘                  The AI-Native Web Framework                 â•‘
â•‘                                                              â•‘
â•‘                 Build Intelligence Into Everything           â•‘
â•‘                                                              â•‘
â•‘  Version: {__version__:<10} | Mode: {mode:<15} â•‘
â•‘  Zero Dependencies | AI-First | Pure Python                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""

# Framework banner for CLI
FRAMEWORK_BANNER = get_framework_banner()


