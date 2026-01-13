# PostgreSQL Integration Guide

## Overview
The project now uses a **single PostgreSQL database** (`logistics_db`) shared across all services instead of file-based storage.

## Database Configuration

### PostgreSQL Service
- **Image**: postgres:15
- **Database**: logistics_db
- **User**: admin
- **Password**: password
- **Port**: 5432
- **Volume**: postgres_data (persistent storage)

### Database Tables

#### 1. shop_orders
Stores orders created from the main shop application.

```sql
CREATE TABLE shop_orders (
    id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    item VARCHAR(200),
    price DECIMAL(10,2),
    country VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. aramex_orders
Stores Tunisia domestic orders handled by Aramex.

```sql
CREATE TABLE aramex_orders (
    id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    item VARCHAR(200),
    price DECIMAL(10,2),
    country VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. dhl_orders
Stores international orders handled by DHL.

```sql
CREATE TABLE dhl_orders (
    id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    item VARCHAR(200),
    price DECIMAL(10,2),
    country VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Service Integration

### Shop Service (Python/Flask)
- **Technology**: Flask-SQLAlchemy + psycopg2-binary
- **Implementation**: 
  - Uses SQLAlchemy ORM with `ShopOrder` model
  - Automatic table creation with `db.create_all()`
  - Database operations: `.add()`, `.commit()`, `.query.filter_by()`
  - Environment variable: `DATABASE_URL`

### Aramex Service (Node.js)
- **Technology**: pg (PostgreSQL client for Node.js)
- **Implementation**:
  - Connection pooling with `Pool`
  - Parameterized queries with `$1, $2, ...` placeholders
  - `CREATE TABLE IF NOT EXISTS` on startup
  - Environment variables: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### DHL Service (PHP)
- **Technology**: PDO with pdo_pgsql extension
- **Implementation**:
  - PDO connection with error handling
  - Named parameters in prepared statements (`:id`, `:first_name`, etc.)
  - `CREATE TABLE IF NOT EXISTS` in all endpoints
  - Environment variables: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
  - Dockerfile includes: `apt-get install libpq-dev` and `docker-php-ext-install pdo pdo_pgsql`

## Key Features

### 1. Data Persistence
- All order data is stored in PostgreSQL
- Data survives container restarts
- No more JSON file storage

### 2. Shared Database
- Single database for all three services
- Separate tables per service for isolation
- Easy to query across services if needed

### 3. Health Checks
- PostgreSQL container has health check with `pg_isready`
- All dependent services wait for PostgreSQL to be healthy before starting
- Dependency chain: `postgres:healthy` → `shop/aramex/dhl`

### 4. Conflict Handling
- All services use `ON CONFLICT DO NOTHING` for duplicate order IDs
- Prevents errors when re-processing orders

## URLs

- **Shop**: http://localhost:5000
- **Aramex Dashboard**: http://localhost:3000
- **DHL Dashboard**: http://localhost:8081
- **Middleware**: http://localhost:8085
- **Kafka UI**: http://localhost:8090
- **PostgreSQL**: localhost:5432

## Database Access

You can connect to the database directly using:

```bash
# Using docker exec
docker exec -it kafka-camel-integration-demo-main-postgres-1 psql -U admin -d logistics_db

# Or using any PostgreSQL client
Host: localhost
Port: 5432
Database: logistics_db
Username: admin
Password: password
```

## Testing the Integration

1. **Create an order in Shop** (http://localhost:5000)
   - Tunisia orders → Stored in `aramex_orders`
   - International orders → Stored in `dhl_orders`

2. **Check the data**:
   ```sql
   SELECT * FROM shop_orders;
   SELECT * FROM aramex_orders;
   SELECT * FROM dhl_orders;
   ```

3. **Update order status in Aramex/DHL**:
   - Mark as delivered/returned
   - Status updates reflected in database
   - Shop service receives updates via Kafka

## Advantages Over File-Based Storage

1. **Concurrent Access**: Multiple processes can safely access the database
2. **Transactions**: ACID compliance ensures data consistency
3. **Querying**: SQL queries for complex data retrieval
4. **Scalability**: Can handle more orders without performance issues
5. **Reliability**: No file corruption or locking issues
6. **Backup**: Easy to backup and restore PostgreSQL data

## Migration Notes

- Removed all `orders.json`, `order_status.json`, `dhl.log` file operations
- Removed `filelock` dependency (no longer needed)
- All data now in PostgreSQL with proper indexing
- Previous file-based data is not migrated automatically
