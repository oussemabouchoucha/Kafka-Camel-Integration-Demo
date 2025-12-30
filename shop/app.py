import json
from flask import Flask, render_template, request, redirect, url_for
from confluent_kafka import Producer, Consumer, KafkaException
import uuid
from datetime import datetime
import threading

app = Flask(__name__)

# Store orders in memory
orders_db = []

# Kafka Producer Configuration
producer_config = {
    'bootstrap.servers': 'kafka:29092',
    'client.id': 'flask-producer'
}
producer = Producer(producer_config)

# Kafka Consumer Configuration for status updates
consumer_config = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'shop-status-consumer',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_config)

# Function to consume status updates from Kafka
def consume_status_updates():
    consumer.subscribe(['order-status-updates'])
    print('✅ Status update consumer started')
    
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'❌ Consumer error: {msg.error()}')
                continue
            
            # Process status update
            status_update = json.loads(msg.value().decode('utf-8'))
            order_id = status_update.get('orderId')
            new_status = status_update.get('status')
            
            print(f'📥 Received status update: Order {order_id} -> {new_status}')
            
            # Update order in memory
            for order in orders_db:
                if order['id'] == order_id:
                    order['status'] = new_status
                    print(f'✅ Order {order_id} status updated to {new_status}')
                    break
                    
        except Exception as e:
            print(f'❌ Error in status consumer: {e}')

# Start status update consumer in background thread
consumer_thread = threading.Thread(target=consume_status_updates, daemon=True)
consumer_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/orders')
def view_orders():
    return render_template('orders.html', orders=orders_db)

@app.route('/api/orders/update-status', methods=['POST'])
def update_status():
    # This endpoint is kept for backward compatibility
    # Status updates are now handled via Kafka consumer
    data = request.json
    order_id = data.get('orderId')
    new_status = data.get('status')
    
    print(f'⚠️ Direct API call (deprecated) - use Kafka instead')  
    print(f'Order ID: {order_id}, Status: {new_status}')
    
    return {'success': True, 'message': 'Status updates are handled via Kafka'}

@app.route('/order', methods=['POST'])
def order():
    form_data = request.form
    order_data = {
        "id": str(uuid.uuid4()),
        "firstName": form_data.get('firstName'),
        "lastName": form_data.get('lastName'),
        "phone": form_data.get('phone'),
        "item": form_data.get('item'),
        "price": form_data.get('price'),
        "country": form_data.get('country'),
        "status": "pending",
        "createdAt": datetime.now().isoformat()
    }
    
    # Store order in memory
    orders_db.append(order_data)
    
    # Send data to Kafka
    producer.produce('orders', key=order_data['id'], value=json.dumps(order_data))
    producer.flush()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)