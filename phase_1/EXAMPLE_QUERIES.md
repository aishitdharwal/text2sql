# Example Queries for Testing

Test the Text2SQL system with these example queries for each database.

## Sales Database (sales_db)

### Basic Queries

**Q1: Show all customers**
- Expected: List of all customers with their details
```
Show me all customers
```

**Q2: List all products**
- Expected: Product catalog with prices
```
List all products with their prices
```

**Q3: Show recent orders**
- Expected: Orders from the database
```
Show me all orders
```

### Analytics Queries

**Q4: Total revenue by product**
- Expected: Revenue aggregated by product
```
What is the total revenue for each product?
```

**Q5: Top customers by order value**
- Expected: Customers ranked by total spending
```
Show me the top 10 customers by total order value
```

**Q6: Sales rep performance**
- Expected: Sales reps with their metrics
```
Show sales rep performance including total orders and commission earned
```

**Q7: Product inventory status**
- Expected: Products with low stock
```
Which products have stock quantity less than 50 units?
```

**Q8: Revenue by category**
- Expected: Revenue grouped by product category
```
What is the total revenue by product category?
```

**Q9: Order status breakdown**
- Expected: Count of orders by status
```
How many orders are there in each status?
```

**Q10: Customer orders**
- Expected: Customers with their order counts
```
Show me customers who have placed more than 2 orders
```

### Advanced Queries

**Q11: Monthly revenue**
- Expected: Revenue aggregated by month
```
Show me total revenue by month
```

**Q12: Territory performance**
- Expected: Sales metrics by territory
```
What is the total revenue and number of orders by sales territory?
```

**Q13: Product profitability**
- Expected: Products with profit margins
```
Show me products with their profit margins (price minus cost)
```

**Q14: Best selling products**
- Expected: Products ranked by quantity sold
```
What are the top 5 best selling products by quantity?
```

**Q15: Customer demographics**
- Expected: Customers grouped by location
```
How many customers do we have in each state?
```

---

## Marketing Database (marketing_db)

### Basic Queries

**Q1: Show all campaigns**
- Expected: List of all marketing campaigns
```
Show me all marketing campaigns
```

**Q2: List all leads**
- Expected: Complete leads list
```
List all leads
```

**Q3: Show ad spend**
- Expected: Advertising spend records
```
Show me all ad spend data
```

### Analytics Queries

**Q4: Campaign performance**
- Expected: Campaigns with their metrics
```
Show campaign performance with total spend and conversions
```

**Q5: Lead conversion rate**
- Expected: Lead status breakdown
```
How many leads are there in each status?
```

**Q6: Best performing channels**
- Expected: Channels ranked by performance
```
What are the total conversions by marketing channel?
```

**Q7: Cost per conversion**
- Expected: Average cost metrics
```
What is the average cost per conversion for each campaign?
```

**Q8: Lead quality**
- Expected: High-scoring leads
```
Show me leads with a lead score above 75
```

**Q9: Email campaign metrics**
- Expected: Email performance data
```
Show email campaign open rates and click rates
```

**Q10: Active campaigns**
- Expected: Currently running campaigns
```
Which campaigns are currently active?
```

### Advanced Queries

**Q11: ROI by campaign**
- Expected: Return on investment calculations
```
Calculate ROI for each campaign (conversion value / spend)
```

**Q12: Lead sources**
- Expected: Leads grouped by source
```
How many leads came from each lead source?
```

**Q13: Daily ad performance**
- Expected: Daily metrics
```
Show me daily ad spend and conversions for the last 30 days
```

**Q14: Campaign budget utilization**
- Expected: Budget vs spend analysis
```
Show campaigns with their budget and total spent
```

**Q15: Conversion funnel**
- Expected: Lead to conversion analysis
```
What percentage of leads convert to customers?
```

---

## Operations Database (operations_db)

### Basic Queries

**Q1: Show all warehouses**
- Expected: Warehouse list with locations
```
Show me all warehouses
```

**Q2: List all suppliers**
- Expected: Supplier directory
```
List all suppliers with their ratings
```

**Q3: Show inventory**
- Expected: Current inventory levels
```
Show me current inventory levels
```

### Analytics Queries

**Q4: Low inventory alert**
- Expected: Items below reorder point
```
Which inventory items are below their reorder level?
```

**Q5: Shipment status**
- Expected: Shipments by status
```
How many shipments are there in each status?
```

**Q6: Warehouse capacity**
- Expected: Warehouse utilization
```
Show me warehouses with their capacity and location
```

**Q7: Supplier performance**
- Expected: Top rated suppliers
```
Which suppliers have a rating above 4.0?
```

**Q8: Delayed shipments**
- Expected: Overdue deliveries
```
Show me shipments where actual delivery is after estimated delivery
```

**Q9: Inventory by warehouse**
- Expected: Stock levels per location
```
What is the total inventory quantity at each warehouse?
```

**Q10: Active shipments**
- Expected: In-transit shipments
```
Show me all shipments with status 'shipped' or 'in_transit'
```

### Advanced Queries

**Q11: Logistics events**
- Expected: Shipment tracking history
```
Show me logistics events for each shipment with timestamps
```

**Q12: Purchase order analysis**
- Expected: PO metrics
```
Show me purchase orders with their status and total amount
```

**Q13: Shipping carriers**
- Expected: Carrier performance
```
How many shipments has each carrier delivered?
```

**Q14: Inventory restock needs**
- Expected: Items to reorder
```
Show me products where quantity on hand is less than reorder quantity
```

**Q15: Warehouse locations**
- Expected: Geographic distribution
```
How many warehouses do we have in each country?
```

---

## Complex Cross-Table Queries

### Sales Database

**Q1: Customer lifetime value**
```
Show me total revenue per customer ordered by highest to lowest
```

**Q2: Product performance with details**
```
Show me products with their total quantity sold and revenue
```

**Q3: Sales rep commission report**
```
Show me each sales rep with their total sales and commission earned
```

**Q4: Monthly order trends**
```
Show me the number of orders and total revenue by month
```

**Q5: Customer order history**
```
Show me customers with their most recent order date
```

### Marketing Database

**Q1: Campaign effectiveness**
```
Show me campaigns with their total spend, conversions, and conversion value
```

**Q2: Lead to customer conversion**
```
Show me the conversion rate (converted leads / total leads) for each campaign
```

**Q3: Channel ROI analysis**
```
Show me total spend and total conversion value by marketing channel
```

**Q4: Email campaign performance**
```
Show me email campaigns with their open rate and click rate percentages
```

**Q5: Lead quality by source**
```
Show me average lead score by lead source
```

### Operations Database

**Q1: Inventory status report**
```
Show me all inventory with warehouse names and reorder status
```

**Q2: Shipment performance**
```
Show me shipments with warehouse names and carrier information
```

**Q3: Supplier order history**
```
Show me suppliers with their total number of purchase orders and total amount
```

**Q4: Warehouse inventory value**
```
Show me each warehouse with its total inventory quantity
```

**Q5: Logistics tracking**
```
Show me shipments with their latest logistics event and timestamp
```

---

## Testing Tips

1. **Start Simple**: Begin with basic queries to verify connection
2. **Test Accuracy**: Verify results match expected data
3. **Edit Queries**: Try editing generated SQL and re-running
4. **Test Errors**: Intentionally enter invalid queries to test error handling
5. **Compare Teams**: Test same query pattern across different databases
6. **Check Formatting**: Ensure results display properly in table format
7. **Performance**: Note any slow queries for optimization

## Expected Behaviors

✅ **Good Results:**
- Clean SQL query generated
- Query executes without errors
- Results display in formatted table
- Row count shows correctly

❌ **Expected Errors to Test:**
- Invalid table name: "Show me all customer" (missing 's')
- Invalid column: "Show me customer age" (column doesn't exist)
- Syntax error: User manually edits SQL incorrectly

## Verification Checklist

For each query test:
- [ ] Natural language input is clear
- [ ] Generated SQL is valid PostgreSQL
- [ ] Query runs without errors
- [ ] Results are accurate
- [ ] Results format properly
- [ ] Row count is displayed
- [ ] Can edit and re-run query

---

Use these queries to thoroughly test the Text2SQL system!
