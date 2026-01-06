"""
Database connection and query execution utilities with comprehensive logging
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import settings
from cloudwatch_logger import get_logger, log_with_context
import time

logger = get_logger(__name__)

class DatabaseManager:
    """Manages database connections and query execution with logging"""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.connection = None
        
        logger.debug(f"DatabaseManager initialized", extra={
            "extra_fields": {"database": database_name}
        })
    
    def connect(self) -> None:
        """Establish database connection"""
        logger.info(f"Attempting to connect to database", extra={
            "extra_fields": {
                "database": self.database_name,
                "host": settings.db_host,
                "port": settings.db_port,
                "user": settings.db_user
            }
        })
        
        start_time = time.time()
        
        try:
            self.connection = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                database=self.database_name,
                user=settings.db_user,
                password=settings.db_password,
                connect_timeout=10  # 10 second timeout
            )
            
            duration = time.time() - start_time
            
            logger.info(f"Successfully connected to database", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "connection_time_ms": round(duration * 1000, 2)
                }
            })
            
        except psycopg2.OperationalError as e:
            duration = time.time() - start_time
            logger.error(f"Database connection failed: Operational error", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "host": settings.db_host,
                    "error": str(e),
                    "connection_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Database connection failed: Unexpected error", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "connection_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            raise
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Database connection closed", extra={
                    "extra_fields": {"database": self.database_name}
                })
            except Exception as e:
                logger.error(f"Error closing database connection", extra={
                    "extra_fields": {
                        "database": self.database_name,
                        "error": str(e)
                    }
                }, exc_info=True)
        else:
            logger.debug(f"No active connection to close", extra={
                "extra_fields": {"database": self.database_name}
            })
    
    def get_tables(self) -> List[Dict[str, str]]:
        """Get list of all tables in the database with their comments"""
        logger.debug(f"Fetching table list", extra={
            "extra_fields": {"database": self.database_name}
        })
        
        start_time = time.time()
        
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
                
                duration = time.time() - start_time
                
                logger.info(f"Tables fetched successfully", extra={
                    "extra_fields": {
                        "database": self.database_name,
                        "table_count": len(tables),
                        "query_time_ms": round(duration * 1000, 2)
                    }
                })
                
                return [dict(row) for row in tables]
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error fetching tables", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "query_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            raise
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table"""
        logger.debug(f"Fetching table schema", extra={
            "extra_fields": {
                "database": self.database_name,
                "table_name": table_name
            }
        })
        
        start_time = time.time()
        
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
                
                duration = time.time() - start_time
                
                logger.info(f"Table schema fetched successfully", extra={
                    "extra_fields": {
                        "database": self.database_name,
                        "table_name": table_name,
                        "column_count": len(schema),
                        "query_time_ms": round(duration * 1000, 2)
                    }
                })
                
                return [dict(row) for row in schema]
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error fetching table schema", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "table_name": table_name,
                    "error": str(e),
                    "query_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            raise
    
    def get_all_schemas(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get schemas for all tables in the database"""
        logger.debug(f"Fetching all table schemas", extra={
            "extra_fields": {"database": self.database_name}
        })
        
        start_time = time.time()
        
        try:
            tables = self.get_tables()
            schemas = {}
            
            for table in tables:
                table_name = table['table_name']
                schemas[table_name] = {
                    'comment': table.get('table_comment'),
                    'columns': self.get_table_schema(table_name)
                }
            
            duration = time.time() - start_time
            
            logger.info(f"All schemas fetched successfully", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "table_count": len(schemas),
                    "total_time_ms": round(duration * 1000, 2)
                }
            })
            
            return schemas
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error fetching all schemas", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "total_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            raise
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return results
        
        Returns:
            Dict with 'success', 'data' (if successful), or 'error' (if failed)
        """
        # Log query (truncate if too long for security)
        query_preview = query[:500] if len(query) > 500 else query
        
        logger.info(f"Executing SQL query", extra={
            "extra_fields": {
                "database": self.database_name,
                "query_length": len(query),
                "query_preview": query_preview
            }
        })
        
        start_time = time.time()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                
                # Check if query returns data (SELECT) or just executes (INSERT, UPDATE, etc.)
                if cursor.description:
                    results = cursor.fetchall()
                    duration = time.time() - start_time
                    
                    logger.info(f"Query executed successfully (SELECT)", extra={
                        "extra_fields": {
                            "database": self.database_name,
                            "row_count": len(results),
                            "execution_time_ms": round(duration * 1000, 2)
                        }
                    })
                    
                    return {
                        'success': True,
                        'data': [dict(row) for row in results],
                        'row_count': len(results)
                    }
                else:
                    self.connection.commit()
                    duration = time.time() - start_time
                    
                    logger.info(f"Query executed successfully (DML)", extra={
                        "extra_fields": {
                            "database": self.database_name,
                            "rows_affected": cursor.rowcount,
                            "execution_time_ms": round(duration * 1000, 2)
                        }
                    })
                    
                    return {
                        'success': True,
                        'message': 'Query executed successfully',
                        'rows_affected': cursor.rowcount
                    }
                    
        except psycopg2.Error as e:
            self.connection.rollback()
            duration = time.time() - start_time
            
            logger.warning(f"Query execution failed: SQL error", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "error_code": e.pgcode if hasattr(e, 'pgcode') else None,
                    "execution_time_ms": round(duration * 1000, 2),
                    "query_preview": query_preview
                }
            })
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_insert(self, query: str, params: tuple) -> Dict[str, Any]:
        """
        Execute an INSERT query with parameters and return the inserted ID
        
        Args:
            query: SQL INSERT query with RETURNING clause
            params: Tuple of parameters for the query
            
        Returns:
            Dict with 'success' and 'id' (if successful) or 'error' (if failed)
        """
        logger.info(f"Executing INSERT query", extra={
            "extra_fields": {
                "database": self.database_name,
                "param_count": len(params) if params else 0
            }
        })
        
        start_time = time.time()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result_id = cursor.fetchone()[0] if cursor.description else None
                self.connection.commit()
                
                duration = time.time() - start_time
                
                logger.info(f"INSERT query executed successfully", extra={
                    "extra_fields": {
                        "database": self.database_name,
                        "inserted_id": result_id,
                        "execution_time_ms": round(duration * 1000, 2)
                    }
                })
                
                return {
                    'success': True,
                    'id': result_id
                }
                
        except psycopg2.Error as e:
            self.connection.rollback()
            duration = time.time() - start_time
            
            logger.warning(f"INSERT query failed: SQL error", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "error_code": e.pgcode if hasattr(e, 'pgcode') else None,
                    "execution_time_ms": round(duration * 1000, 2)
                }
            })
            
            return {
                'success': False,
                'error': str(e)
            }
            
        except Exception as e:
            self.connection.rollback()
            duration = time.time() - start_time
            
            logger.error(f"INSERT query failed: Unexpected error", extra={
                "extra_fields": {
                    "database": self.database_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            
            return {
                'success': False,
                'error': str(e)
            }
