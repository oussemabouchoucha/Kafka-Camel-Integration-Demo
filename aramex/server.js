const express = require('express');
const yaml = require('js-yaml');
const axios = require('axios');
const app = express();
const port = 3000;

// Store orders in memory
let orders = [];

app.use(express.json());
app.use(express.text({ type: 'application/x-yaml' }));
app.use(express.static('public'));

app.post('/aramex', (req, res) => {
  console.log('Received YAML:', req.body);
  
  try {
    // Parse YAML to JSON
    const order = yaml.load(req.body);
    order.receivedAt = new Date().toISOString();
    order.status = 'pending';
    orders.push(order);
    console.log('Order stored:', order);
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
    // Update status in local memory
    const order = orders.find(o => o.id === orderId);
    if (order) {
      order.status = 'delivered';
      console.log('✅ Status updated locally in Aramex');
    } else {
      console.log('❌ Order not found in Aramex:', orderId);
    }
    
    // Send status update to shop via Kafka
    console.log('📤 Sending status update to shop...');
    const statusUpdate = {
      orderId: orderId,
      status: 'Delivered',
      service: 'Aramex'
    };
    
    await axios.post('http://shop:5000/api/kafka/status-update', statusUpdate, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    console.log('✅ Status update sent to shop via Kafka');
    res.json({ success: true });
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
