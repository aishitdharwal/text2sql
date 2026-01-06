"""
Query caching with DynamoDB
"""
import hashlib
import time
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from cloudwatch_logger import get_logger

logger = get_logger(__name__)

class QueryCache:
    """DynamoDB-based query cache for SQL generation"""
    
    def __init__(
        self,
        table_name: str = "text2sql_query_cache",
        region_name: str = "ap-south-1",
        ttl_days: int = 30,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        self.table_name = table_name
        self.ttl_days = ttl_days
        
        # Initialize DynamoDB client
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
        
        self.dynamodb = boto3.resource('dynamodb', **session_kwargs)
        self.table = None
        
        logger.info(f"QueryCache initialized", extra={
            "extra_fields": {
                "table_name": table_name,
                "region": region_name,
                "ttl_days": ttl_days
            }
        })
    
    def _ensure_table_exists(self):
        """Ensure DynamoDB table exists, create if it doesn't"""
        if self.table is not None:
            return
        
        try:
            self.table = self.dynamodb.Table(self.table_name)
            # Try to load table to verify it exists
            self.table.load()
            logger.info(f"Connected to existing cache table", extra={
                "extra_fields": {"table_name": self.table_name}
            })
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Cache table not found, creating...", extra={
                    "extra_fields": {"table_name": self.table_name}
                })
                self._create_table()
            else:
                raise
    
    def _create_table(self):
        """Create DynamoDB table with proper schema"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'cache_key',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'cache_key',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'database_name',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'created_at',
                        'AttributeType': 'N'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'database-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'database_name',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'created_at',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST',  # On-demand pricing
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'Text2SQL'
                    },
                    {
                        'Key': 'Purpose',
                        'Value': 'Query Cache'
                    }
                ]
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            
            # Enable TTL
            table.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )
            
            self.table = table
            logger.info(f"Cache table created successfully", extra={
                "extra_fields": {"table_name": self.table_name}
            })
            
        except Exception as e:
            logger.error(f"Failed to create cache table", extra={
                "extra_fields": {
                    "table_name": self.table_name,
                    "error": str(e)
                }
            }, exc_info=True)
            raise
    
    def _get_schema_version(self, schemas: Dict[str, Any]) -> str:
        """
        Generate schema version from database structure
        Returns 16-character hash
        """
        schema_parts = []
        
        # Sort tables for deterministic order
        for table_name in sorted(schemas.keys()):
            schema_parts.append(f"TABLE:{table_name}")
            
            # Sort columns for deterministic order
            columns = schemas[table_name].get('columns', [])
            for col in sorted(columns, key=lambda x: x['column_name']):
                # Include column name and type
                schema_parts.append(
                    f"{col['column_name']}:{col['data_type']}"
                )
        
        # Create fingerprint
        fingerprint = '|'.join(schema_parts)
        
        # Generate hash
        return hashlib.md5(fingerprint.encode()).hexdigest()[:16]
    
    def _get_cache_key(
        self,
        natural_language_query: str,
        database_name: str,
        schema_version: str
    ) -> str:
        """Generate cache key from query, database, and schema version"""
        # Normalize query (lowercase, strip whitespace)
        normalized_query = natural_language_query.lower().strip()
        
        # Create composite key
        key_string = f"{normalized_query}|{database_name}|{schema_version}"
        
        # Generate hash
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(
        self,
        natural_language_query: str,
        database_name: str,
        schemas: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get cached SQL query
        
        Returns:
            Generated SQL if cache hit, None if cache miss
        """
        self._ensure_table_exists()
        
        # Calculate schema version and cache key
        schema_version = self._get_schema_version(schemas)
        cache_key = self._get_cache_key(natural_language_query, database_name, schema_version)
        
        start_time = time.time()
        
        try:
            response = self.table.get_item(
                Key={'cache_key': cache_key}
            )
            
            duration = time.time() - start_time
            
            if 'Item' in response:
                item = response['Item']
                
                # Update hit count and last accessed time
                self.table.update_item(
                    Key={'cache_key': cache_key},
                    UpdateExpression='SET hit_count = hit_count + :inc, last_accessed_at = :now',
                    ExpressionAttributeValues={
                        ':inc': 1,
                        ':now': int(time.time())
                    }
                )
                
                logger.info(f"Cache HIT", extra={
                    "extra_fields": {
                        "cache_key": cache_key[:16],
                        "database_name": database_name,
                        "hit_count": int(item.get('hit_count', 0)) + 1,
                        "lookup_time_ms": round(duration * 1000, 2)
                    }
                })
                
                return item['generated_sql']
            else:
                logger.info(f"Cache MISS", extra={
                    "extra_fields": {
                        "cache_key": cache_key[:16],
                        "database_name": database_name,
                        "lookup_time_ms": round(duration * 1000, 2)
                    }
                })
                return None
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Cache lookup error", extra={
                "extra_fields": {
                    "cache_key": cache_key[:16],
                    "database_name": database_name,
                    "error": str(e),
                    "lookup_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            return None
    
    def put(
        self,
        natural_language_query: str,
        database_name: str,
        schemas: Dict[str, Any],
        generated_sql: str
    ) -> bool:
        """
        Store generated SQL in cache
        
        Returns:
            True if successful, False otherwise
        """
        self._ensure_table_exists()
        
        # Calculate schema version and cache key
        schema_version = self._get_schema_version(schemas)
        cache_key = self._get_cache_key(natural_language_query, database_name, schema_version)
        
        start_time = time.time()
        
        try:
            # Calculate TTL (current time + ttl_days in seconds)
            ttl = int(time.time()) + (self.ttl_days * 24 * 60 * 60)
            
            self.table.put_item(
                Item={
                    'cache_key': cache_key,
                    'natural_language_query': natural_language_query,
                    'database_name': database_name,
                    'schema_version': schema_version,
                    'generated_sql': generated_sql,
                    'hit_count': 0,
                    'created_at': int(time.time()),
                    'last_accessed_at': int(time.time()),
                    'ttl': ttl
                }
            )
            
            duration = time.time() - start_time
            
            logger.info(f"Cache stored", extra={
                "extra_fields": {
                    "cache_key": cache_key[:16],
                    "database_name": database_name,
                    "schema_version": schema_version,
                    "ttl_days": self.ttl_days,
                    "store_time_ms": round(duration * 1000, 2)
                }
            })
            
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Cache store error", extra={
                "extra_fields": {
                    "cache_key": cache_key[:16],
                    "database_name": database_name,
                    "error": str(e),
                    "store_time_ms": round(duration * 1000, 2)
                }
            }, exc_info=True)
            return False
    
    def get_stats(self, database_name: str) -> Dict[str, Any]:
        """
        Get cache statistics for a database
        
        Returns:
            Dictionary with cache stats
        """
        self._ensure_table_exists()
        
        try:
            response = self.table.query(
                IndexName='database-index',
                KeyConditionExpression='database_name = :db',
                ExpressionAttributeValues={
                    ':db': database_name
                }
            )
            
            items = response.get('Items', [])
            
            total_queries = len(items)
            total_hits = sum(int(item.get('hit_count', 0)) for item in items)
            
            return {
                'database_name': database_name,
                'total_cached_queries': total_queries,
                'total_cache_hits': total_hits,
                'average_hits_per_query': round(total_hits / total_queries, 2) if total_queries > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error fetching cache stats", extra={
                "extra_fields": {
                    "database_name": database_name,
                    "error": str(e)
                }
            }, exc_info=True)
            return {
                'error': str(e)
            }
