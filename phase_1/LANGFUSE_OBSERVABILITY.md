# LangFuse Observability Integration

## Overview

Complete LLM observability with LangFuse - track every Claude API call, monitor costs, analyze performance, and debug issues in production.

---

## What Gets Tracked

**Automatically Captured:**
- ✅ **Every Claude API call** - Input, output, timing
- ✅ **Token usage** - Input tokens, output tokens, total
- ✅ **Costs** - Automatic calculation based on model pricing
- ✅ **Latency** - API call timing and total generation time
- ✅ **Success/Failure** - Errors with stack traces
- ✅ **User context** - Team, database, session
- ✅ **Cache status** - Whether query was cached
- ✅ **Model info** - claude-sonnet-4-5-20250929

**Custom Metadata:**
- Database name
- Table count
- Query length
- Generated SQL length
- Team name (sales/marketing/operations)

---

## Setup

### Step 1: Sign Up for LangFuse

**Option A: Cloud (Easiest)**
1. Go to https://cloud.langfuse.com
2. Sign up (free tier: 50k events/month)
3. Create a project
4. Get API keys: Settings → API Keys

**Option B: Self-Hosted**
```bash
docker run -d \
  -p 3000:3000 \
  -e DATABASE_URL=postgresql://... \
  langfuse/langfuse
```

### Step 2: Add to .env

```bash
# LangFuse Observability
ENABLE_LANGFUSE=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt  # Includes langfuse
```

### Step 4: Restart Backend

```bash
./run.sh
```

You should see: `LangFuse observability enabled`

---

## Using LangFuse Dashboard

### Access Your Dashboard

Go to: https://cloud.langfuse.com

### Key Views

**1. Traces**
- See every SQL generation request
- Click to view full details
- Filter by team, database, success/failure

**2. Generations**
- All Claude API calls
- Token usage per request
- Input/output inspection

**3. Users**
- Group by team (sales/marketing/operations)
- Cost per team
- Usage patterns

**4. Sessions**
- Track user sessions
- See all queries in a session
- Analyze user behavior

**5. Metrics**
- Total cost
- Average latency
- Token usage over time
- Success rate

---

## Example Traces

### Successful Generation

```
Trace: text2sql_generation
├─ Session: abc-123-def
├─ User: sales
├─ Tags: [text2sql, sales, sales_db]
├─ Metadata:
│  ├─ team: sales
│  ├─ database: sales_db
│  └─ cached: false
│
└─ Generation: generate_sql
   ├─ Model: claude-sonnet-4-5-20250929
   ├─ Input: "Show me total revenue for last month"
   ├─ Output: "SELECT SUM(amount) FROM sales WHERE..."
   ├─ Tokens: 234 input, 45 output = 279 total
   ├─ Cost: $0.0042
   ├─ Latency: 2,345ms
   └─ Status: ✅ Success
```

### Cached Query

```
Trace: text2sql_generation
├─ Metadata:
│  └─ cached: true  ← From cache, no Claude API call
├─ Latency: 35ms    ← Much faster
└─ Cost: $0.00025   ← DynamoDB only
```

### Failed Generation

```
Trace: text2sql_generation
└─ Generation: generate_sql
   ├─ Input: "Show me xyz from abc table"
   ├─ Status: ❌ ERROR
   ├─ Error: "Table 'abc' not found"
   └─ Latency: 1,234ms
```

---

## Cost Analysis

### View Costs

**Total Cost:**
```
Dashboard → Metrics → Total Cost
```

**Cost by Team:**
```
Dashboard → Users → Select team → View costs
```

**Cost Trend:**
```
Dashboard → Metrics → Cost over time (chart)
```

### Example Costs

| Metric | Value |
|--------|-------|
| **Per Request** | $0.003-0.015 |
| **Cached Request** | $0.00025 |
| **1000 requests/day** | ~$10/day = $300/month |
| **With 50% cache rate** | ~$5/day = $150/month |

---

## Analytics Queries

### Most Expensive Queries

```
Dashboard → Generations → Sort by Cost (descending)
```

### Slowest Queries

```
Dashboard → Generations → Sort by Latency (descending)
```

### Error Rate

```
Dashboard → Metrics → Success Rate
```

### Team Usage

```
Dashboard → Users → View all users
Filter by: sales, marketing, operations
```

### Token Usage by Database

```
Dashboard → Traces → Group by metadata.database
```

---

## Debugging with LangFuse

### Find Failed Queries

1. Go to **Traces**
2. Filter: `Status = ERROR`
3. Click trace to see full details
4. View error message and stack trace

### Compare Cached vs Uncached

1. Go to **Traces**
2. Filter: `metadata.cached = true`
3. Compare latency with uncached queries

### Analyze Slow Queries

1. Go to **Generations**
2. Filter: `Latency > 5000ms`
3. Look for patterns (long prompts, large schemas)

### Track Specific Team

1. Go to **Users**
2. Select team (e.g., "sales")
3. View all their traces
4. Analyze usage patterns

---

## Alerts & Monitoring

### Set Up Alerts (Self-Hosted Only)

LangFuse doesn't have built-in alerts, but you can:

**Option 1: Use CloudWatch Logs**
```sql
-- Alert on high error rate
fields @timestamp, langfuse
| filter message like /ERROR/
| stats count() by bin(5m)
| filter count > 10
```

**Option 2: Query LangFuse API**
```python
# Daily cost check
from langfuse import Langfuse
langfuse = Langfuse()

# Get today's traces
traces = langfuse.fetch_traces(
    from_timestamp=today,
    to_timestamp=now
)

total_cost = sum(t.cost for t in traces)
if total_cost > DAILY_BUDGET:
    send_alert()
```

---

## Best Practices

### ✅ DO:
- Review traces daily in development
- Set up cost budgets
- Monitor error rates
- Use tags for filtering (team, database)
- Check P95 latency regularly

### ❌ DON'T:
- Log sensitive data in metadata
- Ignore failed traces
- Forget to check costs
- Skip prompt optimization

---

## Prompt Optimization

### Find Inefficient Prompts

1. **High Token Usage**
   - Go to Generations
   - Sort by Input Tokens (descending)
   - Look for patterns

2. **Long Latency**
   - Sort by Latency
   - Check if schema is too large

3. **Failed Generations**
   - Review error messages
   - Improve prompt instructions

---

## Integration with Existing Systems

### Works With:
- ✅ **Query Cache** - Marks cached queries with `cached: true`
- ✅ **CloudWatch Logs** - Complementary logging
- ✅ **User Feedback** - Can correlate with thumbs up/down
- ✅ **Team Auth** - Tracks per-team usage

### Data Flow:
```
1. User request → Main.py
2. Check cache → DynamoDB
3. If miss → SQLGenerator
4. Claude API call → Tracked by LangFuse
5. Response → Cached in DynamoDB
6. User feedback → Stored in PostgreSQL
```

---

## Troubleshooting

### LangFuse not tracking

**Check logs:**
```bash
./run.sh | grep -i langfuse
```

Should see: `LangFuse observability enabled`

**Verify credentials:**
```bash
# In .env
LANGFUSE_PUBLIC_KEY=pk-lf-...  # Must start with pk-lf-
LANGFUSE_SECRET_KEY=sk-lf-...  # Must start with sk-lf-
```

**Test connection:**
```python
from langfuse import Langfuse
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)
print(langfuse.auth_check())  # Should return True
```

### Traces not showing in dashboard

**Wait 10-30 seconds** - LangFuse batches events

**Check network:**
```bash
curl https://cloud.langfuse.com/api/public/health
```

### Missing token counts

Token counts come from Claude API response. If missing, check:
- Claude API version
- Response parsing in sql_generator.py

---

## Cost Optimization Tips

### 1. Increase Cache Hit Rate
```
Current: 50% → Target: 80%
Savings: $150/month → $250/month
```

### 2. Reduce Schema Size
```python
# Only send relevant tables
relevant_tables = filter_tables(schemas, nl_query)
```

### 3. Monitor Expensive Queries
```
Dashboard → Sort by Cost → Optimize top 10
```

### 4. Set Daily Budgets
```python
# Check daily cost
if daily_cost > BUDGET:
    disable_non_critical_features()
```

---

## Advanced: Custom Events

### Track SQL Execution

```python
from langfuse import Langfuse
langfuse = Langfuse()

# After SQL execution
langfuse.score(
    trace_id=trace_id,
    name="sql_execution_success",
    value=1 if success else 0
)
```

### Track User Feedback

```python
# After thumbs up/down
langfuse.score(
    trace_id=trace_id,
    name="user_feedback",
    value=1 if thumbs_up else 0,
    comment=feedback_comment
)
```

---

## Summary

✅ **Zero-config tracking** - Just add API keys
✅ **Comprehensive data** - Tokens, costs, latency, errors
✅ **Beautiful dashboards** - Pre-built analytics
✅ **Team tracking** - Per-team costs and usage
✅ **Cache integration** - Marks cached queries
✅ **Error debugging** - Full stack traces
✅ **Cost optimization** - Identify expensive patterns

**LangFuse observability is production-ready! 🎉**

---

## Next Steps

1. **Sign up**: https://cloud.langfuse.com
2. **Add keys** to `.env`
3. **Restart** backend
4. **Generate** some queries
5. **View** dashboard
6. **Analyze** costs and performance

**You now have enterprise-grade LLM observability! 🚀**
