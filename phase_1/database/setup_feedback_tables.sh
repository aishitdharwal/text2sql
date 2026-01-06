#!/bin/bash

# =====================================================
# SETUP FEEDBACK TABLES IN ALL DATABASES
# =====================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration - UPDATE THESE
DB_HOST="text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com"
DB_PORT="5432"
DB_USER="postgres"
DB_PASSWORD="YourSecurePassword123"

export PGPASSWORD="$DB_PASSWORD"

echo "Setting up feedback tables..."
echo ""

# Sales DB
echo -e "${YELLOW}Creating feedback table in sales_db...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d sales_db -f feedback_schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✓ sales_db feedback table created${NC}"
else
    echo -e "${RED}✗ Failed to create feedback table in sales_db${NC}"
fi

# Marketing DB
echo -e "${YELLOW}Creating feedback table in marketing_db...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d marketing_db -f feedback_schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✓ marketing_db feedback table created${NC}"
else
    echo -e "${RED}✗ Failed to create feedback table in marketing_db${NC}"
fi

# Operations DB
echo -e "${YELLOW}Creating feedback table in operations_db...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d operations_db -f feedback_schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✓ operations_db feedback table created${NC}"
else
    echo -e "${RED}✗ Failed to create feedback table in operations_db${NC}"
fi

unset PGPASSWORD

echo ""
echo -e "${GREEN}Feedback tables setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Restart the backend: cd ../backend && ./run.sh"
echo "2. Test the feedback feature in the dashboard"
