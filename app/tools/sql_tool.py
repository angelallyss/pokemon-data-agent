import logging
from typing import List, Dict, Any
from app.db import db

logger = logging.getLogger(__name__)

ALLOWED_KEYWORDS = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'INNER', 'ON', 'GROUP', 'ORDER', 'LIMIT', 'AS', 'AND', 'OR']

def sql_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute uma consulta SQL segura no banco de dados Pokémon.

    Somente consultas SELECT são permitidas.
    
    Argumentos:
    
    consulta: string de consulta SQL SELECT
    
    Retorno:
    
    Lista de dicionários com os resultados da consulta
    """
    query_upper = query.strip().upper()
    
    # Security: only allow SELECT queries
    if not query_upper.startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Security: block dangerous keywords
    dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    if any(keyword in query_upper for keyword in dangerous):
        raise ValueError("Query contains forbidden keywords")
    
    try:
        db.connect()
        results = db.execute_query(query)
        logger.info(f"Query executed successfully, returned {len(results)} rows")
        return results
    except Exception as e:
        logger.error(f"SQL query failed: {e}")
        raise
    finally:
        db.close()
