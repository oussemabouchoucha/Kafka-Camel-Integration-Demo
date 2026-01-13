const express = require('express');
const yaml = require('js-yaml');
const axios = require('axios');
const { Pool } = require('pg');
const app = express();
const port = 3000;

// PostgreSQL connection
const pool = new Pool({
    host: process.env.DB_HOST || 'postgres',
    database: process.env.DB_NAME || 'logistics_db',
    user: process.env.DB_USER || 'admin',
    password: process.env.DB_PASSWORD || 'password',
    port: 5432,
});

// Create aramex_orders table if not exists
const initDatabase = async () => {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS aramex_orders (
                id VARCHAR(36) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                item VARCHAR(255),
                price VARCHAR(20),
                country VARCHAR(100),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('✅ Aramex database table initialized');
    } catch (e) {
        console.error('❌ Error initializing database:', e);
    }
};

// Initialize database on startup
initDatabase();

app.use(express.json());
app.use(express.text({ type: 'application/x-yaml' }));
app.use(express.static('public'));

app.post('/aramex', async (req, res) => {
  console.log('Received YAML:', req.body);
  
  try {
    const order = yaml.load(req.body);
    
    // Insert order into PostgreSQL
    await pool.query(`
      INSERT INTO aramex_orders (id, first_name, last_name, phone, item, price, country, status)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      ON CONFLICT (id) DO NOTHING
    `, [order.id, order.firstName, order.lastName, order.phone, order.item, order.price, order.country, 'pending']);
    
    console.log('✅ Order stored in database:', order.id);
  } catch (e) {
    console.error('❌ Error processing order:', e);
  }
  
  res.send('Received YAML');
});

// API endpoint to get all orders
app.get('/api/orders', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM aramex_orders ORDER BY created_at DESC');
    const orders = result.rows.map(row => ({
      id: row.id,
      firstName: row.first_name,
      lastName: row.last_name,
      phone: row.phone,
      item: row.item,
      price: row.price,
      country: row.country,
      status: row.status,
      receivedAt: row.created_at
    }));
    res.json(orders);
  } catch (e) {
    console.error('❌ Error fetching orders:', e);
    res.status(500).json({ error: 'Failed to fetch orders' });
  }
});

// API endpoint to mark order as delivered
app.post('/api/mark-delivered', async (req, res) => {
  const { orderId } = req.body;
  
  console.log('=== Mark as Delivered Request ===');
  console.log('Order ID:', orderId);
  
  try {
    // Update status in database
    const result = await pool.query(
      'UPDATE aramex_orders SET status = $1 WHERE id = $2 RETURNING *',
      ['delivered', orderId]
    );
    
    if (result.rows.length > 0) {
      const order = result.rows[0];
      console.log('✅ Status updated in database');
      
      // Send status update to middleware
      console.log('📤 Sending status update to middleware...');
      const statusUpdate = {
        orderId: orderId,
        status: 'delivered',
        service: 'Aramex',
        item: order.item
      };
      
      await axios.post('http://middleware:8085/status-update', statusUpdate, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log('✅ Status update sent to middleware');
      res.json({ success: true });
    } else {
      console.log('❌ Order not found in database:', orderId);
      res.json({ success: false, error: 'Order not found' });
    }
  } catch (error) {
    console.error('❌ Error updating status:', error.message);
    res.json({ success: false, error: error.message });
  }
});

// API endpoint to mark order as returned
app.post('/api/mark-returned', async (req, res) => {
  const { orderId } = req.body;
  
  console.log('=== Mark as Returned Request ===');
  console.log('Order ID:', orderId);
  
  try {
    // Update status in database
    const result = await pool.query(
      'UPDATE aramex_orders SET status = $1 WHERE id = $2 RETURNING *',
      ['returned', orderId]
    );
    
    if (result.rows.length > 0) {
      const order = result.rows[0];
      console.log('✅ Status updated in database');
      
      // Send status update to middleware
      console.log('📤 Sending status update to middleware...');
      const statusUpdate = {
        orderId: orderId,
        status: 'returned',
        service: 'Aramex',
        item: order.item
      };
      
      await axios.post('http://middleware:8085/status-update', statusUpdate, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log('✅ Status update sent to middleware');
      res.json({ success: true });
    } else {
      console.log('❌ Order not found in database:', orderId);
      res.json({ success: false, error: 'Order not found' });
    }
  } catch (error) {
    console.error('❌ Error updating status:', error.message);
    res.json({ success: false, error: error.message });
  }
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

app.listen(port, () => {
  console.log(`Aramex server listening at http://localhost:${port}`);
});