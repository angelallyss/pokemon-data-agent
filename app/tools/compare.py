import logging
from typing import Dict, Any
from app.db import db

logger = logging.getLogger(__name__)

def compare_pokemon(pokemon_a: str, pokemon_b: str, metric: str = "all") -> Dict[str, Any]:
    """
    Compara dois Pokémon por métricas específicas (HP, ataque, defesa, velocidade, etc.)

    Argumentos:
    
    pokemon_a: Nome do primeiro Pokémon
    
    pokemon_b: Nome do segundo Pokémon
    
    métrica: Atributo a ser comparado (HP, ataque, defesa, ataque especial, defesa especial, velocidade, todos)
    
    Retorna:
    
    Dicionário com os resultados da comparação
    """
    db.connect()
    
    try:
        # Get Pokemon IDs
        pokemon_a = pokemon_a.lower()
        pokemon_b = pokemon_b.lower()
        
        if metric == "all":
            query = """
                SELECT p.name, ps.stat_name, ps.base_stat
                FROM pokemon p
                JOIN pokemon_stat ps ON p.id = ps.pokemon_id
                WHERE p.name IN (?, ?)
                ORDER BY p.name, ps.stat_name
            """
            results = db.execute_query(query, (pokemon_a, pokemon_b))
        else:
            query = """
                SELECT p.name, ps.stat_name, ps.base_stat
                FROM pokemon p
                JOIN pokemon_stat ps ON p.id = ps.pokemon_id
                WHERE p.name IN (?, ?) AND ps.stat_name = ?
            """
            results = db.execute_query(query, (pokemon_a, pokemon_b, metric))
        
        if not results:
            return {"error": f"Pokemon not found or metric '{metric}' invalid"}
        
        # Organize results
        comparison = {}
        for row in results:
            name = row['name']
            if name not in comparison:
                comparison[name] = {}
            comparison[name][row['stat_name']] = row['base_stat']
        
        # Determine winner for each stat
        winners = {}
        if metric == "all":
            all_stats = set()
            for stats in comparison.values():
                all_stats.update(stats.keys())
            
            for stat in all_stats:
                a_val = comparison.get(pokemon_a, {}).get(stat, 0)
                b_val = comparison.get(pokemon_b, {}).get(stat, 0)
                
                if a_val > b_val:
                    winners[stat] = pokemon_a
                elif b_val > a_val:
                    winners[stat] = pokemon_b
                else:
                    winners[stat] = "tie"
        else:
            a_val = comparison.get(pokemon_a, {}).get(metric, 0)
            b_val = comparison.get(pokemon_b, {}).get(metric, 0)
            
            if a_val > b_val:
                winners[metric] = pokemon_a
            elif b_val > a_val:
                winners[metric] = pokemon_b
            else:
                winners[metric] = "tie"
        
        return {
            "comparison": comparison,
            "winners": winners,
            "metric": metric
        }
        
    finally:
        db.close()
