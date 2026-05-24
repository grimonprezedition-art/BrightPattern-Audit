<?php
$file = __DIR__ . '/dark-paterne-audit.md';
if (!file_exists($file)) {
    http_response_code(404);
    exit('File not found.');
}
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="dark-paterne-audit.md"');
header('Content-Length: ' . filesize($file));
header('Cache-Control: no-cache');
readfile($file);
