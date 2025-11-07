"""FlaskIt Application - Wrapper autour de Flask"""
from flask import Flask, render_template
import os
from pathlib import Path


class FlaskIt(Flask):
    """
    Classe FlaskIt qui étend Flask avec des fonctionnalités supplémentaires.
    Utilisation : from flaskit import FlaskIt au lieu de from flask import Flask
    """
    
    def __init__(self, *args, **kwargs):
        # Charger automatiquement le fichier .env
        self._load_env_file()
        
        # Configuration par défaut pour les templates et static
        if 'template_folder' not in kwargs:
            kwargs['template_folder'] = 'web/views'
        if 'static_folder' not in kwargs:
            kwargs['static_folder'] = 'web/static'
        
        super().__init__(*args, **kwargs)
        
        # Enregistrer automatiquement les error handlers
        self._register_error_handlers()
    
    def _load_env_file(self):
        """Charge automatiquement le fichier .env s'il existe"""
        try:
            from dotenv import load_dotenv
            
            # Chercher le fichier .env dans le répertoire courant ou parents
            current = Path.cwd()
            for _ in range(5):  # Chercher jusqu'à 5 niveaux
                env_file = current / '.env'
                if env_file.exists():
                    load_dotenv(env_file)
                    break
                current = current.parent
        except ImportError:
            # python-dotenv n'est pas installé, ignorer silencieusement
            pass
    
    def _register_error_handlers(self):
        """Enregistre automatiquement les gestionnaires d'erreurs"""
        
        @self.errorhandler(404)
        def not_found(error):
            try:
                return render_template('pages/errors/404.html'), 404
            except:
                return {'error': 'Page not found'}, 404
        
        @self.errorhandler(500)
        def server_error(error):
            try:
                return render_template('pages/errors/500.html'), 500
            except:
                return {'error': 'Internal server error'}, 500
        
        @self.errorhandler(403)
        def forbidden(error):
            try:
                return render_template('pages/errors/403.html'), 403
            except:
                return {'error': 'Forbidden'}, 403
    
    def register_routes(self, register_func_or_list):
        """
        Enregistre les routes via une fonction ou une liste.
        
        Usage 1 - Fonction:
            app = FlaskIt(__name__)
            app.register_routes(register_routes)
        
        Usage 2 - Liste (style Masonite):
            from routes.web import ROUTES
            app.register_routes(ROUTES)
        """
        # Si c'est une liste de routes
        if isinstance(register_func_or_list, list):
            from flaskit.routing import Route
            route = Route()
            
            for r in register_func_or_list:
                if hasattr(r, 'register'):
                    r.register(self)
            
            return self
        
        # Si c'est une fonction
        result = register_func_or_list(self)
        
        # Si la fonction retourne un objet Route, l'enregistrer automatiquement
        if result and hasattr(result, 'register'):
            result.register(self)
        
        return self


# Fonction helper pour créer une app
def create_app(name=None, config=None):
    """
    Crée et configure une application FlaskIt.
    
    Args:
        name: Nom de l'application (par défaut __name__)
        config: Objet de configuration ou chemin vers fichier config
    
    Returns:
        Instance de FlaskIt configurée
    """
    app = FlaskIt(name or __name__)
    
    if config:
        if isinstance(config, str):
            app.config.from_pyfile(config)
        else:
            app.config.from_object(config)
    
    return app
