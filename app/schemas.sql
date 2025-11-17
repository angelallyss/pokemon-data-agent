-- Pokemon base table
CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    height INTEGER,
    weight INTEGER,
    base_experience INTEGER,
    species_id INTEGER
);

-- Pokemon stats
CREATE TABLE IF NOT EXISTS pokemon_stat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INTEGER NOT NULL,
    stat_name TEXT NOT NULL,
    base_stat INTEGER NOT NULL,
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id),
    UNIQUE(pokemon_id, stat_name)
);

-- Pokemon types
CREATE TABLE IF NOT EXISTS pokemon_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INTEGER NOT NULL,
    type_name TEXT NOT NULL,
    slot INTEGER NOT NULL,
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id),
    UNIQUE(pokemon_id, slot)
);

-- Species information
CREATE TABLE IF NOT EXISTS species (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    evolution_chain_id INTEGER,
    generation INTEGER
);

-- Evolution chain
CREATE TABLE IF NOT EXISTS evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id INTEGER NOT NULL,
    evolves_to_species_id INTEGER,
    min_level INTEGER,
    trigger TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id),
    FOREIGN KEY (evolves_to_species_id) REFERENCES species(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon(name);
CREATE INDEX IF NOT EXISTS idx_pokemon_stat_pokemon_id ON pokemon_stat(pokemon_id);
CREATE INDEX IF NOT EXISTS idx_pokemon_type_pokemon_id ON pokemon_type(pokemon_id);
CREATE INDEX IF NOT EXISTS idx_species_name ON species(name);
CREATE INDEX IF NOT EXISTS idx_evolution_species_id ON evolution(species_id);
