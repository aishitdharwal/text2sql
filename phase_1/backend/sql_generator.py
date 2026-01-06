"""
Claude API integration for SQL query generation with LangFuse observability
"""
from anthropic import Anthropic
from typing import Dict, Any, Optional
from config import settings
from cloudwatch_logger import get_logger
import time

logger = get_logger(__name__)

# Try to import LangFuse
try:
    from langfuse import Langfuse
    from langfuse.types import TraceContext
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None
    TraceContext = None

# Initialize LangFuse client
langfuse_client: Optional[Langfuse] = None
if LANGFUSE_AVAILABLE and settings.enable_langfuse and settings.langfuse_public_key and settings.langfuse_secret_key:
    try:
        langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host
        )
        logger.info("✅ LangFuse observability enabled", extra={
            "extra_fields": {"host": settings.langfuse_host}
        })
    except Exception as e:
        logger.warning(f"Failed to initialize LangFuse, continuing without observability", extra={
            "extra_fields": {"error": str(e)}
        })
        langfuse_client = None
else:
    if not LANGFUSE_AVAILABLE:
        logger.info("LangFuse module not available - install with: pip install langfuse")
    elif not settings.enable_langfuse:
        logger.info("LangFuse observability disabled (ENABLE_LANGFUSE=false)")
    else:
        logger.info("LangFuse observability disabled (missing credentials)")

class SQLGenerator:
    """Generates SQL queries from natural language using Claude"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5-20250929"
        logger.info("SQLGenerator initialized successfully", extra={
            "extra_fields": {"model": self.model}
        })
    
    def generate_sql(
        self, 
        natural_language_query: str, 
        database_schema: Dict[str, Any],
        database_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate SQL query from natural language"""
        
        start_time = time.time()
        trace_id = langfuse_client.create_trace_id() if langfuse_client else None
        
        # Create trace context
        trace_context = None
        if langfuse_client and trace_id:
            trace_context = TraceContext(
                trace_id=trace_id,
                user_id=user_id,
                session_id=session_id,
                tags=["text2sql", database_name, user_id] if user_id else ["text2sql", database_name],
                metadata={
                    "database": database_name,
                    "team": user_id
                }
            )
        
        logger.info("Starting SQL generation", extra={
            "extra_fields": {
                "database": database_name,
                "query_length": len(natural_language_query),
                "trace_id": trace_id
            }
        })
        
        try:
            # Format schema
            schema_text = self._format_schema(database_schema)
            
            # Create prompt
            prompt = f"""You are an expert SQL query generator for PostgreSQL databases. Your task is to convert natural language questions into accurate SQL queries.

DATABASE: {database_name}

AVAILABLE TABLES AND SCHEMAS:
{schema_text}

USER QUESTION: {natural_language_query}

INSTRUCTIONS:
1. Generate a PostgreSQL-compatible SQL query that answers the user's question
2. Use proper JOIN clauses when querying multiple tables
3. Use appropriate WHERE clauses for filtering
4. Use GROUP BY and aggregate functions when needed
5. Always use table aliases for better readability
6. Include LIMIT clauses when appropriate
7. Return ONLY the SQL query without any markdown formatting or explanations

IMPORTANT: Return ONLY the raw SQL query

SQL QUERY:"""
            
            # Call Claude API
            api_start_time = time.time()
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            api_duration = time.time() - api_start_time
            
            # Extract SQL
            sql_query = message.content[0].text.strip()
            sql_query = self._clean_sql_query(sql_query)
            
            total_duration = time.time() - start_time
            
            # Log to LangFuse using create_event with trace_context
            if langfuse_client and trace_context:
                try:
                    input_tokens = message.usage.input_tokens if hasattr(message, 'usage') else 0
                    output_tokens = message.usage.output_tokens if hasattr(message, 'usage') else 0
                    
                    # Calculate cost (Claude Sonnet 4.5: $3 per M input, $15 per M output)
                    cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
                    
                    langfuse_client.create_event(
                        trace_context=trace_context,
                        name="text2sql_generation",
                        input=natural_language_query,
                        output=sql_query,
                        metadata={
                            "database": database_name,
                            "team": user_id,
                            "model": self.model,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": input_tokens + output_tokens,
                            "cost_usd": round(cost, 6),
                            "api_latency_ms": round(api_duration * 1000, 2),
                            "total_latency_ms": round(total_duration * 1000, 2),
                            "query_length": len(sql_query),
                            "success": True
                        },
                        level="DEFAULT"
                    )
                    langfuse_client.flush()
                    logger.debug("✅ Logged to LangFuse successfully")
                except Exception as e:
                    logger.debug(f"Failed to log to LangFuse: {e}")
            
            logger.info("SQL generation successful", extra={
                "extra_fields": {
                    "database": database_name,
                    "total_time_ms": round(total_duration * 1000, 2),
                    "trace_id": trace_id
                }
            })
            
            return {
                'success': True,
                'sql_query': sql_query
            }
            
        except Exception as e:
            total_duration = time.time() - start_time
            
            # Log error to LangFuse
            if langfuse_client and trace_context:
                try:
                    langfuse_client.create_event(
                        trace_context=trace_context,
                        name="text2sql_generation_error",
                        input=natural_language_query,
                        metadata={
                            "database": database_name,
                            "team": user_id,
                            "model": self.model,
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "total_latency_ms": round(total_duration * 1000, 2),
                            "success": False
                        },
                        level="ERROR",
                        status_message=str(e)
                    )
                    langfuse_client.flush()
                except Exception as trace_error:
                    logger.debug(f"Failed to log error to LangFuse: {trace_error}")
            
            logger.error("SQL generation failed", extra={
                "extra_fields": {
                    "database": database_name,
                    "error": str(e),
                    "trace_id": trace_id
                }
            }, exc_info=True)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_schema(self, database_schema: Dict[str, Any]) -> str:
        """Format database schema into readable text"""
        schema_lines = []
        
        for table_name, table_info in database_schema.items():
            schema_lines.append(f"\nTable: {table_name}")
            if table_info.get('comment'):
                schema_lines.append(f"Description: {table_info['comment']}")
            
            schema_lines.append("Columns:")
            for column in table_info['columns']:
                col_line = f"  - {column['column_name']} ({column['data_type']})"
                if column.get('column_comment'):
                    col_line += f" - {column['column_comment']}"
                if column['is_nullable'] == 'NO':
                    col_line += " [NOT NULL]"
                schema_lines.append(col_line)
        
        return "\n".join(schema_lines)
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Remove markdown formatting from SQL"""
        sql_query = sql_query.replace('```sql', '').replace('```', '')
        return sql_query.strip()
