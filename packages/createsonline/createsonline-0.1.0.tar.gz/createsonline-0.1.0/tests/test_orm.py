"""
Tests for the AI-Enhanced ORM.
"""
import pytest
from createsonline.config.orm import AIEnhancedORM

def test_orm_initialization(test_db):
    """Test ORM initialization."""
    assert test_db is not None

def test_get_session(test_db):
    """Test getting a database session."""
    session = test_db.get_session()
    assert session is not None
    session.close()

def test_generate_schema_from_description():
    """Test schema generation from description."""
    orm = AIEnhancedORM("sqlite:///:memory:")
    model = orm.generate_schema_from_description("A product with name and price")
    assert model.__tablename__ == "generated_model"  # This is just the placeholder implementation
