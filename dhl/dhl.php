<?php
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');

// PostgreSQL connection
$host = getenv('DB_HOST') ?: 'postgres';
$dbname = getenv('DB_NAME') ?: 'logistics_db';
$user = getenv('DB_USER') ?: 'admin';
$password = getenv('DB_PASSWORD') ?: 'password';

try {
    $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create dhl_orders table if not exists
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS dhl_orders (
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
    ");
} catch (PDOException $e) {
    error_log("Database connection failed: " . $e->getMessage());
    http_response_code(500);
    echo 'Database connection failed';
    exit;
}

$data = file_get_contents('php://input');

if ($data) {
    // Append order with timestamp to log file
    file_put_contents('dhl.log', $data . PHP_EOL, FILE_APPEND);
    
    // Parse XML and insert into database
    $xml = simplexml_load_string($data);
    if ($xml !== false) {
        $orderId = (string)$xml->id;
        $firstName = (string)$xml->firstName;
        $lastName = (string)$xml->lastName;
        $phone = (string)$xml->phone;
        $item = (string)$xml->item;
        $price = (string)$xml->price;
        $country = (string)$xml->country;
        
        try {
            $stmt = $pdo->prepare("
                INSERT INTO dhl_orders (id, first_name, last_name, phone, item, price, country, status)
                VALUES (:id, :first_name, :last_name, :phone, :item, :price, :country, 'pending')
                ON CONFLICT (id) DO NOTHING
            ");
            
            $stmt->execute([
                ':id' => $orderId,
                ':first_name' => $firstName,
                ':last_name' => $lastName,
                ':phone' => $phone,
                ':item' => $item,
                ':price' => $price,
                ':country' => $country
            ]);
            
            error_log("[DHL] Order $orderId stored in database");
        } catch (PDOException $e) {
            error_log("[DHL] Database error: " . $e->getMessage());
        }
    }
    
    // Log to console
    error_log("[DHL] Received international order: " . substr($data, 0, 100));
    
    echo 'DHL Order Received Successfully - International Delivery Confirmed';
} else {
    http_response_code(400);
    echo 'No data received';
}
?>
