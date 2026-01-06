"""
Claude API integration for SQL query generation with comprehensive logging
"""
from anthropic import Anthropic
from typing import Dict, Any
from config import settings
from cloudwatch_logger import get_logger, log_with_context
import time

logger = get_logger(__name__)

class SQLGenerator:
    """Generates SQL queries from natural language using Claude with logging"""
    
    def __init__(self):
        logger.debug("Initializing SQLGenerator")
        
        try:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = "claude-sonnet-4-5-20250929"
            
            logger.info("SQLGenerator initialized successfully", extra={
                "extra_fields": {
                    "model": self.model,
                    "api_key_prefix": settings.anthropic_api_key[:10] + "..."
                }
            })
            
        except Exception as e:
            logger.error("Failed to initialize SQLGenerator", extra={
                "extra_fields": {"error": str(e)}
            }, exc_info=True)
            raise
    
    def generate_sql(
        self, 
        natural_language_query: str, 
        database_schema: Dict[str, Any],
        database_name: str
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language
        
        Args:
            natural_language_query: User's question in plain English
            database_schema: Complete database schema with table and column info
            database_name: Name of the database (for context)
        
        Returns:
            Dict with 'success', 'sql_query', and optionally 'explanation' or 'error'
        """
        logger.info("Starting SQL generation", extra={
            "extra_fields": {
                "database": database_name,
                "query_length": len(natural_language_query),
                "table_count": len(database_schema),
                "query_preview": natural_language_query[:100]
            }
        })
        
        start_time = time.time()
        
        try:
            # Build the schema context for Claude
            logger.debug("Formatting database schema for Claude")
            schema_text = self._format_schema(database_schema)
            
            schema_size = len(schema_text)
            logger.debug(f"Schema formatted", extra={
                "extra_fields": {
                    "schema_size_chars": schema_size,
                    "table_count": len(database_schema)
                }
            })
            
            # Create the prompt
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
6. Include LIMIT clauses when appropriate to avoid returning too many rows
7. Return ONLY the SQL query without any markdown formatting, explanations, or code blocks
8. The query should be ready to execute as-is

IMPORTANT: 
- Return ONLY the raw SQL query
- Do NOT include ```sql or ``` markers
- Do NOT include any explanatory text before or after the query
- The query should be a single statement that can be executed directly

SQL QUERY:"""

            prompt_size = len(prompt)
            logger.debug(f"Prompt created", extra={
                "extra_fields": {
                    "prompt_size_chars": prompt_size,
                    "estimated_tokens": prompt_size // 4  # Rough estimate
                }
            })
            
            # Call Claude API
            logger.info("Calling Claude API", extra={
                "extra_fields": {
                    "model": self.model,
                    "max_tokens": 1024
                }
            })
            
            api_start_time = time.time()
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            api_duration = time.time() - api_start_time
            
            logger.info("Claude API response received", extra={
                "extra_fields": {
                    "api_call_time_ms": round(api_duration * 1000, 2),
                    "response_tokens": getattr(message.usage, 'output_tokens', 0) if hasattr(message, 'usage') else 0,
                    "input_tokens": getattr(message.usage, 'input_tokens', 0) if hasattr(message, 'usage') else 0
                }
            })
            
            # Extract the SQL query from response
            sql_query = message.content[0].text.strip()
            
            # Clean up the query (remove any accidental markdown if present)
            sql_query = self._clean_sql_query(sql_query)
            
            total_duration = time.time() - start_time
            
            logger.info("SQL generation successful", extra={
                "extra_fields": {
                    "database": database_name,
                    "generated_query_length": len(sql_query),
                    "total_time_ms": round(total_duration * 1000, 2),
                    "api_time_ms": round(api_duration * 1000, 2),
                    "generated_query_preview": sql_query[:200]
                }
            })
            
            return {
                'success': True,
                'sql_query': sql_query
            }
            
        except Exception as e:
            total_duration = time.time() - start_time
            
            logger.error("SQL generation failed", extra={
                "extra_fields": {
                    "database": database_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "total_time_ms": round(total_duration * 1000, 2),
                    "natural_language_query": natural_language_query[:100]
                }
            }, exc_info=True)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_schema(self, database_schema: Dict[str, Any]) -> str:
        """Format database schema into readable text for Claude"""
        logger.debug(f"Formatting schema for {len(database_schema)} tables")
        
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
        
        result = "\n".join(schema_lines)
        
        logger.debug(f"Schema formatted: {len(result)} characters, {len(schema_lines)} lines")
        
        return result
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean up SQL query by removing markdown formatting"""
        original_length = len(sql_query)
        
        # Remove ```sql and ``` markers
        sql_query = sql_query.replace('```sql', '').replace('```', '')
        
        # Remove leading/trailing whitespace
        sql_query = sql_query.strip()
        
        cleaned_length = len(sql_query)
        
        if original_length != cleaned_length:
            logger.debug(f"SQL query cleaned", extra={
                "extra_fields": {
                    "original_length": original_length,
                    "cleaned_length": cleaned_length,
                    "removed_chars": original_length - cleaned_length
                }
            })
        
        return sql_query
