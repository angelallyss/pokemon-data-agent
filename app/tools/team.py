import logging
from typing import List, Dict, Any
from app.db import db

logger = logging.getLogger(__name__)

TYPE_CHART = {
    'normal': {'weak_to': ['fighting'], 'resistant_to': [], 'immune_to': ['ghost']},
    'fire': {'weak_to': ['water', 'ground', 'rock'], 'resistant_to': ['fire', 'grass', 'ice', 'bug', 'steel', 'fairy']},
    'water': {'weak_to': ['electric', 'grass'], 'resistant_to': ['fire', 'water', 'ice', 'steel']},
    'electric': {'weak_to': ['ground'], 'resistant_to': ['electric', 'flying', 'steel']},
    'grass': {'weak_to': ['fire', 'ice', 'poison', 'flying', 'bug'], 'resistant_to': ['water', 'electric', 'grass', 'ground']},
    'ice': {'weak_to': ['fire', 'fighting', 'rock', 'steel'], 'resistant_to': ['ice']},
    'fighting': {'weak_to': ['flying', 'psychic', 'fairy'], 'resistant_to': ['bug', 'rock', 'dark']},
    'poison': {'weak_to': ['ground', 'psychic'], 'resistant_to': ['grass', 'fighting', 'poison', 'bug', 'fairy']},
    'ground': {'weak_to': ['water', 'grass', 'ice'], 'resistant_to': ['poison', 'rock'], 'immune_to': ['electric']},
    'flying': {'weak_to': ['electric', 'ice', 'rock'], 'resistant_to': ['grass', 'fighting', 'bug'], 'immune_to': ['ground']},
    'psychic': {'weak_to': ['bug', 'ghost', 'dark'], 'resistant_to': ['fighting', 'psychic']},
    'bug': {'weak_to': ['fire', 'flying', 'rock'], 'resistant_to': ['grass', 'fighting', 'ground']},
    'rock': {'weak_to': ['water', 'grass', 'fighting', 'ground', 'steel'], 'resistant_to': ['normal', 'fire', 'poison', 'flying']},
    'ghost': {'weak_to': ['ghost', 'dark'], 'resistant_to': ['poison', 'bug'], 'immune_to': ['normal', 'fighting']},
    'dragon': {'weak_to': ['ice', 'dragon', 'fairy'], 'resistant_to': ['fire', 'water', 'electric', 'grass']},
    'dark': {'weak_to': ['fighting', 'bug', 'fairy'], 'resistant_to': ['ghost', 'dark'], 'immune_to': ['psychic']},
    'steel': {'weak_to': ['fire', 'fighting', 'ground'], 'resistant_to': ['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'], 'immune_to': ['poison']},
    'fairy': {'weak_to': ['poison', 'steel'], 'resistant_to': ['fighting', 'bug', 'dark'], 'immune_to': ['dragon']},
}

def suggest_team(goal: str = "balanced", generation: int = None) -> Dict[str, Any]:
    """
    Sugira uma equipe Pokémon equilibrada com base na cobertura de tipos e nos atributos.

    Argumentos:

    objetivo: Objetivo da equipe (equilibrada, ofensiva, defensiva, rápida)

    geração: Limitar a uma geração específica (1 ou 2)

    Retorno:

    Dicionário com a equipe sugerida e sua análise
    """
    db.connect()
    
    try:
        # Build query based on goal
        if goal == "offensive":
            stat_priority = "attack"
        elif goal == "defensive":
            stat_priority = "defense"
        elif goal == "fast":
            stat_priority = "speed"
        else:
            stat_priority = "hp"
        
        gen_filter = ""
        params = []
        if generation:
            gen_filter = "AND s.generation = ?"
            params.append(generation)
        
        query = f"""
            SELECT DISTINCT p.name, pt.type_name, ps.base_stat as priority_stat,
                   GROUP_CONCAT(pt2.type_name) as all_types
            FROM pokemon p
            JOIN pokemon_type pt ON p.id = pt.pokemon_id
            JOIN pokemon_type pt2 ON p.id = pt2.pokemon_id
            JOIN pokemon_stat ps ON p.id = ps.pokemon_id
            JOIN species s ON p.species_id = s.id
            WHERE ps.stat_name = ? {gen_filter}
            GROUP BY p.id
            ORDER BY ps.base_stat DESC
            LIMIT 50
        """
        
        candidates = db.execute_query(query, [stat_priority] + params)
        
        if not candidates:
            return {"error": "No Pokemon found matching criteria"}
        
        # Select diverse team (max 6)
        team = []
        used_types = set()
        
        for pokemon in candidates:
            if len(team) >= 6:
                break
            
            types = pokemon['all_types'].split(',')
            
            # Prefer Pokemon with types we don't have yet
            if goal == "balanced":
                if not any(t in used_types for t in types):
                    team.append(pokemon)
                    used_types.update(types)
            else:
                team.append(pokemon)
                used_types.update(types)
        
        # Calculate type coverage
        coverage = type_coverage([t for t in used_types])
        
        return {
            "team": [{"name": p['name'], "types": p['all_types'], "stat": p['priority_stat']} for p in team],
            "goal": goal,
            "type_coverage": coverage,
            "team_size": len(team)
        }
        
    finally:
        db.close()

def type_coverage(types: List[str]) -> Dict[str, Any]:
    """
    Calcula a cobertura de tipos ofensivos e defensivos para uma lista de tipos.

    Argumentos:
    
    tipos: Lista de tipos de Pokémon
    
    Retorno:
    
    Dicionário com análise de cobertura
    """
    weaknesses = {}
    resistances = {}
    immunities = {}
    
    for poke_type in types:
        if poke_type in TYPE_CHART:
            chart = TYPE_CHART[poke_type]
            
            for weak in chart.get('weak_to', []):
                weaknesses[weak] = weaknesses.get(weak, 0) + 1
            
            for resist in chart.get('resistant_to', []):
                resistances[resist] = resistances.get(resist, 0) + 1
            
            for immune in chart.get('immune_to', []):
                immunities[immune] = immunities.get(immune, 0) + 1
    
    return {
        "weaknesses": weaknesses,
        "resistances": resistances,
        "immunities": immunities,
        "types_covered": len(types)
    }
