-- BrightPattern-Audit — Table migration for nietzsche_xi
-- Run once from DreamHost (MySQL host: mysql.asknietzsche.com):
-- mysql -h mysql.asknietzsche.com -u xiuser -p nietzsche_xi < 001_init.sql

CREATE TABLE IF NOT EXISTS dark_pattern_logs (
    id                  BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    conversation_id     VARCHAR(64)       NOT NULL,
    timestamp           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ai_model_name       VARCHAR(128)      NOT NULL DEFAULT 'unknown',
    user_prompt         TEXT              NOT NULL,
    ai_response         MEDIUMTEXT        NOT NULL,
    dark_pattern_type   VARCHAR(64)       NOT NULL,
    frustration_score   TINYINT UNSIGNED  NOT NULL DEFAULT 0,
    matched_signals     JSON,
    pattern_description TEXT,
    source_ip           VARCHAR(45),
    created_at          DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_conversation    (conversation_id),
    INDEX idx_pattern_type    (dark_pattern_type),
    INDEX idx_frustration     (frustration_score),
    INDEX idx_model           (ai_model_name),
    INDEX idx_timestamp       (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
