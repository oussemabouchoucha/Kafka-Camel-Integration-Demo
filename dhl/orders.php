<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$logFile = 'dhl.log';
$orders = [];

if (file_exists($logFile)) {
    $lines = file($logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    
    foreach ($lines as $index => $line) {
        if (trim($line)) {
            $orders[] = [
                'id' => count($lines) - $index,
                'data' => $line,
                'timestamp' => time() - (count($lines) - $index) * 60 // Approximate timestamp
            ];
        }
    }
}

// Reverse to show newest first
$orders = array_reverse($orders);

echo json_encode($orders);
?>
