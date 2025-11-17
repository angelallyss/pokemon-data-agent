import os
import logging
from typing import Dict, Any, List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from app.tools.sql_tool import sql_query
from app.tools.compare import compare_pokemon
from app.tools.team import suggest_team, type_coverage
from app.tools.evolution import evolution_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define tools using Agno decorators
@tool
def query_pokemon_database(query: str) -> list:
    """
    Execute a SQL SELECT query on the Pokemon database.
    
    Args:
        query: SQL SELECT query to execute
        
    Returns:
        List of dictionaries with query results
    """
    return sql_query(query)

@tool
def compare_two_pokemon(pokemon_a: str, pokemon_b: str, metric: str = "all") -> dict:
    """
    Comparar dois Pokémon por seus atributos.

    Argumentos:

    pokemon_a: Nome do primeiro Pokémon

    pokemon_b: Nome do segundo Pokémon

    métrica: Atributo a ser comparado (HP, Ataque, Defesa, Ataque Especial, Defesa Especial, Velocidade ou todos)

    Retorno:

    Dicionário com os resultados da comparação
    """
    return compare_pokemon(pokemon_a, pokemon_b, metric)

@tool
def suggest_pokemon_team(goal: str = "balanced", generation: int = None) -> dict:
    """
    Sugira uma equipe Pokémon equilibrada com base na cobertura de tipos e na estratégia.

    Argumentos:

    objetivo: Estratégia da equipe (equilibrada, ofensiva, defensiva ou rápida)

    geração: Limitar à geração 1 ou 2 (opcional)

    Retorno:

    Dicionário com a equipe sugerida e a análise
    """
    return suggest_team(goal, generation)

@tool
def get_evolution_chain(pokemon_name: str) -> dict:
    """
    Obtenha a cadeia evolutiva completa de um Pokémon.

    Argumentos:

    nome_do_pokemon: Nome do Pokémon

    Retorno:

    Dicionário com informações da cadeia evolutiva
    """
    return evolution_path(pokemon_name)

@tool
def analyze_type_coverage(types: List[str]) -> dict:
    """
    Calcula a cobertura de tipos (fraquezas, resistências e imunidades) para uma lista de tipos de Pokémon.

    Argumentos:

    tipos: Lista de tipos de Pokémon a serem analisados

    Retorno:

    Dicionário com a análise de cobertura
    """
    return type_coverage(types)

class PokemonAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        # Create Agno agent
        self.agent = Agent(
            name="Pokemon Expert",
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.api_key),
            tools=[
                query_pokemon_database,
                compare_two_pokemon,
                suggest_pokemon_team,
                get_evolution_chain,
                analyze_type_coverage
            ],
            instructions=[
                "Você é um assistente especialista em Pokémon com acesso a um banco de dados abrangente de Pokémon das gerações 1 e 2 (251 Pokémon no total)."
                "Sua função é:"
                "1. Responder perguntas sobre Pokémon usando as ferramentas disponíveis"
                "2. Fornecer explicações claras e concisas"
                "3. Sempre incluir evidências do banco de dados para fundamentar suas respostas"
                "4. Usar a ferramenta apropriada para cada pergunta"
                
                "Seja amigável, preciso e sempre fundamente suas afirmações com dados."
            ],
            markdown=True,
            show_tool_calls=True
        )
        self.tools = None  # Not needed with Agno
        

    
    def chat(self, message: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Envie uma mensagem ao agente e receba uma resposta com evidências.

        Argumentos:

        mensagem: Pergunta ou solicitação do usuário

        max_iterations: Número máximo de chamadas permitidas à ferramenta

        Retorno:

        Dicionário com a resposta e as evidências
        """
        try:
            # Run the agent with the message
            response = self.agent.run(message)
            
            # Extract evidence from tool calls
            evidence = []
            if hasattr(response, 'messages'):
                for msg in response.messages:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            evidence.append({
                                "tool": tool_call.function.name if hasattr(tool_call, 'function') else "unknown",
                                "arguments": tool_call.function.arguments if hasattr(tool_call, 'function') else {},
                                "result": getattr(tool_call, 'result', None)
                            })
            
            return {
                "reply": response.content if hasattr(response, 'content') else str(response),
                "evidence": evidence,
                "iterations": len(evidence)
            }
        except Exception as e:
            logger.error(f"Agent chat error: {e}")
            return {
                "reply": f"Error: {str(e)}",
                "evidence": [],
                "iterations": 0
            }

# Global agent instance
agent = None

def get_agent() -> PokemonAgent:
    """Obtenha ou crie a instância do agente global."""
    global agent
    if agent is None:
        agent = PokemonAgent()
    return agent
