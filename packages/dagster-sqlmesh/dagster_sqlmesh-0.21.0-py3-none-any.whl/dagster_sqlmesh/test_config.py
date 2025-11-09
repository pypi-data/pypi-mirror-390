import pytest

from dagster_sqlmesh.config import SQLMeshContextConfig
from dagster_sqlmesh.translator import SQLMeshDagsterTranslator


def test_get_translator_with_valid_class():
    """Test that get_translator works with the default translator class."""
    config = SQLMeshContextConfig(path="/tmp/test", gateway="local")
    translator = config.get_translator()
    assert isinstance(translator, SQLMeshDagsterTranslator)


def test_get_translator_with_non_class():
    """Test that get_translator raises ValueError when pointing to a non-class."""
    config = SQLMeshContextConfig(
        path="/tmp/test", 
        gateway="local",
        translator_class_name="sys.version"
    )
    
    with pytest.raises(ValueError, match="is not a class"):
        config.get_translator()


def test_get_translator_with_invalid_inheritance():
    """Test that get_translator raises ValueError when class doesn't inherit from SQLMeshDagsterTranslator."""
    config = SQLMeshContextConfig(
        path="/tmp/test", 
        gateway="local",
        translator_class_name="builtins.dict"
    )
    
    with pytest.raises(ValueError, match="must inherit from SQLMeshDagsterTranslator"):
        config.get_translator()


def test_get_translator_with_nonexistent_class():
    """Test that get_translator raises AttributeError when class doesn't exist."""
    config = SQLMeshContextConfig(
        path="/tmp/test", 
        gateway="local",
        translator_class_name="dagster_sqlmesh.translator.NonexistentClass"
    )
    
    with pytest.raises(AttributeError):
        config.get_translator()


class MockValidTranslator(SQLMeshDagsterTranslator):
    """A mock translator for testing custom inheritance."""
    pass


def test_get_translator_with_valid_custom_class():
    """Test that get_translator works with custom classes that inherit from SQLMeshDagsterTranslator."""
    config = SQLMeshContextConfig(
        path="/tmp/test", 
        gateway="local",
        translator_class_name=f"{__name__}.MockValidTranslator"
    )
    
    translator = config.get_translator()
    assert isinstance(translator, SQLMeshDagsterTranslator)
    assert isinstance(translator, MockValidTranslator)
