"""
CREATESONLINE Database Migrations
Simple database migration system for Pure Independence architecture.
"""

from typing import List, Dict, Any
from datetime import datetime
import json
import logging
from pathlib import Path

# Setup logger
logger = logging.getLogger(__name__)

class Migration:
    """
    Represents a single database migration.
    """
    
    def __init__(self, name: str, description: str = "", version: str = ""):
        self.name = name
        self.description = description
        self.version = version
        self.timestamp = datetime.now()
        self.applied = False
    
    def up(self):
        """Apply this migration"""
        raise NotImplementedError("Subclasses must implement up() method")
    
    def down(self):
        """Reverse this migration"""
        raise NotImplementedError("Subclasses must implement down() method")


class MigrationManager:
    """
    Manages database migrations for CREATESONLINE Pure Independence.
    """
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        self.applied_migrations_file = self.migrations_dir / "applied.json"
        self.migrations: List[Migration] = []
        self.applied_migrations = self._load_applied_migrations()
    
    def _load_applied_migrations(self) -> List[str]:
        """Load list of applied migrations"""
        if self.applied_migrations_file.exists():
            try:
                with open(self.applied_migrations_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_applied_migrations(self):
        """Save list of applied migrations"""
        try:
            with open(self.applied_migrations_file, 'w') as f:
                json.dump(self.applied_migrations, f, indent=2)
        except IOError as e:
            logger.warning(f"Could not save applied migrations: {e}")
    
    def add_migration(self, migration: Migration):
        """Add a migration to the manager"""
        self.migrations.append(migration)
    
    def apply_migrations(self):
        """Apply all pending migrations"""
        applied_count = 0
        pending_migrations = [m for m in self.migrations if m.name not in self.applied_migrations]
        
        if not pending_migrations:
            logger.info("No pending migrations to apply")
            return
        
        logger.info(f"Applying {len(pending_migrations)} pending migrations...")
        
        for migration in pending_migrations:
            logger.info(f"Applying migration: {migration.name}")
            try:
                migration.up()
                self.applied_migrations.append(migration.name)
                migration.applied = True
                applied_count += 1
                logger.info(f"âœ… Applied: {migration.name}")
            except Exception as e:
                logger.error(f"âŒ Failed to apply {migration.name}: {e}")
                break
        
        if applied_count > 0:
            self._save_applied_migrations()
            logger.info(f"Applied {applied_count} migrations successfully")
    
    def rollback_migration(self, migration_name: str):
        """Rollback a specific migration"""
        for migration in reversed(self.migrations):
            if migration.name == migration_name:
                if migration_name in self.applied_migrations:
                    logger.info(f"Rolling back migration: {migration_name}")
                    try:
                        migration.down()
                        self.applied_migrations.remove(migration_name)
                        migration.applied = False
                        self._save_applied_migrations()
                        logger.info(f"âœ… Rolled back: {migration_name}")
                    except Exception as e:
                        logger.error(f"âŒ Failed to rollback {migration_name}: {e}")
                else:
                    logger.warning(f"Migration {migration_name} is not applied")
                return
        
        logger.error(f"Migration {migration_name} not found")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get status of all migrations"""
        return {
            "total_migrations": len(self.migrations),
            "applied_migrations": len(self.applied_migrations),
            "pending_migrations": len(self.migrations) - len(self.applied_migrations),
            "migrations": [
                {
                    "name": m.name,
                    "description": m.description,
                    "applied": m.name in self.applied_migrations,
                    "timestamp": m.timestamp.isoformat() if hasattr(m, 'timestamp') else None
                }
                for m in self.migrations
            ]
        }
