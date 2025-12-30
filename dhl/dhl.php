<?php
$data = file_get_contents('php://input');
file_put_contents('dhl.log', $data . PHP_EOL, FILE_APPEND);
echo 'Received XML';
?>
