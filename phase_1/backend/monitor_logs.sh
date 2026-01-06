#!/bin/bash

# Log monitoring and analysis script for Text2SQL

LOGS_DIR="logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================"
echo "Text2SQL Log Monitor"
echo "======================================"
echo ""

# Check if logs directory exists
if [ ! -d "$LOGS_DIR" ]; then
    echo -e "${RED}Error: Logs directory not found!${NC}"
    echo "Make sure the backend has been started at least once."
    exit 1
fi

# Function to count lines in log file
count_log_lines() {
    file=$1
    if [ -f "$LOGS_DIR/$file" ]; then
        wc -l < "$LOGS_DIR/$file"
    else
        echo "0"
    fi
}

# Function to get file size
get_file_size() {
    file=$1
    if [ -f "$LOGS_DIR/$file" ]; then
        du -h "$LOGS_DIR/$file" | cut -f1
    else
        echo "0B"
    fi
}

# Function to count occurrences in log
count_pattern() {
    file=$1
    pattern=$2
    if [ -f "$LOGS_DIR/$file" ]; then
        grep -c "$pattern" "$LOGS_DIR/$file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Log file statistics
echo -e "${BLUE}Log File Statistics:${NC}"
echo "----------------------------------------"
printf "%-30s %10s %10s\n" "File" "Size" "Lines"
echo "----------------------------------------"
printf "%-30s %10s %10s\n" "text2sql-backend_info.log" "$(get_file_size text2sql-backend_info.log)" "$(count_log_lines text2sql-backend_info.log)"
printf "%-30s %10s %10s\n" "text2sql-backend_error.log" "$(get_file_size text2sql-backend_error.log)" "$(count_log_lines text2sql-backend_error.log)"
printf "%-30s %10s %10s\n" "text2sql-backend_debug.log" "$(get_file_size text2sql-backend_debug.log)" "$(count_log_lines text2sql-backend_debug.log)"
echo ""

# Error statistics
echo -e "${RED}Error Statistics:${NC}"
echo "----------------------------------------"
TOTAL_ERRORS=$(count_pattern "text2sql-backend_error.log" '"level":"ERROR"')
echo "Total Errors: $TOTAL_ERRORS"

if [ -f "$LOGS_DIR/text2sql-backend_error.log" ] && [ "$TOTAL_ERRORS" -gt "0" ]; then
    echo ""
    echo "Recent Errors (last 5):"
    tail -5 "$LOGS_DIR/text2sql-backend_error.log" | jq -r '.timestamp + " | " + .message' 2>/dev/null || echo "No errors found"
fi
echo ""

# Login statistics
echo -e "${GREEN}Login Statistics:${NC}"
echo "----------------------------------------"
SUCCESSFUL_LOGINS=$(count_pattern "text2sql-backend_info.log" "Login successful")
FAILED_LOGINS=$(count_pattern "text2sql-backend_info.log" "Login failed")
echo "Successful Logins: $SUCCESSFUL_LOGINS"
echo "Failed Logins: $FAILED_LOGINS"

if [ "$SUCCESSFUL_LOGINS" -gt "0" ]; then
    SUCCESS_RATE=$(echo "scale=2; $SUCCESSFUL_LOGINS * 100 / ($SUCCESSFUL_LOGINS + $FAILED_LOGINS)" | bc 2>/dev/null || echo "100")
    echo "Success Rate: ${SUCCESS_RATE}%"
fi
echo ""

# Query statistics
echo -e "${YELLOW}Query Statistics:${NC}"
echo "----------------------------------------"
QUERIES_GENERATED=$(count_pattern "text2sql-backend_info.log" "SQL generation successful")
QUERIES_EXECUTED=$(count_pattern "text2sql-backend_info.log" "Query executed successfully")
echo "Queries Generated: $QUERIES_GENERATED"
echo "Queries Executed: $QUERIES_EXECUTED"
echo ""

# Performance metrics
echo -e "${BLUE}Performance Metrics:${NC}"
echo "----------------------------------------"

if [ -f "$LOGS_DIR/text2sql-backend_info.log" ]; then
    # Average query execution time
    AVG_EXEC_TIME=$(grep "execution_time_ms" "$LOGS_DIR/text2sql-backend_info.log" 2>/dev/null | \
        jq -r '.execution_time_ms' 2>/dev/null | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')
    
    # Average API call time
    AVG_API_TIME=$(grep "api_call_time_ms" "$LOGS_DIR/text2sql-backend_info.log" 2>/dev/null | \
        jq -r '.api_call_time_ms' 2>/dev/null | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')
    
    echo "Average Query Execution Time: ${AVG_EXEC_TIME} ms"
    echo "Average Claude API Call Time: ${AVG_API_TIME} ms"
fi
echo ""

# Active sessions
echo -e "${GREEN}Session Information:${NC}"
echo "----------------------------------------"
if [ -f "$LOGS_DIR/text2sql-backend_info.log" ]; then
    LATEST_SESSION_COUNT=$(grep "active_sessions_count" "$LOGS_DIR/text2sql-backend_info.log" 2>/dev/null | \
        tail -1 | \
        jq -r '.active_sessions_count' 2>/dev/null || echo "0")
    echo "Latest Active Sessions Count: $LATEST_SESSION_COUNT"
fi
echo ""

# Interactive menu
echo "======================================"
echo "What would you like to do?"
echo "======================================"
echo "1. View recent activity (INFO logs)"
echo "2. View recent errors"
echo "3. View debug logs"
echo "4. Search logs"
echo "5. Tail info logs (live)"
echo "6. Tail error logs (live)"
echo "7. Find slow queries (>1000ms)"
echo "8. View login activity"
echo "9. Exit"
echo ""
read -p "Enter choice [1-9]: " choice

case $choice in
    1)
        echo ""
        echo "Recent Activity (last 20 lines):"
        tail -20 "$LOGS_DIR/text2sql-backend_info.log" | jq -r '.timestamp + " | " + .level + " | " + .message'
        ;;
    2)
        echo ""
        echo "Recent Errors (last 20 lines):"
        tail -20 "$LOGS_DIR/text2sql-backend_error.log" | jq '.'
        ;;
    3)
        echo ""
        echo "Debug Logs (last 20 lines):"
        tail -20 "$LOGS_DIR/text2sql-backend_debug.log" | jq -r '.timestamp + " | " + .level + " | " + .message'
        ;;
    4)
        echo ""
        read -p "Enter search term: " search_term
        echo "Searching all logs for: $search_term"
        grep -r "$search_term" "$LOGS_DIR/" | head -20
        ;;
    5)
        echo ""
        echo "Tailing INFO logs (Ctrl+C to stop)..."
        tail -f "$LOGS_DIR/text2sql-backend_info.log" | jq -r '.timestamp + " | " + .level + " | " + .message'
        ;;
    6)
        echo ""
        echo "Tailing ERROR logs (Ctrl+C to stop)..."
        tail -f "$LOGS_DIR/text2sql-backend_error.log" | jq '.'
        ;;
    7)
        echo ""
        echo "Slow Queries (>1000ms):"
        grep "execution_time_ms" "$LOGS_DIR/text2sql-backend_info.log" | \
            jq 'select(.execution_time_ms > 1000) | .timestamp + " | " + (.execution_time_ms|tostring) + "ms | " + .message'
        ;;
    8)
        echo ""
        echo "Login Activity:"
        grep -E "(Login successful|Login failed)" "$LOGS_DIR/text2sql-backend_info.log" | \
            jq -r '.timestamp + " | " + .message + " | " + .username'
        ;;
    9)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
