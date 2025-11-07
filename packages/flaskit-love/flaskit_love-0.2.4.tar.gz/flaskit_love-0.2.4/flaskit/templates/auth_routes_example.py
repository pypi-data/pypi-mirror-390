"""Exemple de fichier de routes supplémentaire - auth.py"""

TEMPLATE_AUTH_ROUTES = """from flaskit import jsonify

def auth_routes(route):
    \"\"\"Routes d'authentification\"\"\"
    
    with route.group('/auth'):
        route.view('/login', 'auth.login').name('auth.login')
        route.view('/register', 'auth.register').name('auth.register')
        
        # API
        route.post('/api/login', login_handler).name('api.auth.login')
        route.post('/api/register', register_handler).name('api.auth.register')
        route.post('/api/logout', logout_handler).name('api.auth.logout')

def login_handler():
    return jsonify({'message': 'Login endpoint'})

def register_handler():
    return jsonify({'message': 'Register endpoint'})

def logout_handler():
    return jsonify({'message': 'Logout endpoint'})
"""
