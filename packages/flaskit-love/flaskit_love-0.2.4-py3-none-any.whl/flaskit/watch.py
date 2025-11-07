"""
FlaskIt Watch - Internal Dashboard & Monitoring
Real-time project monitoring and debugging
"""
import os
import sys
import psutil
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template_string, jsonify
from typing import Dict, List, Any


class FlaskItWatch:
    """FlaskIt Watch - Internal monitoring dashboard"""
    
    def __init__(self, app=None):
        self.app = app
        self.routes_data = []
        self.request_logs = []
        self.max_logs = 100
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Watch with Flask app"""
        self.app = app
        watch_instance = self
        
        # Create blueprint
        watch_bp = Blueprint('flaskit_watch', __name__, url_prefix='/_watch')
        
        # Register routes
        @watch_bp.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_TEMPLATE, 
                project_info=watch_instance.get_project_info(),
                system_info=watch_instance.get_system_info())
        
        @watch_bp.route('/api/routes')
        def api_routes():
            return jsonify(watch_instance.get_routes())
        
        @watch_bp.route('/api/files')
        def api_files():
            return jsonify(watch_instance.get_project_files())
        
        @watch_bp.route('/api/system')
        def api_system():
            return jsonify(watch_instance.get_system_metrics())
        
        @watch_bp.route('/api/env')
        def api_env():
            return jsonify(watch_instance.get_env_vars())
        
        # Register blueprint
        app.register_blueprint(watch_bp)
        
        # Hook into request lifecycle
        @app.before_request
        def log_request():
            from flask import request
            self.request_logs.append({
                'method': request.method,
                'path': request.path,
                'timestamp': datetime.now().isoformat(),
                'ip': request.remote_addr
            })
            # Keep only last 100 requests
            if len(self.request_logs) > self.max_logs:
                self.request_logs.pop(0)
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        try:
            # Try to load data.json
            data_file = Path.cwd() / 'data.json'
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    app_info = data.get('app', {})
            else:
                app_info = {}
            
            return {
                'name': app_info.get('name', 'FlaskIt Project'),
                'version': app_info.get('version', '1.0.0'),
                'description': app_info.get('description', 'A FlaskIt application'),
                'author': app_info.get('author', 'Unknown'),
                'root_path': str(Path.cwd()),
                'python_version': sys.version.split()[0],
                'flaskit_version': self._get_flaskit_version()
            }
        except Exception as e:
            return {
                'name': 'FlaskIt Project',
                'version': '1.0.0',
                'error': str(e)
            }
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all registered routes"""
        routes = []
        for rule in self.app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule),
                'defaults': rule.defaults or {}
            })
        return sorted(routes, key=lambda x: x['path'])
    
    def get_project_files(self) -> Dict[str, Any]:
        """Get project file structure"""
        root = Path.cwd()
        
        def count_files(directory: Path, extension: str) -> int:
            return len(list(directory.rglob(f'*.{extension}')))
        
        return {
            'python_files': count_files(root, 'py'),
            'html_files': count_files(root, 'html'),
            'css_files': count_files(root, 'css'),
            'js_files': count_files(root, 'js'),
            'json_files': count_files(root, 'json'),
            'structure': self._get_directory_tree(root, max_depth=3)
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'Unknown'
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'total_mb': round(memory.total / 1024 / 1024, 2),
                'used_mb': round(memory.used / 1024 / 1024, 2)
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                'used_gb': round(disk.used / 1024 / 1024 / 1024, 2)
            },
            'requests': {
                'total': len(self.request_logs),
                'recent': self.request_logs[-10:]
            }
        }
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables (filtered)"""
        # Only show non-sensitive env vars
        safe_vars = {}
        for key, value in os.environ.items():
            # Hide sensitive values
            if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                safe_vars[key] = '***HIDDEN***'
            elif key.startswith('DISCORD_'):
                # Show Discord webhooks partially
                safe_vars[key] = value[:30] + '...' if len(value) > 30 else value
            else:
                safe_vars[key] = value
        return safe_vars
    
    def _get_flaskit_version(self) -> str:
        """Get FlaskIt version"""
        try:
            import flaskit
            return flaskit.__version__
        except:
            return 'Unknown'
    
    def _get_directory_tree(self, directory: Path, max_depth: int = 3, current_depth: int = 0) -> List[Dict]:
        """Get directory tree structure"""
        if current_depth >= max_depth:
            return []
        
        tree = []
        try:
            for item in sorted(directory.iterdir()):
                # Skip hidden files and common ignore patterns
                if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', 'venv', 'env']:
                    continue
                
                if item.is_dir():
                    tree.append({
                        'name': item.name,
                        'type': 'directory',
                        'children': self._get_directory_tree(item, max_depth, current_depth + 1)
                    })
                else:
                    tree.append({
                        'name': item.name,
                        'type': 'file',
                        'size': item.stat().st_size
                    })
        except PermissionError:
            pass
        
        return tree


# Dashboard HTML Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlaskIt Watch - {{ project_info.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 2rem;
            border-bottom: 2px solid #334155;
        }
        
        .header h1 {
            font-size: 2rem;
            color: #f97316;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            color: #94a3b8;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 0.75rem;
            padding: 1.5rem;
            transition: all 0.3s;
        }
        
        .card:hover {
            border-color: #f97316;
            box-shadow: 0 10px 30px rgba(249, 115, 22, 0.1);
        }
        
        .card-title {
            font-size: 0.875rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .card-value {
            font-size: 2rem;
            font-weight: 700;
            color: #f97316;
            margin-bottom: 0.25rem;
        }
        
        .card-label {
            font-size: 0.875rem;
            color: #64748b;
        }
        
        .section {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .section-title {
            font-size: 1.25rem;
            color: #f1f5f9;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #334155;
        }
        
        .route-item {
            padding: 0.75rem;
            border-bottom: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .route-item:last-child {
            border-bottom: none;
        }
        
        .route-path {
            font-family: 'Courier New', monospace;
            color: #38bdf8;
        }
        
        .route-methods {
            display: flex;
            gap: 0.5rem;
        }
        
        .method-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .method-get { background: #10b981; color: white; }
        .method-post { background: #3b82f6; color: white; }
        .method-put { background: #f59e0b; color: white; }
        .method-delete { background: #ef4444; color: white; }
        
        .progress-bar {
            background: #334155;
            height: 0.5rem;
            border-radius: 0.25rem;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #f97316, #fb923c);
            transition: width 0.3s;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #334155;
            color: #94a3b8;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            margin-right: 0.5rem;
        }
        
        .refresh-btn {
            background: #f97316;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .refresh-btn:hover {
            background: #ea580c;
            transform: translateY(-2px);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .live-indicator {
            display: inline-block;
            width: 0.5rem;
            height: 0.5rem;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 FlaskIt Watch</h1>
        <p><span class="live-indicator"></span>Real-time monitoring for {{ project_info.name }}</p>
    </div>
    
    <div class="container">
        <!-- Stats Grid -->
        <div class="grid">
            <div class="card">
                <div class="card-title">Project</div>
                <div class="card-value">{{ project_info.name }}</div>
                <div class="card-label">v{{ project_info.version }}</div>
            </div>
            
            <div class="card">
                <div class="card-title">CPU Usage</div>
                <div class="card-value" id="cpu-usage">--</div>
                <div class="card-label">Percent</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Memory</div>
                <div class="card-value" id="memory-usage">--</div>
                <div class="card-label" id="memory-total">-- MB</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-bar" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Routes</div>
                <div class="card-value" id="routes-count">--</div>
                <div class="card-label">Registered endpoints</div>
            </div>
        </div>
        
        <!-- Routes Section -->
        <div class="section">
            <h2 class="section-title">📍 Registered Routes</h2>
            <div id="routes-list">Loading...</div>
        </div>
        
        <!-- System Info -->
        <div class="section">
            <h2 class="section-title">💻 System Information</h2>
            <p><span class="badge">Platform</span> {{ system_info.platform }}</p>
            <p><span class="badge">Python</span> {{ system_info.python_version.split()[0] }}</p>
            <p><span class="badge">CPU Cores</span> {{ system_info.cpu_count }}</p>
            <p><span class="badge">FlaskIt</span> {{ project_info.flaskit_version }}</p>
        </div>
        
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
    </div>
    
    <script>
        async function loadData() {
            try {
                // Load routes
                const routesRes = await fetch('/_watch/api/routes');
                const routes = await routesRes.json();
                
                document.getElementById('routes-count').textContent = routes.length;
                
                const routesList = document.getElementById('routes-list');
                routesList.innerHTML = routes.map(route => `
                    <div class="route-item">
                        <span class="route-path">${route.path}</span>
                        <div class="route-methods">
                            ${route.methods.map(m => `
                                <span class="method-badge method-${m.toLowerCase()}">${m}</span>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
                
                // Load system metrics
                const metricsRes = await fetch('/_watch/api/system');
                const metrics = await metricsRes.json();
                
                document.getElementById('cpu-usage').textContent = metrics.cpu_percent.toFixed(1) + '%';
                document.getElementById('cpu-bar').style.width = metrics.cpu_percent + '%';
                
                document.getElementById('memory-usage').textContent = metrics.memory.percent.toFixed(1) + '%';
                document.getElementById('memory-total').textContent = metrics.memory.used_mb + ' / ' + metrics.memory.total_mb + ' MB';
                document.getElementById('memory-bar').style.width = metrics.memory.percent + '%';
                
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""


# Singleton instance
watch = FlaskItWatch()

__all__ = ['FlaskItWatch', 'watch']
