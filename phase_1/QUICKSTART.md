# Quick Start Guide

## Prerequisites
- Python 3.11 installed
- AWS RDS PostgreSQL database setup (see database/README.md)
- Anthropic API key

## Quick Setup (5 minutes)

### 1. Configure Backend
```bash
cd phase_1/backend
cp .env.example .env
# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required values in `.env`:
```
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PASSWORD=your-db-password
ANTHROPIC_API_KEY=sk-ant-your-api-key
```

### 2. Start All Services
```bash
cd phase_1
chmod +x start_all.sh
./start_all.sh
```

This will start:
- Backend API on http://localhost:8080
- Frontend UI on http://localhost:3000

### 3. Access the Application
Open browser: http://localhost:3000

## Login Credentials

| Team | Username | Password | Database |
|------|----------|----------|----------|
| Sales | sales | sales123 | sales_db |
| Marketing | marketing | marketing123 | marketing_db |
| Operations | operations | operations123 | operations_db |

## Example Queries

### Sales Database
- "Show me total revenue for each product"
- "List top 5 customers by total order value"
- "What are the pending orders?"
- "Show sales rep performance by territory"
- "List products with low stock (less than 50 units)"

### Marketing Database
- "Show campaign performance with conversion rates"
- "List top performing campaigns by ROI"
- "How many leads are in qualified status?"
- "What's the average cost per conversion?"
- "Show email campaign open rates"

### Operations Database
- "List all warehouses with their current capacity"
- "Show pending shipments"
- "Which suppliers have the highest ratings?"
- "Show inventory levels below reorder point"
- "List all shipments delayed by more than 2 days"

## Stopping Services

Press `Ctrl+C` in the terminal where start_all.sh is running

Or manually:
```bash
# Kill backend
pkill -f "python.*main.py"

# Kill frontend
pkill -f "python.*app.py"
```

## Troubleshooting

**Can't connect to database:**
```bash
# Test database connection
psql -h your-endpoint.rds.amazonaws.com -U postgres -d sales_db
```

**Backend error "Invalid API key":**
- Check ANTHROPIC_API_KEY in backend/.env
- Verify API key is active at https://console.anthropic.com

**Frontend shows "Network error":**
- Ensure backend is running on port 8080
- Check backend/.env configuration
- View backend logs for errors

**Port already in use:**
```bash
# Find process using port 8080
lsof -i :8080

# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

## Manual Start (if start_all.sh doesn't work)

**Terminal 1 - Backend:**
```bash
cd phase_1/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd phase_1/frontend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │────────▶│   Frontend   │────────▶│   Backend   │
│ (port 3000) │         │  FastAPI+HTML│         │   FastAPI   │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
                        ┌──────────────┐         ┌─────────────┐
                        │  Claude API  │         │  PostgreSQL │
                        │   (Sonnet)   │         │   AWS RDS   │
                        └──────────────┘         └─────────────┘
```

## File Structure

```
phase_1/
├── start_all.sh              # Start both servers
├── README.md                 # Full documentation
├── QUICKSTART.md             # This file
├── database/
│   ├── setup_rds.sh          # AWS RDS creation
│   ├── create_databases.sql  # Database creation
│   ├── *_schema.sql          # Table schemas
│   └── README.md
├── backend/
│   ├── main.py               # FastAPI app
│   ├── database.py           # DB manager
│   ├── sql_generator.py      # Claude integration
│   ├── config.py             # Configuration
│   ├── .env                  # Your credentials (create this)
│   └── requirements.txt
└── frontend/
    ├── app.py                # Frontend server
    ├── templates/
    │   ├── login.html
    │   └── dashboard.html
    ├── static/
    │   ├── styles.css
    │   ├── login.js
    │   └── dashboard.js
    └── requirements.txt
```

## Support

For issues or questions:
1. Check the main README.md
2. Review troubleshooting section above
3. Check backend logs for detailed errors
4. Verify all environment variables are set correctly
