"""
Database connection and query execution utilities
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and query execution"""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.connection = None
    
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                database=self.database_name,
                user=settings.db_user,
                password=settings.db_password
            )
            logger.info(f"Connected to database: {self.database_name}")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info(f"Disconnected from database: {self.database_name}")
    
    def get_tables(self) -> List[Dict[str, str]]:
        """Get list of all tables in the database with their comments"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        c.table_name,
                        obj_description(pgc.oid, 'pg_class') as table_comment
                    FROM information_schema.tables c
                    JOIN pg_class pgc ON c.table_name = pgc.relname
                    WHERE c.table_schema = 'public'
                    AND c.table_type = 'BASE TABLE'
                    ORDER BY c.table_name
                """)
                tables = cursor.fetchall()
                return [dict(row) for row in tables]
        except Exception as e:
            logger.error(f"Error fetching tables: {str(e)}")
            raise
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        pgd.description as column_comment
                    FROM information_schema.columns c
                    LEFT JOIN pg_catalog.pg_statio_all_tables st 
                        ON c.table_name = st.relname
                    LEFT JOIN pg_catalog.pg_description pgd 
                        ON pgd.objoid = st.relid 
                        AND pgd.objsubid = c.ordinal_position
                    WHERE c.table_name = %s
                    AND c.table_schema = 'public'
                    ORDER BY c.ordinal_position
                """, (table_name,))
                schema = cursor.fetchall()
                return [dict(row) for row in schema]
        except Exception as e:
            logger.error(f"Error fetching schema for {table_name}: {str(e)}")
            raise
    
    def get_all_schemas(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get schemas for all tables in the database"""
        tables = self.get_tables()
        schemas = {}
        for table in tables:
            table_name = table['table_name']
            schemas[table_name] = {
                'comment': table.get('table_comment'),
                'columns': self.get_table_schema(table_name)
            }
        return schemas
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return results
        
        Returns:
            Dict with 'success', 'data' (if successful), or 'error' (if failed)
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                
                # Check if query returns data (SELECT) or just executes (INSERT, UPDATE, etc.)
                if cursor.description:
                    results = cursor.fetchall()
                    return {
                        'success': True,
                        'data': [dict(row) for row in results],
                        'row_count': len(results)
                    }
                else:
                    self.connection.commit()
                    return {
                        'success': True,
                        'message': 'Query executed successfully',
                        'rows_affected': cursor.rowcount
                    }
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Query execution error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
