"""
Script de exemplo para consultar o banco de dados diretamente
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import db

def run_queries():
    """Executa queries de exemplo no banco"""
    
    db.connect()
    
    print("=" * 80)
    print("POKEMON DATABASE - EXAMPLE QUERIES")
    print("=" * 80)
    
    # Query 1: Top 10 fastest Pokemon
    print("\n[1] Top 10 Fastest Pokemon")
    print("-" * 80)
    results = db.execute_query("""
        SELECT p.name, ps.base_stat as speed, GROUP_CONCAT(pt.type_name) as types
        FROM pokemon p
        JOIN pokemon_stat ps ON p.id = ps.pokemon_id
        JOIN pokemon_type pt ON p.id = pt.pokemon_id
        WHERE ps.stat_name = 'speed'
        GROUP BY p.id
        ORDER BY ps.base_stat DESC
        LIMIT 10
    """)
    
    for i, row in enumerate(results, 1):
        print(f"{i:2d}. {row['name']:15s} - Speed: {row['speed']:3d} - Types: {row['types']}")
    
    # Query 2: Type distribution
    print("\n[2] Pokemon Count by Type")
    print("-" * 80)
    results = db.execute_query("""
        SELECT type_name, COUNT(*) as count
        FROM pokemon_type
        GROUP BY type_name
        ORDER BY count DESC
    """)
    
    for row in results:
        print(f"{row['type_name']:15s}: {row['count']:3d} Pokemon")
    
    # Query 3: Strongest by stat
    print("\n[3] Strongest Pokemon by Each Stat")
    print("-" * 80)
    results = db.execute_query("""
        SELECT ps.stat_name, p.name, ps.base_stat
        FROM pokemon_stat ps
        JOIN pokemon p ON ps.pokemon_id = p.id
        WHERE (ps.stat_name, ps.base_stat) IN (
            SELECT stat_name, MAX(base_stat)
            FROM pokemon_stat
            GROUP BY stat_name
        )
        ORDER BY ps.stat_name
    """)
    
    for row in results:
        print(f"{row['stat_name']:20s}: {row['name']:15s} ({row['base_stat']})")
    
    # Query 4: Evolution chains
    print("\n[4] Sample Evolution Chains")
    print("-" * 80)
    results = db.execute_query("""
        SELECT s1.name as from_pokemon, s2.name as to_pokemon, e.min_level, e.trigger
        FROM evolution e
        JOIN species s1 ON e.species_id = s1.id
        JOIN species s2 ON e.evolves_to_species_id = s2.id
        LIMIT 10
    """)
    
    for row in results:
        method = f"Level {row['min_level']}" if row['min_level'] else row['trigger']
        print(f"{row['from_pokemon']:15s} -> {row['to_pokemon']:15s} ({method})")
    
    # Query 5: Database stats
    print("\n[5] Database Statistics")
    print("-" * 80)
    
    pokemon_count = db.execute_query("SELECT COUNT(*) as count FROM pokemon")[0]['count']
    species_count = db.execute_query("SELECT COUNT(*) as count FROM species")[0]['count']
    evolution_count = db.execute_query("SELECT COUNT(*) as count FROM evolution")[0]['count']
    
    print(f"Total Pokemon:    {pokemon_count}")
    print(f"Total Species:    {species_count}")
    print(f"Total Evolutions: {evolution_count}")
    
    db.close()
    
    print("\n" + "=" * 80)
    print("QUERIES COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        run_queries()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you've run the ingestion first:")
        print("  python -m app.ingest --limit 251")
        sys.exit(1)
