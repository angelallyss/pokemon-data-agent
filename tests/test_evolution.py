import pytest
from app.tools.evolution import evolution_path
from app.db import db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Ensure database is connected for tests"""
    db.connect()
    yield
    db.close()

def test_evolution_path_eevee():
    """Test getting evolution path for Eevee (multiple evolutions)"""
    result = evolution_path("eevee")
    
    assert "chain" in result
    assert "pokemon" in result
    assert result["pokemon"] == "eevee"
    assert isinstance(result["chain"], list)

def test_evolution_path_charmander():
    """Test getting evolution path for Charmander"""
    result = evolution_path("charmander")
    
    assert "chain" in result
    assert len(result["chain"]) >= 1
    # Charmander should have evolutions
    assert result.get("total_stages", 0) > 1

def test_evolution_path_not_found():
    """Test with non-existent Pokemon"""
    result = evolution_path("fakemon")
    
    assert "error" in result

def test_evolution_path_no_evolution():
    """Test Pokemon that doesn't evolve (if any in gen 1-2)"""
    # Some Pokemon like Ditto don't evolve
    result = evolution_path("ditto")
    
    # Should return valid response even if no evolution
    assert "chain" in result or "message" in result
