# DRINKOO SKU Management & Freight Tracking Platform - Implementation Plan

## Executive Summary
DRINKOO is building a comprehensive SKU (Stock Keeping Unit) management and real-time freight tracking platform for a beverage company operating across India. This platform enables vendors to track sales performance by state and SKU, manage inventory, and monitor shipments in real-time with near-zero latency ETL processing.

---

## 1. DATA FOUNDATION & ARCHITECTURE

### 1.1 Customer Dataset (1,000 Customers)
**Geographic Distribution:**
- Coverage: All 28 states + 8 union territories of India
- Population-based distribution ensuring realistic market representation
- Every state capital included
- Distribution formula: Customer allocation proportional to state population/economic size

**Customer Data Points:**
- Unique customer_id (UUID)
- State and capital city assignment
- City/region/district
- Customer tier (high/medium/low volume)
- Purchase frequency metadata
- Account creation date

### 1.2 SKU Portfolio (50 Total SKUs)

**Category 1: Soda Flavors (10 SKUs)**
1. Cola
2. Lemon-Lime
3. Orange
4. Grape
5. Strawberry
6. Mango
7. Pineapple
8. Watermelon
9. Peach
10. Mixed Berries

**Category 2: Energy Drinks (8 SKUs)**
- Various formulations and flavors

**Category 3: Fruit Juices (8 SKUs)**
- Orange, Apple, Mango, Pomegranate, Cranberry, etc.

**Category 4: Iced Tea (6 SKUs)**
- Lemon, Mint, Peach, Ginger, etc.

**Category 5: Sparkling Water (6 SKUs)**
- Plain and flavored variants

**Category 6: Health Drinks (6 SKUs)**
- Protein-infused beverages

**Category 7: Regional/Special Products (6 SKUs)**
- Coconut water, Sugarcane juice, regional preferences

### 1.3 SKU Attributes & Specifications

Each SKU contains:
- **SKU_ID**: Unique identifier (e.g., SK_COLA_500ML)
- **Product_Name**: Full product name
- **Category**: Classification
- **Volume_Options**: 200ml, 400ml, 500ml, 750ml, 1L, 1.5L, 2L
  - **IMPORTANT**: Only whole numbers and .5 decimals allowed (1L, 1.5L, 2L)
  - **NOT ALLOWED**: 1.25L, 1.75L, 2.25L (beverage standard compliance)
- **Cost_Manufacturing**: Per-unit manufacturing cost (INR)
- **Cost_Shipping**: Per-shipment shipping cost (INR)
- **Suggested_Retail_Price**: Manufacturer suggested price
- **Created_Date**: Timestamp
- **Active_Status**: Boolean (true/false)

### 1.4 Distribution Logic & Statistical Relevance

**Customer Distribution by State:**
- Use state population data to allocate 1,000 customers proportionally
- Minimum 1 customer per state (ensures all states covered)
- Example: Maharashtra (high population) = 120+ customers; Mizoram (low) = 10+ customers

**SKU Distribution Strategy:**
- **Demand Curve Model**:
  - Tier 1 (Popular): Cola, Lemon-Lime = 35-40% of orders
  - Tier 2 (Mid-market): Energy drinks, Juices, Regional = 30-35% of orders
  - Tier 3 (Niche): Health drinks, Premium variants = 25-30% of orders

- **State-Based Allocation**:
  - Each state receives proportional SKU quantities based on customer population
  - Example: State with 100 customers = ~200-250 monthly transactions across 50 SKUs
  - Smaller states (10 customers) = ~20-25 monthly transactions

- **Seasonality Factors**:
  - Summer months (Apr-Jun): Cold beverages +30%
  - Winter months (Dec-Feb): Hot variants +20%
  - Monsoon months (Jul-Sep): Standard demand

---

## 2. SYSTEM ARCHITECTURE & TECHNOLOGY STACK

### 2.1 Technology Choices
- **Database**: SQLite (lightweight, embedded, ACID-compliant, optimal for this scale)
- **Backend API**: FastAPI with Python (high performance, async support, auto-documentation)
- **Frontend**: React or Vue.js (responsive, modern, JWT integration)
- **Authentication**: JWT (JSON Web Tokens) with role-based access
- **Real-time Processing**: Event-driven ETL pipeline with sub-100ms latency target
- **Deployment**: Docker containers (optional scaling)

### 2.2 Database Schema (SQLite)

**Core Tables:**

1. **users** - Admin authentication
   - user_id (PRIMARY KEY)
   - username (UNIQUE)
   - password_hash
   - role (admin, vendor, viewer)
   - created_at, updated_at

2. **customers** - Customer master data
   - customer_id (PRIMARY KEY)
   - state_id (FOREIGN KEY)
   - city_name
   - customer_tier
   - contact_info
   - created_at

3. **states** - State/UT master reference
   - state_id (PRIMARY KEY)
   - state_name (UNIQUE)
   - capital_city
   - region
   - population_segment
   - total_customers

4. **sku_categories** - Product categories
   - category_id (PRIMARY KEY)
   - category_name (UNIQUE)
   - description

5. **skus** - Product master data
   - sku_id (PRIMARY KEY)
   - product_name
   - category_id (FOREIGN KEY)
   - volume_ml (200, 400, 500, 750, 1000, 1500, 2000)
   - cost_manufacturing
   - cost_shipping
   - suggested_retail_price
   - active_status
   - created_at, updated_at

6. **sales_transactions** - Real-time sales records
   - transaction_id (PRIMARY KEY)
   - customer_id (FOREIGN KEY)
   - sku_id (FOREIGN KEY)
   - state_id (FOREIGN KEY)
   - quantity_units
   - transaction_date
   - transaction_amount

7. **inventory_by_state** - Stock levels by state
   - inventory_id (PRIMARY KEY)
   - state_id (FOREIGN KEY)
   - sku_id (FOREIGN KEY)
   - quantity_in_stock
   - last_updated

8. **shipments** - Freight management
   - shipment_id (PRIMARY KEY)
   - state_id (FOREIGN KEY)
   - sku_id (FOREIGN KEY)
   - quantity_units
   - cost_manufacturing_total
   - cost_shipping_total
   - shipment_date
   - tracking_code (UNIQUE)
   - current_status

9. **shipment_tracking** - Real-time tracking updates
   - tracking_id (PRIMARY KEY)
   - shipment_id (FOREIGN KEY)
   - status (Order Confirmed → In Warehouse → Shipped → In Transit → Out for Delivery → Delivered)
   - location
   - update_timestamp
   - notes

10. **sku_distribution_by_state** - Pre-calculated distribution matrix
    - distribution_id (PRIMARY KEY)
    - state_id (FOREIGN KEY)
    - sku_id (FOREIGN KEY)
    - allocation_percentage
    - expected_monthly_sales

---

## 3. BACKEND API (FastAPI) - Performance-Critical

### 3.1 API Architecture
- **Base URL**: /api/v1/
- **Response Format**: JSON with standardized envelope
- **Error Handling**: Consistent error codes and messages
- **Rate Limiting**: Configurable per endpoint
- **Caching**: Redis/in-memory caching for frequently accessed data
- **Connection Pooling**: SQLite connection management
- **Query Optimization**: Indexed lookups for O(1) access patterns

### 3.2 Core API Endpoints (20+ endpoints)

#### Authentication Endpoints
- POST /api/v1/auth/login - User login with credentials
- POST /api/v1/auth/logout - Invalidate session
- GET /api/v1/auth/verify - Verify JWT token validity
- POST /api/v1/auth/refresh - Refresh expired token

#### State-Wise Data Endpoints
- GET /api/v1/states - List all states/UTs with capitals
- GET /api/v1/states/{state_id} - Get single state details
- GET /api/v1/states/{state_id}/summary - State-level sales summary
- GET /api/v1/states/{state_id}/sku-performance - Top/bottom performing SKUs
- GET /api/v1/states/{state_id}/inventory - Current stock levels
- GET /api/v1/states/{state_id}/revenue - Revenue metrics

#### SKU Management Endpoints
- GET /api/v1/skus - List all SKUs with pagination
- POST /api/v1/skus - Create new SKU (admin only)
- GET /api/v1/skus/{sku_id} - Get SKU details
- PUT /api/v1/skus/{sku_id} - Update SKU (admin only)
- DELETE /api/v1/skus/{sku_id} - Archive SKU (soft delete)
- GET /api/v1/skus/{sku_id}/sales - Sales performance by state
- GET /api/v1/skus/category/{category_id} - Filter by category

#### Sales & Transaction Endpoints
- GET /api/v1/sales/summary - Overall sales statistics
- GET /api/v1/sales/by-state - Sales breakdown by state
- GET /api/v1/sales/by-sku - Sales breakdown by SKU
- GET /api/v1/sales/top-performers - Top 10 performing SKUs
- GET /api/v1/sales/bottom-performers - Bottom 10 SKUs
- POST /api/v1/sales/record - Record new transaction (ETL input)

#### Shipment Management Endpoints
- POST /api/v1/shipments - Create new shipment (admin)
- GET /api/v1/shipments - List shipments (with filters)
- GET /api/v1/shipments/{shipment_id} - Get shipment details
- PUT /api/v1/shipments/{shipment_id}/tracking - Update tracking status
- GET /api/v1/shipments/track/{tracking_code} - Public tracking endpoint
- GET /api/v1/shipments/state/{state_id} - Shipments by state

#### Analytics Endpoints
- GET /api/v1/analytics/profitability/{sku_id} - Profit margins
- GET /api/v1/analytics/trends - Sales trends (daily/weekly/monthly)
- GET /api/v1/analytics/forecast - Demand forecasting

### 3.3 Performance Optimization Strategies

**Query Optimization:**
- Indexed primary keys and foreign keys for O(1) lookups
- Composite indexes on frequently filtered columns (state_id, sku_id)
- Query result caching with TTL
- Batch operations for bulk inserts

**Response Optimization:**
- Pagination (default: 20 items, max: 100)
- Selective field projection (request only needed fields)
- GZIP compression for responses > 1KB
- Delta updates for real-time feeds

**Concurrency:**
- Async/await for non-blocking I/O
- Connection pooling (5-10 connections)
- Transaction isolation levels (READ_COMMITTED)
- Optimistic locking for concurrent updates

**Monitoring:**
- Response time tracking (target: < 100ms for 95th percentile)
- Query execution logging
- Cache hit/miss ratio tracking
- Error rate monitoring

---

## 4. FRONTEND APPLICATION

### 4.1 Authentication & Security

**Login Flow:**
- Username/password form
- Default credentials (non-production only):
  - Username: admin
  - Password: password
- JWT token generation on successful login
- Token stored in secure HTTP-only cookies
- Automatic logout on token expiration (configurable, default: 24 hours)

**Branch-Based Security:**
- **Development/Non-prod branches**: Default credentials allowed
- **Production branches** (prod, production): 
  - Credentials must be externalized (environment variables)
  - Additional security requirements enforced
  - MFA optional (future enhancement)

**Authorization:**
- Role-based access control (RBAC)
- Routes protected with JWT verification
- Unauthorized access redirects to login

### 4.2 Main Dashboard (Post-Authentication)

#### State-Wise Data View
**Dropdown Selection:**
- Search box with autocomplete
- Filter by state name or capital city
- Display all states (default view)
- Sort by customer count or revenue

**State Summary Display:**
- Total customers in state
- Total sales volume (units) - last 30 days
- Total revenue (INR)
- Week-over-week growth %
- Month-over-month growth %

**SKU Performance Grid:**
- Top 5 performing SKUs (by volume)
- Bottom 5 performing SKUs
- Sortable columns: SKU name, units sold, revenue, growth %
- Click to drill down into SKU details

**Inventory Status:**
- Current stock levels by SKU
- Low stock alerts (< 20% of capacity)
- Recommended reorder quantities

#### SKU Management Interface

**Create/Add New SKU:**
Form Fields:
- Flavor Profile (text input)
- Product Name (text input)
- Category (dropdown: Soda, Energy, Juice, etc.)
- Volume (dropdown: 200ml, 400ml, 500ml, 750ml, 1L, 1.5L, 2L)
  * Only valid sizes: no 1.25L, 1.75L decimals
- Cost of Manufacturing (number input, >= 0)
- Cost of Shipping (number input, >= 0)
- Suggested Retail Price (number input)
- Select States (multi-select dropdown)
- Number of Shipments to Supply (number input)
- Active Status (toggle)

Buttons:
- Submit (creates SKU)
- Cancel (returns to list)
- Preview (shows cost breakdown)

**SKU Performance Dashboard:**
- Searchable/filterable SKU table
- Columns: SKU ID, Product Name, Category, Volume, Units Sold, Revenue, Profitability %, Status
- Export to CSV functionality
- Last updated timestamp

**SKU Edit/Update:**
- Edit form pre-populated with current values
- Audit trail of changes (read-only)
- Soft delete (archive) option

### 4.3 Shipment Tracking Interface

**Tracking Code Input:**
- Simple text input for tracking code entry
- Search button
- Clear error messages for invalid codes

**Tracking Status Display:**
Status Progression:
1. Order Confirmed (timestamp)
2. In Warehouse (timestamp, location)
3. Shipped (timestamp, carrier)
4. In Transit (timestamp, current location)
5. Out for Delivery (timestamp)
6. Delivered (timestamp, delivery signature)

**Visual Timeline:**
- Linear progress indicator
- Completed steps highlighted (green)
- Current step (blue)
- Estimated delivery date
- Delay alerts (red) if delayed

**Shipment Details:**
- SKU information
- Quantity shipped
- Destination state/city
- Shipping cost
- Carrier information (if applicable)
- Last updated timestamp

### 4.4 Reports & Analytics Section

**Sales Trends:**
- Line chart: Daily/weekly/monthly sales volume
- Selectable date range
- Comparison with previous period

**SKU Performance Rankings:**
- Top 10 SKUs by volume
- Top 10 SKUs by revenue
- Bottom 10 performers
- Exportable rankings

**State-Wise Comparison:**
- Revenue by state (bar chart)
- Customer count by state
- Average order value by state

**Inventory Dashboard:**
- Stock levels by SKU
- Reorder alerts
- Expiration tracking (if applicable)

---

## 5. IMPLEMENTATION PHASES

### Phase 1: Project Foundation & Database (Week 1)
- [ ] Create SQLite database schema
- [ ] Generate Indian states/capitals master data
- [ ] Generate 1,000 dummy customers (distributed by state)
- [ ] Generate 50 SKU master data (10 sodas + 40 others)
- [ ] Calculate and populate SKU distribution matrix (state-wise allocation)
- [ ] Create initial sales transaction records (~5,000 sample transactions)
- [ ] Set up project directory structure
- **Verification**: Database queries return all states, customers by state, SKUs, and transactions

### Phase 2: Backend API Development (Week 1-2)
- [ ] Set up FastAPI project with SQLite connection
- [ ] Implement JWT authentication endpoints
- [ ] Create state endpoint handlers
- [ ] Create SKU CRUD endpoints
- [ ] Create sales data endpoints
- [ ] Implement shipment management endpoints
- [ ] Add query optimization and caching layer
- [ ] Implement error handling and logging
- [ ] Create API documentation (Swagger/OpenAPI)
- **Verification**: All endpoints tested with sample requests, response times < 100ms

### Phase 3: Frontend - Authentication & Base Setup (Week 2)
- [ ] Initialize React/Vue project
- [ ] Design login page UI
- [ ] Implement JWT authentication flow
- [ ] Create protected route wrapper
- [ ] Set up environment-based configuration
- [ ] Implement logout functionality
- [ ] Add error boundary and error handling
- **Verification**: Login/logout works, credentials valid only in non-prod, redirects work

### Phase 4: Frontend - Main Dashboard & State Views (Week 2-3)
- [ ] Create state dropdown component
- [ ] Build state summary display
- [ ] Implement SKU performance table
- [ ] Add inventory status view
- [ ] Create filters and sorting
- [ ] Set up real-time data refresh
- **Verification**: Dashboard loads correctly, state filtering works, data updates in real-time

### Phase 5: Frontend - SKU Management (Week 3)
- [ ] Design SKU creation form
- [ ] Implement form validation (volume sizes, costs)
- [ ] Create SKU list/search interface
- [ ] Build SKU detail view
- [ ] Implement edit functionality
- [ ] Add soft delete (archive) capability
- **Verification**: Can create/read/update SKUs, form validation prevents invalid sizes

### Phase 6: Shipment Tracking System (Week 3-4)
- [ ] Create tracking code input interface
- [ ] Build tracking status display
- [ ] Implement timeline visualization
- [ ] Create shipment detail view
- [ ] Add real-time status updates
- [ ] Implement notification alerts
- **Verification**: Tracking codes return correct shipment info, status updates appear in real-time

### Phase 7: Analytics & Reports (Week 4)
- [ ] Create sales trends visualization
- [ ] Build SKU performance rankings
- [ ] Create state-wise comparison views
- [ ] Add inventory dashboard
- [ ] Implement export functionality (CSV)
- **Verification**: Charts render correctly, data matches backend aggregations

### Phase 8: Optimization & Testing (Week 4-5)
- [ ] Performance testing on API endpoints
- [ ] Load testing (simulate concurrent users)
- [ ] Database query optimization
- [ ] Frontend rendering optimization
- [ ] Security audit (OWASP Top 10)
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Documentation finalization
- **Verification**: All endpoints < 100ms, no security vulnerabilities, all tests pass

---

## 6. GUARDRAILS & SAFETY RULES (CRITICAL)

### File Operations
1. No deletion without permission - Always ask before deleting any files
2. No DML without permission - Don't execute UPDATE, DELETE, ALTER without explicit approval
3. Second opinions required - For data modification commands, request confirmation

### Technology & Context
4. SQLite only - All SQL code optimized for SQLite
5. Beverage company context - Drinkoo context applied throughout
   - Valid SKU sizes: 200ml, 400ml, 500ml, 750ml, 1L, 1.5L, 2L (only whole/half decimals)
   - Invalid sizes: 1.25L, 1.75L, 2.25L (NOT allowed)

### Code Quality
6. Clear variable names - Must be understandable by junior engineers and interns
7. Full documentation - Code executable by non-technical users
8. Internet usage - Only for sourcing information, never for direct file edits

---

## 7. PROJECT STRUCTURE (Final)

DRNKOO-DE/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── states.py
│   │   │   ├── skus.py
│   │   │   ├── sales.py
│   │   │   └── shipments.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── sku.py
│   │   │   ├── sales.py
│   │   │   └── shipment.py
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── schema.sql
│   │   │   └── seed_data.py
│   │   └── utils/
│   │       ├── auth_utils.py
│   │       ├── validation.py
│   │       └── cache.py
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── StateView.jsx
│   │   │   ├── SKUManagement.jsx
│   │   │   └── ShipmentTracking.jsx
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── utils/
│   │   │   └── auth.js
│   │   ├── App.jsx
│   │   └── index.js
│   └── package.json
├── database/
│   ├── drinkoo.db (SQLite)
│   └── seed_data.csv
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── SETUP_GUIDE.md
│   └── TROUBLESHOOTING.md
└── README.md

---

## 8. API RESPONSE TIME TARGETS & SLAs

| Operation | Target | 95th Percentile |
|-----------|--------|----------------|
| Auth/Login | < 50ms | < 100ms |
| State Summary | < 30ms | < 80ms |
| SKU List (paginated) | < 40ms | < 90ms |
| Sales by State | < 50ms | < 100ms |
| Shipment Tracking | < 25ms | < 60ms |
| Transaction Record | < 20ms | < 50ms |
| Dashboard Load | < 200ms | < 300ms |

---

## 9. SUCCESS CRITERIA & VERIFICATION CHECKLIST

### Phase Completion:
- [ ] Database contains 1,000 customers across all states
- [ ] Database contains 50 SKUs with proper attributes
- [ ] All API endpoints respond in < 100ms (95th percentile)
- [ ] Frontend login works with default credentials (non-prod) or env vars (prod)
- [ ] State dropdown loads and filters correctly
- [ ] SKU creation prevents invalid volume sizes
- [ ] Shipment tracking displays correct status progressions
- [ ] All data is SQLite-compatible
- [ ] Code is documented and readable by junior engineers
- [ ] No files deleted without permission
- [ ] All guardrails adhered to

---

**Document Version**: 1.0
**Created**: June 9, 2026
**Status**: Ready for Implementation

This plan is accessible to all AI agents and should be referenced for consistency across the entire project development cycle.
