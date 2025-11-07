"""FlaskIt Route Class - Elegant routing for Flask"""
from flask import render_template
from typing import List, Callable, Optional


class RouteBuilder:
    """Builder pour créer des routes individuelles de manière fluide"""
    
    def __init__(self, method, path, handler):
        self.method = method
        self.path = path
        self.handler = handler
        self._name = None
        self._middleware = []
    
    def name(self, name):
        """Nomme la route"""
        self._name = name
        return self
    
    def middleware(self, *middleware):
        """Ajoute des middlewares"""
        self._middleware.extend(middleware)
        return self
    
    def register(self, app):
        """Enregistre la route sur l'app Flask"""
        endpoint = self._name or f"{self.method}_{self.path.replace('/', '_')}"
        
        if self.handler:
            app.add_url_rule(
                self.path,
                endpoint=endpoint,
                view_func=self.handler,
                methods=[self.method]
            )


class Route:
    """Elegant routing system for FlaskIt"""
    
    def __init__(self, app=None):
        self.app = app
        self.routes = []
        self._current_route = None
    
    def view(self, path: str, view: str, methods: Optional[List[str]] = None):
        """
        Register a view route
        
        Usage:
            route.view('/', 'home.index').name('home')
            route.view('/about', 'home.about').name('about')
        
        Args:
            path: URL path (e.g., '/', '/about')
            view: View path in format 'folder.template' (e.g., 'home.index')
            methods: HTTP methods (default: ['GET'])
        """
        if methods is None:
            methods = ['GET']
        
        # Parse view path: 'home.index' -> 'pages/home/index.html'
        view_parts = view.split('.')
        if len(view_parts) == 2:
            folder, template = view_parts
            template_path = f'pages/{folder}/{template}.html'
        else:
            template_path = f'pages/{view}.html'
        
        self._current_route = {
            'path': path,
            'template': template_path,
            'methods': methods,
            'name': None,
            'middleware': []
        }
        
        return self
    
    def get(self, path: str, handler: Callable):
        """
        Register a GET route with a handler function
        
        Usage:
            route.get('/api/users', get_users).name('api.users')
        """
        self._current_route = {
            'path': path,
            'handler': handler,
            'methods': ['GET'],
            'name': None,
            'middleware': []
        }
        return self
    
    def post(self, path: str, handler: Callable):
        """Register a POST route"""
        self._current_route = {
            'path': path,
            'handler': handler,
            'methods': ['POST'],
            'name': None,
            'middleware': []
        }
        return self
    
    def put(self, path: str, handler: Callable):
        """Register a PUT route"""
        self._current_route = {
            'path': path,
            'handler': handler,
            'methods': ['PUT'],
            'name': None,
            'middleware': []
        }
        return self
    
    def delete(self, path: str, handler: Callable):
        """Register a DELETE route"""
        self._current_route = {
            'path': path,
            'handler': handler,
            'methods': ['DELETE'],
            'name': None,
            'middleware': []
        }
        return self
    
    def name(self, route_name: str):
        """
        Set the name for the current route
        
        Usage:
            route.view('/', 'home.index').name('home')
        """
        if self._current_route:
            self._current_route['name'] = route_name
            self.routes.append(self._current_route)
            self._current_route = None
        return self
    
    def middleware(self, *middlewares):
        """
        Add middleware to the current route
        
        Usage:
            route.view('/admin', 'admin.dashboard').middleware('auth', 'admin').name('admin')
        """
        if self._current_route:
            self._current_route['middleware'].extend(middlewares)
        return self
    
    def register(self, app):
        """Register all routes with the Flask app"""
        self.app = app
        
        for route_config in self.routes:
            path = route_config['path']
            methods = route_config['methods']
            route_name = route_config['name']
            
            if 'template' in route_config:
                # View route
                template = route_config['template']
                
                def make_view_handler(tmpl):
                    def handler(**kwargs):
                        return render_template(tmpl, **kwargs)
                    return handler
                
                handler = make_view_handler(template)
            else:
                # Handler route
                handler = route_config['handler']
            
            # Register with Flask
            app.add_url_rule(
                path,
                endpoint=route_name,
                view_func=handler,
                methods=methods
            )
    
    def group(self, prefix: str = '', middleware: List[str] = None):
        """
        Create a route group with common prefix and middleware
        
        Usage:
            with route.group('/api', middleware=['auth']):
                route.get('/users', get_users).name('api.users')
        """
        return RouteGroup(self, prefix, middleware or [])


class RouteGroup:
    """Context manager for route groups"""
    
    def __init__(self, route: Route, prefix: str, middleware: List[str]):
        self.route = route
        self.prefix = prefix
        self.middleware = middleware
        self.original_routes_count = len(route.routes)
    
    def __enter__(self):
        return self.route
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Apply prefix and middleware to new routes
        for i in range(self.original_routes_count, len(self.route.routes)):
            route_config = self.route.routes[i]
            route_config['path'] = self.prefix + route_config['path']
            route_config['middleware'].extend(self.middleware)


# Ajout de méthodes statiques pour syntaxe style Masonite
Route.Get = lambda path, handler: RouteBuilder('GET', path, handler)
Route.Post = lambda path, handler: RouteBuilder('POST', path, handler)
Route.Put = lambda path, handler: RouteBuilder('PUT', path, handler)
Route.Delete = lambda path, handler: RouteBuilder('DELETE', path, handler)
Route.Patch = lambda path, handler: RouteBuilder('PATCH', path, handler)
