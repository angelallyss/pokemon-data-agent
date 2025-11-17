import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from app.agent import get_agent
from app.db import db
from app.tools.team import suggest_team

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pokemon Data Agent API",
    description="Assistente Pokémon inteligente com tecnologia OpenAI Agents SDK",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    max_iterations: Optional[int] = 5

class ChatResponse(BaseModel):
    reply: str
    evidence: list
    iterations: int

@app.get("/health")
async def health_check():
    """Ponto final de verificação de integridade"""
    return {"status": "healthy", "service": "pokemon-data-agent"}

@app.get("/pokemon/{name}")
async def get_pokemon(name: str):
    """Obtenha informações detalhadas sobre um Pokémon específico."""
    try:
        db.connect()
        
        # Get basic info
        query = """
            SELECT p.*, GROUP_CONCAT(DISTINCT pt.type_name) as types
            FROM pokemon p
            LEFT JOIN pokemon_type pt ON p.id = pt.pokemon_id
            WHERE p.name = ?
            GROUP BY p.id
        """
        result = db.execute_query(query, (name.lower(),))
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Pokemon '{name}' not found")
        
        pokemon = result[0]
        
        # Get stats
        stats_query = """
            SELECT stat_name, base_stat
            FROM pokemon_stat
            WHERE pokemon_id = ?
        """
        stats = db.execute_query(stats_query, (pokemon['id'],))
        
        pokemon['stats'] = {s['stat_name']: s['base_stat'] for s in stats}
        pokemon['types'] = pokemon['types'].split(',') if pokemon['types'] else []
        
        return pokemon
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Pokemon: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/agent/chat", response_model=ChatResponse)
async def agent_chat(request: ChatRequest):
    """
    Converse com o agente Pokémon. Faça perguntas sobre Pokémon e receba respostas inteligentes.

    Exemplos de perguntas:

    - "Quem é mais rápido, Jolteon ou Aerodactyl?"
    - "Mostre-me a cadeia evolutiva do Eevee"
    - "Monte uma equipe equilibrada da primeira geração"
    - "Qual Pokémon tem a maior defesa?"
    """
    try:
        agent = get_agent()
        response = agent.chat(request.message, request.max_iterations)
        return response
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/team/suggest")
async def get_team_suggestion(goal: str = "balanced", generation: Optional[int] = None):
    """
    Obtenha uma sugestão de equipe Pokémon com base na estratégia e na cobertura de tipos.

    Argumentos:

    objetivo: Estratégia da equipe (equilibrada, ofensiva, defensiva, rápida)

    geração: Limitar à geração 1 ou 2
    """
    try:
        result = suggest_team(goal, generation)
        return result
    except Exception as e:
        logger.error(f"Team suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/top")
async def get_top_pokemon(stat: str = "attack", limit: int = 10, generation: Optional[int] = None):
    """
    Encontre os melhores Pokémon por um atributo específico.

    Argumentos:
    
    stat: Nome do atributo (HP, ataque, defesa, ataque especial, defesa especial, velocidade)
    
    limit: Número de resultados a serem retornados
    generation: Filtrar por geração (1 ou 2)
    """
    try:
        db.connect()
        
        gen_filter = ""
        params = [stat, limit]
        if generation:
            gen_filter = "AND s.generation = ?"
            params.insert(1, generation)
        
        query = f"""
            SELECT p.name, ps.base_stat, GROUP_CONCAT(DISTINCT pt.type_name) as types
            FROM pokemon p
            JOIN pokemon_stat ps ON p.id = ps.pokemon_id
            JOIN pokemon_type pt ON p.id = pt.pokemon_id
            JOIN species s ON p.species_id = s.id
            WHERE ps.stat_name = ? {gen_filter}
            GROUP BY p.id
            ORDER BY ps.base_stat DESC
            LIMIT ?
        """
        
        results = db.execute_query(query, params)
        
        for r in results:
            r['types'] = r['types'].split(',') if r['types'] else []
        
        return {
            "stat": stat,
            "generation": generation,
            "top_pokemon": results
        }
        
    except Exception as e:
        logger.error(f"Top stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
