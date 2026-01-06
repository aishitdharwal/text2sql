# CloudWatch Logging Setup Guide

## Overview

The Text2SQL backend now uses **AWS CloudWatch Logs** instead of local file logging. This provides centralized, scalable logging with powerful search and monitoring capabilities.

## What Changed

### Before (Local File Logging)
- ❌ Logs stored in `backend/logs/` directory
- ❌ Manual log rotation with size limits
- ❌ Difficult to aggregate logs from multiple instances
- ❌ No built-in monitoring or alerts

### After (CloudWatch Logging)
- ✅ Logs sent to AWS CloudWatch Logs
- ✅ Automatic log retention and management
- ✅ Centralized logs from all instances
- ✅ Built-in search, filtering, and metrics
- ✅ Easy integration with CloudWatch Alarms
- ✅ Optional console logging for development

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt  # Now includes boto3
```

### 2. Configure Environment Variables

Update your `.env` file:

```bash
# CloudWatch Logging Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-access-key-id        # Or leave empty to use IAM role
AWS_SECRET_ACCESS_KEY=your-secret-key        # Or leave empty to use IAM role
CLOUDWATCH_LOG_GROUP=/aws/text2sql/backend
ENABLE_CONSOLE_LOGGING=true                  # Set to false in production
LOG_LEVEL=INFO
```

### 3. Start the Application

```bash
./run.sh
```

You should see:
```
✓ CloudWatch logging configured
  Log Group: /aws/text2sql/backend
  Log Stream: text2sql-backend-2025-01-06-12-34-56
  Region: ap-south-1
```

---

## Configuration Options

### AWS Credentials

**Option 1: IAM Role (Recommended for Production)**
```bash
# Leave credentials empty in .env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

The application will use the IAM role attached to your EC2/ECS/Lambda instance.

**Option 2: Access Keys (Development/Testing)**
```bash
# Provide explicit credentials in .env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Log Levels

```bash
LOG_LEVEL=DEBUG   # Most verbose, includes all logs
LOG_LEVEL=INFO    # Normal operations (recommended)
LOG_LEVEL=WARNING # Only warnings and errors
LOG_LEVEL=ERROR   # Only errors
```

### Console Logging

```bash
# Development: Enable console logging for immediate feedback
ENABLE_CONSOLE_LOGGING=true

# Production: Disable console logging to reduce overhead
ENABLE_CONSOLE_LOGGING=false
```

### Log Group and Region

```bash
# Custom log group
CLOUDWATCH_LOG_GROUP=/my-company/text2sql/production

# Different AWS region (default is ap-south-1)
AWS_REGION=us-west-2
```

---

## IAM Permissions

The application needs these IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/text2sql/*"
    }
  ]
}
```

### For EC2 Instance

1. Create an IAM role with the above policy
2. Attach the role to your EC2 instance
3. Leave `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` empty

### For Local Development

1. Create an IAM user with the above policy
2. Generate access keys
3. Add keys to `.env` file

---

## Viewing Logs in AWS Console

### 1. Navigate to CloudWatch Logs

```
AWS Console → CloudWatch → Logs → Log groups
```

### 2. Find Your Log Group

Look for: `/aws/text2sql/backend`

### 3. View Log Streams

Each application restart creates a new log stream named:
```
text2sql-backend-YYYY-MM-DD-HH-MM-SS
```

### 4. Search Logs

Use CloudWatch Logs Insights:

```sql
-- All error logs
fields @timestamp, level, message
| filter level = "ERROR"
| sort @timestamp desc

-- Login attempts
fields @timestamp, username, message
| filter message like /Login/
| sort @timestamp desc

-- Slow queries
fields @timestamp, execution_time_ms, message
| filter execution_time_ms > 1000
| sort execution_time_ms desc

-- Specific session
fields @timestamp, message
| filter session_id = "your-session-id"
| sort @timestamp asc
```

---

## Log Format

All logs are in **JSON format** with these fields:

```json
{
  "timestamp": "2025-01-06T12:34:56.789Z",
  "level": "INFO",
  "logger": "main",
  "message": "Login successful",
  "module": "main",
  "function": "login",
  "line": 123,
  "username": "sales",
  "database": "sales_db",
  "session_id": "abc-123-def"
}
```

---

## Monitoring and Alerts

### Create CloudWatch Alarms

**Example: Alert on High Error Rate**

1. Go to CloudWatch → Alarms → Create Alarm
2. Select metric: Log group → /aws/text2sql/backend
3. Create metric filter:
   ```
   { $.level = "ERROR" }
   ```
4. Set threshold: Errors > 10 in 5 minutes
5. Configure SNS notification

**Example: Alert on Slow Queries**

1. Create metric filter:
   ```
   { $.execution_time_ms > 5000 }
   ```
2. Set threshold: Slow queries > 5 in 10 minutes

---

## Cost Optimization

### Log Retention

Set retention period to manage costs:

```bash
aws logs put-retention-policy \
  --log-group-name /aws/text2sql/backend \
  --retention-in-days 30
```

Options: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653 days

### Estimate Costs

CloudWatch Logs pricing (ap-south-1):
- Ingestion: $0.50 per GB
- Storage: $0.03 per GB/month
- Insights queries: $0.005 per GB scanned

**Example calculation:**
- 1000 requests/day
- ~1 KB per log entry
- ~30 MB/day = ~900 MB/month
- Cost: ~$0.45/month ingestion + ~$0.03/month storage = **~$0.50/month**

---

## Troubleshooting

### Logs not appearing in CloudWatch

**Check 1: IAM Permissions**
```bash
# Test with AWS CLI
aws logs describe-log-groups --log-group-name-prefix /aws/text2sql

# If you get an error, check your IAM permissions
```

**Check 2: Application Output**
```bash
# Look for CloudWatch setup messages
./run.sh

# Should see:
# ✓ CloudWatch logging configured
```

**Check 3: Console Fallback**
```bash
# If CloudWatch fails, the application falls back to console logging
# Look for error messages in the output
```

### Permission Denied Errors

```bash
# Check your IAM policy includes all required actions:
# - logs:CreateLogGroup
# - logs:CreateLogStream  
# - logs:PutLogEvents
# - logs:DescribeLogStreams
```

### Sequence Token Errors

These are handled automatically by the logger. If you see many of these, there might be a concurrency issue. The handler will retry with the correct token.

---

## Migration from File Logging

### Old Files Location
```
backend/logs/
├── text2sql-backend_info.log
├── text2sql-backend_error.log
└── text2sql-backend_debug.log
```

### Migrating Old Logs (Optional)

If you want to preserve old logs:

```bash
# Compress old logs
cd backend/logs
tar -czf old-logs-$(date +%Y-%m-%d).tar.gz *.log

# Upload to S3 for archival
aws s3 cp old-logs-*.tar.gz s3://your-bucket/text2sql-logs/

# Remove local files
rm *.log
```

### Cleanup

The `logs/` directory is no longer used. You can safely delete it:

```bash
rm -rf backend/logs/
```

---

## Development vs Production

### Development Setup
```bash
# .env for development
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-dev-key
AWS_SECRET_ACCESS_KEY=your-dev-secret
CLOUDWATCH_LOG_GROUP=/aws/text2sql/dev
ENABLE_CONSOLE_LOGGING=true
LOG_LEVEL=DEBUG
```

### Production Setup
```bash
# .env for production
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=              # Empty - uses IAM role
AWS_SECRET_ACCESS_KEY=          # Empty - uses IAM role
CLOUDWATCH_LOG_GROUP=/aws/text2sql/production
ENABLE_CONSOLE_LOGGING=false
LOG_LEVEL=INFO
```

---

## Advanced Features

### Custom Log Dimensions

Add custom dimensions to your logs:

```python
from cloudwatch_logger import get_logger, log_with_context

logger = get_logger(__name__)

log_with_context(
    logger, "info", "Custom event",
    user_id="user123",
    action="query_executed",
    database="sales_db",
    duration_ms=234
)
```

### Multiple Log Groups

For different environments:

```python
# In config.py, set different log groups
if os.getenv("ENVIRONMENT") == "production":
    cloudwatch_log_group = "/aws/text2sql/production"
elif os.getenv("ENVIRONMENT") == "staging":
    cloudwatch_log_group = "/aws/text2sql/staging"
else:
    cloudwatch_log_group = "/aws/text2sql/dev"
```

---

## Summary

✅ **Centralized Logging** - All logs in one place  
✅ **Scalable** - Handles high-volume logging  
✅ **Searchable** - Powerful query capabilities  
✅ **Monitorable** - Easy integration with alarms  
✅ **Cost-Effective** - Pay only for what you use  
✅ **Production-Ready** - IAM role support, automatic failover  

**Your application is now logging to CloudWatch! 🎉**
