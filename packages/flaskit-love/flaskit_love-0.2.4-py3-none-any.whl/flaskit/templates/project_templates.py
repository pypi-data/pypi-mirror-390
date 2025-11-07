"""Project Templates for FlaskIt CLI"""

# Main App Template
TEMPLATE_APP = """from flaskit import FlaskIt, watch
from app.config.config import Config
from app.database import init_db
from routes.web import register_routes

# Note: FlaskIt charge automatiquement le fichier .env
# Pas besoin d'importer ou d'appeler load_dotenv() !

def create_app():
    app = FlaskIt(__name__)
    app.config.from_object(Config)
    
    # Initialize Watch dashboard (accessible at /_watch)
    watch.init_app(app)
    
    init_db(app)
    app.register_routes(register_routes)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
"""

# Configuration Template
TEMPLATE_CONFIG = """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/app/database/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Debug
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
"""

# Database Init Template
TEMPLATE_DATABASE_INIT = """from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
"""

# Model Example Template
TEMPLATE_MODEL_EXAMPLE = """from app.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
"""

# Service Example Template
TEMPLATE_SERVICE_EXAMPLE = """from app.models.user import User
from app.database import db

class UserService:
    @staticmethod
    def create_user(username, email):
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_all_users():
        return User.query.all()
    
    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
"""

# Logic Example Template - Users Logic (MVL Pattern)
TEMPLATE_LOGIC_EXAMPLE = """# Logique métier pour les utilisateurs (MVL Pattern)
from flaskit import jsonify, request
from app.services.user_service import UserService

class Users:
    \"\"\"Logique métier pour les utilisateurs - Couche Logic du pattern MVL\"\"\"
    
    @staticmethod
    def getall():
        \"\"\"Récupère tous les utilisateurs\"\"\"
        users = UserService.get_all_users()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    
    @staticmethod
    def getone(id):
        \"\"\"Récupère un utilisateur par ID\"\"\"
        user = UserService.get_user_by_id(id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    
    @staticmethod
    def create():
        \"\"\"Crée un nouvel utilisateur\"\"\"
        data = request.get_json()
        
        # Validation
        if not data.get('username') or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Username and email are required'
            }), 400
        
        # Création via le service
        user = UserService.create_user(
            username=data['username'],
            email=data['email']
        )
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': user.to_dict()
        }), 201
    
    @staticmethod
    def update(id):
        \"\"\"Met à jour un utilisateur\"\"\"
        data = request.get_json()
        user = UserService.get_user_by_id(id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Mise à jour des champs
        if data.get('username'):
            user.username = data['username']
        if data.get('email'):
            user.email = data['email']
        
        from app.database import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict()
        })
    
    @staticmethod
    def delete(id):
        \"\"\"Supprime un utilisateur\"\"\"
        success = UserService.delete_user(id)
        
        if not success:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200


class BusinessLogic:
    \"\"\"Logique métier générale\"\"\"
    
    @staticmethod
    def validate_email(email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def process_data(data):
        # Traitement des données métier
        return data
"""

# Routes Template with FlaskIt routing system
TEMPLATE_ROUTES = """from flaskit import Route

def register_routes(app):
    route = Route()
    
    route.view('/', 'home.index').name('home')
    route.view('/about', 'home.about').name('about')
    
    return route
"""

# Home Routes Template (legacy - kept for reference)
TEMPLATE_HOME_ROUTES = """from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('pages/home/index.html', title='Accueil')

@home_bp.route('/about')
def about():
    return render_template('pages/home/about.html', title='À propos')
"""

# Layout Template
TEMPLATE_LAYOUT = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}FlaskIt App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'components/footer.html' %}
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

# Navbar Component Template
TEMPLATE_NAVBAR = """<nav class="navbar">
    <div class="container">
     <a href="/" class="logo">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <rect width="32" height="32" rx="8" fill="#FBBF24"/>
                    <path d="M8 12h16M8 20h16M16 8v16" stroke="#000" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <span>FlaskIt</span>
            </a>
.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    text-decoration: none;
}
        <ul class="nav-links">
            <li><a href="{{ url_for('home') }}">Accueil</a></li>
            <li><a href="{{ url_for('about') }}">À propos</a></li>
        </ul>
    </div>
</nav>
"""

# Footer Component Template
TEMPLATE_FOOTER = """<footer class="footer">
    <div class="container">
        <p>&copy; 2024 FlaskIt - Généré avec ❤️ par FlaskIt Framework</p>
    </div>
</footer>
"""

# Home Page Template - Ultra-modern Next.js/Nuxt.js style
TEMPLATE_HOME_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlaskIt - The Modern Full-Stack Framework</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Animated Background -->
    <div class="bg-gradient"></div>
    
    <!-- Navigation -->
    <nav class="navbar">
        <div class="container">
            <div class="nav-content">
                <a href="/" class="logo">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect width="32" height="32" rx="8" fill="#FBBF24"/>
                        <path d="M8 12h16M8 20h16M16 8v16" stroke="#000" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>FlaskIt</span>
                </a>
                <div class="nav-links">
                    <a href="#features">Features</a>
                    <a href="#docs">Docs</a>
                    <a href="/_watch">Dashboard</a>
                    <a href="https://flaskit.dev" class="nav-btn">Website</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1 class="hero-title">FLASKIT</h1>
            <p class="hero-subtitle">⚡ The Full-Stack Framework Developers Love to Build With</p>
            
            <div class="features-grid">
                <div class="feature">
                    <span class="feature-icon">🚀</span>
                    <span>No Decorators</span>
                </div>
                <div class="feature">
                    <span class="feature-icon">🏗️</span>
                    <span>MVL Architecture</span>
                </div>
                <div class="feature">
                    <span class="feature-icon">⚙️</span>
                    <span>Batteries Included</span>
                </div>
                <div class="feature">
                    <span class="feature-icon">🎯</span>
                    <span>Modern CLI</span>
                </div>
            </div>
        </div>
    </section>

            <!-- Footer -->
            <footer class="footer">
                <p>Built with ❤️ by FlaskIt Team</p>
            </footer>
        </div>
    </div>
</body>
</html>
"""

# About Page Template
TEMPLATE_ABOUT_PAGE = """{% extends 'layouts/base.html' %}

{% block title %}À propos - FlaskIt{% endblock %}

{% block content %}
<div class="page-content">
    <div class="container">
        <h1>À propos de FlaskIt</h1>
        <p>FlaskIt est un framework moderne pour créer des applications Flask avec une architecture professionnelle.</p>
        <h2>Fonctionnalités</h2>
        <ul>
            <li>Routing élégant inspiré de Laravel</li>
            <li>Architecture MVC propre</li>
            <li>CLI puissant pour générer des projets</li>
            <li>Support des middlewares</li>
        </ul>
    </div>
</div>
{% endblock %}
"""

# 404 Error Page Template
TEMPLATE_404_PAGE = """{% extends 'layouts/base.html' %}

{% block title %}Page non trouvée - FlaskIt{% endblock %}

{% block content %}
<div class="error-page">
    <div class="container">
        <h1>404</h1>
        <p>Page non trouvée</p>
        <a href="{{ url_for('home') }}" class="btn">Retour à l'accueil</a>
    </div>
</div>
{% endblock %}
"""

# 500 Error Page Template
TEMPLATE_500_PAGE = """{% extends 'layouts/base.html' %}

{% block title %}Erreur serveur - FlaskIt{% endblock %}

{% block content %}
<div class="error-page">
    <div class="container">
        <h1>500</h1>
        <p>Erreur interne du serveur</p>
        <a href="{{ url_for('home') }}" class="btn">Retour à l'accueil</a>
    </div>
</div>
{% endblock %}
"""

# 403 Error Page Template
TEMPLATE_403_PAGE = """{% extends 'layouts/base.html' %}

{% block title %}Accès interdit - FlaskIt{% endblock %}

{% block content %}
<div class="error-page">
    <div class="container">
        <h1>403</h1>
        <p>Accès interdit</p>
        <a href="{{ url_for('home') }}" class="btn">Retour à l'accueil</a>
    </div>
</div>
{% endblock %}
"""

# Public Data JSON Template
TEMPLATE_DATA_JSON = """{
  "_comment": "⚠️ PUBLIC DATA ONLY - No passwords, API keys, or secrets here!",
  
  "app": {
    "name": "FlaskIt App",
    "version": "1.0.0",
    "description": "A modern full-stack application built with FlaskIt",
    "author": "Your Name",
    "license": "MIT"
  },
  
  "contact": {
    "email": "contact@example.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, Country",
    "support_hours": "Mon-Fri 9AM-5PM"
  },
  
  "web": {
    "social": {
      "whatsapp": "https://wa.me/1234567890",
      "facebook": "https://facebook.com/yourpage",
      "twitter": "https://twitter.com/yourhandle",
      "instagram": "https://instagram.com/yourhandle",
      "linkedin": "https://linkedin.com/company/yourcompany",
      "youtube": "https://youtube.com/@yourchannel"
    },
    "links": {
      "website": "https://example.com",
      "blog": "https://blog.example.com",
      "docs": "https://docs.example.com",
      "support": "https://support.example.com"
    }
  },
  
  "features": {
    "registration_enabled": true,
    "comments_enabled": true,
    "newsletter_enabled": true,
    "dark_mode": true
  }
}
"""

# CSS Template - Ultra-modern Next.js/Nuxt.js style
TEMPLATE_CSS = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary: #FBBF24;
    --primary-hover: #F59E0B;
    --text: #000000;
    --text-muted: #6B7280;
    --border: #E5E7EB;
    --bg: #FFFFFF;
    --bg-subtle: #F9FAFB;
    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Simple Background */
.bg-gradient {
    display: none;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* Navigation */
.navbar {
    position: sticky;
    top: 0;
    background: white;
    border-bottom: 2px solid var(--border);
    z-index: 100;
}

.nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.nav-links a {
    color: var(--text-muted);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.9375rem;
    transition: color 0.2s;
}

.nav-links a:hover {
    color: var(--text);
}

.nav-btn {
    background: var(--text);
    color: white !important;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    transition: all 0.2s;
}

.nav-btn:hover {
    background: var(--primary);
}

/* Hero Section */
.hero {
    text-align: center;
    padding: 6rem 0 4rem;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--primary);
    color: var(--text);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 2rem;
}

.badge-dot {
    width: 8px;
    height: 8px;
    background: var(--text);
    border-radius: 50%;
}

.hero-title {
    font-size: clamp(2.5rem, 7vw, 5rem);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    color: var(--text);
}

.gradient-text {
    color: var(--primary);
}

.hero-subtitle {
    font-size: 1.25rem;
    color: var(--text-muted);
    max-width: 700px;
    margin: 0 auto 3rem;
    line-height: 1.8;
}

/* Hero Actions */
.hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 4rem;
    flex-wrap: wrap;
}

.btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--primary);
    color: var(--text);
    padding: 1rem 2rem;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-primary:hover {
    background: var(--primary-hover);
}

.btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: white;
    color: var(--text);
    padding: 1rem 2rem;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: none;
    border: 2px solid var(--text);
    transition: all 0.2s;
}

.btn-secondary:hover {
    background: var(--text);
    color: white;
}

/* Hero Stats */
.hero-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 3rem;
    max-width: 600px;
    margin: 0 auto;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 3rem;
    font-weight: 800;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.stat-label {
    color: var(--text-muted);
    font-size: 0.875rem;
    font-weight: 500;
}

/* Features Section */
.features-section {
    padding: 6rem 0;
    background: white;
}

.section-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 4rem;
    color: var(--text);
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: var(--bg-subtle);
    border: 2px solid var(--border);
    border-radius: 8px;
    padding: 2rem;
    transition: all 0.2s;
}

.feature-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

.feature-card h3 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    color: var(--text);
}

.feature-card p {
    color: var(--text-muted);
    line-height: 1.7;
    font-size: 0.9375rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 4rem 0;
    border-top: 1px solid var(--border);
    background: white;
}

.footer p {
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    font-size: 0.9375rem;
}

.footer a {
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.footer a:hover {
    color: var(--primary-hover);
}

.footer-links {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    align-items: center;
}

.footer-links span {
    color: var(--border);
}

/* Minimal Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Responsive */
@media (max-width: 768px) {
    .nav-links {
        display: none;
    }
    
    .hero {
        padding: 4rem 0 2rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-actions {
        flex-direction: column;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
}

.cta-buttons {
    margin-top: 2rem;
}

.btn {
    display: inline-block;
    padding: 0.8rem 2rem;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    text-decoration: none;
    border-radius: 10px;
    transition: all 0.3s;
}

.btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.page-content {
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.page-content h2 {
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.page-content ul {
    list-style-position: inside;
    margin-left: 1rem;
}

.page-content li {
    margin-bottom: 0.5rem;
}

.footer {
    background: rgba(0, 0, 0, 0.2);
    padding: 2rem 0;
    text-align: center;
    margin-top: auto;
}

.error-page {
    min-height: 80vh;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

/* Hero Section Styles */
.hero {
    padding: 8rem 0 4rem 0;
    text-align: center;
}

.hero-title {
    font-size: 6rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.5rem;
    color: var(--text-muted);
    margin-bottom: 3rem;
    font-weight: 500;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    max-width: 800px;
    margin: 0 auto;
}

.feature {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--bg-subtle);
    border-radius: 8px;
    border: 1px solid var(--border);
    font-weight: 500;
    color: var(--text);
}

.feature-icon {
    font-size: 1.2rem;
}
"""

# JavaScript Template
TEMPLATE_JS = """// Main JavaScript file
console.log('FlaskIt App loaded ❤️');

// Exemple de fonction
function init() {
    console.log('Application initialized');
}

document.addEventListener('DOMContentLoaded', init);
"""

# Requirements Template
TEMPLATE_REQUIREMENTS = """flaskit>=0.1.0
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0
"""

# Environment Template
TEMPLATE_ENV = """FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
"""

# Gitignore Template
TEMPLATE_GITIGNORE = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
*.db
instance/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
"""

# README Template
TEMPLATE_README = """# {project_name}

Projet généré avec ❤️ par **FlaskIt Framework**

## Structure du projet

```
{project_name}/
├── app/                    # Logique métier
│   ├── models/            # Modèles de données
│   ├── services/          # Services métier
│   ├── configs/           # Configuration
│   ├── logics/            # Logique métier
│   └── database/          # Base de données
├── routes/                # Routes de l'application
│   └── web.py            # Routes web avec FlaskIt routing
├── web/                   # Couche présentation
│   ├── views/            # Templates
│   │   ├── layouts/      # Layouts de base
│   │   ├── components/   # Composants réutilisables
│   │   └── pages/        # Pages
│   │       └── home/     # Pages home
│   └── static/           # Fichiers statiques
│       ├── css/
│       ├── js/
│       └── images/
└── app.py                # Point d'entrée

```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copiez `.env.example` vers `.env` et configurez vos variables d'environnement.

## Lancement

```bash
python app.py
```

L'application sera disponible sur http://localhost:5000

## Architecture

- **app/** : Contient toute la logique métier
- **routes/** : Définition des routes avec FlaskIt routing system
- **web/** : Couche de présentation (templates et assets)

## FlaskIt Routing

FlaskIt utilise un système de routing élégant :

```python
from flaskit.routing import Route
from app.logics.users import Users

route = Route()

# Routes de vues
route.view('/', 'home.index').name('home')

# Routes API avec pattern MVL
route.get('/api/users', Users.getall).name('api.users')
route.post('/api/users', Users.create).name('api.users.store')

# Groupes de routes
with route.group('/api', middleware=['auth']):
    route.get('/profile', Users.profile).name('api.profile')
```

## Pattern MVL (Model-View-Logic)

FlaskIt utilise le pattern **MVL** pour une architecture claire :

- **Model** (`app/models/`) : Définition des données
- **Service** (`app/services/`) : Opérations CRUD
- **Logic** (`app/logics/`) : Logique métier et validation
- **View** (`web/views/`) : Templates HTML
- **Routes** (`routes/`) : Définition des endpoints

### Exemple de flux

```
Route → Logic → Service → Model
```

```python
# routes/web.py
route.get('/api/users', Users.getall)

# app/logics/users.py
class Users:
    @staticmethod
    def getall():
        users = UserService.get_all_users()
        return jsonify({{'data': [u.to_dict() for u in users]}})

# app/services/user_service.py
class UserService:
    @staticmethod
    def get_all_users():
        return User.query.all()
```

---
Généré avec ❤️ par FlaskIt
"""
