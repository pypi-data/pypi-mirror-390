"""
CREATESONLINE API Documentation Generator

Generates beautiful HTML API documentation from route definitions.
"""
import json
from datetime import datetime
import platform
import sys
from typing import Dict, Any


class APIDocumentationGenerator:
    """Generate HTML API documentation for CREATESONLINE applications"""
    
    def __init__(self, app):
        self.app = app
    
    def generate_beautiful_api_docs(self):
        """Generate beautiful HTML API documentation with dynamic backend data"""
        spec = self._build_api_spec()
        html_content = self._render_html_template(spec)
        return self._create_html_response(html_content)
    
    def _build_api_spec(self) -> Dict[str, Any]:
        """Build OpenAPI specification"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.app.title,
                "description": self.app.description,
                "version": self.app.version,
                "x-framework": "CREATESONLINE",
                "x-ai-enabled": len(self.app._ai_features) > 0,
                "x-mode": "internal",
                "x-timestamp": datetime.utcnow().isoformat(),
                "x-python-version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "x-platform": platform.system(),
                "x-architecture": platform.machine()
            },
            "servers": [
                {
                    "url": "/",
                    "description": "CREATESONLINE Development Server",
                    "variables": {
                        "protocol": {"default": "http", "enum": ["http", "https"]},
                        "host": {"default": "127.0.0.1:8000"}
                    }
                }
            ],
            "paths": self._generate_enhanced_api_paths(),
            "components": {
                "schemas": self._generate_api_schemas(),
                "securitySchemes": {
                    "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                    "BearerAuth": {"type": "http", "scheme": "bearer"}
                }
            },
            "x-system-info": {
                "framework": "CREATESONLINE",
                "mode": "AI-Native",
                "features": self.app._ai_features,
                "total_routes": len(self.app._internal_routes),
                "ai_routes": len([r for r in self.app._internal_routes.keys() if 'ai' in r.lower()]),
                "admin_routes": len([r for r in self.app._internal_routes.keys() if 'admin' in r.lower()]),
                "startup_time": datetime.utcnow().isoformat(),
                "health_status": "operational",
                "debug_mode": self.app.debug
            }
        }
    
    def _generate_enhanced_api_paths(self) -> Dict[str, Any]:
        """Generate OpenAPI paths from registered routes"""
        paths = {}
        for path in self.app._internal_routes.keys():
            route_info = self.app._internal_routes[path]
            method = route_info.get('method', 'GET').lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = {
                "summary": self._get_route_description(path, method),
                "tags": self._get_route_tags(path),
                "parameters": self._get_route_parameters(path),
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "example": self._get_example_response(path, method)
                            }
                        }
                    }
                },
                "x-code-samples": self._generate_code_samples(path, method)
            }
        
        return paths
    
    def _get_route_description(self, path: str, method: str) -> str:
        """Get route description"""
        if 'admin' in path:
            return "Admin interface"
        elif 'health' in path:
            return "Health check endpoint"
        elif 'framework' in path:
            return "Framework information"
        return f"{method.upper()} {path}"
    
    def _get_route_tags(self, path: str) -> list:
        """Get route tags"""
        tags = []
        if 'admin' in path:
            tags.append('Admin')
        if 'ai' in path:
            tags.append('AI')
        if not tags:
            tags.append('API')
        return tags
    
    def _get_route_parameters(self, path: str) -> list:
        """Extract path parameters"""
        import re
        params = []
        pattern = r'\{([^}]+)\}'
        for match in re.finditer(pattern, path):
            param_name = match.group(1)
            params.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"The {param_name} parameter"
            })
        return params
    
    def _get_example_response(self, path: str, method: str) -> Dict[str, Any]:
        """Generate example response"""
        return {
            "status": "success",
            "data": f"Response from {method.upper()} {path}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_api_schemas(self) -> Dict[str, Any]:
        """Generate OpenAPI schemas"""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "integer"}
                }
            },
            "Success": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"},
                    "timestamp": {"type": "string"}
                }
            }
        }
    
    def _generate_code_samples(self, path: str, method: str) -> list:
        """Generate code samples for endpoint"""
        base_url = "http://localhost:8000"
        return [
            {
                "lang": "curl",
                "source": f'curl -X {method.upper()} "{base_url}{path}" \\\n  -H "Accept: application/json"'
            },
            {
                "lang": "javascript",
                "source": f'fetch("{base_url}{path}", {{\n  method: "{method.upper()}",\n  headers: {{"Accept": "application/json"}}\n}})'
            },
            {
                "lang": "python",
                "source": f'import requests\nresponse = requests.{method.lower()}("{base_url}{path}")\nprint(response.json())'
            }
        ]
    
    def _render_html_template(self, spec: Dict[str, Any]) -> str:
        """Render HTML documentation template"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.app.title} - API Documentation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #ffffff 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .header {{
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            border-bottom: 1px solid #333;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .api-section {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e5e5e5;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #000;
            border-bottom: 2px solid #6366f1;
            padding-bottom: 0.5rem;
        }}
        
        .endpoint {{
            border: 1px solid #e5e5e5;
            border-radius: 6px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background: #f9f9f9;
        }}
        
        .endpoint-method {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 1rem;
            font-size: 0.875rem;
        }}
        
        .method-get {{ background: #10b981; color: white; }}
        .method-post {{ background: #3b82f6; color: white; }}
        .method-put {{ background: #f59e0b; color: white; }}
        .method-delete {{ background: #ef4444; color: white; }}
        
        .endpoint-path {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-weight: 600;
            color: #333;
        }}
        
        .code-block {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Monaco', monospace;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-top: 1rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #6366f1;
            color: white;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .system-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .info-value {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .info-label {{
            font-size: 0.875rem;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.app.title}</h1>
        <p>{self.app.description}</p>
    </div>
    
    <div class="container">
        <div class="api-section">
            <h2 class="section-title">📊 System Information</h2>
            <div class="system-info">
                <div class="info-card">
                    <div class="info-value">{spec['x-system-info']['total_routes']}</div>
                    <div class="info-label">Total Endpoints</div>
                </div>
                <div class="info-card">
                    <div class="info-value">{spec['x-system-info']['ai_routes']}</div>
                    <div class="info-label">AI-Powered Routes</div>
                </div>
                <div class="info-card">
                    <div class="info-value">v{self.app.version}</div>
                    <div class="info-label">Version</div>
                </div>
                <div class="info-card">
                    <div class="info-value">{sys.version_info.major}.{sys.version_info.minor}</div>
                    <div class="info-label">Python</div>
                </div>
            </div>
        </div>
        
        <div class="api-section">
            <h2 class="section-title">🔌 API Endpoints</h2>
            {self._render_endpoints_html(spec)}
        </div>
    </div>
</body>
</html>
"""
    
    def _render_endpoints_html(self, spec: Dict[str, Any]) -> str:
        """Render endpoints in HTML"""
        html = ""
        for path, methods in spec.get('paths', {}).items():
            for method, details in methods.items():
                if method.startswith('x-'):
                    continue
                method_class = f"method-{method.lower()}"
                html += f"""
        <div class="endpoint">
            <div>
                <span class="endpoint-method {method_class}">{method.upper()}</span>
                <span class="endpoint-path">{path}</span>
            </div>
            <p>{details.get('summary', 'No description')}</p>
            {f'<div class="code-block">curl -X {method.upper()} "{path}"</div>' if path else ''}
        </div>
        """
        return html
    
    def _create_html_response(self, content: str):
        """Create HTML response object"""
        class HTMLResponse:
            def __init__(self, content, status_code=200, headers=None):
                self.content = content
                self.status_code = status_code
                self.headers = headers or {'content-type': 'text/html'}
        
        return HTMLResponse(content)
