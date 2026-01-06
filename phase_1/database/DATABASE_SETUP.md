# Database Setup - Complete Guide

## 🚀 Quick Setup (Recommended)

Run this single script to set up everything:

```bash
cd database

# Update the script with your credentials first!
# Edit setup_complete_database.sh and update:
# - DB_HOST
# - DB_PASSWORD

chmod +x setup_complete_database.sh
./setup_complete_database.sh
```

This script will:
1. Create all 3 databases (sales_db, marketing_db, operations_db)
2. Create all schemas (17 tables total)
3. Install Python dependencies
4. Populate all databases with sample data
5. Verify the setup

---

## 📋 What Gets Created

### Sales Database (sales_db)
**6 tables with relationships:**
- `customers` - 50 customer records
- `products` - 30 product records  
- `sales_reps` - 20 sales representatives
- `orders` - 100 orders
- `order_items` - Order line items
- `revenue` - Revenue tracking with profit margins

### Marketing Database (marketing_db)
**5 tables with campaign data:**
- `campaigns` - 30 marketing campaigns
- `leads` - 200 leads
- `ad_spend` - Daily ad spend records
- `conversions` - Lead conversion tracking
- `email_metrics` - Email campaign performance

### Operations Database (operations_db)
**6 tables for logistics:**
- `warehouses` - 10 warehouse locations
- `suppliers` - 20 suppliers
- `inventory` - ~120 inventory records
- `shipments` - 100 shipment records
- `logistics` - Shipment tracking events
- `purchase_orders` - 50 purchase orders

---

## 🔧 Manual Setup (Step by Step)

If you prefer to run steps individually:

### Step 1: Configure Database Credentials

Update credentials in each populate script:
- `populate_sales_db.py`
- `populate_marketing_db.py`
- `populate_operations_db.py`

Or pass as command-line arguments (recommended for security).

### Step 2: Create Databases

```bash
# Connect to your PostgreSQL instance
psql -h YOUR_HOST -U postgres

# In psql:
CREATE DATABASE sales_db;
CREATE DATABASE marketing_db;
CREATE DATABASE operations_db;
\q
```

### Step 3: Create Schemas

```bash
# Sales DB
psql -h YOUR_HOST -U postgres -d sales_db -f sales_schema.sql

# Marketing DB
psql -h YOUR_HOST -U postgres -d marketing_db -f marketing_schema.sql

# Operations DB
psql -h YOUR_HOST -U postgres -d operations_db -f operations_schema.sql
```

### Step 4: Install Python Dependencies

```bash
pip install psycopg2-binary Faker
```

### Step 5: Populate Databases

```bash
# With command-line arguments (recommended)
python3 populate_sales_db.py YOUR_HOST postgres YOUR_PASSWORD 5432
python3 populate_marketing_db.py YOUR_HOST postgres YOUR_PASSWORD 5432
python3 populate_operations_db.py YOUR_HOST postgres YOUR_PASSWORD 5432

# Or with hardcoded credentials in scripts
python3 populate_sales_db.py
python3 populate_marketing_db.py
python3 populate_operations_db.py
```

### Step 6: Verify Setup

```bash
# Check sales_db
psql -h YOUR_HOST -U postgres -d sales_db -c "SELECT COUNT(*) FROM customers;"

# Check marketing_db
psql -h YOUR_HOST -U postgres -d marketing_db -c "SELECT COUNT(*) FROM campaigns;"

# Check operations_db
psql -h YOUR_HOST -U postgres -d operations_db -c "SELECT COUNT(*) FROM warehouses;"
```

---

## 📁 Files in This Directory

**Schema Files:**
- `sales_schema.sql` - Sales database schema (6 tables)
- `marketing_schema.sql` - Marketing database schema (5 tables)
- `operations_schema.sql` - Operations database schema (6 tables)

**Population Scripts:**
- `populate_sales_db.py` - Generate sample sales data
- `populate_marketing_db.py` - Generate sample marketing data
- `populate_operations_db.py` - Generate sample operations data

**Setup Scripts:**
- `setup_complete_database.sh` - Master setup script (RECOMMENDED)
- `create_databases.sql` - SQL to create databases

**Configuration:**
- `requirements.txt` - Python dependencies

---

## 🔍 Verification Queries

After setup, test with these queries:

**Sales DB:**
```sql
-- Total revenue
SELECT SUM(gross_revenue) FROM revenue;

-- Top customers
SELECT first_name, last_name, COUNT(*) as order_count 
FROM customers c 
JOIN orders o ON c.customer_id = o.customer_id 
GROUP BY c.customer_id, first_name, last_name 
ORDER BY order_count DESC 
LIMIT 5;
```

**Marketing DB:**
```sql
-- Active campaigns
SELECT COUNT(*) FROM campaigns WHERE status = 'active';

-- Lead conversion rate
SELECT 
  lead_status, 
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM leads 
GROUP BY lead_status;
```

**Operations DB:**
```sql
-- Low inventory items
SELECT w.warehouse_name, i.product_id, i.quantity_on_hand, i.reorder_level
FROM inventory i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.quantity_on_hand < i.reorder_level;

-- Shipment status summary
SELECT shipment_status, COUNT(*) 
FROM shipments 
GROUP BY shipment_status;
```

---

## 🔒 Security Notes

**For Production:**
- Never hardcode credentials in scripts
- Use environment variables or secure vaults
- Implement proper user permissions
- Enable SSL/TLS for database connections
- Use read-only users for query-only access

**For Development:**
- Keep test credentials separate from production
- Don't commit credentials to version control
- Use `.env` files (already in `.gitignore`)

---

## 🐛 Troubleshooting

**Connection Failed:**
- Verify database host is accessible
- Check security group allows your IP
- Confirm credentials are correct
- Ensure PostgreSQL port (5432) is open

**Schema Creation Failed:**
- Make sure database was created first
- Check you're connected to correct database
- Verify you have CREATE privileges

**Population Script Failed:**
- Install dependencies: `pip install psycopg2-binary`
- Check database credentials in script
- Ensure schemas were created successfully
- Verify sufficient disk space

**Missing Data:**
- Run population scripts in order
- Check for error messages in output
- Verify foreign key relationships

---

## 📊 Data Summary

After successful setup:

| Database | Tables | Sample Records |
|----------|--------|----------------|
| sales_db | 6 | 50 customers, 30 products, 100 orders |
| marketing_db | 5 | 30 campaigns, 200 leads, ad spend data |
| operations_db | 6 | 10 warehouses, 20 suppliers, 100 shipments |

**Total:** 17 tables with realistic, interconnected data ready for testing.

---

## 🎯 Next Steps

After database setup:
1. Update `../backend/.env` with database credentials
2. Start the backend: `cd ../backend && ./run.sh`
3. Start the frontend: `cd ../frontend && ./run.sh`
4. Test queries at http://localhost:3000

---

**Need help?** Check the troubleshooting section or refer to the main README.md
