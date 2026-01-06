"""
Generate sample data for Sales Database
Run this after creating the schema
Usage: python3 populate_sales_db.py [host] [user] [password] [port]
"""

import psycopg2
from datetime import datetime, timedelta
import random
import sys

def get_db_config():
    """Get database configuration from command line or defaults"""
    if len(sys.argv) >= 5:
        return {
            'host': sys.argv[1],
            'database': 'sales_db',
            'user': sys.argv[2],
            'password': sys.argv[3],
            'port': int(sys.argv[4])
        }
    else:
        # Default configuration - UPDATE THESE
        return {
            'host': 'text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com',
            'database': 'sales_db',
            'user': 'postgres',
            'password': 'YourSecurePassword123',
            'port': 5432
        }

def get_connection():
    config = get_db_config()
    return psycopg2.connect(**config)

def populate_customers(conn):
    """Populate customers table with 50 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE customers CASCADE;")
    
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
        ('Daniel', 'Clark', 'daniel.clark@email.com', '555-0121', '456 Elm Ave', 'Atlanta', 'GA', '30301'),
        ('Nancy', 'Rodriguez', 'nancy.rodriguez@email.com', '555-0122', '789 Oak Dr', 'Miami', 'FL', '33101'),
        ('Matthew', 'Lewis', 'matthew.lewis@email.com', '555-0123', '321 Pine Ln', 'Portland', 'OR', '97201'),
        ('Betty', 'Lee', 'betty.lee@email.com', '555-0124', '654 Maple Rd', 'Las Vegas', 'NV', '89101'),
        ('Mark', 'Walker', 'mark.walker@email.com', '555-0125', '987 Cedar St', 'Detroit', 'MI', '48201'),
        ('Donna', 'Hall', 'donna.hall@email.com', '555-0126', '147 Birch Pl', 'Baltimore', 'MD', '21201'),
        ('Paul', 'Allen', 'paul.allen@email.com', '555-0127', '258 Spruce Way', 'Milwaukee', 'WI', '53201'),
        ('Carol', 'Young', 'carol.young@email.com', '555-0128', '369 Ash Ave', 'Nashville', 'TN', '37201'),
        ('Steven', 'Hernandez', 'steven.h@email.com', '555-0129', '741 Willow Dr', 'Oklahoma City', 'OK', '73101'),
        ('Sandra', 'King', 'sandra.king@email.com', '555-0130', '852 Poplar Rd', 'Louisville', 'KY', '40201'),
        ('Kenneth', 'Wright', 'kenneth.wright@email.com', '555-0131', '963 Hickory Ln', 'Memphis', 'TN', '38101'),
        ('Ashley', 'Lopez', 'ashley.lopez@email.com', '555-0132', '159 Walnut St', 'Richmond', 'VA', '23218'),
        ('Kevin', 'Hill', 'kevin.hill@email.com', '555-0133', '357 Chestnut Way', 'New Orleans', 'LA', '70112'),
        ('Kimberly', 'Scott', 'kimberly.scott@email.com', '555-0134', '486 Sycamore Pl', 'Salt Lake City', 'UT', '84101'),
        ('Brian', 'Green', 'brian.green@email.com', '555-0135', '264 Redwood Ave', 'Raleigh', 'NC', '27601'),
        ('Lisa', 'Adams', 'lisa.adams@email.com', '555-0136', '795 Sequoia Dr', 'Birmingham', 'AL', '35201'),
        ('Jason', 'Baker', 'jason.baker@email.com', '555-0137', '135 Magnolia Rd', 'Tucson', 'AZ', '85701'),
        ('Helen', 'Gonzalez', 'helen.gonzalez@email.com', '555-0138', '246 Dogwood Ln', 'Fresno', 'CA', '93701'),
        ('Jeff', 'Nelson', 'jeff.nelson@email.com', '555-0139', '879 Beech Way', 'Sacramento', 'CA', '94203'),
        ('Deborah', 'Carter', 'deborah.carter@email.com', '555-0140', '456 Elm Pl', 'Kansas City', 'MO', '64101'),
        ('Gary', 'Mitchell', 'gary.mitchell@email.com', '555-0141', '789 Oak St', 'Mesa', 'AZ', '85201'),
        ('Angela', 'Perez', 'angela.perez@email.com', '555-0142', '321 Pine Ave', 'Omaha', 'NE', '68101'),
        ('Ryan', 'Roberts', 'ryan.roberts@email.com', '555-0143', '654 Maple Way', 'Cleveland', 'OH', '44101'),
        ('Melissa', 'Turner', 'melissa.turner@email.com', '555-0144', '987 Cedar Pl', 'Miami', 'FL', '33130'),
        ('Nicholas', 'Phillips', 'nicholas.phillips@email.com', '555-0145', '147 Birch Dr', 'Oakland', 'CA', '94601'),
        ('Stephanie', 'Campbell', 'stephanie.campbell@email.com', '555-0146', '258 Spruce Rd', 'Tulsa', 'OK', '74101'),
        ('Jacob', 'Parker', 'jacob.parker@email.com', '555-0147', '369 Ash Ln', 'Minneapolis', 'MN', '55401'),
        ('Amy', 'Evans', 'amy.evans@email.com', '555-0148', '741 Willow St', 'Wichita', 'KS', '67201'),
        ('Eric', 'Edwards', 'eric.edwards@email.com', '555-0149', '852 Poplar Ave', 'Arlington', 'TX', '76010'),
        ('Virginia', 'Collins', 'virginia.collins@email.com', '555-0150', '963 Hickory Way', 'Bakersfield', 'CA', '93301'),
    ]
    
    for customer in customers_data:
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, customer)
    
    conn.commit()
    print(f"  ✓ Inserted {len(customers_data)} customers")

def populate_products(conn):
    """Populate products table with 30 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE products CASCADE;")
    
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
        ('Gaming Keyboard RGB', 'Electronics', 'TechGear', 99.99, 45.00, 95, 'Mechanical gaming keyboard with RGB lighting'),
        ('Bamboo Cutting Board', 'Home & Kitchen', 'ChefPro', 29.99, 12.00, 175, 'Extra large bamboo cutting board'),
        ('Foam Roller', 'Sports & Fitness', 'FitLife', 34.99, 14.00, 130, 'High-density foam roller for muscle recovery'),
        ('Essential Oil Diffuser', 'Home & Kitchen', 'CleanAir', 39.99, 15.00, 200, 'Ultrasonic aromatherapy diffuser'),
        ('USB-C Cable 6ft', 'Electronics', 'TechGear', 14.99, 4.00, 600, 'Fast charging USB-C cable'),
        ('Stainless Steel Pan 12in', 'Home & Kitchen', 'ChefPro', 69.99, 30.00, 80, 'Professional grade stainless steel frying pan'),
        ('Jump Rope Speed', 'Sports & Fitness', 'FitLife', 19.99, 7.00, 250, 'Adjustable speed jump rope'),
        ('Shower Filter', 'Home & Kitchen', 'CleanAir', 44.99, 18.00, 140, '15-stage shower water filter'),
        ('Laptop Stand Aluminum', 'Accessories', 'TechGear', 49.99, 20.00, 120, 'Ergonomic aluminum laptop stand'),
        ('Green Tea Organic 100 Bags', 'Food & Beverage', 'BrewMaster', 12.99, 5.00, 380, 'Organic green tea bags'),
    ]
    
    for product in products_data:
        cursor.execute("""
            INSERT INTO products (product_name, category, brand, price, cost, stock_quantity, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, product)
    
    conn.commit()
    print(f"  ✓ Inserted {len(products_data)} products")

def populate_sales_reps(conn):
    """Populate sales_reps table with 20 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE sales_reps CASCADE;")
    
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
    print(f"  ✓ Inserted {len(sales_reps_data)} sales reps")

def populate_orders_and_items(conn):
    """Populate orders and order_items tables with 100 orders"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE orders CASCADE;")
    cursor.execute("TRUNCATE TABLE order_items CASCADE;")
    
    # Get all available product IDs and prices
    cursor.execute("SELECT product_id, price FROM products ORDER BY product_id")
    products = cursor.fetchall()
    
    if not products:
        print("  ✗ No products found! Run populate_products first.")
        return
    
    product_map = {pid: price for pid, price in products}
    available_product_ids = list(product_map.keys())
    
    # Get all available customer IDs
    cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    if not customer_ids:
        print("  ✗ No customers found! Run populate_customers first.")
        return
    
    # Get all available sales rep IDs
    cursor.execute("SELECT rep_id FROM sales_reps ORDER BY rep_id")
    rep_ids = [row[0] for row in cursor.fetchall()]
    
    if not rep_ids:
        print("  ✗ No sales reps found! Run populate_sales_reps first.")
        return
    
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'delivered', 'delivered']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'credit_card', 'credit_card']
    
    for i in range(100):
        customer_id = random.choice(customer_ids)
        rep_id = random.choice(rep_ids)
        order_date = datetime.now() - timedelta(days=random.randint(1, 180))
        status = random.choice(statuses)
        payment_method = random.choice(payment_methods)
        
        # Get random products for this order (1-4 items)
        num_items = min(random.randint(1, 4), len(available_product_ids))
        selected_product_ids = random.sample(available_product_ids, num_items)
        
        # Calculate total
        total_amount = 0
        items = []
        
        for product_id in selected_product_ids:
            price = product_map[product_id]
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
    print(f"  ✓ Inserted 100 orders with items")

def populate_revenue(conn):
    """Populate revenue table based on orders"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE revenue CASCADE;")
    
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
    print(f"  ✓ Inserted {len(orders)} revenue records")

def main():
    print("\nPopulating Sales Database...")
    
    try:
        conn = get_connection()
        print("  ✓ Connected to database")
        
        populate_customers(conn)
        populate_products(conn)
        populate_sales_reps(conn)
        populate_orders_and_items(conn)
        populate_revenue(conn)
        
        conn.close()
        print("  ✓ Sales database population complete!\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
