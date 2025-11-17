import httpx
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from app.db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class PokeAPIClient:
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
    
    def get_cached_or_fetch(self, endpoint: str, cache_name: str) -> Optional[Dict[str, Any]]:
        """Obtenha dados do cache ou busque dados na API."""
        cache_file = CACHE_DIR / f"{cache_name}.json"
        
        if cache_file.exists():
            logger.info(f"Loading from cache: {cache_name}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            logger.info(f"Fetching: {url}")
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return data
        except Exception as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")
            return None
    
    def close(self):
        self.client.close()

def ingest_pokemon(limit: int = 251):
    """Ingerir dados de Pokémon da PokeAPI"""
    client = PokeAPIClient()
    db.connect()
    db.init_schema()
    
    logger.info(f"Starting ingestion for {limit} Pokemon")
    
    for pokemon_id in range(1, limit + 1):
        # Fetch Pokemon data
        pokemon_data = client.get_cached_or_fetch(
            f"pokemon/{pokemon_id}",
            f"pokemon_{pokemon_id}"
        )
        
        if not pokemon_data:
            continue
        
        # Insert Pokemon
        db.execute_write(
            """INSERT OR REPLACE INTO pokemon (id, name, height, weight, base_experience, species_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                pokemon_data['id'],
                pokemon_data['name'],
                pokemon_data['height'],
                pokemon_data['weight'],
                pokemon_data.get('base_experience'),
                pokemon_data['species']['url'].split('/')[-2]
            )
        )
        
        # Insert stats
        for stat in pokemon_data['stats']:
            db.execute_write(
                """INSERT OR REPLACE INTO pokemon_stat (pokemon_id, stat_name, base_stat)
                   VALUES (?, ?, ?)""",
                (
                    pokemon_data['id'],
                    stat['stat']['name'],
                    stat['base_stat']
                )
            )
        
        # Insert types
        for type_data in pokemon_data['types']:
            db.execute_write(
                """INSERT OR REPLACE INTO pokemon_type (pokemon_id, type_name, slot)
                   VALUES (?, ?, ?)""",
                (
                    pokemon_data['id'],
                    type_data['type']['name'],
                    type_data['slot']
                )
            )
        
        # Fetch species data
        species_id = pokemon_data['species']['url'].split('/')[-2]
        species_data = client.get_cached_or_fetch(
            f"pokemon-species/{species_id}",
            f"species_{species_id}"
        )
        
        if species_data:
            evolution_chain_id = None
            if species_data.get('evolution_chain'):
                evolution_chain_id = species_data['evolution_chain']['url'].split('/')[-2]
            
            db.execute_write(
                """INSERT OR REPLACE INTO species (id, name, evolution_chain_id, generation)
                   VALUES (?, ?, ?, ?)""",
                (
                    int(species_id),
                    species_data['name'],
                    evolution_chain_id,
                    int(species_data['generation']['url'].split('/')[-2])
                )
            )
        
        logger.info(f"Ingested: {pokemon_data['name']} ({pokemon_id}/{limit})")
    
    # Ingest evolution chains
    ingest_evolution_chains(client)
    
    client.close()
    db.close()
    logger.info("Ingestion complete!")

def ingest_evolution_chains(client: PokeAPIClient):
    """Ingerir dados da cadeia evolutiva"""
    logger.info("Ingesting evolution chains...")
    
    # Get all unique evolution chain IDs
    chains = db.execute_query(
        "SELECT DISTINCT evolution_chain_id FROM species WHERE evolution_chain_id IS NOT NULL"
    )
    
    for chain_row in chains:
        chain_id = chain_row['evolution_chain_id']
        chain_data = client.get_cached_or_fetch(
            f"evolution-chain/{chain_id}",
            f"evolution_chain_{chain_id}"
        )
        
        if chain_data:
            process_evolution_chain(chain_data['chain'])

def process_evolution_chain(chain: Dict[str, Any], from_species_id: Optional[int] = None):
    """Processar recursivamente a cadeia de evolução"""
    species_id = int(chain['species']['url'].split('/')[-2])
    
    if from_species_id:
        min_level = None
        trigger = None
        
        if chain.get('evolution_details'):
            details = chain['evolution_details'][0]
            min_level = details.get('min_level')
            trigger = details.get('trigger', {}).get('name')
        
        db.execute_write(
            """INSERT OR IGNORE INTO evolution (species_id, evolves_to_species_id, min_level, trigger)
               VALUES (?, ?, ?, ?)""",
            (from_species_id, species_id, min_level, trigger)
        )
    
    for evolves_to in chain.get('evolves_to', []):
        process_evolution_chain(evolves_to, species_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Pokemon data from PokeAPI")
    parser.add_argument("--limit", type=int, default=251, help="Number of Pokemon to ingest")
    args = parser.parse_args()
    
    ingest_pokemon(args.limit)
