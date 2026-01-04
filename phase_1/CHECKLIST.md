# Phase 1 - Setup Checklist

Use this checklist to ensure everything is configured correctly before running the system.

## ☐ Prerequisites

- [ ] Python 3.11 installed
  ```bash
  python3.11 --version
  ```

- [ ] pip installed and updated
  ```bash
  pip --version
  ```

- [ ] AWS CLI installed (for RDS setup)
  ```bash
  aws --version
  ```

- [ ] PostgreSQL client installed (for testing)
  ```bash
  psql --version
  ```

- [ ] Anthropic API account created
  - [ ] API key generated at https://console.anthropic.com

## ☐ Database Setup

- [ ] AWS RDS Aurora PostgreSQL instance created
  - [ ] Endpoint noted: ___________________________
  - [ ] Port: 5432 (default)
  - [ ] Master username: postgres (default)
  - [ ] Master password set: ___________________________
  - [ ] Publicly accessible: Yes
  - [ ] Security group allows inbound on port 5432

- [ ] Three databases created
  - [ ] sales_db
  - [ ] marketing_db
  - [ ] operations_db

- [ ] Schemas created in each database
  - [ ] sales_db schema loaded
  - [ ] marketing_db schema loaded
  - [ ] operations_db schema loaded

- [ ] Test connection works
  ```bash
  psql -h YOUR-ENDPOINT -U postgres -d sales_db
  ```

## ☐ Backend Configuration

- [ ] Navigate to backend directory
  ```bash
  cd phase_1/backend
  ```

- [ ] Create .env file from template
  ```bash
  cp .env.example .env
  ```

- [ ] Update .env with credentials
  - [ ] DB_HOST=your-rds-endpoint
  - [ ] DB_PASSWORD=your-password
  - [ ] ANTHROPIC_API_KEY=sk-ant-...

- [ ] Test .env file is readable
  ```bash
  cat .env
  ```

- [ ] Make run script executable
  ```bash
  chmod +x run.sh
  ```

## ☐ Frontend Configuration

- [ ] Navigate to frontend directory
  ```bash
  cd phase_1/frontend
  ```

- [ ] Make run script executable
  ```bash
  chmod +x run.sh
  ```

## ☐ Startup Scripts

- [ ] Navigate to phase_1 directory
  ```bash
  cd phase_1
  ```

- [ ] Make startup script executable
  ```bash
  chmod +x start_all.sh
  ```

## ☐ First Run

- [ ] Start both servers
  ```bash
  ./start_all.sh
  ```

- [ ] Backend starts successfully
  - [ ] No error messages in terminal
  - [ ] See "Uvicorn running on http://0.0.0.0:8080"
  - [ ] Test: http://localhost:8080 returns {"status": "healthy"}

- [ ] Frontend starts successfully
  - [ ] No error messages in terminal
  - [ ] See "Uvicorn running on http://0.0.0.0:3000"
  - [ ] Test: http://localhost:3000 shows login page

## ☐ Login Test

- [ ] Open browser: http://localhost:3000

- [ ] Test sales team login
  - [ ] Username: sales
  - [ ] Password: sales123
  - [ ] Login successful
  - [ ] Redirected to dashboard
  - [ ] Tables list loads
  - [ ] Schema panel works

- [ ] Test logout
  - [ ] Click logout button
  - [ ] Redirected to login page

## ☐ Query Generation Test

- [ ] Login as sales team

- [ ] View tables in left sidebar
  - [ ] All 6 tables visible
  - [ ] Table descriptions show

- [ ] Click on a table
  - [ ] Schema loads in right panel
  - [ ] Columns show with types
  - [ ] Descriptions display

- [ ] Test query generation
  - [ ] Enter: "Show me all customers"
  - [ ] Click "Generate SQL Query"
  - [ ] SQL appears in text area
  - [ ] Execute button becomes enabled

- [ ] Test query execution
  - [ ] Click "Execute Query"
  - [ ] Results table appears
  - [ ] Row count displays

- [ ] Test query editing
  - [ ] Manually edit generated SQL
  - [ ] Click "Execute Query"
  - [ ] Modified query runs

- [ ] Test error handling
  - [ ] Enter invalid SQL: "SELEC * FROM customers"
  - [ ] Click "Execute Query"
  - [ ] Error message displays

## ☐ All Teams Test

- [ ] Test marketing team
  - [ ] Login with marketing/marketing123
  - [ ] Dashboard loads
  - [ ] Tables list shows marketing tables
  - [ ] Generate and execute a query

- [ ] Test operations team
  - [ ] Login with operations/operations123
  - [ ] Dashboard loads
  - [ ] Tables list shows operations tables
  - [ ] Generate and execute a query

## ☐ Common Issues Checklist

If something doesn't work, check:

**Backend won't start:**
- [ ] .env file exists in backend/ directory
- [ ] All required env variables are set
- [ ] Port 8080 is not in use
- [ ] Python 3.11 is being used
- [ ] Dependencies installed (pip install -r requirements.txt)

**Frontend won't start:**
- [ ] Port 3000 is not in use
- [ ] Dependencies installed
- [ ] templates/ and static/ directories exist

**Can't login:**
- [ ] Backend is running
- [ ] Check backend terminal for errors
- [ ] Database connection works
- [ ] Credentials are correct (sales/sales123)

**Can't generate query:**
- [ ] ANTHROPIC_API_KEY is correct
- [ ] API key has credits
- [ ] Check backend logs for API errors

**Can't execute query:**
- [ ] Database connection is active
- [ ] SQL syntax is valid PostgreSQL
- [ ] Table/column names are correct

**Query fails with error:**
- [ ] Check exact error message
- [ ] Verify table exists
- [ ] Check column names spelling
- [ ] Ensure query is valid SQL

## ☐ Success Criteria

System is working correctly if:

- [ ] All three teams can login
- [ ] Tables list loads for each team
- [ ] Schemas display correctly
- [ ] Natural language queries generate SQL
- [ ] Generated SQL executes successfully
- [ ] Results display in table format
- [ ] Manual SQL edits work
- [ ] Error messages show for invalid queries
- [ ] Logout works correctly

## ☐ Ready for Demo

- [ ] All checklist items above completed
- [ ] Test queries prepared for each database
- [ ] Example questions ready
- [ ] Backend and frontend running smoothly
- [ ] No errors in console logs

---

## Quick Reference

**Start System:**
```bash
cd phase_1
./start_all.sh
```

**Stop System:**
Press Ctrl+C in the terminal

**Access Application:**
http://localhost:3000

**Check Backend API:**
http://localhost:8080

**Login Credentials:**
- sales / sales123
- marketing / marketing123
- operations / operations123

**Logs Location:**
- Backend: Terminal running start_all.sh
- Frontend: Same terminal

---

✅ Checklist complete! System ready for use.
