<?php
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');

$data = file_get_contents('php://input');

if ($data) {
    // Append order with timestamp
    file_put_contents('dhl.log', $data . PHP_EOL, FILE_APPEND);
    
    // Parse XML and store order details
    $ordersFile = 'order_details.json';
    $orderDetails = [];
    if (file_exists($ordersFile)) {
        $orderDetails = json_decode(file_get_contents($ordersFile), true) ?: [];
    }
    
    // Extract order information from XML
    $xml = simplexml_load_string($data);
    if ($xml !== false) {
        $orderId = (string)$xml->id;
        $orderDetails[$orderId] = [
            'item' => (string)$xml->item,
            'firstName' => (string)$xml->firstName,
            'lastName' => (string)$xml->lastName,
            'phone' => (string)$xml->phone,
            'price' => (string)$xml->price,
            'country' => (string)$xml->country
        ];
        file_put_contents($ordersFile, json_encode($orderDetails, JSON_PRETTY_PRINT));
    }
    
    // Log to console
    error_log("[DHL] Received international order: " . substr($data, 0, 100));
    
    echo 'DHL Order Received Successfully - International Delivery Confirmed';
} else {
    http_response_code(400);
    echo 'No data received';
}
?>
