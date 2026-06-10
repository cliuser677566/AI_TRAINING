-- DRINKOO SQLite Database Schema
-- Version: 1.0
-- Purpose: Complete SKU management and freight tracking system

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'vendor', 'viewer')) DEFAULT 'viewer',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS states (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_name TEXT UNIQUE NOT NULL,
    capital_city TEXT NOT NULL,
    region TEXT,
    population_segment TEXT,
    total_customers INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    state_id INTEGER NOT NULL,
    city_name TEXT NOT NULL,
    customer_tier TEXT CHECK(customer_tier IN ('high', 'medium', 'low')) DEFAULT 'medium',
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

CREATE TABLE IF NOT EXISTS sku_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skus (
    sku_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    volume_ml INTEGER CHECK(volume_ml IN (200, 400, 500, 750, 1000, 1500, 2000)) NOT NULL,
    cost_manufacturing REAL NOT NULL CHECK(cost_manufacturing > 0),
    cost_shipping REAL NOT NULL CHECK(cost_shipping > 0),
    suggested_retail_price REAL NOT NULL CHECK(suggested_retail_price > 0),
    active_status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES sku_categories(category_id)
);

CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    sku_id TEXT NOT NULL,
    state_id INTEGER NOT NULL,
    quantity_units INTEGER NOT NULL CHECK(quantity_units > 0),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_amount REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

CREATE TABLE IF NOT EXISTS inventory_by_state (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id INTEGER NOT NULL,
    sku_id TEXT NOT NULL,
    quantity_in_stock INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id),
    UNIQUE(state_id, sku_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    state_id INTEGER NOT NULL,
    sku_id TEXT NOT NULL,
    quantity_units INTEGER NOT NULL CHECK(quantity_units > 0),
    cost_manufacturing_total REAL NOT NULL,
    cost_shipping_total REAL NOT NULL,
    shipment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tracking_code TEXT UNIQUE NOT NULL,
    current_status TEXT CHECK(current_status IN ('Order Confirmed', 'In Warehouse', 'Shipped', 'In Transit', 'Out for Delivery', 'Delivered')) DEFAULT 'Order Confirmed',
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id)
);

CREATE TABLE IF NOT EXISTS shipment_tracking (
    tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id TEXT NOT NULL,
    status TEXT CHECK(status IN ('Order Confirmed', 'In Warehouse', 'Shipped', 'In Transit', 'Out for Delivery', 'Delivered')) NOT NULL,
    location TEXT,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

CREATE TABLE IF NOT EXISTS sku_distribution_by_state (
    distribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id INTEGER NOT NULL,
    sku_id TEXT NOT NULL,
    allocation_percentage REAL NOT NULL CHECK(allocation_percentage > 0 AND allocation_percentage <= 100),
    expected_monthly_sales INTEGER NOT NULL,
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id),
    UNIQUE(state_id, sku_id)
);

CREATE INDEX IF NOT EXISTS idx_customers_state ON customers(state_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_sku ON sales_transactions(sku_id);
CREATE INDEX IF NOT EXISTS idx_sales_state ON sales_transactions(state_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_inventory_state ON inventory_by_state(state_id);
CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_by_state(sku_id);
CREATE INDEX IF NOT EXISTS idx_shipments_state ON shipments(state_id);
CREATE INDEX IF NOT EXISTS idx_shipments_sku ON shipments(sku_id);
CREATE INDEX IF NOT EXISTS idx_shipment_tracking_shipment ON shipment_tracking(shipment_id);
CREATE INDEX IF NOT EXISTS idx_sku_category ON skus(category_id);