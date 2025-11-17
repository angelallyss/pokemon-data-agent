import logging
from typing import List, Dict, Any
from app.db import db

logger = logging.getLogger(__name__)

def evolution_path(pokemon_name: str) -> Dict[str, Any]:
    """
    Obtenha a cadeia evolutiva completa de um Pokémon.

    Argumentos:

    nome_do_pokemon: Nome do Pokémon

    Retorno:

    Dicionário com informações da cadeia evolutiva
    """
    db.connect()
    
    try:
        pokemon_name = pokemon_name.lower()
        
        # Get species ID for the Pokemon
        query = """
            SELECT s.id, s.name, s.evolution_chain_id
            FROM species s
            JOIN pokemon p ON s.id = p.species_id
            WHERE p.name = ?
        """
        result = db.execute_query(query, (pokemon_name,))
        
        if not result:
            return {"error": f"Pokemon '{pokemon_name}' not found"}
        
        species_id = result[0]['id']
        chain_id = result[0]['evolution_chain_id']
        
        if not chain_id:
            return {
                "pokemon": pokemon_name,
                "chain": [pokemon_name],
                "message": "This Pokemon does not evolve"
            }
        
        # Get all evolutions in the chain
        query = """
            SELECT e.species_id, e.evolves_to_species_id, e.min_level, e.trigger,
                   s1.name as from_name, s2.name as to_name
            FROM evolution e
            JOIN species s1 ON e.species_id = s1.id
            LEFT JOIN species s2 ON e.evolves_to_species_id = s2.id
            WHERE s1.evolution_chain_id = ?
            ORDER BY e.species_id
        """
        evolutions = db.execute_query(query, (chain_id,))
        
        # Build evolution tree
        chain = build_evolution_tree(evolutions, species_id)
        
        return {
            "pokemon": pokemon_name,
            "chain": chain,
            "total_stages": len(chain)
        }
        
    finally:
        db.close()

def build_evolution_tree(evolutions: List[Dict[str, Any]], current_species_id: int) -> List[Dict[str, Any]]:
    """Construa uma cadeia de evolução linear a partir de dados de evolução."""
    # Find the base Pokemon (one that doesn't evolve from anything)
    all_to_ids = {e['evolves_to_species_id'] for e in evolutions if e['evolves_to_species_id']}
    all_from_ids = {e['species_id'] for e in evolutions}
    
    base_ids = all_from_ids - all_to_ids
    
    if not base_ids:
        # If no clear base, use the current Pokemon
        base_id = current_species_id
    else:
        base_id = min(base_ids)
    
    # Build chain from base
    chain = []
    evolution_map = {e['species_id']: e for e in evolutions}
    
    current_id = base_id
    visited = set()
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        
        if current_id in evolution_map:
            evo = evolution_map[current_id]
            stage = {
                "name": evo['from_name'],
                "species_id": evo['species_id']
            }
            
            if evo['evolves_to_species_id']:
                stage["evolves_to"] = evo['to_name']
                stage["method"] = {
                    "trigger": evo['trigger'],
                    "min_level": evo['min_level']
                }
            
            chain.append(stage)
            current_id = evo['evolves_to_species_id']
        else:
            # Last in chain
            query = "SELECT name FROM species WHERE id = ?"
            db_result = db.execute_query(query, (current_id,))
            if db_result:
                chain.append({
                    "name": db_result[0]['name'],
                    "species_id": current_id
                })
            break
    
    return chain
