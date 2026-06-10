"""
DRINKOO Database Initialization and Seed Data Generation Script
Purpose: Create SQLite database with all required tables and populate with realistic dummy data
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random
import os

# Database path
DATABASE_PATH = r'c:\Users\Administrator\Downloads\DRNKOO-DE\database\drinkoo.db'
SCHEMA_PATH = r'c:\Users\Administrator\Downloads\DRNKOO-DE\backend\app\database\schema.sql'

# Indian States and Capitals (28 states + 8 UTs = 36 total)
INDIAN_STATES_CAPITALS = {
    'Andhra Pradesh': 'Hyderabad',
    'Arunachal Pradesh': 'Itanagar',
    'Assam': 'Dispur',
    'Bihar': 'Patna',
    'Chhattisgarh': 'Raipur',
    'Goa': 'Panaji',
    'Gujarat': 'Gandhinagar',
    'Haryana': 'Chandigarh',
    'Himachal Pradesh': 'Shimla',
    'Jharkhand': 'Ranchi',
    'Karnataka': 'Bangalore',
    'Kerala': 'Thiruvananthapuram',
    'Madhya Pradesh': 'Bhopal',
    'Maharashtra': 'Mumbai',
    'Manipur': 'Imphal',
    'Meghalaya': 'Shillong',
    'Mizoram': 'Aizawl',
    'Nagaland': 'Kohima',
    'Odisha': 'Bhubaneswar',
    'Punjab': 'Chandigarh',
    'Rajasthan': 'Jaipur',
    'Sikkim': 'Gangtok',
    'Tamil Nadu': 'Chennai',
    'Telangana': 'Hyderabad',
    'Tripura': 'Agartala',
    'Uttar Pradesh': 'Lucknow',
    'Uttarakhand': 'Dehradun',
    'West Bengal': 'Kolkata',
    # Union Territories
    'Andaman and Nicobar Islands': 'Port Blair',
    'Chandigarh': 'Chandigarh',
    'Dadra and Nagar Haveli': 'Silvassa',
    'Daman and Diu': 'Daman',
    'Delhi': 'New Delhi',
    'Jammu and Kashmir': 'Srinagar',
    'Ladakh': 'Leh',
    'Lakshadweep': 'Kavaratti',
    'Puducherry': 'Puducherry'
}

# Population segments for realistic distribution
POPULATION_SEGMENTS = {
    'Maharashtra': 150, 'Uttar Pradesh': 140, 'Karnataka': 110, 'Tamil Nadu': 100,
    'Gujarat': 95, 'West Bengal': 90, 'Rajasthan': 85, 'Madhya Pradesh': 80,
    'Andhra Pradesh': 75, 'Telangana': 70, 'Bihar': 65, 'Punjab': 55,
    'Haryana': 50, 'Kerala': 48, 'Jharkhand': 45, 'Odisha': 42,
    'Chhattisgarh': 40, 'Assam': 38, 'Himachal Pradesh': 25, 'Uttarakhand': 23,
    'Goa': 18, 'Tripura': 15, 'Manipur': 12, 'Nagaland': 10, 'Arunachal Pradesh': 10,
    'Meghalaya': 12, 'Sikkim': 8, 'Mizoram': 8, 'Andaman and Nicobar Islands': 5,
    'Chandigarh': 12, 'Dadra and Nagar Haveli': 5, 'Daman and Diu': 4,
    'Delhi': 85, 'Jammu and Kashmir': 40, 'Ladakh': 3, 'Lakshadweep': 2, 'Puducherry': 8
}

def create_database():
    """Create database and execute schema"""
    print("[1/7] Creating database and schema...")
    
    # Remove existing database if present
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    
    # Read and execute schema
    with open(SCHEMA_PATH, 'r') as schema_file:
        schema_sql = schema_file.read()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    print("   ✓ Database created with all 10 tables and indexes")
    return conn

def populate_states(conn):
    """Populate Indian states and capitals"""
    print("[2/7] Populating states/capitals master data...")
    cursor = conn.cursor()
    
    for state_name, capital_city in INDIAN_STATES_CAPITALS.items():
        population_segment = POPULATION_SEGMENTS.get(state_name, 10)
        cursor.execute('''
            INSERT INTO states (state_name, capital_city, region, population_segment)
            VALUES (?, ?, ?, ?)
        ''', (state_name, capital_city, capital_city, population_segment))
    
    conn.commit()
    print(f"   ✓ Populated {len(INDIAN_STATES_CAPITALS)} states/UTs with capitals")

def populate_sku_categories(conn):
    """Populate SKU categories"""
    print("[3/7] Populating SKU categories...")
    cursor = conn.cursor()
    
    categories = [
        ('Soda', 'Carbonated soft drinks - Cola, Lemon-Lime, Fruit Flavors'),
        ('Energy Drinks', 'High-energy formulations for active individuals'),
        ('Fruit Juices', 'Pure and mixed fruit juices'),
        ('Iced Tea', 'Cold tea beverages in various flavors'),
        ('Sparkling Water', 'Carbonated water with natural flavors'),
        ('Health Drinks', 'Protein and nutrient-enriched beverages'),
        ('Regional/Special', 'Regional preferences including coconut water, sugarcane')
    ]
    
    for category_name, description in categories:
        cursor.execute('''
            INSERT INTO sku_categories (category_name, description)
            VALUES (?, ?)
        ''', (category_name, description))
    
    conn.commit()
    print(f"   ✓ Populated {len(categories)} product categories")

def populate_skus(conn):
    """Generate 50 SKUs"""
    print("[4/7] Generating 50 SKUs...")
    cursor = conn.cursor()
    
    skus_data = [
        # Soda (10 SKUs)
        ('SK_COLA_500ML', 'Cola Premium', 1, 500, 12, 8, 35),
        ('SK_LEMONLIME_500ML', 'Lemon-Lime Blast', 1, 500, 11, 8, 32),
        ('SK_ORANGE_500ML', 'Orange Crush', 1, 500, 11, 8, 30),
        ('SK_GRAPE_500ML', 'Grape Fizz', 1, 500, 10, 8, 28),
        ('SK_STRAWBERRY_500ML', 'Strawberry Splash', 1, 500, 10, 8, 28),
        ('SK_MANGO_500ML', 'Mango Burst', 1, 500, 10, 8, 30),
        ('SK_PINEAPPLE_500ML', 'Pineapple Pop', 1, 500, 10, 8, 28),
        ('SK_WATERMELON_500ML', 'Watermelon Wave', 1, 500, 9, 8, 26),
        ('SK_PEACH_500ML', 'Peach Passion', 1, 500, 10, 8, 28),
        ('SK_MIXEDBERRIES_500ML', 'Mixed Berry Mix', 1, 500, 11, 8, 32),
        # Energy Drinks (8 SKUs)
        ('SK_ENERGY_ULTRA_500ML', 'Ultra Energy Boost', 2, 500, 25, 10, 80),
        ('SK_ENERGY_POWER_500ML', 'Power Surge', 2, 500, 24, 10, 78),
        ('SK_ENERGY_EXTREME_500ML', 'Extreme Energy', 2, 500, 26, 10, 85),
        ('SK_ENERGY_BERRY_500ML', 'Berry Energy', 2, 500, 24, 10, 76),
        ('SK_ENERGY_CITRUS_500ML', 'Citrus Charge', 2, 500, 23, 10, 74),
        ('SK_ENERGY_MANGO_500ML', 'Mango Energy', 2, 500, 24, 10, 75),
        ('SK_ENERGY_TROPICAL_500ML', 'Tropical Thunder', 2, 500, 25, 10, 78),
        ('SK_ENERGY_MINT_500ML', 'Mint Rush', 2, 500, 23, 10, 72),
        # Fruit Juices (8 SKUs)
        ('SK_JUICE_ORANGE_500ML', 'Fresh Orange Juice', 3, 500, 15, 9, 45),
        ('SK_JUICE_APPLE_500ML', 'Pure Apple Juice', 3, 500, 14, 9, 42),
        ('SK_JUICE_MANGO_500ML', 'Mango Nectar', 3, 500, 16, 9, 48),
        ('SK_JUICE_POMEGRANATE_500ML', 'Pomegranate Power', 3, 500, 18, 9, 55),
        ('SK_JUICE_CRANBERRY_500ML', 'Cranberry Fresh', 3, 500, 17, 9, 52),
        ('SK_JUICE_MIXED_500ML', 'Mixed Fruit Blend', 3, 500, 16, 9, 48),
        ('SK_JUICE_PINEAPPLE_500ML', 'Pineapple Juice', 3, 500, 15, 9, 44),
        ('SK_JUICE_GRAPE_500ML', 'Grape Juice', 3, 500, 14, 9, 42),
        # Iced Tea (6 SKUs)
        ('SK_TEA_LEMON_500ML', 'Iced Lemon Tea', 4, 500, 12, 8, 38),
        ('SK_TEA_MINT_500ML', 'Iced Mint Tea', 4, 500, 11, 8, 36),
        ('SK_TEA_PEACH_500ML', 'Peach Iced Tea', 4, 500, 12, 8, 38),
        ('SK_TEA_GINGER_500ML', 'Ginger Zest Tea', 4, 500, 13, 8, 40),
        ('SK_TEA_HIBISCUS_500ML', 'Hibiscus Tea', 4, 500, 11, 8, 35),
        ('SK_TEA_CHAMOMILE_500ML', 'Chamomile Tea', 4, 500, 10, 8, 32),
        # Sparkling Water (6 SKUs)
        ('SK_SPARKLE_PLAIN_500ML', 'Plain Sparkling Water', 5, 500, 6, 7, 18),
        ('SK_SPARKLE_LEMON_500ML', 'Lemon Sparkling Water', 5, 500, 7, 7, 20),
        ('SK_SPARKLE_BERRY_500ML', 'Berry Sparkling Water', 5, 500, 7, 7, 21),
        ('SK_SPARKLE_CUCUMBER_500ML', 'Cucumber Sparkling Water', 5, 500, 7, 7, 20),
        ('SK_SPARKLE_ORANGE_500ML', 'Orange Sparkling Water', 5, 500, 7, 7, 20),
        ('SK_SPARKLE_GRAPEFRUIT_500ML', 'Grapefruit Sparkling', 5, 500, 8, 7, 22),
        # Health Drinks (6 SKUs)
        ('SK_HEALTH_PROTEIN_500ML', 'Protein Shake Plus', 6, 500, 28, 11, 85),
        ('SK_HEALTH_WELLNESS_500ML', 'Wellness Blend', 6, 500, 26, 11, 78),
        ('SK_HEALTH_IMMUNITY_500ML', 'Immunity Booster', 6, 500, 27, 11, 82),
        ('SK_HEALTH_VITAMINS_500ML', 'Vitamin Rich', 6, 500, 25, 11, 75),
        ('SK_HEALTH_FIBER_500ML', 'Fiber Complete', 6, 500, 24, 11, 72),
        ('SK_HEALTH_ENERGY_500ML', 'Healthy Energy', 6, 500, 26, 11, 78),
        # Regional/Special (6 SKUs)
        ('SK_REGIONAL_COCONUT_500ML', 'Fresh Coconut Water', 7, 500, 14, 9, 42),
        ('SK_REGIONAL_SUGARCANE_500ML', 'Pure Sugarcane Juice', 7, 500, 13, 9, 38),
        ('SK_REGIONAL_BUTTER_500ML', 'Buttermilk Traditional', 7, 500, 8, 8, 24),
        ('SK_REGIONAL_LASSI_500ML', 'Sweet Lassi', 7, 500, 10, 8, 30),
        ('SK_REGIONAL_NIMBU_500ML', 'Nimbu Pani', 7, 500, 6, 7, 18),
        ('SK_REGIONAL_BADAM_500ML', 'Almond Milk', 7, 500, 18, 9, 54)
    ]
    
    for sku_id, product_name, category_id, volume_ml, cost_mfg, cost_ship, retail_price in skus_data:
        cursor.execute('''
            INSERT INTO skus (sku_id, product_name, category_id, volume_ml, cost_manufacturing, cost_shipping, suggested_retail_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sku_id, product_name, category_id, volume_ml, cost_mfg, cost_ship, retail_price))
    
    conn.commit()
    print(f"   ✓ Generated {len(skus_data)} SKUs (10 sodas + 40 others)")

def populate_customers(conn):
    """Generate 1,000 customers distributed by state population"""
    print("[5/7] Generating 1,000 customers distributed by state...")
    cursor = conn.cursor()
    
    # Get all states with their IDs
    cursor.execute('SELECT state_id, state_name FROM states')
    states = cursor.fetchall()
    state_dict = {state[1]: state[0] for state in states}
    
    # Calculate customer distribution
    total_population = sum(POPULATION_SEGMENTS.values())
    customer_count = 0
    customers_data = []
    
    for state_name, state_id in state_dict.items():
        population_segment = POPULATION_SEGMENTS.get(state_name, 5)
        allocated_customers = max(1, int((population_segment / total_population) * 1000))
        
        for _ in range(allocated_customers):
            customer_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"
            city_name = state_name  # Simplified: use state name as city
            customer_tier = random.choices(['high', 'medium', 'low'], weights=[10, 60, 30])[0]
            customers_data.append((customer_id, state_id, city_name, customer_tier, f"contact_{customer_id}@drinkoo.com"))
            customer_count += 1
            
            if customer_count >= 1000:
                break
        
        if customer_count >= 1000:
            break
    
    # Ensure exactly 1000 customers
    customers_data = customers_data[:1000]
    
    # Insert customers
    cursor.executemany('''
        INSERT INTO customers (customer_id, state_id, city_name, customer_tier, contact_info)
        VALUES (?, ?, ?, ?, ?)
    ''', customers_data)
    
    conn.commit()
    print(f"   ✓ Generated 1,000 customers across all {len(state_dict)} states/UTs")

def populate_sku_distribution(conn):
    """Calculate and populate SKU distribution by state"""
    print("[6/7] Calculating SKU distribution by state...")
    cursor = conn.cursor()
    
    cursor.execute('SELECT state_id FROM states')
    states = cursor.fetchall()
    
    cursor.execute('SELECT sku_id FROM skus')
    skus = cursor.fetchall()
    
    # Demand distribution by tier
    demand_tiers = {
        'Tier1': 0.375,  # 37.5% - Popular SKUs (sodas)
        'Tier2': 0.325,  # 32.5% - Mid-market SKUs
        'Tier3': 0.30    # 30% - Niche SKUs
    }
    
    sku_tier_map = {
        'SK_COLA_500ML': 'Tier1', 'SK_LEMONLIME_500ML': 'Tier1',
        'SK_ORANGE_500ML': 'Tier2', 'SK_GRAPE_500ML': 'Tier2', 'SK_STRAWBERRY_500ML': 'Tier2',
        'SK_MANGO_500ML': 'Tier2', 'SK_PINEAPPLE_500ML': 'Tier2', 'SK_WATERMELON_500ML': 'Tier2',
        'SK_PEACH_500ML': 'Tier2', 'SK_MIXEDBERRIES_500ML': 'Tier2'
    }
    
    distribution_data = []
    
    for state in states:
        state_id = state[0]
        # Get customer count for state to estimate monthly sales
        cursor.execute('SELECT COUNT(*) FROM customers WHERE state_id = ?', (state_id,))
        customer_count = cursor.fetchone()[0]
        
        for sku in skus:
            sku_id = sku[0]
            sku_tier = sku_tier_map.get(sku_id, 'Tier3')
            allocation_percentage = demand_tiers[sku_tier]
            expected_monthly_sales = max(5, int(customer_count * 2 * allocation_percentage / 50))  # ~2 transactions per customer per month
            
            distribution_data.append((state_id, sku_id, allocation_percentage * 100, expected_monthly_sales))
    
    cursor.executemany('''
        INSERT INTO sku_distribution_by_state (state_id, sku_id, allocation_percentage, expected_monthly_sales)
        VALUES (?, ?, ?, ?)
    ''', distribution_data)
    
    conn.commit()
    print(f"   ✓ Generated distribution matrix for {len(distribution_data)} state-SKU combinations")

def populate_sales_transactions(conn):
    """Generate ~5,000 initial sales transactions"""
    print("[7/7] Generating ~5,000 initial sales transactions...")
    cursor = conn.cursor()
    
    # Get all customers, SKUs, and states
    cursor.execute('SELECT customer_id, state_id FROM customers')
    customers = cursor.fetchall()
    
    cursor.execute('SELECT sku_id, suggested_retail_price FROM skus')
    skus = {sku[0]: sku[1] for sku in cursor.fetchall()}
    
    transactions_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    # Generate transactions proportional to customers
    for customer_id, state_id in customers:
        # Each customer makes 3-5 purchases per month on average
        num_transactions = random.randint(3, 5)
        
        for _ in range(num_transactions):
            transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
            sku_id = random.choice(list(skus.keys()))
            quantity_units = random.randint(1, 20)
            transaction_date = base_date + timedelta(days=random.randint(0, 30))
            retail_price = skus[sku_id]
            transaction_amount = quantity_units * retail_price * random.uniform(0.8, 1.0)  # 80-100% of retail
            
            transactions_data.append((
                transaction_id, customer_id, sku_id, state_id, quantity_units,
                transaction_date.strftime('%Y-%m-%d %H:%M:%S'), transaction_amount
            ))
    
    cursor.executemany('''
        INSERT INTO sales_transactions (transaction_id, customer_id, sku_id, state_id, quantity_units, transaction_date, transaction_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', transactions_data)
    
    conn.commit()
    print(f"   ✓ Generated {len(transactions_data)} sales transactions")

def main():
    print("\n" + "="*80)
    print("DRINKOO DATABASE INITIALIZATION - PHASE 1 EXECUTION")
    print("="*80 + "\n")
    
    try:
        # Create database
        conn = create_database()
        
        # Populate master data
        populate_states(conn)
        populate_sku_categories(conn)
        populate_skus(conn)
        populate_customers(conn)
        populate_sku_distribution(conn)
        populate_sales_transactions(conn)
        
        # Verify data
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM states')
        state_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM customers')
        customer_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM skus')
        sku_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM sales_transactions')
        transaction_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n" + "="*80)
        print("PHASE 1 EXECUTION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\nDatabase Summary:")
        print(f"  • States/UTs: {state_count}")
        print(f"  • Customers: {customer_count}")
        print(f"  • SKUs: {sku_count}")
        print(f"  • Sales Transactions: {transaction_count}")
        print(f"  • Database Location: {DATABASE_PATH}")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
