"""
Claude API integration for SQL query generation
"""
from anthropic import Anthropic
from typing import Dict, Any
from config import settings
import logging
import json

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Generates SQL queries from natural language using Claude"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5-20250929"
    
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
        try:
            # Build the schema context for Claude
            schema_text = self._format_schema(database_schema)
            
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

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the SQL query from response
            sql_query = message.content[0].text.strip()
            
            # Clean up the query (remove any accidental markdown if present)
            sql_query = self._clean_sql_query(sql_query)
            
            logger.info(f"Generated SQL query: {sql_query}")
            
            return {
                'success': True,
                'sql_query': sql_query
            }
            
        except Exception as e:
            logger.error(f"SQL generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_schema(self, database_schema: Dict[str, Any]) -> str:
        """Format database schema into readable text for Claude"""
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
        """Clean up SQL query by removing markdown formatting"""
        # Remove ```sql and ``` markers
        sql_query = sql_query.replace('```sql', '').replace('```', '')
        
        # Remove leading/trailing whitespace
        sql_query = sql_query.strip()
        
        return sql_query
