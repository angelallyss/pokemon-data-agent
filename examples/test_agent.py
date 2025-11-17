"""
Script de exemplo para testar o Pokemon Agent localmente
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from app.agent import get_agent

load_dotenv()

def test_questions():
    """Testa várias perguntas ao agente"""
    
    questions = [
        "What type is Pikachu?",
        "Who is faster, Jolteon or Aerodactyl?",
        "Show me the evolution chain of Charmander",
        "Compare Mewtwo and Mew in all stats",
        "Which Pokemon has the highest attack stat?",
        "Suggest a balanced team from generation 1",
    ]
    
    agent = get_agent()
    
    print("=" * 80)
    print("POKEMON DATA AGENT - TEST SCRIPT")
    print("=" * 80)
    print()
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}] {question}")
        print("-" * 80)
        
        try:
            response = agent.chat(question, max_iterations=5)
            
            print(f"\n[Reply]\n{response['reply']}")
            print(f"\n[Evidence] {len(response['evidence'])} tool calls")
            
            for j, evidence in enumerate(response['evidence'], 1):
                print(f"  {j}. {evidence['tool']}({evidence['arguments']})")
            
            print(f"\n[Iterations] {response['iterations']}")
            
        except Exception as e:
            print(f"\n[Error] {e}")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        sys.exit(1)
    
    test_questions()
