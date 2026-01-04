# Database Setup Guide

## Part 1: AWS RDS Aurora PostgreSQL Setup

### Step 1: Create RDS Instance

1. Update the variables in `setup_rds.sh`:
   - `SECURITY_GROUP_ID`: Your VPC security group ID
   - `SUBNET_GROUP_NAME`: Your DB subnet group name
   - `REGION`: Your preferred AWS region
   - `MASTER_PASSWORD`: Choose a strong password

2. Make the script executable and run it:
```bash
chmod +x setup_rds.sh
./setup_rds.sh
```

3. **Important**: Update your security group to allow inbound traffic on port 5432 from your IP address.

4. Note down the RDS endpoint from the output.

### Step 2: Create Databases

Connect to your RDS instance using psql:
```bash
psql -h your-rds-endpoint.rds.amazonaws.com -U postgres -d postgres
```

Run the database creation script:
```bash
\i create_databases.sql
```

### Step 3: Create Schemas

For each database, run the corresponding schema file:

**Sales Database:**
```bash
psql -h your-rds-endpoint.rds.amazonaws.com -U postgres -d sales_db -f sales_schema.sql
```

**Marketing Database:**
```bash
psql -h your-rds-endpoint.rds.amazonaws.com -U postgres -d marketing_db -f marketing_schema.sql
```

**Operations Database:**
```bash
psql -h your-rds-endpoint.rds.amazonaws.com -U postgres -d operations_db -f operations_schema.sql
```

### Step 4: Populate Sample Data

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Update the `DB_CONFIG` in each populate script with your RDS endpoint and password:
- `populate_sales_db.py`
- (Marketing and Operations scripts coming in next parts)

Run the population scripts:
```bash
python populate_sales_db.py
```

### Database Overview

**sales_db** - 6 tables with 20 rows each:
- customers
- products  
- sales_reps
- orders (with order_items)
- revenue

**marketing_db** - 5 tables (schema ready, data population coming next):
- campaigns
- leads
- ad_spend
- conversions
- email_metrics

**operations_db** - 6 tables (schema ready, data population coming next):
- warehouses
- suppliers
- inventory
- shipments
- logistics
- purchase_orders

### Next Steps

Part 1 is complete! The sales database is fully populated. 

In the next parts, we'll:
1. Populate marketing and operations databases
2. Build the FastAPI backend
3. Create the frontend UI
4. Integrate Claude API for SQL generation
