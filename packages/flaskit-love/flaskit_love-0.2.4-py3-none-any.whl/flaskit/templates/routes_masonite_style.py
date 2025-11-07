"""Template alternatif pour routes - Style Masonite"""

TEMPLATE_ROUTES_MASONITE = """from flaskit import Route

# Importez vos autres fichiers de routes ici
# from .auth import auth_routes

ROUTES = [
    Route.Get('/', home_index).name('home'),
    Route.Get('/about', home_about).name('about'),
    
    # Ajoutez d'autres routes ici
    # *auth_routes,
]

def home_index():
    from flaskit import render_template
    return render_template('pages/home/index.html')

def home_about():
    from flaskit import render_template
    return render_template('pages/home/about.html')
"""

# Dans app.py
TEMPLATE_APP_MASONITE = """from flaskit import FlaskIt
from app.configs.config import Config
from app.database import init_db
from routes.web import ROUTES

def create_app():
    app = FlaskIt(__name__)
    app.config.from_object(Config)
    
    init_db(app)
    
    # Enregistrer les routes (style liste)
    app.register_routes(ROUTES)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
"""
