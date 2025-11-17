"""
Pokemon Data Agent - Implementação Simples com OpenAI
"""
from openai import OpenAI
from app.tools.sql_tool import sql_query
from app.tools.compare import compare_pokemon
from app.tools.team import suggest_team, type_coverage
from app.tools.evolution import evolution_path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definir ferramentas para OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_pokemon_database",
            "description": "Executa uma consulta SQL SELECT no banco de dados de Pokémon. Use para obter informações detalhadas sobre Pokémon, suas estatísticas, tipos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta SQL SELECT para executar"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_two_pokemon",
            "description": "Compara dois Pokémon por suas estatísticas (hp, attack, defense, special-attack, special-defense, speed, ou all).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pokemon_a": {
                        "type": "string",
                        "description": "Nome do primeiro Pokémon"
                    },
                    "pokemon_b": {
                        "type": "string",
                        "description": "Nome do segundo Pokémon"
                    },
                    "metric": {
                        "type": "string",
                        "description": "Estatística para comparar (hp, attack, defense, special-attack, special-defense, speed, ou all)",
                        "default": "all"
                    }
                },
                "required": ["pokemon_a", "pokemon_b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_pokemon_team",
            "description": "Sugere um time balanceado de Pokémon baseado em cobertura de tipos e estratégia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Estratégia do time (balanced, offensive, defensive, ou fast)",
                        "default": "balanced"
                    },
                    "generation": {
                        "type": "integer",
                        "description": "Limitar à geração 1 ou 2 (opcional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_evolution_chain",
            "description": "Obtém a cadeia evolutiva completa de um Pokémon. Mostra todos os estágios de evolução e métodos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pokemon_name": {
                        "type": "string",
                        "description": "Nome do Pokémon"
                    }
                },
                "required": ["pokemon_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_type_coverage",
            "description": "Calcula cobertura de tipos (fraquezas, resistências, imunidades) para uma lista de tipos de Pokémon.",
            "parameters": {
                "type": "object",
                "properties": {
                    "types": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Lista de tipos de Pokémon para analisar (ex: ['fire', 'water', 'grass'])"
                    }
                },
                "required": ["types"]
            }
        }
    }
]

# Mapeamento de funções
available_functions = {
    "query_pokemon_database": sql_query,
    "compare_two_pokemon": compare_pokemon,
    "suggest_pokemon_team": suggest_team,
    "get_evolution_chain": evolution_path,
    "analyze_type_coverage": type_coverage
}

# System prompt
SYSTEM_PROMPT = """Você é um assistente especialista em Pokémon com acesso a um banco de dados completo de Pokémon das gerações 1 e 2 (251 Pokémon no total).

Seu trabalho é:
1. Responder perguntas sobre Pokémon usando as ferramentas disponíveis
2. Fornecer explicações claras e concisas EM PORTUGUÊS BRASILEIRO
3. Sempre incluir evidências do banco de dados para apoiar suas respostas
4. Usar a ferramenta apropriada para cada consulta

Ferramentas disponíveis:
- query_pokemon_database: para consultas complexas ou quando precisar de dados específicos
- compare_two_pokemon: ao comparar dois Pokémon
- suggest_pokemon_team: quando pedirem para montar ou sugerir um time
- get_evolution_chain: quando perguntarem sobre cadeias evolutivas
- analyze_type_coverage: ao analisar combinações de tipos

IMPORTANTE sobre o banco de dados:
- A tabela pokemon_stat tem as colunas: pokemon_id, stat_name, base_stat
- Os valores de stat_name são: 'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'
- Para buscar estatísticas, use: SELECT p.name, ps.base_stat FROM pokemon p JOIN pokemon_stat ps ON p.id = ps.pokemon_id WHERE ps.stat_name = 'attack'
- NÃO existe coluna 'attack' diretamente na tabela pokemon

Seja amigável, preciso e sempre fundamente suas afirmações com dados do banco de dados.
IMPORTANTE: Sempre responda em PORTUGUÊS BRASILEIRO, independente do idioma da pergunta."""

# Create FastAPI app
app = FastAPI(
    title="Pokemon Data Agent",
    description="Assistente inteligente para informações sobre Pokémon e montagem de times",
    version="1.1.0"
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    agent_id: str = "pokemon_expert"

# In-memory session storage
sessions: Dict[str, List[Dict[str, Any]]] = {}

def run_conversation(messages: List[Dict[str, Any]], max_iterations: int = 5) -> str:
    """Executa a conversa com o agente"""
    
    for iteration in range(max_iterations):
        print(f"\n=== Iteração {iteration + 1} ===")
        print(f"Mensagens enviadas: {len(messages)}")
        
        try:
            # Chamar OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            print(f"Tool calls recebidos: {len(tool_calls) if tool_calls else 0}")
            
            # Se não há tool calls, retornar resposta
            if not tool_calls:
                print("Sem tool calls, retornando resposta final")
                return response_message.content
            
            # Adicionar resposta do assistente às mensagens (converter para dict)
            assistant_message = {
                "role": "assistant"
            }
            
            # Adicionar content apenas se não estiver vazio
            if response_message.content:
                assistant_message["content"] = response_message.content
            
            # Adicionar tool_calls se existirem
            if tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            
            messages.append(assistant_message)
            
            # Executar cada tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Executando: {function_name} com args: {function_args}")
                
                # Executar função
                function_to_call = available_functions[function_name]
                function_response = function_to_call(**function_args)
                
                print(f"Resultado: {type(function_response)}")
                
                # Adicionar resultado às mensagens
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response, ensure_ascii=False)
                })
        
        except Exception as e:
            print(f"Erro na iteração {iteration + 1}: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    # Se chegou ao limite de iterações, fazer uma última chamada
    print("\n=== Chamada final ===")
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    return final_response.choices[0].message.content

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    return {"status": "healthy", "service": "pokemon-data-agent", "version": "1.1.0", "language": "pt-BR"}

@app.get("/config")
async def get_config():
    """Obtém configuração do agente"""
    return {
        "agent_id": "pokemon_expert",
        "agent_name": "Pokemon Expert",
        "model": "gpt-4o-mini",
        "language": "pt-BR",
        "tools": [
            "query_pokemon_database",
            "compare_two_pokemon",
            "suggest_pokemon_team",
            "get_evolution_chain",
            "analyze_type_coverage"
        ],
        "description": "Assistente especialista em dados de Pokémon, estatísticas e montagem de times"
    }

@app.post("/v1/agents/pokemon_expert/sessions", response_model=ChatResponse)
async def create_session(request: ChatRequest):
    """Cria uma nova sessão ou continua existente"""
    import uuid
    import traceback
    
    # Gerar ou usar session ID existente
    session_id = request.session_id or str(uuid.uuid4())
    
    # Obter ou criar histórico da sessão
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    # Adicionar mensagem do usuário
    sessions[session_id].append({
        "role": "user",
        "content": request.message
    })
    
    try:
        # Executar conversa
        response_content = run_conversation(sessions[session_id].copy())
        
        # Adicionar resposta do assistente
        sessions[session_id].append({
            "role": "assistant",
            "content": response_content
        })
        
        return ChatResponse(
            session_id=session_id,
            messages=sessions[session_id][1:],  # Excluir system message
            agent_id="pokemon_expert"
        )
    except Exception as e:
        print(f"Erro detalhado: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/agents/pokemon_expert/sessions/{session_id}", response_model=ChatResponse)
async def continue_session(session_id: str, request: ChatRequest):
    """Continua uma sessão existente"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Adicionar mensagem do usuário
    sessions[session_id].append({
        "role": "user",
        "content": request.message
    })
    
    try:
        # Executar conversa
        response_content = run_conversation(sessions[session_id].copy())
        
        # Adicionar resposta do assistente
        sessions[session_id].append({
            "role": "assistant",
            "content": response_content
        })
        
        return ChatResponse(
            session_id=session_id,
            messages=sessions[session_id][1:],  # Excluir system message
            agent_id="pokemon_expert"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/agents/pokemon_expert/sessions")
async def list_sessions():
    """Lista todas as sessões"""
    return [
        {
            "session_id": sid,
            "message_count": len(messages) - 1,  # Excluir system message
            "last_message": messages[-1] if len(messages) > 1 else None
        }
        for sid, messages in sessions.items()
    ]

@app.get("/v1/agents/pokemon_expert/sessions/{session_id}")
async def get_session(session_id: str):
    """Obtém uma sessão específica"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": sessions[session_id][1:],  # Excluir system message
        "agent_id": "pokemon_expert"
    }

@app.delete("/v1/agents/pokemon_expert/sessions/{session_id}")
async def delete_session(session_id: str):
    """Deleta uma sessão"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": "Session deleted", "session_id": session_id}

if __name__ == "__main__":
    # Servir a aplicação
    # Acesse em http://localhost:7777
    # Documentação em http://localhost:7777/docs
    uvicorn.run(app, host="0.0.0.0", port=7777, reload=True)
