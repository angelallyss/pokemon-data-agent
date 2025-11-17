"""
Script interativo para conversar com o Pokemon Agent
"""
import requests
import json
import sys

BASE_URL = "http://localhost:7777"
session_id = None

def chat(message):
    """Envia mensagem para o agente"""
    global session_id
    
    try:
        if session_id is None:
            # Criar nova sessão
            url = f"{BASE_URL}/v1/agents/pokemon_expert/sessions"
            print(" Criando nova sessão...")
        else:
            # Continuar sessão existente
            url = f"{BASE_URL}/v1/agents/pokemon_expert/sessions/{session_id}"
            print(f" Continuando sessão {session_id[:8]}...")
        
        response = requests.post(
            url,
            json={"message": message},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            # Pegar última mensagem do assistente
            messages = result["messages"]
            assistant_message = None
            for msg in reversed(messages):
                if msg["role"] == "assistant":
                    assistant_message = msg["content"]
                    break
            
            print("\n" + "="*60)
            print(" Pokemon Expert:")
            print("="*60)
            print(assistant_message)
            print("="*60 + "\n")
            
        else:
            print(f" Erro: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(" Erro: Não foi possível conectar ao servidor.")
        print("   Certifique-se que o servidor está rodando em http://localhost:7777")
        sys.exit(1)
    except Exception as e:
        print(f" Erro: {e}")

def main():
    print("="*60)
    print(" POKEMON DATA AGENT - Chat Interativo")
    print("="*60)
    print("Digite suas perguntas ou 'sair' para encerrar")
    print("Exemplos:")
    print("  - Quem é mais rápido, Pikachu ou Raichu?")
    print("  - Mostre a cadeia evolutiva do Eevee")
    print("  - Sugira um time balanceado")
    print("  - Compare Charizard e Blastoise")
    print("  - Qual Pokémon tem maior ataque?")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("👤 Você: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['sair', 'exit', 'quit', 'q']:
                print("\n Até logo!")
                break
            
            chat(user_input)
            
        except KeyboardInterrupt:
            print("\n\n Até logo!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
