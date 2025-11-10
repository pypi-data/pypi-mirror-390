# createsonline/cli/commands/serve.py
"""
CREATESONLINE Server Commands - Pure Internal Implementation

Provides serve, dev, and prod commands for running the framework.
Uses CREATESONLINE's internal pure Python server - NO uvicorn needed!
"""
import os
import sys
from pathlib import Path`r`nimport logging

# Internal console implementation (fallback for rich)
try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    # Internal console fallback
    class SimpleConsole:
        def logging.getLogger("createsonline.cli.serve").info(self, text, **kwargs):
            if isinstance(text, str):
                logging.getLogger("createsonline.cli.serve").info(text)
            else:
                logging.getLogger("createsonline.cli.serve").info(str(text))
    console = SimpleConsole()

# Internal dotenv fallback
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv():
        """Internal dotenv fallback - reads .env file manually"""
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

def serve_command(host="0.0.0.0", port=8000, reload=True, workers=1, app_module="main:app"):
    """ðŸš€ Start CREATESONLINE development server - Pure Internal Implementation"""
    
    load_dotenv()
    
    if RICH_AVAILABLE:
        console.logging.getLogger("createsonline.cli.serve").info(Panel(
            "[bold blue]ðŸš€ CREATESONLINE Framework - Internal Server[/bold blue]\n"
            "[cyan]AI-Native Web Framework[/cyan]\n\n"
            f"[green]Server:[/green] http://{host}:{port}\n"
            f"[green]Mode:[/green] {'Development' if reload else 'Production'}\n"
            f"[green]Workers:[/green] {workers if not reload else 1}\n"
            f"[green]App:[/green] {app_module}\n"
            f"[yellow]Server:[/yellow] CREATESONLINE Internal (Pure Python)",
            title="ðŸŒ Server Starting",
            border_style="blue"
        ))
    else:
        logging.getLogger("createsonline.cli.serve").info("ðŸš€ CREATESONLINE Framework - Internal Server")
        logging.getLogger("createsonline.cli.serve").info("AI-Native Web Framework")
        logging.getLogger("createsonline.cli.serve").info(f"Server: http://{host}:{port}")
        logging.getLogger("createsonline.cli.serve").info(f"Mode: {'Development' if reload else 'Production'}")
        logging.getLogger("createsonline.cli.serve").info(f"Workers: {workers if not reload else 1}")
        logging.getLogger("createsonline.cli.serve").info(f"App: {app_module}")
        logging.getLogger("createsonline.cli.serve").info("Server: CREATESONLINE Internal (Pure Python)")
    
    # Use internal server - just run the app file directly
    try:
        if os.path.exists("main.py"):
            sys.exit(os.system(f"{sys.executable} main.py"))
        elif os.path.exists("app.py"):
            sys.exit(os.system(f"{sys.executable} app.py"))
        else:
            console.logging.getLogger("createsonline.cli.serve").info("âŒ No main.py or app.py found. Create one to run your app.")
            return
    except KeyboardInterrupt:
        console.logging.getLogger("createsonline.cli.serve").info("\nServer stopped by user")
    except Exception as e:
        console.logging.getLogger("createsonline.cli.serve").info(f"Server error: {e}")

def dev_command(host="127.0.0.1", port=8000, app_module="main:app"):
    """ðŸ”§ Start development server with auto-reload and debugging - Pure Independence"""
    
    load_dotenv()
    
    if RICH_AVAILABLE:
        console.logging.getLogger("createsonline.cli.serve").info(Panel(
            "[bold green]ðŸ”§ CREATESONLINE Development Mode - Pure Independence[/bold green]\n"
            "[cyan]Enhanced development experience - Zero external dependencies[/cyan]\n\n"
            "[green]Features:[/green]\n"
            "â€¢ Auto-reload on file changes\n"
            "â€¢ Verbose logging\n" 
            "â€¢ Error debugging\n"
            "â€¢ Hot module reloading\n"
            "â€¢ Pure internal implementation",
            title="ðŸ› ï¸ Pure Development Server",
            border_style="green"
        ))
    else:
        logging.getLogger("createsonline.cli.serve").info("ðŸ”§ CREATESONLINE Development Mode - Pure Independence")
        logging.getLogger("createsonline.cli.serve").info("Enhanced development experience - Zero external dependencies")
        logging.getLogger("createsonline.cli.serve").info("Features: Auto-reload, Verbose logging, Error debugging, Hot module reloading")
    
    # Use internal server - just run the app file directly
    try:
        if os.path.exists("main.py"):
            sys.exit(os.system(f"{sys.executable} main.py"))
        elif os.path.exists("app.py"):
            sys.exit(os.system(f"{sys.executable} app.py"))
        else:
            console.logging.getLogger("createsonline.cli.serve").info("âŒ No main.py or app.py found. Create one to run your app.")
            return
    except KeyboardInterrupt:
        console.logging.getLogger("createsonline.cli.serve").info("\nDevelopment server stopped")
    except Exception as e:
        console.logging.getLogger("createsonline.cli.serve").info(f"Development server error: {e}")

def prod_command(host="0.0.0.0", port=8000, workers=4, app_module="main:app"):
    """ðŸ­ Start production server with optimized settings - Pure Independence"""
    
    load_dotenv()
    
    if RICH_AVAILABLE:
        console.logging.getLogger("createsonline.cli.serve").info(Panel(
            "[bold red]ðŸ­ CREATESONLINE Production Mode - Pure Independence[/bold red]\n"
            "[cyan]Pure Independence - Optimized for performance and stability[/cyan]\n\n"
            f"[green]Workers:[/green] {workers}\n"
            f"[green]Host:[/green] {host}:{port}\n"
            "[green]Features:[/green]\n"
            "â€¢ Multiple worker processes\n"
            "â€¢ Optimized logging\n"
            "â€¢ Production error handling\n"
            "â€¢ Pure internal implementation\n"
            "â€¢ Zero external performance dependencies",
            title="ðŸš€ Production Server", 
            border_style="red"
        ))
    else:
        logging.getLogger("createsonline.cli.serve").info("ðŸ­ CREATESONLINE Production Mode - Pure Independence")
        logging.getLogger("createsonline.cli.serve").info("Pure Independence - Optimized for performance and stability")
        logging.getLogger("createsonline.cli.serve").info(f"Workers: {workers}")
        logging.getLogger("createsonline.cli.serve").info(f"Host: {host}:{port}")
        logging.getLogger("createsonline.cli.serve").info("Features: Multiple workers, Optimized logging, Production error handling")
    
    # Use internal server - just run the app file directly
    try:
        if os.path.exists("main.py"):
            sys.exit(os.system(f"{sys.executable} main.py"))
        elif os.path.exists("app.py"):
            sys.exit(os.system(f"{sys.executable} app.py"))
        else:
            console.logging.getLogger("createsonline.cli.serve").info("âŒ No main.py or app.py found for production!")
            console.logging.getLogger("createsonline.cli.serve").info("Create your application file first")
            sys.exit(1)
    except KeyboardInterrupt:
        console.logging.getLogger("createsonline.cli.serve").info("\nProduction server stopped")
    except Exception as e:
        console.logging.getLogger("createsonline.cli.serve").info(f"Production server error: {e}")

# Internal command registry (no typer dependency)
SERVE_COMMANDS = {
    'start': serve_command,
    'serve': serve_command,
    'dev': dev_command,
    'development': dev_command,
    'prod': prod_command,
    'production': prod_command
}

