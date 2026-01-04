#!/bin/bash

# AWS RDS Aurora PostgreSQL Serverless V2 Setup
# Make sure you have AWS CLI configured with proper credentials

# Variables
DB_CLUSTER_IDENTIFIER="text2sql-cluster"
DB_INSTANCE_IDENTIFIER="text2sql-cluster-instance-1"
MASTER_USERNAME="postgres"
MASTER_PASSWORD="YourSecurePassword123"  # Change this to a secure password
DB_NAME="postgres"
REGION="ap-south-1"  # Change to your preferred region
SECURITY_GROUP_ID="sg-03f3f12f4e2bc83dc"  # Replace with your security group ID
SUBNET_GROUP_NAME="default"  # Replace with your DB subnet group name

echo "Creating Aurora Serverless V2 Cluster..."

# Create the Aurora Serverless V2 cluster
# aws rds create-db-cluster \
#     --db-cluster-identifier $DB_CLUSTER_IDENTIFIER \
#     --engine aurora-postgresql \
#     --engine-version 17.7 \
#     --master-username $MASTER_USERNAME \
#     --master-user-password $MASTER_PASSWORD \
#     --database-name $DB_NAME \
#     --vpc-security-group-ids $SECURITY_GROUP_ID \
#     --db-subnet-group-name $SUBNET_GROUP_NAME \
#     --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=1 \
#     --publicly-accessible \
#     --region $REGION

echo "Waiting for cluster to be available..."
aws rds wait db-cluster-available --db-cluster-identifier $DB_CLUSTER_IDENTIFIER --region $REGION

echo "Creating Aurora Serverless V2 Instance..."

# Create the instance in the cluster
# aws rds create-db-instance \
#     --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
#     --db-cluster-identifier $DB_CLUSTER_IDENTIFIER \
#     --db-instance-class db.serverless \
#     --engine aurora-postgresql \
#     --publicly-accessible \
#     --region $REGION

echo "Waiting for instance to be available..."
aws rds wait db-instance-available --db-instance-identifier $DB_INSTANCE_IDENTIFIER --region $REGION

echo "Getting endpoint information..."
aws rds describe-db-clusters \
    --db-cluster-identifier $DB_CLUSTER_IDENTIFIER \
    --region $REGION \
    --query 'DBClusters[0].Endpoint' \
    --output text

echo ""
echo "Setup complete!"
echo "Endpoint will be available at: $DB_CLUSTER_IDENTIFIER.<random>.us-east-1.rds.amazonaws.com"
echo "Master Username: $MASTER_USERNAME"
echo "Database Name: $DB_NAME"
echo ""
echo "IMPORTANT: Update your security group to allow inbound PostgreSQL (port 5432) from your IP"
