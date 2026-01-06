"""
FastAPI application - Main entry point with comprehensive logging
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import uuid

from config import settings, TEAM_CREDENTIALS
from database import DatabaseManager
from sql_generator import SQLGenerator
from cloudwatch_logger import setup_logging, get_logger, log_with_context
from query_cache import QueryCache

# Setup CloudWatch logging
setup_logging(
    app_name="text2sql-backend",
    log_level=settings.log_level,
    log_group=settings.cloudwatch_log_group,
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
    aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
    enable_console=settings.enable_console_logging
)
logger = get_logger(__name__)

# Initialize query cache
query_cache = None
if settings.enable_cache:
    try:
        query_cache = QueryCache(
            table_name=settings.cache_table_name,
            region_name=settings.aws_region,
            ttl_days=settings.cache_ttl_days,
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None
        )
        logger.info("Query cache enabled", extra={
            "extra_fields": {
                "cache_table": settings.cache_table_name,
                "ttl_days": settings.cache_ttl_days
            }
        })
    except Exception as e:
        logger.warning(f"Failed to initialize query cache, continuing without cache", extra={
            "extra_fields": {"error": str(e)}
        })
        query_cache = None
else:
    logger.info("Query cache disabled")

# Log application startup
logger.info("Starting Text2SQL Backend Application", extra={
    "extra_fields": {
        "db_host": settings.db_host,
        "db_port": settings.db_port,
        "app_port": settings.app_port
    }
})

# Initialize FastAPI app
app = FastAPI(
    title="Text2SQL API",
    description="Natural language to SQL query generator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# Store active sessions (in production, use Redis or similar)
active_sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    team: Optional[str] = None
    database: Optional[str] = None
    session_id: Optional[str] = None

class QueryRequest(BaseModel):
    session_id: str
    natural_language_query: str

class ExecuteRequest(BaseModel):
    session_id: str
    sql_query: str

class FeedbackRequest(BaseModel):
    session_id: str
    natural_language_query: str
    generated_sql: str
    rating: str  # 'thumbs_up' or 'thumbs_down'
    feedback_comment: Optional[str] = None

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log incoming request
    log_with_context(
        logger, "info", f"Incoming request: {request.method} {request.url.path}",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        log_with_context(
            logger, "info", f"Request completed: {request.method} {request.url.path}",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2)
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path}", extra={
            "extra_fields": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e)
            }
        }, exc_info=True)
        raise

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "Text2SQL API"}

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and create session
    """
    username = request.username.lower()
    
    log_with_context(
        logger, "info", "Login attempt",
        username=username,
        attempt_timestamp=time.time()
    )
    
    # Validate credentials
    if username not in TEAM_CREDENTIALS:
        logger.warning(f"Login failed: Invalid username", extra={
            "extra_fields": {"username": username, "reason": "user_not_found"}
        })
        raise HTTPException(status_code=401, detail="Invalid username")
    
    if TEAM_CREDENTIALS[username]["password"] != request.password:
        logger.warning(f"Login failed: Invalid password", extra={
            "extra_fields": {"username": username, "reason": "invalid_password"}
        })
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create session
    session_id = str(uuid.uuid4())
    database_name = TEAM_CREDENTIALS[username]["database"]
    
    logger.info(f"Creating session for user", extra={
        "extra_fields": {
            "username": username,
            "database": database_name,
            "session_id": session_id
        }
    })
    
    # Initialize database connection
    try:
        db_manager = DatabaseManager(database_name)
        db_manager.connect()
        
        # Store session
        active_sessions[session_id] = {
            "team": username,
            "database": database_name,
            "db_manager": db_manager,
            "created_at": time.time()
        }
        
        logger.info(f"Login successful", extra={
            "extra_fields": {
                "username": username,
                "database": database_name,
                "session_id": session_id,
                "active_sessions_count": len(active_sessions)
            }
        })
        
        return LoginResponse(
            success=True,
            message="Login successful",
            team=username,
            database=database_name,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Login failed: Database connection error", extra={
            "extra_fields": {
                "username": username,
                "database": database_name,
                "error": str(e)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/logout")
async def logout(session_id: str):
    """
    End user session and close database connection
    """
    log_with_context(
        logger, "info", "Logout request",
        session_id=session_id
    )
    
    if session_id in active_sessions:
        session_info = active_sessions[session_id]
        team = session_info.get("team")
        
        try:
            db_manager = session_info["db_manager"]
            db_manager.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting database during logout", extra={
                "extra_fields": {
                    "session_id": session_id,
                    "team": team,
                    "error": str(e)
                }
            }, exc_info=True)
        
        del active_sessions[session_id]
        
        logger.info(f"Logout successful", extra={
            "extra_fields": {
                "session_id": session_id,
                "team": team,
                "active_sessions_count": len(active_sessions)
            }
        })
        
        return {"success": True, "message": "Logged out successfully"}
    
    logger.warning(f"Logout failed: Invalid session", extra={
        "extra_fields": {"session_id": session_id}
    })
    return {"success": False, "message": "Invalid session"}

@app.get("/api/tables")
async def get_tables(session_id: str):
    """
    Get list of all tables in the user's database
    """
    log_with_context(
        logger, "info", "Get tables request",
        session_id=session_id
    )
    
    if session_id not in active_sessions:
        logger.warning("Tables request failed: Invalid session", extra={
            "extra_fields": {"session_id": session_id}
        })
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        session_info = active_sessions[session_id]
        db_manager = session_info["db_manager"]
        
        tables = db_manager.get_tables()
        
        logger.info(f"Tables retrieved successfully", extra={
            "extra_fields": {
                "session_id": session_id,
                "team": session_info["team"],
                "database": session_info["database"],
                "table_count": len(tables)
            }
        })
        
        return {"success": True, "tables": tables}
    except Exception as e:
        logger.error(f"Error fetching tables", extra={
            "extra_fields": {
                "session_id": session_id,
                "error": str(e)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
async def get_schema(session_id: str, table_name: Optional[str] = None):
    """
    Get schema for a specific table or all tables
    """
    log_with_context(
        logger, "info", "Get schema request",
        session_id=session_id,
        table_name=table_name
    )
    
    if session_id not in active_sessions:
        logger.warning("Schema request failed: Invalid session", extra={
            "extra_fields": {"session_id": session_id}
        })
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        session_info = active_sessions[session_id]
        db_manager = session_info["db_manager"]
        
        if table_name:
            schema = db_manager.get_table_schema(table_name)
            logger.info(f"Table schema retrieved", extra={
                "extra_fields": {
                    "session_id": session_id,
                    "table_name": table_name,
                    "column_count": len(schema)
                }
            })
            return {"success": True, "table": table_name, "schema": schema}
        else:
            schemas = db_manager.get_all_schemas()
            logger.info(f"All schemas retrieved", extra={
                "extra_fields": {
                    "session_id": session_id,
                    "team": session_info["team"],
                    "table_count": len(schemas)
                }
            })
            return {"success": True, "schemas": schemas}
    except Exception as e:
        logger.error(f"Error fetching schema", extra={
            "extra_fields": {
                "session_id": session_id,
                "table_name": table_name,
                "error": str(e)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-query")
async def generate_query(request: QueryRequest):
    """
    Generate SQL query from natural language
    """
    log_with_context(
        logger, "info", "Generate query request",
        session_id=request.session_id,
        query_length=len(request.natural_language_query)
    )
    
    if request.session_id not in active_sessions:
        logger.warning("Query generation failed: Invalid session", extra={
            "extra_fields": {"session_id": request.session_id}
        })
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    start_time = time.time()
    
    try:
        session = active_sessions[request.session_id]
        db_manager = session["db_manager"]
        
        logger.debug(f"Fetching database schemas", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "database": session["database"]
            }
        })
        
        # Get database schema
        schemas = db_manager.get_all_schemas()
        
        # Check cache first
        cached_sql = None
        if query_cache:
            cached_sql = query_cache.get(
                natural_language_query=request.natural_language_query,
                database_name=session["database"],
                schemas=schemas
            )
        
        if cached_sql:
            duration = time.time() - start_time
            
            logger.info(f"SQL query returned from cache", extra={
                "extra_fields": {
                    "session_id": request.session_id,
                    "team": session["team"],
                    "cached": True,
                    "generation_time_ms": round(duration * 1000, 2)
                }
            })
            
            return {
                "success": True,
                "sql_query": cached_sql,
                "cached": True
            }
        
        logger.debug(f"Calling Claude API for SQL generation", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "natural_language_query": request.natural_language_query[:100],  # First 100 chars
                "table_count": len(schemas)
            }
        })
        
        # Generate SQL using Claude
        sql_gen = SQLGenerator()
        
        result = sql_gen.generate_sql(
            natural_language_query=request.natural_language_query,
            database_schema=schemas,
            database_name=session["database"],
            user_id=session["team"],
            session_id=request.session_id
        )
        
        duration = time.time() - start_time
        
        if result.get("success"):
            # Store in cache
            if query_cache and result.get("sql_query"):
                query_cache.put(
                    natural_language_query=request.natural_language_query,
                    database_name=session["database"],
                    schemas=schemas,
                    generated_sql=result["sql_query"]
                )
            
            logger.info(f"SQL query generated successfully", extra={
                "extra_fields": {
                    "session_id": request.session_id,
                    "team": session["team"],
                    "query_length": len(result.get("sql_query", "")),
                    "cached": False,
                    "generation_time_ms": round(duration * 1000, 2)
                }
            })
            
            # Add cached flag to response
            result["cached"] = False
        else:
            logger.error(f"SQL generation failed", extra={
                "extra_fields": {
                    "session_id": request.session_id,
                    "error": result.get("error"),
                    "generation_time_ms": round(duration * 1000, 2)
                }
            })
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating query", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "error": str(e),
                "generation_time_ms": round(duration * 1000, 2)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-query")
async def execute_query(request: ExecuteRequest):
    """
    Execute SQL query and return results
    """
    log_with_context(
        logger, "info", "Execute query request",
        session_id=request.session_id,
        sql_query_length=len(request.sql_query)
    )
    
    if request.session_id not in active_sessions:
        logger.warning("Query execution failed: Invalid session", extra={
            "extra_fields": {"session_id": request.session_id}
        })
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    start_time = time.time()
    
    try:
        session_info = active_sessions[request.session_id]
        db_manager = session_info["db_manager"]
        
        logger.debug(f"Executing SQL query", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "team": session_info["team"],
                "database": session_info["database"],
                "sql_query": request.sql_query[:200]  # First 200 chars for security
            }
        })
        
        result = db_manager.execute_query(request.sql_query)
        
        duration = time.time() - start_time
        
        if result.get("success"):
            logger.info(f"Query executed successfully", extra={
                "extra_fields": {
                    "session_id": request.session_id,
                    "team": session_info["team"],
                    "row_count": result.get("row_count", result.get("rows_affected", 0)),
                    "execution_time_ms": round(duration * 1000, 2)
                }
            })
        else:
            logger.warning(f"Query execution failed", extra={
                "extra_fields": {
                    "session_id": request.session_id,
                    "team": session_info["team"],
                    "error": result.get("error"),
                    "execution_time_ms": round(duration * 1000, 2)
                }
            })
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error executing query", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "error": str(e),
                "execution_time_ms": round(duration * 1000, 2)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback on generated SQL query
    """
    log_with_context(
        logger, "info", "Feedback submission",
        session_id=request.session_id,
        rating=request.rating
    )
    
    if request.session_id not in active_sessions:
        logger.warning("Feedback submission failed: Invalid session", extra={
            "extra_fields": {"session_id": request.session_id}
        })
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Validate rating
    if request.rating not in ['thumbs_up', 'thumbs_down']:
        raise HTTPException(status_code=400, detail="Invalid rating. Must be 'thumbs_up' or 'thumbs_down'")
    
    try:
        session_info = active_sessions[request.session_id]
        db_manager = session_info["db_manager"]
        team = session_info["team"]
        
        # Insert feedback into database
        feedback_sql = """
            INSERT INTO query_feedback 
            (session_id, team_name, natural_language_query, generated_sql, rating, feedback_comment)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING feedback_id
        """
        
        result = db_manager.execute_insert(
            feedback_sql,
            (
                request.session_id,
                team,
                request.natural_language_query,
                request.generated_sql,
                request.rating,
                request.feedback_comment
            )
        )
        
        if not result['success']:
            raise Exception(result.get('error', 'Unknown error'))
        
        feedback_id = result['id']
        
        logger.info(f"Feedback submitted successfully", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "team": team,
                "rating": request.rating,
                "feedback_id": feedback_id,
                "has_comment": bool(request.feedback_comment)
            }
        })
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback", extra={
            "extra_fields": {
                "session_id": request.session_id,
                "error": str(e)
            }
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info("Application startup complete", extra={
        "extra_fields": {
            "app_name": "Text2SQL Backend",
            "version": "1.0.0",
            "port": settings.app_port
        }
    })

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutdown initiated", extra={
        "extra_fields": {
            "active_sessions_count": len(active_sessions)
        }
    })
    
    # Close all active database connections
    for session_id, session_info in active_sessions.items():
        try:
            session_info["db_manager"].disconnect()
            logger.info(f"Closed database connection for session", extra={
                "extra_fields": {
                    "session_id": session_id,
                    "team": session_info.get("team")
                }
            })
        except Exception as e:
            logger.error(f"Error closing database connection", extra={
                "extra_fields": {
                    "session_id": session_id,
                    "error": str(e)
                }
            }, exc_info=True)
    
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server", extra={
        "extra_fields": {
            "host": settings.app_host,
            "port": settings.app_port
        }
    })
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
