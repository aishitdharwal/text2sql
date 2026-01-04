"""
FastAPI application - Main entry point
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from config import settings, TEAM_CREDENTIALS
from database import DatabaseManager
from sql_generator import SQLGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Text2SQL API"}

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and create session
    """
    username = request.username.lower()
    password = request.password
    
    # Validate credentials
    if username not in TEAM_CREDENTIALS:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    if TEAM_CREDENTIALS[username]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create session
    import uuid
    session_id = str(uuid.uuid4())
    database_name = TEAM_CREDENTIALS[username]["database"]
    
    # Initialize database connection
    try:
        db_manager = DatabaseManager(database_name)
        db_manager.connect()
        
        # Store session
        active_sessions[session_id] = {
            "team": username,
            "database": database_name,
            "db_manager": db_manager
        }
        
        logger.info(f"User {username} logged in successfully")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            team=username,
            database=database_name,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/logout")
async def logout(session_id: str):
    """
    End user session and close database connection
    """
    if session_id in active_sessions:
        db_manager = active_sessions[session_id]["db_manager"]
        db_manager.disconnect()
        del active_sessions[session_id]
        return {"success": True, "message": "Logged out successfully"}
    
    return {"success": False, "message": "Invalid session"}

@app.get("/api/tables")
async def get_tables(session_id: str):
    """
    Get list of all tables in the user's database
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        db_manager = active_sessions[session_id]["db_manager"]
        tables = db_manager.get_tables()
        return {"success": True, "tables": tables}
    except Exception as e:
        logger.error(f"Error fetching tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
async def get_schema(session_id: str, table_name: Optional[str] = None):
    """
    Get schema for a specific table or all tables
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        db_manager = active_sessions[session_id]["db_manager"]
        
        if table_name:
            schema = db_manager.get_table_schema(table_name)
            return {"success": True, "table": table_name, "schema": schema}
        else:
            schemas = db_manager.get_all_schemas()
            return {"success": True, "schemas": schemas}
    except Exception as e:
        logger.error(f"Error fetching schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-query")
async def generate_query(request: QueryRequest):
    """
    Generate SQL query from natural language
    """
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        session = active_sessions[request.session_id]
        db_manager = session["db_manager"]
        
        # Get database schema
        schemas = db_manager.get_all_schemas()
        
        # Generate SQL using Claude
        sql_gen = SQLGenerator()
        result = sql_gen.generate_sql(
            natural_language_query=request.natural_language_query,
            database_schema=schemas,
            database_name=session["database"]
        )
        
        return result
    except Exception as e:
        logger.error(f"Error generating query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-query")
async def execute_query(request: ExecuteRequest):
    """
    Execute SQL query and return results
    """
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    try:
        db_manager = active_sessions[request.session_id]["db_manager"]
        result = db_manager.execute_query(request.sql_query)
        return result
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
