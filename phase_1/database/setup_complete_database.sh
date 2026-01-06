#!/bin/bash

# =====================================================
# COMPLETE DATABASE SETUP SCRIPT
# This script creates databases, schemas, and populates data
# =====================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - UPDATE THESE VALUES
DB_HOST="text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com"
DB_PORT="5432"
DB_USER="postgres"
DB_PASSWORD="YourSecurePassword123"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    echo "=================================================="
    echo "$1"
    echo "=================================================="
    echo ""
}

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    print_message "$RED" "✗ Error: psql is not installed"
    print_message "$YELLOW" "  Install it with: brew install postgresql (macOS) or apt-get install postgresql-client (Linux)"
    exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    print_message "$RED" "✗ Error: python3 is not installed"
    exit 1
fi

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

print_header "TEXT2SQL DATABASE SETUP"
print_message "$BLUE" "Host: $DB_HOST"
print_message "$BLUE" "Port: $DB_PORT"
print_message "$BLUE" "User: $DB_USER"
echo ""

# Test connection
print_message "$YELLOW" "Testing database connection..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null; then
    print_message "$GREEN" "✓ Database connection successful"
else
    print_message "$RED" "✗ Failed to connect to database"
    print_message "$YELLOW" "  Please check your connection parameters"
    exit 1
fi

# Step 1: Create databases
print_header "STEP 1: Creating Databases"
print_message "$YELLOW" "Creating sales_db, marketing_db, operations_db..."

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<EOF
-- Create databases if they don't exist
SELECT 'CREATE DATABASE sales_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sales_db')\gexec
SELECT 'CREATE DATABASE marketing_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'marketing_db')\gexec
SELECT 'CREATE DATABASE operations_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'operations_db')\gexec
EOF

print_message "$GREEN" "✓ Databases created"

# Step 2: Create schemas
print_header "STEP 2: Creating Schemas"

print_message "$YELLOW" "Creating sales_db schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d sales_db -f sales_schema.sql > /dev/null
print_message "$GREEN" "✓ sales_db schema created (6 tables)"

print_message "$YELLOW" "Creating marketing_db schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d marketing_db -f marketing_schema.sql > /dev/null
print_message "$GREEN" "✓ marketing_db schema created (5 tables)"

print_message "$YELLOW" "Creating operations_db schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d operations_db -f operations_schema.sql > /dev/null
print_message "$GREEN" "✓ operations_db schema created (6 tables)"

# Step 3: Install Python dependencies
print_header "STEP 3: Installing Python Dependencies"
print_message "$YELLOW" "Installing psycopg2-binary and Faker..."
python3 -m pip install -q psycopg2-binary Faker
print_message "$GREEN" "✓ Python dependencies installed"

# Step 4: Populate databases
print_header "STEP 4: Populating Databases with Sample Data"

print_message "$YELLOW" "Populating sales_db..."
python3 populate_sales_db.py "$DB_HOST" "$DB_USER" "$DB_PASSWORD" "$DB_PORT"
print_message "$GREEN" "✓ sales_db populated"

print_message "$YELLOW" "Populating marketing_db..."
python3 populate_marketing_db.py "$DB_HOST" "$DB_USER" "$DB_PASSWORD" "$DB_PORT"
print_message "$GREEN" "✓ marketing_db populated"

print_message "$YELLOW" "Populating operations_db..."
python3 populate_operations_db.py "$DB_HOST" "$DB_USER" "$DB_PASSWORD" "$DB_PORT"
print_message "$GREEN" "✓ operations_db populated"

# Step 5: Verify setup
print_header "STEP 5: Verifying Setup"

print_message "$YELLOW" "Checking sales_db..."
SALES_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d sales_db -t -c "SELECT COUNT(*) FROM customers;")
print_message "$GREEN" "✓ sales_db has $SALES_COUNT customers"

print_message "$YELLOW" "Checking marketing_db..."
MARKETING_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d marketing_db -t -c "SELECT COUNT(*) FROM campaigns;")
print_message "$GREEN" "✓ marketing_db has $MARKETING_COUNT campaigns"

print_message "$YELLOW" "Checking operations_db..."
OPERATIONS_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d operations_db -t -c "SELECT COUNT(*) FROM warehouses;")
print_message "$GREEN" "✓ operations_db has $OPERATIONS_COUNT warehouses"

# Cleanup
unset PGPASSWORD

print_header "SETUP COMPLETE! 🎉"
print_message "$GREEN" "All three databases are ready:"
echo ""
print_message "$BLUE" "  • sales_db      - 6 tables with sample data"
print_message "$BLUE" "  • marketing_db  - 5 tables with sample data"
print_message "$BLUE" "  • operations_db - 6 tables with sample data"
echo ""
print_message "$YELLOW" "Next steps:"
print_message "$BLUE" "  1. Update backend/.env with these database credentials"
print_message "$BLUE" "  2. Start the backend: cd ../backend && ./run.sh"
print_message "$BLUE" "  3. Start the frontend: cd ../frontend && ./run.sh"
print_message "$BLUE" "  4. Open http://localhost:3000"
echo ""
