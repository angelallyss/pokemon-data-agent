import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "pokemon.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Estabelecer conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
        
    def close(self):
        """Fechar conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_schema(self):
        """Inicializar esquema do banco de dados"""
        schema_path = Path(__file__).parent / "schemas.sql"
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        self.conn.executescript(schema)
        self.conn.commit()
        logger.info("Database schema initialized")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute uma consulta SELECT e retorne os resultados como uma lista de dicionários."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_write(self, query: str, params: tuple = ()):
        """Executar consulta INSERT/UPDATE/DELETE"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Write operation failed: {e}")
            self.conn.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute várias operações de gravação"""
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Batch write operation failed: {e}")
            self.conn.rollback()
            raise

# Global database instance
db = Database()
