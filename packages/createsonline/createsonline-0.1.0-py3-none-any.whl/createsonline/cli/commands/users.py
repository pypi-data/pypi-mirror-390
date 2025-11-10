"""
CREATESONLINE User Management Commands

Create and manage users for the admin interface.
Lazy imports are used to avoid hard dependencies when not needed.
"""

import logging

_cli_logger = logging.getLogger("createsonline.cli.users")


def createsuperuser_command():
    """Create admin superuser interactively"""

    # Import dependencies only when command is used
    try:
        import typer
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
    except ImportError as e:
        _cli_logger.error("This command requires additional dependencies. Install with: pip install rich typer")
        # handled above
        return

    console = Console()

    console.print(Panel(
        "[bold blue]CREATESONLINE Admin User Creation[/bold blue]\n\n"
        "[cyan]Create a superuser account for the admin interface.[/cyan]\n"
        "[dim]This user will have full administrative privileges.[/dim]",
        title="Create Superuser",
        border_style="blue"
    ))

    # Get user information
    try:
        username = Prompt.ask("[cyan]Username[/cyan]", default="admin")
        email = Prompt.ask("[cyan]Email address[/cyan]", default=f"{username}@example.com")
        password = Prompt.ask("[cyan]Password[/cyan]", password=True)
        password_confirm = Prompt.ask("[cyan]Confirm password[/cyan]", password=True)

        if password != password_confirm:
            console.print("[red]Passwords don't match![/red]")
            raise typer.Exit(1)

        # Confirm creation
        console.print(f"\n[green]Creating superuser:[/green]")
        console.print(f"  Username: [cyan]{username}[/cyan]")
        console.print(f"  Email: [cyan]{email}[/cyan]")

        if not Confirm.ask("\n[yellow]Create this superuser?[/yellow]"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        # Create the user
        success = create_superuser(username, email, password, console)

        if success:
            console.print(Panel(
                f"[bold green]âœ… Superuser '{username}' created successfully![/bold green]\n\n"
                "[cyan]You can now:[/cyan]\n"
                "â€¢ Login to admin interface\n"
                "â€¢ Manage users and permissions\n"
                "â€¢ Configure application settings\n\n"
                "[green]Admin URL:[/green] http://localhost:8000/admin/",
                title="Success!",
                border_style="green"
            ))
        else:
            console.print("[red]Failed to create superuser[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error creating superuser: {e}[/red]")
        raise typer.Exit(1)


def create_superuser(username: str, email: str, password: str, console=None) -> bool:
    """Create a superuser in the database.

    Returns True on success, False otherwise. Accepts optional `console`
    for rich output; falls back to print when not provided.
    """

    try:
        # Try to import and use the auth models
        from createsonline.auth.models import User, Group, Permission, hash_password
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os

        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")

        # Create database engine and session
        engine = create_engine(database_url)

        # Create tables if they don't exist
        User.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                (console.print(f"[yellow]User '{username}' already exists![/yellow]") if console else _cli_logger.info(f"User '{username}' already exists!"))
                return False

            # Hash the password
            hashed_password = hash_password(password)

            # Create the user
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                is_active=True,
                is_superuser=True,
                is_staff=True
            )

            session.add(user)
            session.commit()

            (console.print(f"[green]User '{username}' created in database[/green]") if console else _cli_logger.info(f"User '{username}' created in database"))
            return True

        finally:
            session.close()

    except ImportError:
        # Fallback to simple file-based storage for demo
        _cli_logger.error("Database models not available. Configure your database and try again.")
        return False
    except Exception as e:
        _cli_logger.error(f"Database error: {e}")
        _cli_logger.info("User creation aborted due to configuration error.")
        return False




