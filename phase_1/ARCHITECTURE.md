# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                │
│                         http://localhost:3000                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND SERVER (Port 3000)                      │
│                           FastAPI + Jinja2                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Templates:                    Static Files:                            │
│  • login.html                  • styles.css                             │
│  • dashboard.html              • login.js                               │
│                                • dashboard.js                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ REST API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND API (Port 8080)                         │
│                              FastAPI                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Endpoints:                     Core Modules:                           │
│  POST   /api/login              • main.py                              │
│  POST   /api/logout             • database.py                          │
│  GET    /api/tables             • sql_generator.py                     │
│  GET    /api/schema             • config.py                            │
│  POST   /api/generate-query                                            │
│  POST   /api/execute-query                                             │
│                                                                         │
│  Session Management:                                                    │
│  {                                                                      │
│    session_id: "uuid",                                                 │
│    team: "sales",                                                      │
│    database: "sales_db",                                               │
│    db_manager: DatabaseManager()                                       │
│  }                                                                      │
│                                                                         │
└──────────┬────────────────────────────────┬─────────────────────────────┘
           │                                │
           │                                │
           ▼                                ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    CLAUDE API            │    │    AWS RDS POSTGRESQL    │
│  (Anthropic)             │    │   Aurora Serverless V2   │
├──────────────────────────┤    ├──────────────────────────┤
│                          │    │                          │
│  Model:                  │    │  Databases:              │
│  claude-sonnet-4-5       │    │  • sales_db              │
│                          │    │  • marketing_db          │
│  Input:                  │    │  • operations_db         │
│  • NL Query              │    │                          │
│  • DB Schema             │    │  Connection per team:    │
│  • Table Descriptions    │    │  sales → sales_db        │
│                          │    │  marketing → marketing_db│
│  Output:                 │    │  operations → ops_db     │
│  • SQL Query             │    │                          │
│                          │    │  Features:               │
└──────────────────────────┘    │  • Foreign Keys          │
                                │  • Indexes               │
                                │  • Comments              │
                                │  • ~17 tables total      │
                                └──────────────────────────┘


DATA FLOW DIAGRAM:
==================

1. LOGIN FLOW
   User → Frontend → Backend → PostgreSQL
   ↓
   Backend creates session with team's DB connection
   ↓
   Frontend stores session_id
   ↓
   Redirect to Dashboard


2. SCHEMA LOADING FLOW
   Dashboard loads → GET /api/tables → PostgreSQL
   ↓
   Returns all tables with descriptions
   ↓
   GET /api/schema → PostgreSQL
   ↓
   Returns all table schemas with column info
   ↓
   Frontend displays in sidebar and schema panel


3. QUERY GENERATION FLOW
   User types question
   ↓
   POST /api/generate-query
   ↓
   Backend → Claude API with:
     • Natural language query
     • Complete database schema
     • Table/column descriptions
   ↓
   Claude generates SQL
   ↓
   Backend returns SQL to frontend
   ↓
   Frontend displays in editable textarea


4. QUERY EXECUTION FLOW
   User clicks "Execute" (with generated or edited SQL)
   ↓
   POST /api/execute-query
   ↓
   Backend executes SQL on PostgreSQL
   ↓
   Results returned as JSON
   ↓
   Frontend renders results table
   ↓
   OR displays error message if query fails


AUTHENTICATION FLOW:
====================

┌──────────┐
│  User    │
└────┬─────┘
     │
     │ Selects team: "sales"
     │ Enters password: "sales123"
     │
     ▼
┌──────────────────┐
│  Backend         │
├──────────────────┤
│ 1. Validate      │─── Check TEAM_CREDENTIALS dict
│    credentials   │
│                  │
│ 2. Generate      │─── UUID session_id
│    session       │
│                  │
│ 3. Connect to    │─── PostgreSQL: sales_db
│    team DB       │
│                  │
│ 4. Store in      │─── active_sessions[session_id] = {
│    memory        │       team: "sales",
│                  │       database: "sales_db",
│                  │       db_manager: DatabaseManager()
│                  │     }
└──────────────────┘


SESSION STRUCTURE:
==================

active_sessions = {
  "uuid-1": {
    "team": "sales",
    "database": "sales_db",
    "db_manager": DatabaseManager(sales_db)
  },
  "uuid-2": {
    "team": "marketing", 
    "database": "marketing_db",
    "db_manager": DatabaseManager(marketing_db)
  },
  "uuid-3": {
    "team": "operations",
    "database": "operations_db", 
    "db_manager": DatabaseManager(operations_db)
  }
}


TEAM → DATABASE MAPPING:
=========================

┌──────────┐      ┌─────────────┐      ┌─────────────────┐
│  sales   │─────→│  sales_db   │─────→│ 6 tables:       │
└──────────┘      └─────────────┘      │ • customers     │
                                        │ • products      │
                                        │ • sales_reps    │
                                        │ • orders        │
                                        │ • order_items   │
                                        │ • revenue       │
                                        └─────────────────┘

┌──────────┐      ┌─────────────┐      ┌─────────────────┐
│marketing │─────→│ marketing_db│─────→│ 5 tables:       │
└──────────┘      └─────────────┘      │ • campaigns     │
                                        │ • leads         │
                                        │ • ad_spend      │
                                        │ • conversions   │
                                        │ • email_metrics │
                                        └─────────────────┘

┌──────────┐      ┌─────────────┐      ┌─────────────────┐
│operations│─────→│operations_db│─────→│ 6 tables:       │
└──────────┘      └─────────────┘      │ • warehouses    │
                                        │ • suppliers     │
                                        │ • inventory     │
                                        │ • shipments     │
                                        │ • logistics     │
                                        │ • purchase_ord. │
                                        └─────────────────┘


TECHNOLOGY STACK:
=================

┌─────────────────────────────────────────────────────────┐
│                    FRONTEND STACK                        │
├─────────────────────────────────────────────────────────┤
│  • FastAPI (server)                                     │
│  • Jinja2 (templating)                                  │
│  • HTML5                                                │
│  • CSS3 (responsive design, gradients)                  │
│  • Vanilla JavaScript (no frameworks)                   │
│  • Fetch API (AJAX requests)                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    BACKEND STACK                         │
├─────────────────────────────────────────────────────────┤
│  • FastAPI (web framework)                              │
│  • Python 3.11                                          │
│  • Pydantic (data validation)                           │
│  • psycopg2 (PostgreSQL driver)                         │
│  • anthropic (Claude API client)                        │
│  • uvicorn (ASGI server)                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   DATABASE STACK                         │
├─────────────────────────────────────────────────────────┤
│  • PostgreSQL 15.4                                      │
│  • AWS RDS Aurora Serverless V2                         │
│  • 3 databases, 17 tables                               │
│  • Foreign keys, indexes, comments                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      AI STACK                            │
├─────────────────────────────────────────────────────────┤
│  • Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)      │
│  • Anthropic API                                        │
│  • Text to SQL generation                               │
└─────────────────────────────────────────────────────────┘
```
