import json
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from confluent_kafka import Producer, Consumer, KafkaException
import uuid
from datetime import datetime
import threading

app = Flask(__name__)

# PostgreSQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://admin:password@postgres:5432/logistics_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define ShopOrder Model
class ShopOrder(db.Model):
    __tablename__ = 'shop_orders'
    
    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    item = db.Column(db.String(255))
    price = db.Column(db.String(20))
    country = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'phone': self.phone,
            'item': self.item,
            'price': self.price,
            'country': self.country,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

# Create tables
with app.app_context():
    db.create_all()
    print('✅ Database tables created successfully')

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
            
            # Update order in database
            with app.app_context():
                order = ShopOrder.query.filter_by(id=order_id).first()
                if order:
                    order.status = new_status
                    db.session.commit()
                    print(f'✅ Order {order_id} status updated to {new_status} in database.')
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
    orders = ShopOrder.query.order_by(ShopOrder.created_at.desc()).all()
    orders_list = [order.to_dict() for order in orders]
    return render_template('orders.html', orders=orders_list)

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
    order_id = str(uuid.uuid4())
    
    # Create new order in database first
    new_order = ShopOrder(
        id=order_id,
        first_name=form_data.get('firstName'),
        last_name=form_data.get('lastName'),
        phone=form_data.get('phone'),
        item=form_data.get('item'),
        price=form_data.get('price'),
        country=form_data.get('country'),
        status='pending'
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    # Convert to dict for Kafka
    order_data = new_order.to_dict()
    
    # Send data to Kafka
    producer.produce('orders', key=order_data['id'], value=json.dumps(order_data))
    producer.flush()
    
    print(f'✅ Order {order_id} saved to database and sent to Kafka')

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)