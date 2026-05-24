<?php
/**
 * BrightPattern-Audit — DreamHost MySQL Proxy
 * Called by the Flask VPS backend. Authenticates via X-BP-Secret header.
 * Actions: insert | stats
 */

header('Content-Type: application/json; charset=utf-8');

// ── Auth ──────────────────────────────────────────────────────────────────────
$secret = getenv('BP_PROXY_SECRET') ?: 'change_me_in_env';
$incoming = $_SERVER['HTTP_X_BP_SECRET'] ?? '';
if (!hash_equals($secret, $incoming)) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

// ── DB connection ─────────────────────────────────────────────────────────────
$host = getenv('BP_DB_HOST') ?: 'mysql.asknietzsche.com';
$db   = 'nietzsche_xi';
$user = 'xiuser';
$pass = getenv('BP_DB_PASS') ?: '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'DB connection failed']);
    exit;
}

// ── Routing ───────────────────────────────────────────────────────────────────
$action = $_GET['action'] ?? '';

if ($action === 'insert' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = json_decode(file_get_contents('php://input'), true);
    if (!$body) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid JSON body']);
        exit;
    }

    $sql = "INSERT INTO dark_pattern_logs
        (conversation_id, timestamp, ai_model_name, user_prompt, ai_response,
         dark_pattern_type, frustration_score, matched_signals, pattern_description, source_ip)
        VALUES
        (:conversation_id, :timestamp, :ai_model_name, :user_prompt, :ai_response,
         :dark_pattern_type, :frustration_score, :matched_signals, :pattern_description, :source_ip)";

    $stmt = $pdo->prepare($sql);
    $ids  = [];

    $records = isset($body[0]) ? $body : [$body];
    foreach ($records as $row) {
        $stmt->execute([
            ':conversation_id'     => $row['conversation_id']     ?? '',
            ':timestamp'           => $row['timestamp']           ?? date('Y-m-d H:i:s'),
            ':ai_model_name'       => $row['ai_model_name']       ?? 'unknown',
            ':user_prompt'         => $row['user_prompt']         ?? '',
            ':ai_response'         => $row['ai_response']         ?? '',
            ':dark_pattern_type'   => $row['dark_pattern_type']   ?? '',
            ':frustration_score'   => (int)($row['frustration_score'] ?? 0),
            ':matched_signals'     => is_array($row['matched_signals'] ?? null)
                                        ? json_encode($row['matched_signals'])
                                        : ($row['matched_signals'] ?? '[]'),
            ':pattern_description' => $row['pattern_description'] ?? '',
            ':source_ip'           => $row['source_ip']           ?? null,
        ]);
        $ids[] = $pdo->lastInsertId();
    }

    echo json_encode(['inserted' => count($ids), 'ids' => $ids]);
    exit;
}

if ($action === 'stats' && $_SERVER['REQUEST_METHOD'] === 'GET') {
    $total = $pdo->query("SELECT COUNT(*) FROM dark_pattern_logs")->fetchColumn();
    $avg   = $pdo->query("SELECT ROUND(AVG(frustration_score),2) FROM dark_pattern_logs")->fetchColumn();

    $byPattern = $pdo->query(
        "SELECT dark_pattern_type, COUNT(*) as count, ROUND(AVG(frustration_score),2) as avg_score
         FROM dark_pattern_logs GROUP BY dark_pattern_type ORDER BY count DESC"
    )->fetchAll();

    $byModel = $pdo->query(
        "SELECT ai_model_name, COUNT(*) as count
         FROM dark_pattern_logs GROUP BY ai_model_name ORDER BY count DESC"
    )->fetchAll();

    $recent = $pdo->query(
        "SELECT conversation_id, timestamp, ai_model_name, dark_pattern_type, frustration_score
         FROM dark_pattern_logs ORDER BY timestamp DESC LIMIT 50"
    )->fetchAll();

    echo json_encode([
        'total_entries'    => (int)$total,
        'avg_frustration'  => (float)$avg,
        'by_pattern'       => $byPattern,
        'by_model'         => $byModel,
        'recent'           => $recent,
    ]);
    exit;
}

http_response_code(400);
echo json_encode(['error' => 'Unknown action. Use ?action=insert or ?action=stats']);
