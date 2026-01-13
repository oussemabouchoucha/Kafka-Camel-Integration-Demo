# 📦 Full Integration Project: E-Commerce Logistics 🚚

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=flat&logo=github)](https://github.com/oussemabouchoucha/Kafka-Camel-Integration-Demo)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete microservices architecture demonstrating **Enterprise Application Integration (EAI)** using **Kafka**, **Apache Camel (Spring Boot)**, **Python**, **Node.js**, and **PHP**.  
Everything is fully containerized with **Docker** 🐳.

### 🌟 Key Features

- ✅ **Real-time Order Processing** - Orders flow instantly through Kafka
- ✅ **Smart Content-Based Routing** - Automatic delivery partner selection
- ✅ **Live Status Updates** - Real-time order tracking across all services
- ✅ **Interactive Dashboards** - Modern UI for each delivery partner
- ✅ **Event-Driven Architecture** - Kafka-powered asynchronous communication
- ✅ **Multi-Format Support** - JSON, YAML, and XML transformations
- ✅ **PostgreSQL Database** - Persistent storage for all orders across services
- ✅ **pgAdmin Integration** - Web-based database management interface


## 📝 Project Description


This project simulates a real-world e-commerce logistics system designed to handle order processing and routing to different shipping partners based on geographical criteria. It showcases a robust, scalable, and extensible architecture built upon microservices communicating asynchronously.


The core components include:


- 🛒 **E-commerce Shop** (Python/Flask): A simple frontend application where users can place orders.
- 📨 **Apache Kafka**: High-throughput message broker ensuring reliable communication and decoupling between services.
- 🧠 **Integration Middleware** (Spring Boot + Apache Camel): The central nervous system that consumes orders, applies routing logic (EIP patterns), and transforms messages (JSON → YAML/XML).
- 🚛 **Logistics Partners**:
  - 🇹🇳 **Aramex** (Node.js/Express): Handles domestic deliveries (Tunisia).
  - 🌍 **DHL** (PHP/Apache): Handles international deliveries.


## 🛠️ Technologies Used


| Category           | Technology                                   |
|--------------------|----------------------------------------------|
| Orchestration      | Docker, Docker Compose                       |
| Message Broker     | Apache Kafka, Zookeeper                      |
| Integration        | Apache Camel (EIP patterns)                  |
| Backend Frameworks | Spring Boot (Java), Flask (Python), Express.js (Node.js) |
| Web Server         | Apache HTTP Server (for PHP)                 |
| Database           | PostgreSQL 15                                |
| Database Management| pgAdmin 4                                    |
| Data Formats       | JSON, YAML, XML                              |
| Monitoring         | Hawtio, Kafka UI                             |


## 📋 Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Git (for cloning the repository)
- ✅ At least 8GB RAM available for Docker
- ✅ Ports available: 5000, 3000, 5050, 5432, 8080, 8081, 8090, 9092

**Note:** You do **NOT** need to install Java, Maven, Python, Node.js, or PHP locally. Docker handles the entire environment!


## 🚀 How to Run

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oussemabouchoucha/Kafka-Camel-Integration-Demo.git
   cd Kafka-Camel-Integration-Demo
   ```

2. **Start the entire system:**
   ```bash
   docker-compose up -d --build
   ```
   This builds the Shop, Middleware, Aramex, and DHL services and starts Kafka/Zookeeper.

3. **Verify everything is running:**
   ```bash
   docker-compose ps
   ```
   All services should show as "Up".

4. **Wait for services to be ready** (approximately 30-60 seconds for Kafka initialization)


## 🖥️ How to Use


### 1. 🛒 Place an Order (The Shop)
Open your browser:  
👉 http://localhost:5000


- Enter **Item**, **Price**, and select a **Country**  
- Click **Send Order**


### 2. 📊 Visualize the Flow (Middleware Dashboard)
See real-time routing, diagrams, and counters:  
👉 http://localhost:8080/actuator/hawtio


Navigate to: **Camel** (left sidebar) → **Routes** → **route1** → **Route Diagram**


### 3. 📈 Monitor Kafka Topics (Kafka UI)
Inspect messages directly in the Kafka broker:  
👉 http://localhost:8090


- Go to **Topics** → **orders** to see raw JSON messages arriving from the Shop.


### 4. � Track Orders in Delivery Partner Dashboards

**View Aramex Orders (Tunisia):**  
👉 http://localhost:3000

- See all Tunisia domestic deliveries
- Mark orders as "Delivered" with one click
- Real-time status synchronization via Kafka

**View DHL Orders (International):**  
👉 http://localhost:8081

- See all international deliveries
- Update order status: "Delivered" or "Returned"
- Real-time status updates across all services

**View All Orders (Shop Dashboard):**  
👉 http://localhost:5000/orders

- Complete order history with live status updates
- Status changes from DHL/Aramex are reflected instantly


### 5. 🗄️ Database Management (pgAdmin)

**Access pgAdmin for database inspection:**  
👉 http://localhost:5050

**Login credentials:**
- Email: `admin@admin.com`
- Password: `admin`

**Connect to PostgreSQL:**
- Right-click "Servers" → "Register" → "Server"
- Name: `Logistics DB`
- Host: `postgres`
- Port: `5432`
- Database: `logistics_db`
- Username: `admin`
- Password: `password`

**Database Tables:**
- `shop_orders` - All orders from the shop
- `aramex_orders` - Tunisia domestic deliveries
- `dhl_orders` - International deliveries

### 6. 🔍 Check the Logs (Debugging)


- **Middleware** (routing logic):
  ```bash
  docker-compose logs -f middleware
  ```


- **Aramex** (Tunisia orders):
  ```bash
  docker-compose logs -f aramex
  ```


- **DHL** (international orders):
  ```bash
  docker-compose logs -f dhl
  ```


## ⚙️ Architecture & Logic


### Order Placement Flow

1. **Producer**: The Shop App (Python/Flask) sends the order as JSON to the Kafka topic `orders`.
2. **Consumer**: The Middleware (Spring Boot + Camel) listens to the topic.
3. **Routing (Content-Based Router)**:
   - 🇹🇳 If **Country = Tunisia** → Convert to **YAML** → Send to **Aramex** (Node.js)
   - 🌍 For **any other country** (e.g., France, Germany) → Convert to **XML** → Send to **DHL** (PHP)

### Status Update Flow (NEW ✨)

4. **Status Management**: Delivery partners (DHL/Aramex) can update order status via their dashboards
5. **Kafka Publishing**: Status updates are published to Kafka topic `order-status-updates`
6. **Real-time Sync**: Shop service consumes status updates and reflects changes instantly


```mermaid
graph LR
    subgraph "Producer Layer"
        P["🛒 Shop App<br/>(Python/Flask)"]
    end


    subgraph "Messaging Layer"
        K[("📨 Apache Kafka<br/>(Topic: orders)")]
        KS[("📨 Kafka<br/>(Topic: order-status-updates)")]
    end


    subgraph "Integration Layer (The Brain)"
        C{{"🐫 Middleware<br/>(Spring Boot + Camel)"}}
    end


    subgraph "Consumer Layer (Logistics)"
        A["🇹🇳 Aramex<br/>(Node.js/Express)"]
        D["🌍 DHL<br/>(PHP/Apache)"]
    end


    P -- "1. JSON" --> K
    K -- "2. Stream" --> C
    C -- "3a. YAML (Tunisia)" --> A
    C -- "3b. XML (Others)" --> D
    A -- "4a. Status Update" --> KS
    D -- "4b. Status Update" --> KS
    KS -- "5. Real-time Sync" --> P


    style C fill:#f9f,stroke:#333,stroke-width:4px
    style K fill:#ccf,stroke:#333,stroke-width:2px
    style KS fill:#cfc,stroke:#333,stroke-width:2px
```


## 📁 Project Structure

```
Kafka-Camel-Integration-Demo/
├── docker-compose.yml          # Orchestrates all services
├── README.md                   # Project documentation (you are here)
├── RapportTechnique.md        # Technical report (French)
├── shop/                       # Python Flask App (Producer)
│   ├── app.py                 # Main application
│   ├── producer.py            # Kafka producer logic
│   ├── templates/             # HTML templates
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── middleware/                 # Spring Boot + Camel App (Integration)
│   ├── src/main/java/com/example/middleware/
│   │   ├── MiddlewareApplication.java  # Main Spring Boot app
│   │   └── IntegrationRoute.java       # Apache Camel routing logic
│   ├── src/main/resources/
│   │   └── application.properties      # Configuration
│   ├── pom.xml                # Maven dependencies
│   └── Dockerfile
├── aramex/                     # Node.js App (Aramex endpoint)
│   ├── server.js              # Express.js server
│   ├── public/                # Static files
│   ├── package.json           # Node dependencies
│   └── Dockerfile
└── dhl/                        # PHP App (DHL endpoint)
    ├── dhl.php                # REST endpoint handler
    ├── dhl.log                # Delivery logs
    └── (uses php:apache image)
```


## 🛑 How to Stop

Stop all containers and clean up the network:
```bash
docker-compose down
```

To remove volumes (reset Kafka data):
```bash
docker-compose down -v
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests

### How to Contribute

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📝 Additional Documentation

- **Technical Report (French):** See [RapportTechnique.md](RapportTechnique.md) for detailed technical documentation
- **PostgreSQL Integration Guide:** See [POSTGRESQL_INTEGRATION.md](POSTGRESQL_INTEGRATION.md) for database setup and migration details
- **Repository:** [GitHub - Kafka-Camel-Integration-Demo](https://github.com/oussemabouchoucha/Kafka-Camel-Integration-Demo)

## 📊 Service Ports Reference

| Service      | Port  | URL                              | Description                    |
|--------------|-------|----------------------------------|--------------------------------|
| Shop         | 5000  | http://localhost:5000            | Order placement interface      |
| Shop Orders  | 5000  | http://localhost:5000/orders     | View all orders & status       |
| Middleware   | 8080  | http://localhost:8080/actuator/hawtio | Camel routes dashboard |
| Aramex       | 3000  | http://localhost:3000            | Tunisia deliveries dashboard   |
| DHL          | 8081  | http://localhost:8081            | International deliveries dashboard |
| Kafka UI     | 8090  | http://localhost:8090            | Kafka topic monitoring         |
| pgAdmin      | 5050  | http://localhost:5050            | PostgreSQL database management |
| PostgreSQL   | 5432  | localhost:5432                   | Database connection (internal) |
| Kafka Broker | 9092  | localhost:9092                   | Kafka connection (internal)    |

## 🔧 Troubleshooting

### Common Issues:

**Port already in use:**
```bash
# Check which services are using the ports
docker-compose down
# Check if any containers are still running
docker ps -a
```

**Kafka connection issues:**
- Wait 30-60 seconds after `docker-compose up` for Kafka to fully initialize
- Check logs: `docker-compose logs kafka`

**Middleware not starting:**
```bash
docker-compose logs middleware
# Often related to Kafka not being ready yet
```

**Orders not appearing:**
- Verify Kafka is running: `docker-compose logs kafka`
- Check middleware logs: `docker-compose logs -f middleware`
- Access Kafka UI at http://localhost:8090 to inspect topics

## 📜 License

This project is created for educational purposes demonstrating Enterprise Integration Patterns.

## 👨‍💻 Authors

- **Oussema Bouchoucha** - [GitHub](https://github.com/oussemabouchoucha)

---

Enjoy exploring this full EAI integration scenario! 🎉
