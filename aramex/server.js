const express = require('express');
const yaml = require('js-yaml');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 3000;

// Define the path for the persistent order data
const DATA_DIR = '/app/data';
const ORDERS_FILE = path.join(DATA_DIR, 'orders.json');

// Ensure the data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Store orders in memory, loaded from file
let orders = [];

const loadOrders = () => {
    try {
        if (fs.existsSync(ORDERS_FILE)) {
            const data = fs.readFileSync(ORDERS_FILE, 'utf8');
            orders = JSON.parse(data);
            console.log(`✅ Loaded ${orders.length} orders from ${ORDERS_FILE}`);
        } else {
            console.log(`⚠️ Orders file not found at ${ORDERS_FILE}, starting fresh.`);
        }
    } catch (e) {
        console.error('❌ Error loading orders:', e);
    }
};

const saveOrders = () => {
    try {
        fs.writeFileSync(ORDERS_FILE, JSON.stringify(orders, null, 2));
    } catch (e) {
        console.error('❌ Error saving orders:', e);
    }
};

// Load orders on startup
loadOrders();

app.use(express.json());
app.use(express.text({ type: 'application/x-yaml' }));
app.use(express.static('public'));

app.post('/aramex', (req, res) => {
  console.log('Received YAML:', req.body);
  
  try {
    const order = yaml.load(req.body);
    order.receivedAt = new Date().toISOString();
    order.status = 'pending';
    orders.push(order);
    saveOrders(); // Save after adding
    console.log('Order stored and saved:', order);
  } catch (e) {
    console.error('Error parsing YAML:', e);
  }
  
  res.send('Received YAML');
});

// API endpoint to get all orders
app.get('/api/orders', (req, res) => {
  res.json(orders);
});

// API endpoint to mark order as delivered
app.post('/api/mark-delivered', async (req, res) => {
  const { orderId } = req.body;
  
  console.log('=== Mark as Delivered Request ===');
  console.log('Order ID:', orderId);
  
  try {
    const order = orders.find(o => o.id === orderId);
    if (order) {
      order.status = 'delivered';
      saveOrders(); // Save after updating status
      console.log('✅ Status updated locally and saved in Aramex');
    } else {
      console.log('❌ Order not found in Aramex:', orderId);
    }
    
    // Send status update to middleware
    console.log('📤 Sending status update to middleware...');
    const statusUpdate = {
      orderId: orderId,
      status: 'Delivered',
      service: 'Aramex'
    };
    
    await axios.post('http://middleware:8085/status-update', statusUpdate, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    console.log('✅ Status update sent to middleware');
    res.json({ success: true });
  } catch (error) {
    console.error('❌ Error updating status:', error.message);
    res.json({ success: false, error: error.message });
  }
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/public/index.html'));
});

app.listen(port, () => {
  console.log(`Aramex server listening at http://localhost:${port}`);
});