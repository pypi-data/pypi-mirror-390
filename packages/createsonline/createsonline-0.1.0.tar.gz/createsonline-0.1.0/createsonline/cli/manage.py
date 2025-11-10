#!/usr/bin/env python
"""
CREATESONLINE Management CLI

Similar to Django's manage.py - provides database and user management commands.
"""
import sys
import os
import logging

logger = logging.getLogger("createsonline.cli.manage")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        migrate_database()
    elif command == "createsuperuser":
        create_superuser()
    elif command == "initdb":
        init_database()
    elif command == "shell":
        open_shell()
    elif command == "help":
        print_help()
    else:
        logger.info(f"âŒ Unknown command: {command}")
        print_help()


def print_help():
    """Print help message"""
    logger.info("""
CREATESONLINE Management Commands

Usage: createsonline-admin <command>

Available commands:
    migrate           Create database tables (like Django migrate)
    createsuperuser   Create a superuser account
    initdb            Initialize database with tables and default data
    shell             Open Python shell with app context
    help              Show this help message

Examples:
    createsonline-admin migrate
    createsonline-admin createsuperuser
    createsonline-admin initdb
""")


def migrate_database():
    """Create/update database tables (like Django migrate)"""
    logger.info("ðŸ”„ Running migrations...")
    
    try:
        from sqlalchemy import create_engine
        from createsonline.auth.models import Base as AuthBase
        # Content models now use same Base as auth models
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        logger.info(f"ðŸ“ Database: {database_url}")
        
        engine = create_engine(database_url, echo=False)
        
        logger.info("ðŸ“¦ Creating tables...")
        # Import content models to register them with Base
        try:
            from createsonline.admin import content  # This registers the models
        except:
            pass
        
        AuthBase.metadata.create_all(engine)
        
        logger.info("âœ… Migrations completed successfully!")
        logger.info(f"ðŸ’¾ Database: {database_url.replace('sqlite:///./', '')}")
        
    except Exception as e:
        logger.info(f"âŒ Migration failed: {e}")
        import traceback
        traceback.print_exc()


def create_superuser():
    """Create a superuser (like Django createsuperuser)"""
    logger.info("ðŸ‘¤ Create Superuser")
    logger.info("=" * 50)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, create_superuser as create_su
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Get username
            while True:
                username = input("Username: ").strip()
                if not username:
                    logger.info("âŒ Username cannot be empty")
                    continue
                
                # Check if user exists
                existing = session.query(User).filter_by(username=username).first()
                if existing:
                    logger.info(f"âŒ User '{username}' already exists")
                    continue
                
                break
            
            # Get email
            while True:
                email = input("Email address: ").strip()
                if not email:
                    logger.info("âŒ Email cannot be empty")
                    continue
                
                if '@' not in email:
                    logger.info("âŒ Invalid email format")
                    continue
                
                break
            
            # Get password
            import getpass
            while True:
                password = getpass.getpass("Password: ")
                if not password:
                    logger.info("âŒ Password cannot be empty")
                    continue
                
                if len(password) < 8:
                    logger.info("âŒ Password must be at least 8 characters")
                    continue
                
                password_confirm = getpass.getpass("Password (again): ")
                if password != password_confirm:
                    logger.info("âŒ Passwords don't match")
                    continue
                
                break
            
            # Create superuser
            user = create_su(
                username=username,
                email=email,
                password=password
            )
            
            session.add(user)
            session.commit()
            
            logger.info("\nâœ… Superuser created successfully!")
            logger.info(f"ðŸ‘¤ Username: {username}")
            logger.info(f"ðŸ“§ Email: {email}")
            logger.info(f"\nðŸš€ You can now login at: http://localhost:8000/admin")
            
        except KeyboardInterrupt:
            logger.info("\nâš ï¸ Operation cancelled")
        except Exception as e:
            session.rollback()
            logger.info(f"\nâŒ Error: {e}")
        finally:
            session.close()
            
    except ImportError as e:
        logger.info(f"âŒ Missing dependency: {e}")
        logger.info("ðŸ’¡ Install SQLAlchemy: pip install sqlalchemy")
    except Exception as e:
        logger.info(f"âŒ Error: {e}")


def init_database():
    """Initialize database with tables and default data"""
    logger.info("ðŸ”§ Initializing CREATESONLINE database...")
    logger.info("=" * 50)
    
    # Run migrations first
    migrate_database()
    
    # Create default permissions
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import Permission, create_default_permissions
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            logger.info("\nðŸ” Creating default permissions...")
            permissions = create_default_permissions()
            
            for perm in permissions:
                existing = session.query(Permission).filter_by(
                    codename=perm.codename,
                    content_type=perm.content_type
                ).first()
                
                if not existing:
                    session.add(perm)
                    logger.info(f"  âœ… {perm.content_type}.{perm.codename}")
            
            session.commit()
            logger.info("âœ… Default permissions created")
            
        except Exception as e:
            session.rollback()
            logger.info(f"âš ï¸ Could not create permissions: {e}")
        finally:
            session.close()
    
    except Exception as e:
        logger.info(f"âš ï¸ Could not create permissions: {e}")
    
    # Prompt to create superuser
    logger.info("\n" + "=" * 50)
    response = input("Do you want to create a superuser now? [y/N] ").strip().lower()
    
    if response in ['y', 'yes']:
        create_superuser()
    else:
        logger.info("\nðŸ’¡ You can create a superuser later with:")
        logger.info("   createsonline-admin createsuperuser")
    
    logger.info("\nâœ… Database initialization complete!")


def open_shell():
    """Open interactive Python shell"""
    logger.info("ðŸ CREATESONLINE Interactive Shell")
    logger.info("=" * 50)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, Group, Permission
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        logger.info("\nImported:")
        logger.info("  - User, Group, Permission from createsonline.auth.models")
        logger.info("  - session (SQLAlchemy session)")
        logger.info(f"\nDatabase: {database_url}")
        logger.info("\nExample:")
        logger.info("  users = session.query(User).all()")
        logger.info("  for user in users: logger.info(user.username)")
        logger.info()
        
        import code
        code.interact(local=locals())
        
    except Exception as e:
        logger.info(f"âŒ Error: {e}")


if __name__ == "__main__":
    main()

