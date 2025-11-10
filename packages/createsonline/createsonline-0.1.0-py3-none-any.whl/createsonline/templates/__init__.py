# createsonline/templates/__init__.py
"""
CREATESONLINE Internal Template System

Pure Python template engine to replace Jinja2.
Zero external dependencies, built specifically for CREATESONLINE.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from pathlib import Path

# ========================================
# CORE TEMPLATE ENGINE
# ========================================

class CreatesonlineTemplate:
    """Individual template class"""
    
    def __init__(self, content: str, name: str = ""):
        self.content = content
        self.name = name
        self.compiled = None
        self._compile()
    
    def _compile(self):
        """Pre-compile template for better performance"""
        self.compiled = self.content
        
        # Pre-process includes and extends
        self.compiled = self._process_includes(self.compiled)
        
        # Cache variable patterns
        self.variable_pattern = re.compile(r'\{\{\s*([^}]+)\s*\}\}')
        self.if_pattern = re.compile(r'\{\%\s*if\s+([^%]+)\s*\%\}(.*?)\{\%\s*endif\s*\%\}', re.DOTALL)
        self.for_pattern = re.compile(r'\{\%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}(.*?)\{\%\s*endfor\s*\%\}', re.DOTALL)
        self.block_pattern = re.compile(r'\{\%\s*block\s+(\w+)\s*\%\}(.*?)\{\%\s*endblock\s*\%\}', re.DOTALL)
        self.include_pattern = re.compile(r'\{\%\s*include\s+["\']([^"\']+)["\']\s*\%\}')
    
    def _process_includes(self, content: str) -> str:
        """Process include statements"""
        # This would be enhanced to actually load and include files
        return content
    
    def render(self, context: Dict[str, Any] = None) -> str:
        """Render template with context"""
        context = context or {}
        result = self.compiled
        
        # Add template functions to context
        enhanced_context = {
            **self._get_builtin_functions(),
            **context
        }
        
        # Process template directives in order
        result = self._process_blocks(result, enhanced_context)
        result = self._process_for_loops(result, enhanced_context)
        result = self._process_if_statements(result, enhanced_context)
        result = self._process_variables(result, enhanced_context)
        result = self._process_filters(result, enhanced_context)
        
        return result
    
    def _get_builtin_functions(self) -> Dict[str, Any]:
        """Get built-in template functions"""
        return {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'datetime': datetime,
            'now': datetime.now,
            'utcnow': datetime.utcnow,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'title': lambda x: str(x).title(),
            'capitalize': lambda x: str(x).capitalize(),
            'strip': lambda x: str(x).strip(),
            'replace': lambda x, old, new: str(x).replace(old, new),
            'split': lambda x, sep=None: str(x).split(sep),
            'join': lambda lst, sep='': sep.join(str(x) for x in lst),
            'default': lambda value, default_val: default_val if value is None else value,
            'truncate': lambda text, length=100: str(text)[:length] + '...' if len(str(text)) > length else str(text),
            'format_number': lambda num: f"{num:,}" if isinstance(num, (int, float)) else str(num),
            'pluralize': lambda count, singular='', plural='s': plural if count != 1 else singular,
        }
    
    def _process_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{ variable }} substitutions"""
        def replace_var(match):
            var_expr = match.group(1).strip()
            try:
                value = self._evaluate_expression(var_expr, context)
                return str(value) if value is not None else ""
            except:
                return f"{{{{ {var_expr} }}}}"  # Return original if evaluation fails
        
        return self.variable_pattern.sub(replace_var, content)
    
    def _process_if_statements(self, content: str, context: Dict[str, Any]) -> str:
        """Process {% if %} statements"""
        def replace_if(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            
            try:
                # Handle else clause
                if '{% else %}' in if_content:
                    if_part, else_part = if_content.split('{% else %}', 1)
                else:
                    if_part = if_content
                    else_part = ""
                
                # Evaluate condition
                result = self._evaluate_condition(condition, context)
                
                if result:
                    return self._process_template_content(if_part, context)
                else:
                    return self._process_template_content(else_part, context)
            except:
                return if_content  # Return content if condition evaluation fails
        
        return self.if_pattern.sub(replace_if, content)
    
    def _process_for_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process {% for %} loops"""
        def replace_for(match):
            var_name = match.group(1)
            list_expr = match.group(2)
            loop_content = match.group(3)
            
            try:
                items = self._evaluate_expression(list_expr, context)
                if not items:
                    return ""
                
                result_parts = []
                for index, item in enumerate(items):
                    loop_context = {
                        **context,
                        var_name: item,
                        'loop': {
                            'index': index + 1,
                            'index0': index,
                            'first': index == 0,
                            'last': index == len(items) - 1,
                            'length': len(items),
                        }
                    }
                    
                    item_result = self._process_template_content(loop_content, loop_context)
                    result_parts.append(item_result)
                
                return "".join(result_parts)
            except:
                return loop_content
        
        return self.for_pattern.sub(replace_for, content)
    
    def _process_blocks(self, content: str, context: Dict[str, Any]) -> str:
        """Process {% block %} statements"""
        def replace_block(match):
            block_name = match.group(1)
            block_content = match.group(2)
            
            # Check if block is overridden in context
            blocks = context.get('_blocks', {})
            if block_name in blocks:
                return blocks[block_name]
            
            return self._process_template_content(block_content, context)
        
        return self.block_pattern.sub(replace_block, content)
    
    def _process_filters(self, content: str, context: Dict[str, Any]) -> str:
        """Process variable filters like {{ var|filter }}"""
        filter_pattern = re.compile(r'\{\{\s*([^}|]+)\|([^}]+)\s*\}\}')
        
        def apply_filter(match):
            var_expr = match.group(1).strip()
            filter_expr = match.group(2).strip()
            
            try:
                value = self._evaluate_expression(var_expr, context)
                
                # Parse filter and arguments
                if ':' in filter_expr:
                    filter_name, filter_args = filter_expr.split(':', 1)
                    filter_name = filter_name.strip()
                    # Simple argument parsing
                    args = [arg.strip().strip('"\'') for arg in filter_args.split(',')]
                else:
                    filter_name = filter_expr.strip()
                    args = []
                
                # Apply filter
                filter_func = context.get(filter_name) or getattr(self, f'_filter_{filter_name}', None)
                
                if filter_func and callable(filter_func):
                    return str(filter_func(value, *args))
                elif filter_name in context and callable(context[filter_name]):
                    return str(context[filter_name](value, *args))
                else:
                    # Built-in filters
                    return str(self._apply_builtin_filter(value, filter_name, args))
                
            except:
                return f"{{{{ {var_expr}|{filter_expr} }}}}"
        
        return filter_pattern.sub(apply_filter, content)
    
    def _process_template_content(self, content: str, context: Dict[str, Any]) -> str:
        """Process template content recursively"""
        result = content
        result = self._process_for_loops(result, context)
        result = self._process_if_statements(result, context)
        result = self._process_variables(result, context)
        result = self._process_filters(result, context)
        return result
    
    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        """Safely evaluate template expressions"""
        # Handle dot notation (object.attribute)
        if '.' in expr:
            parts = expr.split('.')
            value = context
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        
        # Handle array/dict access
        if '[' in expr and ']' in expr:
            var_name = expr.split('[')[0]
            key_expr = expr.split('[')[1].split(']')[0].strip('"\'')
            
            if var_name in context:
                try:
                    if key_expr.isdigit():
                        return context[var_name][int(key_expr)]
                    else:
                        return context[var_name][key_expr]
                except (KeyError, IndexError, TypeError):
                    return None
        
        # Simple variable lookup
        return context.get(expr, None)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate conditional expressions"""
        condition = condition.strip()
        
        # Handle 'not' operator
        if condition.startswith('not '):
            var_expr = condition[4:].strip()
            value = self._evaluate_expression(var_expr, context)
            return not bool(value)
        
        # Handle comparison operators
        for op in ['==', '!=', '>=', '<=', '>', '<']:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._evaluate_expression(left.strip(), context)
                right_val = self._evaluate_expression(right.strip().strip('"\''), context)
                
                if op == '==': return left_val == right_val
                elif op == '!=': return left_val != right_val
                elif op == '>=': return left_val >= right_val
                elif op == '<=': return left_val <= right_val
                elif op == '>': return left_val > right_val
                elif op == '<': return left_val < right_val
        
        # Handle 'in' operator
        if ' in ' in condition:
            item, container = condition.split(' in ', 1)
            item_val = self._evaluate_expression(item.strip(), context)
            container_val = self._evaluate_expression(container.strip(), context)
            return item_val in container_val if container_val else False
        
        # Handle 'and' and 'or'
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(self._evaluate_condition(part.strip(), context) for part in parts)
        
        if ' or ' in condition:
            parts = condition.split(' or ')
            return any(self._evaluate_condition(part.strip(), context) for part in parts)
        
        # Simple boolean evaluation
        value = self._evaluate_expression(condition, context)
        return bool(value)
    
    def _apply_builtin_filter(self, value: Any, filter_name: str, args: List[str]) -> Any:
        """Apply built-in template filters"""
        if filter_name == 'default':
            return args[0] if value is None else value
        elif filter_name == 'length':
            return len(value) if hasattr(value, '__len__') else 0
        elif filter_name == 'upper':
            return str(value).upper()
        elif filter_name == 'lower':
            return str(value).lower()
        elif filter_name == 'title':
            return str(value).title()
        elif filter_name == 'capitalize':
            return str(value).capitalize()
        elif filter_name == 'truncate':
            length = int(args[0]) if args else 100
            text = str(value)
            return text[:length] + '...' if len(text) > length else text
        elif filter_name == 'join':
            separator = args[0] if args else ''
            return separator.join(str(x) for x in value)
        elif filter_name == 'date':
            format_str = args[0] if args else '%Y-%m-%d'
            if isinstance(value, datetime):
                return value.strftime(format_str)
            return str(value)
        elif filter_name == 'json':
            return json.dumps(value)
        elif filter_name == 'safe':
            return str(value)  # In real implementation, this would mark as safe HTML
        else:
            return value

# ========================================
# TEMPLATE LOADER AND ENVIRONMENT
# ========================================

class CreatesonlineTemplateLoader:
    """Template loader for file-based templates"""
    
    def __init__(self, template_dirs: List[str] = None):
        self.template_dirs = template_dirs or []
        self.cache = {}
        self.auto_reload = True
    
    def add_template_dir(self, directory: str):
        """Add template directory"""
        if directory not in self.template_dirs:
            self.template_dirs.append(directory)
    
    def load_template(self, template_name: str) -> CreatesonlineTemplate:
        """Load template from file"""
        # Check cache first
        if template_name in self.cache and not self.auto_reload:
            return self.cache[template_name]
        
        # Find template file
        template_content = self._find_template_file(template_name)
        
        if template_content is None:
            raise FileNotFoundError(f"Template '{template_name}' not found")
        
        # Create and cache template
        # Create and cache template
        template = CreatesonlineTemplate(template_content, template_name)
        self.cache[template_name] = template
        
        return template
    
    def _find_template_file(self, template_name: str) -> Optional[str]:
        """Find template file in template directories"""
        for template_dir in self.template_dirs:
            template_path = os.path.join(template_dir, template_name)
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    continue
        
        return None
    
    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()

class CreatesonlineTemplateEnvironment:
    """Main template environment for CREATESONLINE"""
    
    def __init__(self, template_dirs: List[str] = None, auto_reload: bool = True):
        self.loader = CreatesonlineTemplateLoader(template_dirs)
        self.loader.auto_reload = auto_reload
        self.globals = {}
        self.filters = {}
        self.tests = {}
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in template functions and filters"""
        self.globals.update({
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'datetime': datetime,
            'now': datetime.now,
            'utcnow': datetime.utcnow,
        })
        
        self.filters.update({
            'default': lambda value, default_val: default_val if value is None else value,
            'length': lambda value: len(value) if hasattr(value, '__len__') else 0,
            'upper': lambda value: str(value).upper(),
            'lower': lambda value: str(value).lower(),
            'title': lambda value: str(value).title(),
            'capitalize': lambda value: str(value).capitalize(),
            'truncate': lambda value, length=100: str(value)[:length] + '...' if len(str(value)) > length else str(value),
            'join': lambda value, separator='': separator.join(str(x) for x in value),
            'replace': lambda value, old, new: str(value).replace(old, new),
            'split': lambda value, sep=None: str(value).split(sep),
            'strip': lambda value: str(value).strip(),
            'format_number': lambda value: f"{value:,}" if isinstance(value, (int, float)) else str(value),
            'date': lambda value, format_str='%Y-%m-%d': value.strftime(format_str) if isinstance(value, datetime) else str(value),
            'json': lambda value: json.dumps(value),
            'safe': lambda value: str(value),  # Mark as safe HTML
            'escape': lambda value: str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;'),
        })
    
    def add_template_dir(self, directory: str):
        """Add template directory"""
        self.loader.add_template_dir(directory)
    
    def get_template(self, template_name: str) -> CreatesonlineTemplate:
        """Get template by name"""
        return self.loader.load_template(template_name)
    
    def render_template(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """Render template with context"""
        template = self.get_template(template_name)
        full_context = {**self.globals, **self.filters, **(context or {})}
        return template.render(full_context)
    
    def render_string(self, template_string: str, context: Dict[str, Any] = None) -> str:
        """Render template string with context"""
        template = CreatesonlineTemplate(template_string)
        full_context = {**self.globals, **self.filters, **(context or {})}
        return template.render(full_context)
    
    def add_global(self, name: str, value: Any):
        """Add global variable"""
        self.globals[name] = value
    
    def add_filter(self, name: str, filter_func: Callable):
        """Add custom filter"""
        self.filters[name] = filter_func

# ========================================
# DEFAULT ADMIN TEMPLATES
# ========================================

DEFAULT_ADMIN_TEMPLATES = {
    "admin/base.html": """<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default:"CREATESONLINE Admin" }}</title>
    <link rel="stylesheet" href="/static/css/dashboard.css">
    <style>
        /* CREATESONLINE Admin Styles */
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .admin-container { min-height: 100vh; display: flex; flex-direction: column; }
        .admin-header { background: #000; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .admin-header h1 { margin: 0; font-size: 1.5rem; }
        .admin-nav { background: white; border-bottom: 1px solid #e5e5e5; padding: 0 2rem; }
        .admin-nav ul { list-style: none; margin: 0; padding: 0; display: flex; }
        .admin-nav li { margin-right: 2rem; }
        .admin-nav a { text-decoration: none; color: #374151; padding: 1rem 0; display: block; border-bottom: 2px solid transparent; }
        .admin-nav a:hover, .admin-nav a.active { color: #000; border-color: #000; }
        .admin-content { flex: 1; padding: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .card-header { padding: 1.5rem; border-bottom: 1px solid #e5e5e5; }
        .card-body { padding: 1.5rem; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: 500; }
        .btn-primary { background: #000; color: white; }
        .btn-primary:hover { background: #374151; }
        .btn-secondary { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
        .btn-secondary:hover { background: #e5e7eb; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e5e5; }
        .table th { font-weight: 600; background: #f9fafb; }
        .table tbody tr:hover { background: #f9fafb; }
        .status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
        .status-active { background: #d1fae5; color: #065f46; }
        .status-inactive { background: #fee2e2; color: #991b1b; }
        .alert { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
        .alert-success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
        .alert-info { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    </style>
</head>
<body>
    <div class="admin-container">
        <!-- Header -->
        <header class="admin-header">
            <h1><img src="/static/image/favicon-32x32.png" alt="CREATESONLINE" style="width: 32px; height: 32px; vertical-align: middle; margin-right: 10px;">CREATESONLINE Admin</h1>
            <div style="display: flex; align-items: center; gap: 1rem;">
                {% if user %}
                <span>{{ user.username|default:"Admin" }}</span>
                <a href="/admin/logout/" style="color: white;">Logout</a>
                {% else %}
                <a href="/admin/login/" style="color: white;">Login</a>
                {% endif %}
            </div>
        </header>
        
        <!-- Navigation -->
        <nav class="admin-nav">
            <ul>
                <li><a href="/admin/" class="{% if request.path == '/admin/' %}active{% endif %}">Dashboard</a></li>
                <li><a href="/admin/users/">Users</a></li>
                <li><a href="/admin/ai-models/">AI Models</a></li>
                <li><a href="/admin/settings/">Settings</a></li>
                <li><a href="/admin/ai/">AI Dashboard</a></li>
            </ul>
        </nav>
        
        <!-- Content -->
        <main class="admin-content">
            {% block content %}
            <div class="card">
                <div class="card-body">
                    <h2>Welcome to CREATESONLINE Admin</h2>
                    <p>The AI-Native Framework Administration Interface</p>
                </div>
            </div>
            {% endblock %}
        </main>
    </div>
</body>
</html>""",

    "admin/dashboard.html": """{% block content %}
<div class="card">
    <div class="card-header">
        <h2 style="margin: 0;">ðŸ“Š Dashboard Overview</h2>
    </div>
    <div class="card-body">
        <!-- Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            {% for metric in metrics %}
            <div class="card">
                <div class="card-body" style="text-align: center;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">
                        {{ metric.title }}
                    </h3>
                    <div style="font-size: 2.25rem; font-weight: 700; color: #111827; line-height: 1;">
                        {{ metric.value }}
                    </div>
                    <div style="color: #059669; font-size: 0.875rem; margin-top: 0.5rem;">
                        {{ metric.change }}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- AI Models Section -->
        {% if ai_models %}
        <div class="card">
            <div class="card-header">
                <h3 style="margin: 0;">ðŸ§  Active AI Models</h3>
            </div>
            <div class="card-body">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    {% for model in ai_models %}
                    <div class="card" style="border: 1px solid #e5e7eb;">
                        <div class="card-body">
                            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                                <h4 style="margin: 0; font-size: 1rem;">{{ model.name }}</h4>
                                <span class="status-badge {% if model.status == 'active' %}status-active{% else %}status-inactive{% endif %}">
                                    {{ model.status|title }}
                                </span>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                                {% if model.accuracy %}
                                <div>
                                    <div style="font-weight: 600;">{{ model.accuracy }}</div>
                                    <div style="font-size: 0.75rem; color: #6b7280;">Accuracy</div>
                                </div>
                                {% endif %}
                                {% if model.predictions %}
                                <div>
                                    <div style="font-weight: 600;">{{ model.predictions }}</div>
                                    <div style="font-size: 0.75rem; color: #6b7280;">Predictions</div>
                                </div>
                                {% endif %}
                                {% if model.generated %}
                                <div>
                                    <div style="font-weight: 600;">{{ model.generated }}</div>
                                    <div style="font-size: 0.75rem; color: #6b7280;">Generated</div>
                                </div>
                                {% endif %}
                                {% if model.searches %}
                                <div>
                                    <div style="font-weight: 600;">{{ model.searches }}</div>
                                    <div style="font-size: 0.75rem; color: #6b7280;">Searches</div>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Recent Activity -->
        <div class="card">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">ðŸ“‹ Recent Activity</h3>
                <a href="/admin/activity/" class="btn btn-secondary" style="font-size: 0.875rem;">View All</a>
            </div>
            <div class="card-body">
                {% if activities %}
                <div style="space-y: 1rem;">
                    {% for activity in activities %}
                    <div style="padding: 1rem 0; border-bottom: 1px solid #f3f4f6; display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: 600; color: #111827;">{{ activity.title }}</div>
                            <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.25rem;">{{ activity.description }}</div>
                        </div>
                        <div style="color: #9ca3af; font-size: 0.75rem; white-space: nowrap; margin-left: 1rem;">
                            {{ activity.time }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div style="text-align: center; color: #6b7280; padding: 2rem 0;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">ðŸ“</div>
                    <p>No recent activity to display</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    "admin/model_list.html": """{% block content %}
<div class="card">
    <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="margin: 0;">{{ model_name|title }} Management</h2>
        <a href="/admin/{{ app_label }}/{{ model_name }}/add/" class="btn btn-primary">
            âž• Add {{ model_name|title }}
        </a>
    </div>
    <div class="card-body">
        {% if objects %}
        <div style="overflow-x: auto;">
            <table class="table">
                <thead>
                    <tr>
                        {% for field in list_display %}
                        <th>{{ field|title }}</th>
                        {% endfor %}
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for obj in objects %}
                    <tr>
                        {% for field in list_display %}
                        <td>{{ obj[field]|default:"-" }}</td>
                        {% endfor %}
                        <td>
                            <div style="display: flex; gap: 0.5rem;">
                                <a href="/admin/{{ app_label }}/{{ model_name }}/{{ obj.id }}/" class="btn btn-secondary" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">
                                    Edit
                                </a>
                                <a href="/admin/{{ app_label }}/{{ model_name }}/{{ obj.id }}/delete/" 
                                   class="btn btn-secondary" 
                                   style="font-size: 0.75rem; padding: 0.25rem 0.5rem; color: #dc2626;"
                                   onclick="return confirm('Are you sure you want to delete this {{ model_name }}?')">
                                    Delete
                                </a>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div style="text-align: center; color: #6b7280; padding: 4rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">ðŸ“‹</div>
            <h3>No {{ model_name }} found</h3>
            <p>Get started by creating your first {{ model_name }}.</p>
            <a href="/admin/{{ app_label }}/{{ model_name }}/add/" class="btn btn-primary" style="margin-top: 1rem;">
                Add {{ model_name|title }}
            </a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    "admin/login.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CREATESONLINE Admin - Login</title>
    <link rel="stylesheet" href="/static/css/login.css">
</head>
<body class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="w-full max-w-md">
        <div class="form-card rounded-2xl p-8 shadow-lg slide-in">
            <!-- Logo Section -->
            <div class="text-center mb-8">
                <div class="logo-container logo-spin">
                    <div class="logo-icon">C</div>
                </div>
                <h1 class="text-3xl font-bold text-black mb-2">CREATESONLINE</h1>
                <p class="text-gray-600 text-sm">Build Intelligence Into Everything</p>
            </div>
            
            <!-- Login Form -->
            <form method="post" class="space-y-6">
                <div class="form-group">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" id="username" name="username" class="form-input focus-ring" 
                           placeholder="Enter your username" required autocomplete="username">
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-input focus-ring"
                           placeholder="Enter your password" required autocomplete="current-password">
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <input type="checkbox" id="remember" name="remember" class="checkbox focus-ring">
                        <label for="remember" class="ml-2 text-sm text-gray-600">Remember me</label>
                    </div>
                    <a href="#" class="text-sm link">Forgot password?</a>
                </div>
                
                <button type="submit" class="btn btn-primary w-full py-4 text-base font-semibold">
                    Sign In to Admin
                </button>
            </form>
            
            <div class="mt-8 text-center">
                <p class="text-xs text-gray-500">
                    <a href="/" class="link">â† Back to Homepage</a>
                </p>
                <p class="text-xs text-gray-400 mt-2">
                </p>
            </div>
        </div>
        
        <div class="mt-6 text-center">
            <div class="status-indicator">
                <div class="status-dot"></div>
                AI System Online
            </div>
        </div>
    </div>
</body>
</html>"""
}

# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def create_template_environment(template_dirs: List[str] = None) -> CreatesonlineTemplateEnvironment:
    """Create a CREATESONLINE template environment"""
    env = CreatesonlineTemplateEnvironment(template_dirs)
    
    # Add default template directories
    current_dir = os.path.dirname(__file__)
    default_dirs = [
        os.path.join(current_dir, "templates"),
        os.path.join(current_dir, "..", "static", "templates"),
        os.path.join(current_dir, "..", "..", "templates"),
    ]
    
    for dir_path in default_dirs:
        if os.path.exists(dir_path):
            env.add_template_dir(dir_path)
    
    return env

def get_default_template_environment() -> CreatesonlineTemplateEnvironment:
    """Get the default CREATESONLINE template environment"""
    return _default_env

def render_template(template_name: str, context: Dict[str, Any] = None) -> str:
    """Quick template rendering function"""
    return get_default_template_environment().render_template(template_name, context)

def render_string(template_string: str, context: Dict[str, Any] = None) -> str:
    """Quick string template rendering function"""
    return get_default_template_environment().render_string(template_string, context)

def setup_default_templates():
    """Setup default admin templates"""
    env = get_default_template_environment()
    
    # Store default templates in memory
    for template_name, content in DEFAULT_ADMIN_TEMPLATES.items():
        template = CreatesonlineTemplate(content, template_name)
        env.loader.cache[template_name] = template

# ========================================
# GLOBAL INSTANCE
# ========================================

# Create default template environment
_default_env = create_template_environment()
setup_default_templates()

# Export main components
__all__ = [
    'CreatesonlineTemplate',
    'CreatesonlineTemplateLoader', 
    'CreatesonlineTemplateEnvironment',
    'create_template_environment',
    'get_default_template_environment',
    'render_template',
    'render_string',
    'setup_default_templates',
    'DEFAULT_ADMIN_TEMPLATES'
]
