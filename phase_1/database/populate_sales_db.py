"""
Generate sample data for Sales Database
Run this after creating the schema
"""

import psycopg2
from datetime import datetime, timedelta
import random

# Database connection parameters - UPDATE THESE
DB_CONFIG = {
    'host': 'text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com',
    'database': 'sales_db',
    'user': 'postgres',
    'password': 'YourSecurePassword123',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def populate_customers(conn):
    """Populate customers table with 20 records"""
    cursor = conn.cursor()
    
    customers_data = [
        ('John', 'Doe', 'john.doe@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001'),
        ('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
        ('Michael', 'Johnson', 'michael.j@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601'),
        ('Emily', 'Williams', 'emily.w@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001'),
        ('David', 'Brown', 'david.brown@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001'),
        ('Sarah', 'Davis', 'sarah.davis@email.com', '555-0106', '987 Cedar Ln', 'Philadelphia', 'PA', '19101'),
        ('James', 'Miller', 'james.miller@email.com', '555-0107', '147 Birch St', 'San Antonio', 'TX', '78201'),
        ('Jennifer', 'Wilson', 'jennifer.w@email.com', '555-0108', '258 Spruce Ave', 'San Diego', 'CA', '92101'),
        ('Robert', 'Moore', 'robert.moore@email.com', '555-0109', '369 Ash Rd', 'Dallas', 'TX', '75201'),
        ('Linda', 'Taylor', 'linda.taylor@email.com', '555-0110', '741 Willow Way', 'San Jose', 'CA', '95101'),
        ('William', 'Anderson', 'william.a@email.com', '555-0111', '852 Poplar Pl', 'Austin', 'TX', '73301'),
        ('Patricia', 'Thomas', 'patricia.t@email.com', '555-0112', '963 Hickory Ct', 'Jacksonville', 'FL', '32099'),
        ('Richard', 'Jackson', 'richard.j@email.com', '555-0113', '159 Walnut Blvd', 'Fort Worth', 'TX', '76101'),
        ('Barbara', 'White', 'barbara.white@email.com', '555-0114', '357 Chestnut St', 'Columbus', 'OH', '43004'),
        ('Christopher', 'Harris', 'chris.harris@email.com', '555-0115', '486 Sycamore Ave', 'Charlotte', 'NC', '28201'),
        ('Susan', 'Martin', 'susan.martin@email.com', '555-0116', '264 Redwood Dr', 'San Francisco', 'CA', '94101'),
        ('Joseph', 'Thompson', 'joseph.t@email.com', '555-0117', '795 Sequoia Ln', 'Indianapolis', 'IN', '46201'),
        ('Jessica', 'Garcia', 'jessica.garcia@email.com', '555-0118', '135 Magnolia Way', 'Seattle', 'WA', '98101'),
        ('Thomas', 'Martinez', 'thomas.m@email.com', '555-0119', '246 Dogwood Pl', 'Denver', 'CO', '80201'),
        ('Karen', 'Robinson', 'karen.robinson@email.com', '555-0120', '879 Beech Ct', 'Boston', 'MA', '02101'),
    ]
    
    for customer in customers_data:
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, customer)
    
    conn.commit()
    print("✓ Inserted 20 customers")

def populate_products(conn):
    """Populate products table with 20 records"""
    cursor = conn.cursor()
    
    products_data = [
        ('Wireless Bluetooth Headphones', 'Electronics', 'AudioTech', 79.99, 35.00, 150, 'Premium wireless headphones with noise cancellation'),
        ('Stainless Steel Water Bottle', 'Home & Kitchen', 'HydroFlask', 24.99, 8.50, 300, 'Insulated water bottle keeps drinks cold for 24 hours'),
        ('Yoga Mat Pro', 'Sports & Fitness', 'FitLife', 39.99, 15.00, 200, 'Extra thick yoga mat with carrying strap'),
        ('Smart Watch Series 5', 'Electronics', 'TechTime', 299.99, 120.00, 75, 'Fitness tracking smartwatch with heart rate monitor'),
        ('Organic Coffee Beans 2lb', 'Food & Beverage', 'BrewMaster', 18.99, 7.00, 500, 'Fair trade organic whole bean coffee'),
        ('Running Shoes Air Max', 'Sports & Fitness', 'SportPro', 89.99, 40.00, 120, 'Lightweight running shoes with air cushioning'),
        ('Laptop Backpack', 'Accessories', 'TravelGear', 59.99, 25.00, 180, 'Water-resistant laptop backpack with USB charging port'),
        ('Protein Powder Vanilla 5lb', 'Health & Wellness', 'NutriMax', 49.99, 22.00, 250, 'Whey protein isolate powder'),
        ('Ceramic Cookware Set', 'Home & Kitchen', 'ChefPro', 149.99, 65.00, 90, '10-piece non-stick ceramic cookware set'),
        ('Wireless Mouse Ergonomic', 'Electronics', 'TechGear', 34.99, 12.00, 220, 'Ergonomic wireless mouse with adjustable DPI'),
        ('Resistance Bands Set', 'Sports & Fitness', 'FitLife', 29.99, 10.00, 350, 'Set of 5 resistance bands with different strengths'),
        ('Air Purifier HEPA', 'Home & Kitchen', 'CleanAir', 129.99, 55.00, 100, 'HEPA air purifier for large rooms'),
        ('Desk Lamp LED', 'Home & Kitchen', 'BrightLight', 44.99, 18.00, 160, 'Adjustable LED desk lamp with USB charging'),
        ('Travel Pillow Memory Foam', 'Accessories', 'TravelGear', 24.99, 9.00, 280, 'Memory foam neck pillow for travel'),
        ('Vitamin D3 Supplements', 'Health & Wellness', 'NutriMax', 16.99, 6.00, 400, '5000 IU vitamin D3 supplement, 180 capsules'),
        ('Blender Professional', 'Home & Kitchen', 'ChefPro', 89.99, 38.00, 110, 'High-power blender for smoothies and shakes'),
        ('Phone Case iPhone 15', 'Accessories', 'TechGear', 19.99, 5.00, 450, 'Protective phone case with screen protector'),
        ('Dumbbells Set 20lb', 'Sports & Fitness', 'FitLife', 79.99, 32.00, 85, 'Pair of adjustable dumbbells'),
        ('Electric Kettle', 'Home & Kitchen', 'BrewMaster', 39.99, 16.00, 190, 'Fast-boiling electric kettle with auto shut-off'),
        ('Sunglasses Polarized', 'Accessories', 'SportPro', 59.99, 22.00, 210, 'UV protection polarized sunglasses'),
    ]
    
    for product in products_data:
        cursor.execute("""
            INSERT INTO products (product_name, category, brand, price, cost, stock_quantity, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, product)
    
    conn.commit()
    print("✓ Inserted 20 products")

def populate_sales_reps(conn):
    """Populate sales_reps table with 20 records"""
    cursor = conn.cursor()
    
    hire_dates = [datetime.now().date() - timedelta(days=random.randint(180, 1825)) for _ in range(20)]
    
    sales_reps_data = [
        ('Alex', 'Thompson', 'alex.thompson@company.com', '555-1001', hire_dates[0], 'Northeast', 7.5),
        ('Maria', 'Rodriguez', 'maria.rodriguez@company.com', '555-1002', hire_dates[1], 'Southwest', 8.0),
        ('Daniel', 'Lee', 'daniel.lee@company.com', '555-1003', hire_dates[2], 'West Coast', 7.0),
        ('Rachel', 'Cohen', 'rachel.cohen@company.com', '555-1004', hire_dates[3], 'Midwest', 6.5),
        ('Marcus', 'Washington', 'marcus.washington@company.com', '555-1005', hire_dates[4], 'Southeast', 8.5),
        ('Sophie', 'Chen', 'sophie.chen@company.com', '555-1006', hire_dates[5], 'Northeast', 7.0),
        ('Tyler', 'Brooks', 'tyler.brooks@company.com', '555-1007', hire_dates[6], 'West Coast', 6.0),
        ('Olivia', 'Patel', 'olivia.patel@company.com', '555-1008', hire_dates[7], 'Southwest', 7.5),
        ('Nathan', 'Kim', 'nathan.kim@company.com', '555-1009', hire_dates[8], 'Midwest', 8.0),
        ('Emma', 'Foster', 'emma.foster@company.com', '555-1010', hire_dates[9], 'Southeast', 7.0),
        ('Carlos', 'Ruiz', 'carlos.ruiz@company.com', '555-1011', hire_dates[10], 'Southwest', 6.5),
        ('Hannah', 'Morrison', 'hannah.morrison@company.com', '555-1012', hire_dates[11], 'Northeast', 8.0),
        ('Kevin', 'O\'Brien', 'kevin.obrien@company.com', '555-1013', hire_dates[12], 'West Coast', 7.5),
        ('Priya', 'Sharma', 'priya.sharma@company.com', '555-1014', hire_dates[13], 'Midwest', 7.0),
        ('Brandon', 'Hughes', 'brandon.hughes@company.com', '555-1015', hire_dates[14], 'Southeast', 6.0),
        ('Zoe', 'Campbell', 'zoe.campbell@company.com', '555-1016', hire_dates[15], 'Northeast', 8.5),
        ('Jordan', 'Mitchell', 'jordan.mitchell@company.com', '555-1017', hire_dates[16], 'West Coast', 7.0),
        ('Aisha', 'Johnson', 'aisha.johnson@company.com', '555-1018', hire_dates[17], 'Southwest', 7.5),
        ('Ryan', 'Peterson', 'ryan.peterson@company.com', '555-1019', hire_dates[18], 'Midwest', 6.5),
        ('Maya', 'Singh', 'maya.singh@company.com', '555-1020', hire_dates[19], 'Southeast', 8.0),
    ]
    
    for rep in sales_reps_data:
        cursor.execute("""
            INSERT INTO sales_reps (first_name, last_name, email, phone, hire_date, territory, commission_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, rep)
    
    conn.commit()
    print("✓ Inserted 20 sales reps")

def populate_orders_and_items(conn):
    """Populate orders and order_items tables with 20 orders"""
    cursor = conn.cursor()
    
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'delivered', 'delivered']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'credit_card', 'credit_card']
    
    for i in range(20):
        customer_id = random.randint(1, 20)
        rep_id = random.randint(1, 20)
        order_date = datetime.now() - timedelta(days=random.randint(1, 90))
        status = random.choice(statuses)
        payment_method = random.choice(payment_methods)
        
        # Get random products for this order (1-3 items)
        num_items = random.randint(1, 3)
        product_ids = random.sample(range(1, 21), num_items)
        
        # Calculate total
        total_amount = 0
        items = []
        
        for product_id in product_ids:
            cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            price = cursor.fetchone()[0]
            quantity = random.randint(1, 3)
            subtotal = float(price) * quantity
            total_amount += subtotal
            items.append((product_id, quantity, price, subtotal))
        
        # Insert order
        cursor.execute("""
            INSERT INTO orders (customer_id, rep_id, order_date, status, total_amount, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """, (customer_id, rep_id, order_date, status, total_amount, payment_method))
        
        order_id = cursor.fetchone()[0]
        
        # Insert order items
        for product_id, quantity, price, subtotal in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id, quantity, price, subtotal))
    
    conn.commit()
    print("✓ Inserted 20 orders with their items")

def populate_revenue(conn):
    """Populate revenue table based on orders"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.order_id, o.order_date, o.total_amount, sr.commission_rate
        FROM orders o
        JOIN sales_reps sr ON o.rep_id = sr.rep_id
    """)
    
    orders = cursor.fetchall()
    
    for order_id, order_date, total_amount, commission_rate in orders:
        # Get COGS for this order
        cursor.execute("""
            SELECT SUM(oi.quantity * p.cost)
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        cost_of_goods = cursor.fetchone()[0] or 0
        commission_paid = float(total_amount) * float(commission_rate) / 100
        net_revenue = float(total_amount) - float(cost_of_goods) - commission_paid
        
        cursor.execute("""
            INSERT INTO revenue (order_id, revenue_date, gross_revenue, cost_of_goods, net_revenue, commission_paid)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, order_date.date(), total_amount, cost_of_goods, net_revenue, commission_paid))
    
    conn.commit()
    print("✓ Inserted revenue records")

def main():
    print("Populating Sales Database...")
    print("=" * 50)
    
    try:
        conn = get_connection()
        print("✓ Connected to database")
        
        populate_customers(conn)
        populate_products(conn)
        populate_sales_reps(conn)
        populate_orders_and_items(conn)
        populate_revenue(conn)
        
        conn.close()
        print("=" * 50)
        print("✓ Sales database population complete!")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
