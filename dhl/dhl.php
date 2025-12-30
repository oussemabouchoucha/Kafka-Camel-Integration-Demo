<?php
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');

$data = file_get_contents('php://input');

if ($data) {
    // Append order with timestamp
    file_put_contents('dhl.log', $data . PHP_EOL, FILE_APPEND);
    
    // Log to console
    error_log("[DHL] Received international order: " . substr($data, 0, 100));
    
    echo 'DHL Order Received Successfully - International Delivery Confirmed';
} else {
    http_response_code(400);
    echo 'No data received';
}
?>
