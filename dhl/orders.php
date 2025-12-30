<?php
// Suppress all PHP errors/warnings from output
error_reporting(0);
ini_set('display_errors', '0');

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$logFile = 'dhl.log';
$statusFile = 'order_status.json';
$orders = [];

// Load statuses from JSON file
$statuses = [];
if (file_exists($statusFile)) {
    $statusJson = file_get_contents($statusFile);
    $statuses = json_decode($statusJson, true) ?: [];
}

if (file_exists($logFile)) {
    $lines = file($logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    
    foreach ($lines as $index => $line) {
        if (trim($line)) {
            // Parse XML to extract orderId
            $orderId = '';
            if (preg_match('/<id>(.*?)<\/id>/', $line, $matches)) {
                $orderId = $matches[1];
            }
            
            $orderNumber = count($lines) - $index;
            $orders[] = [
                'id' => $orderNumber,
                'data' => $line,
                'timestamp' => time() - (count($lines) - $index) * 60,
                'status' => !empty($orderId) && isset($statuses[$orderId]) ? $statuses[$orderId] : 'pending'
            ];
        }
    }
}

// Reverse to show newest first
$orders = array_reverse($orders);

echo json_encode($orders);
?>
