<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Get JSON input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

$orderId = $data['orderId'] ?? null;
$status = $data['status'] ?? null;

if (!$orderId || !$status) {
    echo json_encode(['success' => false, 'error' => 'Missing orderId or status']);
    exit;
}

// Validate status
if (!in_array($status, ['pending', 'delivered', 'returned'])) {
    echo json_encode(['success' => false, 'error' => 'Invalid status']);
    exit;
}

// Load existing statuses
$statusFile = 'order_status.json';
$statuses = [];
if (file_exists($statusFile)) {
    $statusJson = file_get_contents($statusFile);
    $statuses = json_decode($statusJson, true) ?: [];
}

// Update status
$statuses[$orderId] = $status;

// Save to file
file_put_contents($statusFile, json_encode($statuses, JSON_PRETTY_PRINT));

// Send status update to Kafka using curl to the shop's internal API
$kafkaMessage = [
    'orderId' => $orderId,
    'status' => $status,
    'timestamp' => date('Y-m-d H:i:s'),
    'service' => 'DHL'
];

// Try to send to shop's kafka producer endpoint
$ch = curl_init('http://shop:5000/api/kafka/status-update');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($kafkaMessage));
curl_setopt($ch, CURLOPT_TIMEOUT, 2);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Log the update
error_log("[DHL] Status updated: Order $orderId -> $status (Kafka: $httpCode)");

echo json_encode([
    'success' => true,
    'orderId' => $orderId,
    'status' => $status,
    'kafkaNotified' => $httpCode == 200
]);
?>
