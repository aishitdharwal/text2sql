-- =====================================================
-- SALES DATABASE SCHEMA
-- =====================================================

-- Create sales database (run this separately as postgres user)
-- CREATE DATABASE sales_db;

-- Connect to sales_db before running below
-- \c sales_db;

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE customers IS 'Stores customer information for the ecommerce platform';
COMMENT ON COLUMN customers.customer_id IS 'Unique identifier for each customer';
COMMENT ON COLUMN customers.email IS 'Customer email address, must be unique';
COMMENT ON COLUMN customers.created_at IS 'Timestamp when customer account was created';

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS 'Product catalog with pricing and inventory information';
COMMENT ON COLUMN products.product_id IS 'Unique identifier for each product';
COMMENT ON COLUMN products.price IS 'Selling price to customers';
COMMENT ON COLUMN products.cost IS 'Cost of goods sold (COGS)';
COMMENT ON COLUMN products.stock_quantity IS 'Current available inventory';

-- Sales Reps Table
CREATE TABLE IF NOT EXISTS sales_reps (
    rep_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE,
    territory VARCHAR(100),
    commission_rate DECIMAL(5, 2) DEFAULT 5.00
);

COMMENT ON TABLE sales_reps IS 'Sales representatives managing customer relationships';
COMMENT ON COLUMN sales_reps.territory IS 'Geographic territory assigned to the sales rep';
COMMENT ON COLUMN sales_reps.commission_rate IS 'Commission percentage on sales';

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    rep_id INTEGER REFERENCES sales_reps(rep_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT,
    payment_method VARCHAR(50)
);

COMMENT ON TABLE orders IS 'Customer orders with status and payment information';
COMMENT ON COLUMN orders.status IS 'Order status: pending, processing, shipped, delivered, cancelled';
COMMENT ON COLUMN orders.total_amount IS 'Total order value including all items';
COMMENT ON COLUMN orders.payment_method IS 'Payment method used: credit_card, debit_card, paypal, etc';

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

COMMENT ON TABLE order_items IS 'Line items for each order showing products purchased';
COMMENT ON COLUMN order_items.unit_price IS 'Price per unit at the time of order';
COMMENT ON COLUMN order_items.subtotal IS 'Total for this line item (quantity * unit_price)';

-- Revenue Table (aggregated view)
CREATE TABLE IF NOT EXISTS revenue (
    revenue_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    revenue_date DATE NOT NULL,
    gross_revenue DECIMAL(10, 2) NOT NULL,
    cost_of_goods DECIMAL(10, 2) NOT NULL,
    net_revenue DECIMAL(10, 2) NOT NULL,
    commission_paid DECIMAL(10, 2) DEFAULT 0
);

COMMENT ON TABLE revenue IS 'Revenue tracking with profit margins and commission data';
COMMENT ON COLUMN revenue.gross_revenue IS 'Total revenue before costs';
COMMENT ON COLUMN revenue.net_revenue IS 'Profit after deducting COGS and commission';

-- Create indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_rep ON orders(rep_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_revenue_date ON revenue(revenue_date);
