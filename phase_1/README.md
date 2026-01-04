# Text2SQL - Phase 1 POC

Natural Language to SQL Query Generator with team-based database access.

## Project Structure

```
phase_1/
├── database/           # Database setup and schema files
├── backend/           # FastAPI backend API (port 8080)
└── frontend/          # FastAPI + HTML frontend (port 3000)
```

## Features

✅ Team-based authentication (Sales, Marketing, Operations)  
✅ Database-specific access control  
✅ View all tables and schemas with descriptions  
✅ Natural language to SQL conversion using Claude API  
✅ Manual SQL query editing  
✅ Query execution and results display  
✅ Error handling and display  

## Setup Instructions

### 1. Database Setup

Navigate to the database directory:
```bash
cd phase_1/database
```

Follow the instructions in `database/README.md`:
1. Create AWS RDS Aurora PostgreSQL instance
2. Create the three databases (sales_db, marketing_db, operations_db)
3. Run schema files to create tables

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd phase_1/backend
```

Create `.env` file from template:
```bash
cp .env.example .env
```

Update `.env` with your credentials:
```env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=YourSecurePassword123!
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
APP_HOST=0.0.0.0
APP_PORT=8080
```

Make the run script executable and start the backend:
```bash
chmod +x run.sh
./run.sh
```

The backend API will be available at `http://localhost:8080`

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:
```bash
cd phase_1/frontend
```

Make the run script executable and start the frontend:
```bash
chmod +x run.sh
./run.sh
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`

2. Login with team credentials:
   - **Sales Team**: username: `sales`, password: `sales123`
   - **Marketing Team**: username: `marketing`, password: `marketing123`
   - **Operations Team**: username: `operations`, password: `operations123`

3. Browse tables and schemas in the left sidebar

4. Ask questions in natural language, for example:
   - "Show me total revenue by product category"
   - "List top 10 customers by order value"
   - "What are the most popular products?"
   - "Show me campaign performance metrics"
   - "List all pending shipments"

5. Click "Generate SQL Query" to convert your question to SQL

6. Review and optionally edit the generated SQL query

7. Click "Execute Query" to run the query and see results

## Team Access

Each team has access to their specific database:

- **Sales Team** → `sales_db`
  - customers, products, sales_reps, orders, order_items, revenue

- **Marketing Team** → `marketing_db`
  - campaigns, leads, ad_spend, conversions, email_metrics

- **Operations Team** → `operations_db`
  - warehouses, suppliers, inventory, shipments, logistics, purchase_orders

## API Endpoints

**Backend API (port 8080):**

- `POST /api/login` - Authenticate and create session
- `POST /api/logout` - End session
- `GET /api/tables` - Get all tables in user's database
- `GET /api/schema` - Get table schemas (all or specific table)
- `POST /api/generate-query` - Generate SQL from natural language
- `POST /api/execute-query` - Execute SQL query

**Frontend (port 3000):**

- `GET /` - Login page
- `GET /dashboard` - Main dashboard

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: FastAPI, HTML, CSS, JavaScript
- **Database**: PostgreSQL (AWS RDS Aurora Serverless V2)
- **AI**: Claude API (claude-sonnet-4-5-20250929)
- **Authentication**: Session-based with hardcoded credentials

## Notes

- This is a POC (Proof of Concept) implementation
- Credentials are hardcoded for demo purposes
- No persistent session storage (sessions reset on server restart)
- CORS is enabled for all origins in development
- Error messages are displayed directly to users

## Troubleshooting

**Backend won't start:**
- Check if `.env` file exists and has correct values
- Verify database connection (host, port, credentials)
- Ensure port 8080 is not already in use

**Frontend won't start:**
- Ensure port 3000 is not already in use
- Check that backend is running on port 8080

**Login fails:**
- Check backend logs for database connection errors
- Verify RDS instance is publicly accessible
- Check security group allows inbound traffic on port 5432

**Query generation fails:**
- Verify ANTHROPIC_API_KEY is correct in .env
- Check backend logs for Claude API errors
- Ensure you have API credits available

**Query execution fails:**
- Check if the generated SQL is valid PostgreSQL syntax
- Verify table and column names exist in the database
- Look at the error message for specific SQL errors

## Next Steps

Phase 1 is complete! Future enhancements could include:
- Query history and saved queries
- Export results to CSV/Excel
- Query performance metrics
- Advanced filtering and pagination
- User management and real authentication
- Rate limiting and query timeouts
- Caching for schema information
- Multi-tenant support
