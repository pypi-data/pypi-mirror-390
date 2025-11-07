import os
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from flaskit.templates import (
    TEMPLATE_APP, TEMPLATE_CONFIG, TEMPLATE_DATABASE_INIT,
    TEMPLATE_ROUTES, TEMPLATE_LAYOUT, TEMPLATE_NAVBAR,
    TEMPLATE_FOOTER, TEMPLATE_HOME_PAGE, TEMPLATE_ABOUT_PAGE, TEMPLATE_404_PAGE,
    TEMPLATE_500_PAGE, TEMPLATE_403_PAGE, TEMPLATE_CSS, TEMPLATE_JS, 
    TEMPLATE_REQUIREMENTS, TEMPLATE_ENV, TEMPLATE_DATA_JSON, TEMPLATE_GITIGNORE, TEMPLATE_README
)

console = Console()


LOGO = """[bold green]
    ╔═══════════════════════════════════╗
    ║                                   ║

         ❤️  F  L  A  S  K  I  T  ❤️ 

    ║                                   ║
    ╚═══════════════════════════════════╝
                                 
[/bold green][bold yellow]  ⚡ The Full-Stack Framework Developers Love to Build With v0.2.4[/bold yellow]
"""


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """FlaskIt - ⚡ The Full-Stack Framework Developers Love to Build With """
    # Only show logo if no subcommand is provided
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(LOGO, border_style="yellow"))
        console.print("\n[yellow]Use --help to see available commands[/yellow]\n")


@click.command()
@click.argument("name")
def new(name):
    """Create a new FlaskIt app with complete structure"""
    console.print(Panel.fit(LOGO, border_style="yellow"))
    
    if os.path.exists(name):
        console.print(f"\n[bold red]⚠️  Folder '{name}' already exists.[/bold red]")
        return

    console.print(f"\n[bold cyan]📦 Creating FlaskIt project '{name}'...[/bold cyan]\n")
    
    # Structure des dossiers - Architecture professionnelle
    folders = [
        name,
        # Dossier app - Logique métier
        os.path.join(name, "app"),
        os.path.join(name, "app", "model"),
        os.path.join(name, "app", "service"),
        os.path.join(name, "app", "logic"),
        os.path.join(name, "app", "config"),
        os.path.join(name, "app", "middleware"),
        os.path.join(name, "app", "database"),
        # Dossier routes
        os.path.join(name, "routes"),
        # Dossier web - Présentation
        os.path.join(name, "web"),
        os.path.join(name, "web", "views"),
        os.path.join(name, "web", "views", "layouts"),
        os.path.join(name, "web", "views", "components"),
        os.path.join(name, "web", "views", "pages"),
        os.path.join(name, "web", "views", "pages", "home"),
        os.path.join(name, "web", "views", "pages", "errors"),
        os.path.join(name, "web", "static"),
        os.path.join(name, "web", "static", "css"),
        os.path.join(name, "web", "static", "js"),
        os.path.join(name, "web", "static", "images"),
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Fichiers à créer
    files = {
        # Racine
        os.path.join(name, "app.py"): TEMPLATE_APP,
        os.path.join(name, "requirements.txt"): TEMPLATE_REQUIREMENTS,
        os.path.join(name, ".env"): TEMPLATE_ENV,
        os.path.join(name, "data.json"): TEMPLATE_DATA_JSON,
        os.path.join(name, ".gitignore"): TEMPLATE_GITIGNORE,
        os.path.join(name, "README.md"): TEMPLATE_README.format(project_name=name),
        
        # App - Config
        os.path.join(name, "app", "config", "config.py"): TEMPLATE_CONFIG,
        os.path.join(name, "app", "config", "__init__.py"): "",
        
        # App - Service
        os.path.join(name, "app", "service", "__init__.py"): "",
        
        # App - Logic
        os.path.join(name, "app", "logic", "__init__.py"): "",
        
        # App - Middleware
        os.path.join(name, "app", "middleware", "__init__.py"): "",
        
        # App - Database
        os.path.join(name, "app", "database", "__init__.py"): TEMPLATE_DATABASE_INIT,
        
        # App - Model
        os.path.join(name, "app", "model", "__init__.py"): "",
        
        # App - Init
        os.path.join(name, "app", "__init__.py"): "",
        
        # Routes
        os.path.join(name, "routes", "__init__.py"): "",
        os.path.join(name, "routes", "web.py"): TEMPLATE_ROUTES,
        
        # Web - Views - Layouts
        os.path.join(name, "web", "views", "layouts", "base.html"): TEMPLATE_LAYOUT,
        
        # Web - Views - Components
        os.path.join(name, "web", "views", "components", "navbar.html"): TEMPLATE_NAVBAR,
        os.path.join(name, "web", "views", "components", "footer.html"): TEMPLATE_FOOTER,
        
        # Web - Views - Pages - Home
        os.path.join(name, "web", "views", "pages", "home", "index.html"): TEMPLATE_HOME_PAGE,
        os.path.join(name, "web", "views", "pages", "home", "about.html"): TEMPLATE_ABOUT_PAGE,
        
        # Web - Views - Pages - Errors
        os.path.join(name, "web", "views", "pages", "errors", "404.html"): TEMPLATE_404_PAGE,
        os.path.join(name, "web", "views", "pages", "errors", "500.html"): TEMPLATE_500_PAGE,
        os.path.join(name, "web", "views", "pages", "errors", "403.html"): TEMPLATE_403_PAGE,
        
        # Web - Static
        os.path.join(name, "web", "static", "css", "style.css"): TEMPLATE_CSS,
        os.path.join(name, "web", "static", "js", "main.js"): TEMPLATE_JS,
    }
    
    for filepath, content in files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    console.print(f"\n[bold green]✨ Project '{name}' created successfully![/bold green]")
    console.print("\n[bold yellow]📝 Next steps:[/bold yellow]")
    console.print(f"  [cyan]1.[/cyan] cd {name}")
    console.print(f"  [cyan]2.[/cyan] pip install -r requirements.txt")
    console.print(f"  [cyan]3.[/cyan] flaskit serve")
    console.print(f"\n[bold cyan]🌐 Your app will be available at:[/bold cyan]")
    console.print(f"   • [link]http://127.0.0.1:5000[/link] - Home page")
    console.print(f"   • [link]http://127.0.0.1:5000/_watch[/link] - Dashboard\n")


@click.command()
@click.option('--host', default='127.0.0.1', help='Host to run on')
@click.option('--port', default=5000, help='Port to run on')
@click.option('--debug/--no-debug', default=True, help='Enable debug mode')
def serve(host, port, debug):
    """Start the FlaskIt development server"""
    console.print(f"\n[bold cyan]🚀 Starting FlaskIt server...[/bold cyan]")
    if not os.path.exists('app.py'):
        console.print("[bold red]❌ File app.py not found[/bold red]")
        console.print("[yellow]Make sure you are in the project folder[/yellow]")
        return
    
    console.print(f"\n[bold green]🚀 FlaskIt is running![/bold green]\n")
    console.print(f"[cyan]➡️  Local:[/cyan]   http://{host}:{port}")
    
    # Get network IP
    import socket
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        console.print(f"[cyan]📡 Network:[/cyan] http://{local_ip}:{port} [dim](same Wi-Fi devices)[/dim]")
    except:
        console.print(f"[cyan]📡 Network:[/cyan] [dim]Not available[/dim]")
    
    console.print(f"\n[dim]Debug mode: {'enabled' if debug else 'disabled'}[/dim]\n")
    
    # Ajouter le dossier courant au path
    import sys
    sys.path.insert(0, os.getcwd())
    
    try:
        # Import app.py module (not the app/ package)
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Create and run the app
        app = app_module.create_app()
        # Run with localhost and 127.0.0.1 both working
        app.run(host='0.0.0.0', port=port, debug=debug)
    except FileNotFoundError:
        console.print("[bold red]❌ File app.py not found[/bold red]")
    except AttributeError:
        console.print("[bold red]❌ Function create_app() not found in app.py[/bold red]")
        console.print("[yellow]Make sure app.py contains a create_app() function[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@click.command()
@click.option('--force', is_flag=True, help='Force update (overwrite existing files)')
def update(force):
    """Update an existing FlaskIt project with new features"""
    console.print(Panel.fit(LOGO, border_style="yellow"))
    console.print("\n[bold cyan]🔄 Updating FlaskIt project...[/bold cyan]\n")
    
    if not os.path.exists('app.py'):
        console.print("[bold red]❌ Not a FlaskIt project[/bold red]")
        console.print("[yellow]Run this command in your project folder[/yellow]")
        return
    
    
    updates_made = []
    
    # 1. Update requirements.txt
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Add missing dependencies
        if 'requests' not in content:
            with open('requirements.txt', 'a') as f:
                f.write('\nrequests>=2.31.0\n')
            updates_made.append('✅ Added requests to requirements.txt')
        
        if 'python-dotenv' not in content:
            with open('requirements.txt', 'a') as f:
                f.write('python-dotenv>=1.0.0\n')
            updates_made.append('✅ Added python-dotenv to requirements.txt')
    
    # 2. Create data.json if missing
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as f:
            f.write(TEMPLATE_DATA_JSON)
        updates_made.append('✅ Created data.json')
    
    # 3. Update .env with Discord webhooks if missing
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
        
        if 'DISCORD_' not in env_content:
            with open('.env', 'a') as f:
                f.write('\n# Discord Webhooks (optional)\n')
                f.write('# Get webhooks from: https://discord.com/developers/applications\n')
                f.write('DISCORD_NEWUSER=\n')
                f.write('DISCORD_CONTACT=\n')
                f.write('DISCORD_ERRORS=\n')
            updates_made.append('✅ Added Discord webhook variables to .env')
    
    # 4. Update app.py comment if needed
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if 'load_dotenv' in app_content and force:
            # Remove manual load_dotenv if user wants
            app_content = app_content.replace('from dotenv import load_dotenv', '')
            app_content = app_content.replace('load_dotenv()', '')
            
            # Add comment about auto-loading
            if 'FlaskIt charge automatiquement' not in app_content:
                app_content = app_content.replace(
                    'from routes.web import register_routes',
                    'from routes.web import register_routes\n\n# Note: FlaskIt charge automatiquement le fichier .env\n# Pas besoin d\'importer ou d\'appeler load_dotenv() !'
                )
            
            with open('app.py', 'w') as f:
                f.write(app_content)
            updates_made.append('✅ Updated app.py (removed manual load_dotenv)')
    
    # 5. Show summary
    console.print("\n[bold green]📦 Update Summary:[/bold green]\n")
    
    if updates_made:
        for update in updates_made:
            console.print(f"  {update}")
        
        console.print("\n[bold cyan]Next steps:[/bold cyan]")
        console.print("  1. pip install -r requirements.txt")
        console.print("  2. Update your code to use new features:")
        console.print("     [cyan]•[/cyan] from flaskit import discord, discord_colors")
        console.print("     [cyan]•[/cyan] from flaskit import get_data")
        console.print("     [cyan]•[/cyan] from flaskit import watch")
        console.print("\n[bold green]✅ Update complete![/bold green]")
        console.print("\n[bold yellow]📝 Next steps:[/bold yellow]")
        console.print("  [cyan]1.[/cyan] pip install -r requirements.txt")
        console.print("  [cyan]2.[/cyan] flaskit serve")
        console.print("  [cyan]3.[/cyan] Visit http://127.0.0.1:5000/_watch for dashboard\n")
    else:
        console.print("  [bold yellow]✓ No updates needed - project is up to date![/bold yellow]\n")


cli.add_command(new)
cli.add_command(serve)
cli.add_command(update)


if __name__ == '__main__':
    cli()
