# User Feedback System

## Overview

Complete user feedback system for SQL query generation. Users can rate generated SQL queries with thumbs up/down and optionally provide comments for negative feedback.

---

## Components

### 1. Database Schema (`database/feedback_schema.sql`)

```sql
CREATE TABLE query_feedback (
    feedback_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    team_name VARCHAR(50) NOT NULL,
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    rating VARCHAR(10) NOT NULL CHECK (rating IN ('thumbs_up', 'thumbs_down')),
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Backend API (`backend/main.py`)

**Endpoint:** `POST /api/feedback`

**Request:**
```json
{
  "session_id": "uuid",
  "natural_language_query": "Show me total revenue",
  "generated_sql": "SELECT SUM(revenue) FROM sales",
  "rating": "thumbs_up",  // or "thumbs_down"
  "feedback_comment": "Optional comment"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": 123
}
```

### 3. Frontend UI

**Features:**
- Feedback section appears after SQL generation
- Two buttons: 👍 Yes / 👎 No
- Thumbs down prompts for optional comment
- Success/error messages
- Buttons disabled after submission

---

## Setup Instructions

### Step 1: Create Feedback Tables

Run the schema in each database:

```bash
# Connect to each database and run
psql -h YOUR_HOST -U postgres -d sales_db -f database/feedback_schema.sql
psql -h YOUR_HOST -U postgres -d marketing_db -f database/feedback_schema.sql
psql -h YOUR_HOST -U postgres -d operations_db -f database/feedback_schema.sql
```

### Step 2: Restart Backend

The feedback endpoint is already added to `backend/main.py`:

```bash
cd backend
./run.sh
```

### Step 3: Test the Feature

1. Login to the dashboard
2. Generate an SQL query
3. See feedback buttons appear
4. Click thumbs up or down
5. For thumbs down, optionally add a comment

---

## User Flow

```
1. User enters natural language query
2. Click "Generate SQL Query"
3. SQL appears → Feedback section shows
4. User clicks 👍 or 👎
5. If 👎: Prompt for comment (optional)
6. Feedback saved to database
7. "Thank you" message displays
8. Buttons disabled to prevent duplicate submissions
```

---

## Viewing Feedback Data

### Query Feedback by Team

```sql
-- Sales team feedback
SELECT 
    rating,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM query_feedback
WHERE team_name = 'sales'
GROUP BY rating;
```

### Recent Negative Feedback

```sql
SELECT 
    team_name,
    natural_language_query,
    generated_sql,
    feedback_comment,
    created_at
FROM query_feedback
WHERE rating = 'thumbs_down'
  AND feedback_comment IS NOT NULL
ORDER BY created_at DESC
LIMIT 20;
```

### Feedback Statistics

```sql
SELECT 
    team_name,
    COUNT(*) as total_feedback,
    COUNT(*) FILTER (WHERE rating = 'thumbs_up') as positive,
    COUNT(*) FILTER (WHERE rating = 'thumbs_down') as negative,
    ROUND(COUNT(*) FILTER (WHERE rating = 'thumbs_up') * 100.0 / COUNT(*), 2) as satisfaction_rate
FROM query_feedback
GROUP BY team_name
ORDER BY total_feedback DESC;
```

### Find Problem Queries

```sql
-- Queries with multiple negative feedback
SELECT 
    natural_language_query,
    COUNT(*) as negative_count,
    array_agg(DISTINCT feedback_comment) FILTER (WHERE feedback_comment IS NOT NULL) as comments
FROM query_feedback
WHERE rating = 'thumbs_down'
GROUP BY natural_language_query
HAVING COUNT(*) >= 2
ORDER BY negative_count DESC;
```

---

## CloudWatch Logging

All feedback submissions are logged with:
- Session ID
- Team name
- Rating (thumbs_up/thumbs_down)
- Feedback ID
- Whether comment was provided

**View feedback logs:**

```sql
-- CloudWatch Logs Insights
fields @timestamp, rating, team, feedback_id
| filter message like /Feedback submitted/
| sort @timestamp desc
```

---

## Features

✅ **Simple UI** - Clean thumbs up/down buttons
✅ **Optional Comments** - For negative feedback
✅ **Prevents Duplicates** - Buttons disabled after submission
✅ **Per-Query Tracking** - Each generated query can be rated
✅ **Team-Based** - Tracks which team provided feedback
✅ **Complete Context** - Stores both NL query and generated SQL
✅ **Timestamped** - Created_at for trend analysis

---

## Future Enhancements

Consider adding:
- View feedback analytics in dashboard
- Email notifications for negative feedback
- Feedback trends over time chart
- Export feedback to CSV
- Filter queries by satisfaction rate

---

## Troubleshooting

**Feedback buttons not appearing?**
- Check that SQL was generated successfully
- Look for `feedbackSection` display style in browser console

**Feedback not saving?**
- Check that feedback table exists in the database
- Verify backend logs for errors
- Ensure session is valid

**Prompt not showing for thumbs down?**
- Check browser console for JavaScript errors
- Verify `prompt()` is not blocked by browser

---

## Testing

```bash
# Test feedback submission
curl -X POST http://localhost:8080/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-id",
    "natural_language_query": "Show total revenue",
    "generated_sql": "SELECT SUM(revenue) FROM sales",
    "rating": "thumbs_up"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": 1
}
```

---

**Feedback system is now complete and ready to use! 🎉**
