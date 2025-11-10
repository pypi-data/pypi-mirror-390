# createsonline/cli/commands/initdb.py
"""
Database initialization command

Creates all tables and initial data.
"""
import os`r`nimport sys`r`nimport logging`r`nlogger = logging.getLogger("createsonline.cli.initdb")


def init_database():
    """Initialize database with all tables"""
    logger.info("ðŸ”§ Initializing CREATESONLINE database...")
    
    try:
        from sqlalchemy import create_engine
        from createsonline.auth.models import Base as AuthBase, User, Group, Permission, create_default_permissions, create_superuser
        from createsonline.admin.content import Base as ContentBase
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        logger.info(f"ðŸ“ Database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        # Create all tables
        logger.info("\nðŸ“¦ Creating tables...")
        AuthBase.metadata.create_all(engine)
        ContentBase.metadata.create_all(engine)
        logger.info("âœ… Tables created successfully")
        
        # Create session
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Create default permissions
            logger.info("\nðŸ” Creating default permissions...")
            permissions = create_default_permissions()
            for perm in permissions:
                # Check if permission already exists
                existing = session.query(Permission).filter_by(
                    codename=perm.codename,
                    content_type=perm.content_type
                ).first()
                
                if not existing:
                    session.add(perm)
                    logger.info(f"  âœ… Created permission: {perm.content_type}.{perm.codename}")
            
            session.commit()
            logger.info("âœ… Default permissions created")
            
            # Check if superuser exists
            superuser = session.query(User).filter_by(is_superuser=True).first()
            
            if not superuser:
                logger.info("\nðŸ‘¤ No superuser found. Let's create one!")
                username = input("Username (admin): ").strip() or "admin"
                email = input("Email (admin@createsonline.com): ").strip() or "admin@createsonline.com"
                password = input("Password: ").strip()
                
                if not password:
                    logger.info("âŒ Password cannot be empty")
                    return False
                
                # Create superuser
                superuser = create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                session.add(superuser)
                session.commit()
                
                logger.info(f"âœ… Superuser '{username}' created successfully!")
                logger.info(f"\nðŸ” Login credentials:")
                logger.info(f"   Username: {username}")
                logger.info(f"   Password: {password}")
                logger.info(f"\nðŸš€ Start your server and login at /admin")
            else:
                logger.info(f"\nâœ… Superuser already exists: {superuser.username}")
            
            # Migrate from superuser.json if exists
            if os.path.exists("superuser.json"):
                logger.info("\nðŸ“¦ Found superuser.json - migrating...")
                import json
                with open("superuser.json", "r") as f:
                    data = json.load(f)
                    
                    # Check if user already exists
                    existing_user = session.query(User).filter_by(username=data["username"]).first()
                    
                    if not existing_user:
                        migrated_user = User(
                            username=data["username"],
                            email=f"{data['username']}@createsonline.com",
                            password_hash=data["password_hash"],
                            is_staff=True,
                            is_superuser=True,
                            is_active=True,
                            email_verified=True
                        )
                        session.add(migrated_user)
                        session.commit()
                        logger.info(f"âœ… Migrated user from superuser.json: {data['username']}")
                    else:
                        logger.info(f"âš ï¸  User {data['username']} already exists - skipping migration")
            
            logger.info("\nâœ… Database initialized successfully!")
            logger.info("ðŸš€ You can now run your CREATESONLINE application")
            
            return True
            
        except Exception as e:
            session.rollback()
            logger.info(f"\nâŒ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
            
    except ImportError as e:
        logger.info(f"\nâŒ Missing dependency: {e}")
        logger.info("ðŸ’¡ Install SQLAlchemy: pip install sqlalchemy")
        return False
    except Exception as e:
        logger.info(f"\nâŒ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_superuser_command():
    """Create a new superuser"""
    logger.info("ðŸ‘¤ Creating CREATESONLINE superuser...")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from createsonline.auth.models import User, create_superuser
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///./createsonline.db")
        logger.info(f"ðŸ“ Database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            username = input("Username: ").strip()
            if not username:
                logger.info("âŒ Username cannot be empty")
                return False
            
            # Check if user exists
            existing = session.query(User).filter_by(username=username).first()
            if existing:
                logger.info(f"âŒ User '{username}' already exists")
                return False
            
            email = input("Email: ").strip()
            if not email:
                logger.info("âŒ Email cannot be empty")
                return False
            
            password = input("Password: ").strip()
            if not password:
                logger.info("âŒ Password cannot be empty")
                return False
            
            confirm_password = input("Confirm password: ").strip()
            if password != confirm_password:
                logger.info("âŒ Passwords do not match")
                return False
            
            # Create superuser
            user = create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            session.add(user)
            session.commit()
            
            logger.info(f"\nâœ… Superuser '{username}' created successfully!")
            logger.info(f"ðŸ” Login at /admin with username: {username}")
            
            return True
            
        except Exception as e:
            session.rollback()
            logger.info(f"\nâŒ Error: {e}")
            return False
        finally:
            session.close()
            
    except ImportError as e:
        logger.info(f"\nâŒ Missing dependency: {e}")
        logger.info("ðŸ’¡ Install SQLAlchemy: pip install sqlalchemy")
        return False
    except Exception as e:
        logger.info(f"\nâŒ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "createsuperuser":
        create_superuser_command()
    else:
        init_database()

