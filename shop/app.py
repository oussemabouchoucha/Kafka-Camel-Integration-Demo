import json
import os
from flask import Flask, render_template, request, redirect, url_for
from confluent_kafka import Producer, Consumer, KafkaException
import uuid
from datetime import datetime
import threading
from filelock import FileLock

app = Flask(__name__)

# Define the path for the persistent order data
DATA_DIR = '/app/data'
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
LOCK_FILE = os.path.join(DATA_DIR, 'orders.json.lock')

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Global variable to hold orders
orders_db = []

# Create a lock object
lock = FileLock(LOCK_FILE)

def load_orders():
    """Load orders from the JSON file into memory."""
    global orders_db
    with lock:
        try:
            if os.path.exists(ORDERS_FILE):
                with open(ORDERS_FILE, 'r') as f:
                    orders_db = json.load(f)
                    print(f"✅ Loaded {len(orders_db)} orders from {ORDERS_FILE}")
            else:
                orders_db = []
                print(f"⚠️ Orders file not found at {ORDERS_FILE}, starting fresh.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Error loading orders: {e}. Starting with an empty list.")
            orders_db = []

def save_orders():
    """Save the current orders from memory to the JSON file."""
    with lock:
        try:
            with open(ORDERS_FILE, 'w') as f:
                json.dump(orders_db, f, indent=4)
        except IOError as e:
            print(f"❌ Error saving orders: {e}")

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
            
            status_update = json.loads(msg.value().decode('utf-8'))
            order_id = status_update.get('orderId')
            new_status = status_update.get('status')
            
            print(f'📥 Received status update: Order {order_id} -> {new_status}')
            
            # Find and update order, then save
            # No need for separate load_orders() call here, as orders_db is in-memory
            order_found = False
            for order in orders_db:
                if order['id'] == order_id:
                    order['status'] = new_status
                    order_found = True
                    break
            
            if order_found:
                save_orders() # Persist the change
                print(f'✅ Order {order_id} status updated to {new_status} and saved.')
            else:
                print(f'⚠️ Order {order_id} not found in database for status update.')
                    
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
    # To ensure the view is up-to-date, we can reload from the file.
    # This is a simple approach; for high-traffic sites, a more sophisticated
    # state management would be needed.
    load_orders()
    return render_template('orders.html', orders=orders_db)

@app.route('/api/kafka/status-update', methods=['POST'])
def kafka_status_update():
    """Endpoint for DHL/Aramex to publish status updates to Kafka, which are then consumed."""
    try:
        data = request.json
        order_id = data.get('orderId')
        new_status = data.get('status')
        service = data.get('service', 'Unknown')
        
        if not order_id or not new_status:
            return {'success': False, 'error': 'Missing orderId or status'}, 400
        
        status_message = {
            'orderId': order_id,
            'status': new_status,
            'service': service,
            'timestamp': datetime.now().isoformat()
        }
        
        producer.produce(
            'order-status-updates',
            key=order_id,
            value=json.dumps(status_message)
        )
        producer.flush()
        
        print(f'✅ Published status update to Kafka: Order {order_id} -> {new_status} (from {service})')
        
        # The consumer will handle the update and persistence.
        
        return {'success': True, 'message': 'Status update published to Kafka'}
        
    except Exception as e:
        print(f'❌ Error publishing status update: {e}')
        return {'success': False, 'error': str(e)}, 500

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
    
    # Add order to the list and save
    orders_db.append(order_data)
    save_orders()
    
    # Send data to Kafka
    producer.produce('orders', key=order_data['id'], value=json.dumps(order_data))
    producer.flush()

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Load initial data from file
    load_orders()
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)