import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.db import db
import os

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Ensure we have an API key for testing
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set, skipping E2E tests")
    
    db.connect()
    yield
    db.close()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_pokemon():
    """Test getting a specific Pokemon"""
    response = client.get("/pokemon/pikachu")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "pikachu"
    assert "stats" in data
    assert "types" in data
    assert "electric" in data["types"]

def test_get_pokemon_not_found():
    """Test getting non-existent Pokemon"""
    response = client.get("/pokemon/fakemon")
    assert response.status_code == 404

def test_team_suggestion():
    """Test team suggestion endpoint"""
    response = client.get("/team/suggest?goal=balanced&generation=1")
    assert response.status_code == 200
    
    data = response.json()
    assert "team" in data
    assert "type_coverage" in data
    assert len(data["team"]) <= 6

def test_top_stats():
    """Test top Pokemon by stat endpoint"""
    response = client.get("/stats/top?stat=speed&limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert "top_pokemon" in data
    assert len(data["top_pokemon"]) <= 5
    assert data["stat"] == "speed"

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI API key")
def test_agent_chat():
    """Test agent chat endpoint (requires API key)"""
    response = client.post(
        "/agent/chat",
        json={"message": "What type is Pikachu?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "reply" in data
    assert "evidence" in data
    assert "iterations" in data
    assert isinstance(data["evidence"], list)

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI API key")
def test_agent_chat_comparison():
    """Test agent comparison question"""
    response = client.post(
        "/agent/chat",
        json={"message": "Who is faster, Pikachu or Raichu?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "reply" in data
    assert len(data["evidence"]) > 0
    # Should have used compare_pokemon tool
    assert any("compare" in str(e.get("tool", "")).lower() for e in data["evidence"])
