<?php
// Suppress all PHP errors/warnings from output
error_reporting(0);
ini_set('display_errors', '0');

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// PostgreSQL connection
$host = getenv('DB_HOST') ?: 'postgres';
$dbname = getenv('DB_NAME') ?: 'logistics_db';
$user = getenv('DB_USER') ?: 'admin';
$password = getenv('DB_PASSWORD') ?: 'password';

try {
    $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create table if not exists
    $pdo->exec("CREATE TABLE IF NOT EXISTS dhl_orders (
        id VARCHAR(50) PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20),
        item VARCHAR(200),
        price DECIMAL(10,2),
        country VARCHAR(100),
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )");
    
    // Fetch all DHL orders from database
    $stmt = $pdo->query("SELECT * FROM dhl_orders ORDER BY created_at DESC");
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    $orders = [];
    foreach ($rows as $row) {
        $orders[] = [
            'id' => $row['id'],
            'firstName' => $row['first_name'],
            'lastName' => $row['last_name'],
            'phone' => $row['phone'],
            'item' => $row['item'],
            'price' => $row['price'],
            'country' => $row['country'],
            'status' => $row['status'],
            'timestamp' => strtotime($row['created_at'])
        ];
    }
    
    echo json_encode($orders);
} catch (PDOException $e) {
    error_log("[DHL] Database error: " . $e->getMessage());
    echo json_encode(['error' => 'Database connection failed']);
}
?>
