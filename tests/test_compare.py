import pytest
from app.tools.compare import compare_pokemon
from app.db import db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Ensure database is connected for tests"""
    db.connect()
    yield
    db.close()

def test_compare_pokemon_speed():
    """Test comparing two Pokemon by speed"""
    result = compare_pokemon("pikachu", "raichu", "speed")
    
    assert "comparison" in result
    assert "winners" in result
    assert "pikachu" in result["comparison"]
    assert "raichu" in result["comparison"]
    assert "speed" in result["winners"]

def test_compare_pokemon_all_stats():
    """Test comparing all stats between two Pokemon"""
    result = compare_pokemon("bulbasaur", "charmander", "all")
    
    assert result["metric"] == "all"
    assert "comparison" in result
    assert len(result["winners"]) > 1  # Should have multiple stats

def test_compare_pokemon_not_found():
    """Test comparing with non-existent Pokemon"""
    result = compare_pokemon("fakemon", "pikachu", "attack")
    
    assert "error" in result or "fakemon" not in result.get("comparison", {})

def test_compare_pokemon_invalid_metric():
    """Test with invalid metric"""
    result = compare_pokemon("pikachu", "raichu", "invalid_stat")
    
    # Should either return error or empty results
    assert "error" in result or not result.get("comparison")
