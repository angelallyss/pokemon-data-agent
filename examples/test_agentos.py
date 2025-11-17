"""
Script de exemplo para testar o Pokemon AgentOS
"""
import requests
import json
import sys

BASE_URL = "http://localhost:7777"

def test_agentos():
    """Testa o AgentOS com várias perguntas"""
    
    questions = [
        "Qual é o tipo do Pikachu?",
        "Quem é mais rápido, Jolteon ou Aerodactyl?",
        "Mostre-me a cadeia evolutiva do Charmander",
        "Compare Mewtwo e Mew em todos os atributos",
        "Qual Pokémon tem o maior ataque?",
        "Sugira uma equipe equilibrada da primeira geração",
    ]
    
    print("=" * 80)
    print("POKEMON AGENTOS - TEST SCRIPT")
    print("=" * 80)
    print(f"\nTesting AgentOS at: {BASE_URL}")
    print()
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(" AgentOS is running!")
        else:
            print(" AgentOS health check failed")
            return
    except requests.exceptions.ConnectionError:
        print(" Cannot connect to AgentOS. Make sure it's running:")
        print("   python pokemon_os.py")
        sys.exit(1)
    
    # Test agent
    agent_id = "pokemon_expert"
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}] {question}")
        print("-" * 80)
        
        try:
            # Create session and send message
            response = requests.post(
                f"{BASE_URL}/v1/agents/{agent_id}/sessions",
                json={"message": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response
                if "messages" in data:
                    for msg in data["messages"]:
                        if msg.get("role") == "assistant":
                            print(f"\n[Reply]\n{msg.get('content', 'No content')}")
                            break
                else:
                    print(f"\n[Reply]\n{data}")
                
                # Show session info
                if "session_id" in data:
                    print(f"\n[Session ID] {data['session_id']}")
                
            else:
                print(f"\n[Error] Status {response.status_code}")
                print(response.text)
            
        except Exception as e:
            print(f"\n[Error] {e}")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n Tips:")
    print("  - View all sessions: GET /v1/agents/pokemon_expert/sessions")
    print("  - View agent config: GET /config")
    print("  - API docs: http://localhost:7777/docs")

def test_session_management():
    """Testa gerenciamento de sessões"""
    
    print("\n" + "=" * 80)
    print("SESSION MANAGEMENT TEST")
    print("=" * 80)
    
    agent_id = "pokemon_expert"
    
    # Create a session
    print("\n[1] Creating session...")
    response = requests.post(
        f"{BASE_URL}/v1/agents/{agent_id}/sessions",
        json={"message": "Hello! What can you help me with?"}
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get("session_id")
        print(f" Session created: {session_id}")
        
        # Continue conversation in same session
        print("\n[2] Continuing conversation...")
        response = requests.post(
            f"{BASE_URL}/v1/agents/{agent_id}/sessions/{session_id}",
            json={"message": "Tell me about Pikachu"}
        )
        
        if response.status_code == 200:
            print(" Message sent to existing session")
        
        # List all sessions
        print("\n[3] Listing all sessions...")
        response = requests.get(f"{BASE_URL}/v1/agents/{agent_id}/sessions")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f" Found {len(sessions)} session(s)")
    else:
        print(f" Failed to create session: {response.status_code}")

if __name__ == "__main__":
    print("\n Pokemon AgentOS Test Suite\n")
    
    # Test basic functionality
    test_agentos()
    
    # Test session management
    test_session_management()
    
    print("\n All tests complete!")
    print("\n Next steps:")
    print("  - Explore the API: http://localhost:7777/docs")
    print("  - View config: http://localhost:7777/config")
    print("  - Connect to AgentOS Control Plane for enhanced management")
