<?php
/**
 * BrightPattern-Audit — DreamHost reverse proxy to Flask VPS:8090
 * https://xi-app.pro/brightpattern/api.php/* → http://204.168.193.81:8090/*
 */

set_time_limit(60);

$VPS_BASE = "http://204.168.193.81:8090";
$method   = $_SERVER["REQUEST_METHOD"];

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, X-Api-Key");
if ($method === "OPTIONS") { http_response_code(200); exit; }

// Strip /brightpattern/api.php prefix, keep the rest as the Flask path
$uri   = $_SERVER["REQUEST_URI"];
$path  = parse_url($uri, PHP_URL_PATH);
$query = parse_url($uri, PHP_URL_QUERY);

// /brightpattern/api.php/analyze → /analyze
$tail  = preg_replace("#^/brightpattern/api\.php#", "", $path);
$tail  = $tail ?: "/";
$qs    = $query ? "?" . $query : "";

$target = $VPS_BASE . $tail . $qs;

$ch = curl_init($target);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

$req_headers = [];
if ($method === "POST") {
    $body = file_get_contents("php://input");
    curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    $req_headers[] = "Content-Type: application/json";
    $req_headers[] = "Content-Length: " . strlen($body);
}

// Forward X-Api-Key if present
if (isset($_SERVER["HTTP_X_API_KEY"])) {
    $req_headers[] = "X-Api-Key: " . $_SERVER["HTTP_X_API_KEY"];
}
if ($req_headers) {
    curl_setopt($ch, CURLOPT_HTTPHEADER, $req_headers);
}

$result = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$ctype  = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

http_response_code($status ?: 502);
if ($ctype) header("Content-Type: " . $ctype);
echo $result;
