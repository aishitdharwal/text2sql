-- =====================================================
-- OPERATIONS DATABASE SCHEMA
-- =====================================================

-- Create operations database (run this separately as postgres user)
-- CREATE DATABASE operations_db;

-- Connect to operations_db before running below
-- \c operations_db;

-- Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    capacity INTEGER NOT NULL,
    manager_name VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE warehouses IS 'Warehouse locations and capacity information';
COMMENT ON COLUMN warehouses.capacity IS 'Total storage capacity in square feet';
COMMENT ON COLUMN warehouses.manager_name IS 'Name of warehouse manager';

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    rating DECIMAL(3, 2),
    payment_terms VARCHAR(100)
);

COMMENT ON TABLE suppliers IS 'Supplier information and contact details';
COMMENT ON COLUMN suppliers.rating IS 'Supplier rating from 0.00 to 5.00';
COMMENT ON COLUMN suppliers.payment_terms IS 'Payment terms: net_30, net_60, advance, cod';

-- Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    product_id INTEGER NOT NULL,
    quantity_on_hand INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,
    last_restock_date DATE,
    location_bin VARCHAR(50)
);

COMMENT ON TABLE inventory IS 'Current inventory levels across warehouses';
COMMENT ON COLUMN inventory.product_id IS 'Reference to product ID from sales database';
COMMENT ON COLUMN inventory.reorder_level IS 'Minimum quantity before reorder is triggered';
COMMENT ON COLUMN inventory.reorder_quantity IS 'Standard quantity to reorder';
COMMENT ON COLUMN inventory.location_bin IS 'Physical location within warehouse';

-- Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    carrier VARCHAR(100) NOT NULL,
    tracking_number VARCHAR(255),
    ship_date TIMESTAMP,
    estimated_delivery DATE,
    actual_delivery DATE,
    shipment_status VARCHAR(50) DEFAULT 'preparing',
    shipping_cost DECIMAL(10, 2)
);

COMMENT ON TABLE shipments IS 'Order shipment tracking and delivery information';
COMMENT ON COLUMN shipments.order_id IS 'Reference to order ID from sales database';
COMMENT ON COLUMN shipments.carrier IS 'Shipping carrier: fedex, ups, usps, dhl';
COMMENT ON COLUMN shipments.shipment_status IS 'Status: preparing, shipped, in_transit, delivered, failed';

-- Logistics Table
CREATE TABLE IF NOT EXISTS logistics (
    logistics_id SERIAL PRIMARY KEY,
    shipment_id INTEGER NOT NULL REFERENCES shipments(shipment_id),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(255),
    event_type VARCHAR(100),
    event_description TEXT,
    delay_reason VARCHAR(255)
);

COMMENT ON TABLE logistics IS 'Shipment tracking events and logistics updates';
COMMENT ON COLUMN logistics.event_type IS 'Event: picked_up, in_transit, out_for_delivery, delivered, exception';
COMMENT ON COLUMN logistics.delay_reason IS 'Reason for delay if applicable: weather, customs, address_issue';

-- Purchase Orders Table
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    order_date DATE NOT NULL,
    expected_delivery DATE,
    actual_delivery DATE,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL
);

COMMENT ON TABLE purchase_orders IS 'Purchase orders from suppliers for inventory replenishment';
COMMENT ON COLUMN purchase_orders.status IS 'Status: pending, confirmed, shipped, received, cancelled';

-- Create indexes for performance
CREATE INDEX idx_inventory_warehouse ON inventory(warehouse_id);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_shipments_order ON shipments(order_id);
CREATE INDEX idx_shipments_warehouse ON shipments(warehouse_id);
CREATE INDEX idx_shipments_status ON shipments(shipment_status);
CREATE INDEX idx_logistics_shipment ON logistics(shipment_id);
CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_warehouse ON purchase_orders(warehouse_id);
