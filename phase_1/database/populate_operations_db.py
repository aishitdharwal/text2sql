"""
Generate sample data for Operations Database
Run this after creating the schema
Usage: python3 populate_operations_db.py [host] [user] [password] [port]
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
            'database': 'operations_db',
            'user': sys.argv[2],
            'password': sys.argv[3],
            'port': int(sys.argv[4])
        }
    else:
        # Default configuration - UPDATE THESE
        return {
            'host': 'text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com',
            'database': 'operations_db',
            'user': 'postgres',
            'password': 'YourSecurePassword123',
            'port': 5432
        }

def get_connection():
    config = get_db_config()
    return psycopg2.connect(**config)

def populate_warehouses(conn):
    """Populate warehouses table with 10 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE warehouses CASCADE;")
    
    warehouses_data = [
        ('East Coast Distribution Center', '1500 Industrial Pkwy', 'Newark', 'NJ', 'USA', 150000, 'Robert Chen', '555-2001'),
        ('West Coast Fulfillment Hub', '2700 Commerce Dr', 'Los Angeles', 'CA', 'USA', 200000, 'Maria Garcia', '555-2002'),
        ('Midwest Logistics Center', '850 Warehouse Blvd', 'Chicago', 'IL', 'USA', 175000, 'James Wilson', '555-2003'),
        ('Southern Distribution Hub', '3200 Freight Ln', 'Dallas', 'TX', 'USA', 180000, 'Sarah Johnson', '555-2004'),
        ('Pacific Northwest Center', '1200 Cargo Way', 'Seattle', 'WA', 'USA', 140000, 'David Kim', '555-2005'),
        ('Southwest Operations Hub', '2100 Supply Chain Dr', 'Phoenix', 'AZ', 'USA', 165000, 'Jennifer Lee', '555-2006'),
        ('Mountain Region Center', '950 Distribution Ave', 'Denver', 'CO', 'USA', 130000, 'Michael Brown', '555-2007'),
        ('Southeast Fulfillment', '1800 Logistics Pkwy', 'Atlanta', 'GA', 'USA', 190000, 'Lisa Martinez', '555-2008'),
        ('Northeast Operations', '2500 Warehouse Rd', 'Boston', 'MA', 'USA', 155000, 'Kevin White', '555-2009'),
        ('Central Distribution', '1100 Industrial Way', 'Kansas City', 'MO', 'USA', 145000, 'Amanda Taylor', '555-2010'),
    ]
    
    for warehouse in warehouses_data:
        cursor.execute("""
            INSERT INTO warehouses (warehouse_name, location, city, state, country, capacity, manager_name, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, warehouse)
    
    conn.commit()
    print(f"  ✓ Inserted {len(warehouses_data)} warehouses")

def populate_suppliers(conn):
    """Populate suppliers table with 20 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE suppliers CASCADE;")
    
    suppliers_data = [
        ('Global Tech Supplies', 'John Anderson', 'john@globaltech.com', '555-3001', '100 Tech Park', 'San Francisco', 'USA', 4.5, 'net_30'),
        ('Pacific Electronics Co', 'Lisa Chen', 'lisa@pacificelec.com', '555-3002', '250 Electronics Way', 'Seattle', 'USA', 4.7, 'net_30'),
        ('EuroSupply International', 'Hans Mueller', 'hans@eurosupply.com', '555-3003', '50 Trade Street', 'London', 'UK', 4.2, 'net_60'),
        ('Asian Manufacturing Ltd', 'Wei Zhang', 'wei@asianmfg.com', '555-3004', '88 Industrial Rd', 'Shanghai', 'China', 4.6, 'net_45'),
        ('American Parts Wholesale', 'Sarah Johnson', 'sarah@amparts.com', '555-3005', '500 Supply Dr', 'Chicago', 'USA', 4.4, 'net_30'),
        ('Quality Components Inc', 'Michael Davis', 'michael@qualitycomp.com', '555-3006', '1200 Parts Ave', 'Detroit', 'USA', 4.8, 'net_30'),
        ('NextGen Materials', 'Emily Wilson', 'emily@nextgen.com', '555-3007', '300 Innovation Blvd', 'Austin', 'USA', 4.3, 'net_45'),
        ('Global Logistics Supply', 'Robert Lee', 'robert@globallog.com', '555-3008', '750 Shipping Ln', 'Los Angeles', 'USA', 4.5, 'net_30'),
        ('TechParts Distribution', 'Jennifer Garcia', 'jennifer@techparts.com', '555-3009', '400 Distribution Dr', 'Dallas', 'USA', 4.6, 'net_30'),
        ('Industrial Solutions Co', 'David Martinez', 'david@indsolutions.com', '555-3010', '900 Industrial Pkwy', 'Houston', 'USA', 4.4, 'net_60'),
        ('Premium Supplies Ltd', 'Amanda Brown', 'amanda@premiumsup.com', '555-3011', '150 Premium Way', 'Boston', 'USA', 4.7, 'net_30'),
        ('Reliable Components', 'Kevin Thompson', 'kevin@reliablecomp.com', '555-3012', '600 Component St', 'Atlanta', 'USA', 4.5, 'net_45'),
        ('Smart Materials Group', 'Linda White', 'linda@smartmat.com', '555-3013', '200 Materials Rd', 'Phoenix', 'USA', 4.3, 'net_30'),
        ('Advanced Tech Supply', 'James Rodriguez', 'james@advtech.com', '555-3014', '850 Tech Center', 'Denver', 'USA', 4.6, 'net_30'),
        ('Precision Parts Co', 'Patricia Kim', 'patricia@precisionparts.com', '555-3015', '1500 Precision Ave', 'Miami', 'USA', 4.4, 'net_60'),
        ('Global Components Hub', 'Christopher Lee', 'chris@globalcomp.com', '555-3016', '2000 Hub Blvd', 'Orlando', 'USA', 4.5, 'net_30'),
        ('Superior Supply Chain', 'Barbara Chen', 'barbara@superiorsup.com', '555-3017', '700 Supply Chain Dr', 'Tampa', 'USA', 4.7, 'net_45'),
        ('Elite Manufacturing', 'Richard Wang', 'richard@elitemfg.com', '555-3018', '1100 Manufacturing Way', 'Charlotte', 'USA', 4.8, 'net_30'),
        ('Quality First Supplies', 'Susan Patel', 'susan@qualityfirst.com', '555-3019', '300 Quality Ln', 'Portland', 'USA', 4.6, 'net_30'),
        ('Trusted Partners Co', 'Daniel Foster', 'daniel@trustedpart.com', '555-3020', '950 Partners Ave', 'Nashville', 'USA', 4.5, 'net_60'),
    ]
    
    for supplier in suppliers_data:
        cursor.execute("""
            INSERT INTO suppliers (supplier_name, contact_person, email, phone, address, city, country, rating, payment_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, supplier)
    
    conn.commit()
    print(f"  ✓ Inserted {len(suppliers_data)} suppliers")

def populate_inventory(conn):
    """Populate inventory table - products distributed across warehouses"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE inventory CASCADE;")
    
    # Get warehouse IDs
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouse_ids = [row[0] for row in cursor.fetchall()]
    
    # Create inventory records for products 1-30 across different warehouses
    for product_id in range(1, 31):
        # Each product in 3-5 random warehouses
        num_warehouses = random.randint(3, 5)
        selected_warehouses = random.sample(warehouse_ids, num_warehouses)
        
        for warehouse_id in selected_warehouses:
            quantity = random.randint(10, 500)
            reorder_level = random.randint(20, 100)
            reorder_quantity = random.randint(50, 200)
            last_restock = datetime.now().date() - timedelta(days=random.randint(1, 90))
            location_bin = f"{chr(random.randint(65, 72))}-{random.randint(1, 20)}-{random.randint(1, 10)}"
            
            cursor.execute("""
                INSERT INTO inventory (warehouse_id, product_id, quantity_on_hand, reorder_level, 
                                     reorder_quantity, last_restock_date, location_bin)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (warehouse_id, product_id, quantity, reorder_level, reorder_quantity, last_restock, location_bin))
    
    conn.commit()
    total_records = 30 * 4  # Approximately
    print(f"  ✓ Inserted ~{total_records} inventory records")

def populate_shipments(conn):
    """Populate shipments table - for orders from sales database"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE shipments CASCADE;")
    
    carriers = ['fedex', 'ups', 'usps', 'dhl']
    statuses = ['preparing', 'shipped', 'in_transit', 'delivered', 'delivered', 'delivered']
    
    # Get warehouse IDs
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouse_ids = [row[0] for row in cursor.fetchall()]
    
    # Create shipments for orders 1-100
    for order_id in range(1, 101):
        warehouse_id = random.choice(warehouse_ids)
        carrier = random.choice(carriers)
        tracking_number = f"{carrier.upper()}{random.randint(100000000, 999999999)}"
        
        ship_date = datetime.now() - timedelta(days=random.randint(1, 90))
        estimated_delivery = (ship_date + timedelta(days=random.randint(3, 7))).date()
        
        status = random.choice(statuses)
        
        if status == 'delivered':
            actual_delivery = (ship_date + timedelta(days=random.randint(3, 8))).date()
        else:
            actual_delivery = None
        
        shipping_cost = round(random.uniform(5.99, 29.99), 2)
        
        cursor.execute("""
            INSERT INTO shipments (order_id, warehouse_id, carrier, tracking_number, ship_date, 
                                 estimated_delivery, actual_delivery, shipment_status, shipping_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (order_id, warehouse_id, carrier, tracking_number, ship_date, estimated_delivery, 
              actual_delivery, status, shipping_cost))
    
    conn.commit()
    print(f"  ✓ Inserted 100 shipments")

def populate_logistics(conn):
    """Populate logistics table - tracking events for shipments"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE logistics CASCADE;")
    
    event_types = ['picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'exception']
    locations = ['Origin Facility', 'Regional Hub', 'Local Distribution Center', 'Out for Delivery', 'Delivered']
    delay_reasons = [None, None, None, 'weather', 'customs', 'address_issue']
    
    # Get shipments
    cursor.execute("SELECT shipment_id, ship_date, shipment_status FROM shipments")
    shipments = cursor.fetchall()
    
    total_events = 0
    for shipment_id, ship_date, status in shipments:
        # Generate 3-6 tracking events per shipment
        num_events = random.randint(3, 6)
        current_time = ship_date
        
        for i in range(num_events):
            event_type = event_types[min(i, len(event_types)-1)]
            location = locations[min(i, len(locations)-1)]
            delay = random.choice(delay_reasons) if event_type == 'exception' else None
            
            description = f"Package {event_type.replace('_', ' ')} at {location}"
            if delay:
                description += f" - Delayed due to {delay}"
            
            cursor.execute("""
                INSERT INTO logistics (shipment_id, event_timestamp, location, event_type, 
                                     event_description, delay_reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (shipment_id, current_time, location, event_type, description, delay))
            
            current_time += timedelta(hours=random.randint(6, 24))
            total_events += 1
    
    conn.commit()
    print(f"  ✓ Inserted {total_events} logistics events")

def populate_purchase_orders(conn):
    """Populate purchase_orders table - orders from suppliers"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE purchase_orders CASCADE;")
    
    statuses = ['pending', 'confirmed', 'shipped', 'received', 'received', 'received']
    
    # Get supplier and warehouse IDs
    cursor.execute("SELECT supplier_id FROM suppliers")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouse_ids = [row[0] for row in cursor.fetchall()]
    
    # Create 50 purchase orders
    for i in range(50):
        supplier_id = random.choice(supplier_ids)
        warehouse_id = random.choice(warehouse_ids)
        order_date = (datetime.now() - timedelta(days=random.randint(1, 180))).date()
        expected_delivery = order_date + timedelta(days=random.randint(7, 30))
        status = random.choice(statuses)
        
        if status == 'received':
            actual_delivery = order_date + timedelta(days=random.randint(7, 35))
        else:
            actual_delivery = None
        
        total_amount = round(random.uniform(5000, 50000), 2)
        
        cursor.execute("""
            INSERT INTO purchase_orders (supplier_id, warehouse_id, order_date, expected_delivery, 
                                        actual_delivery, status, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (supplier_id, warehouse_id, order_date, expected_delivery, actual_delivery, status, total_amount))
    
    conn.commit()
    print(f"  ✓ Inserted 50 purchase orders")

def main():
    print("\nPopulating Operations Database...")
    
    try:
        conn = get_connection()
        print("  ✓ Connected to database")
        
        populate_warehouses(conn)
        populate_suppliers(conn)
        populate_inventory(conn)
        populate_shipments(conn)
        populate_logistics(conn)
        populate_purchase_orders(conn)
        
        conn.close()
        print("  ✓ Operations database population complete!\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
