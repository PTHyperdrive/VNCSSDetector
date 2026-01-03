-- VNCSSDetector Web Service - MySQL Database Schema
-- Compatible with MySQL 8.0+

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS vncssd_web 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE vncssd_web;

-- ============================================
-- Users and Authentication
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role ENUM('admin', 'operator', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- VNCSSDetector Nodes
-- ============================================
CREATE TABLE IF NOT EXISTS nodes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    device_type ENUM('orbic', 'tplink', 'tmobile', 'wingtech', 'pinephone', 'msm8916', 'other') NOT NULL,
    status ENUM('online', 'offline', 'warning', 'error') DEFAULT 'offline',
    ip_address VARCHAR(45),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_name VARCHAR(255),
    api_key_hash VARCHAR(255),
    last_seen_at TIMESTAMP NULL,
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_uuid (uuid),
    INDEX idx_status (status),
    INDEX idx_device_type (device_type),
    INDEX idx_last_seen (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Recordings (QMDL files)
-- ============================================
CREATE TABLE IF NOT EXISTS recordings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    node_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT UNSIGNED DEFAULT 0,
    status ENUM('recording', 'stopped', 'analyzing', 'analyzed', 'error') DEFAULT 'recording',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stopped_at TIMESTAMP NULL,
    analysis_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    warning_count INT UNSIGNED DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    INDEX idx_node_id (node_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at),
    INDEX idx_analysis_status (analysis_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Analysis Results
-- ============================================
CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recording_id BIGINT UNSIGNED NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type ENUM('informational', 'warning', 'critical') NOT NULL,
    analyzer_name VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE,
    INDEX idx_recording_id (recording_id),
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_analyzer (analyzer_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Alerts
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    node_id BIGINT UNSIGNED NOT NULL,
    recording_id BIGINT UNSIGNED,
    analysis_result_id BIGINT UNSIGNED,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by_id BIGINT UNSIGNED,
    acknowledged_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_result_id) REFERENCES analysis_results(id) ON DELETE SET NULL,
    FOREIGN KEY (acknowledged_by_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_node_id (node_id),
    INDEX idx_severity (severity),
    INDEX idx_acknowledged (is_acknowledged),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- System Logs
-- ============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    node_id BIGINT UNSIGNED,
    level ENUM('debug', 'info', 'warning', 'error') NOT NULL,
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    extra_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    INDEX idx_node_id (node_id),
    INDEX idx_level (level),
    INDEX idx_source (source),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Audit Logs
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id BIGINT UNSIGNED,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Default Admin User (password: admin123)
-- Change this immediately after first login!
-- ============================================
INSERT INTO users (email, password_hash, full_name, role, is_active)
VALUES (
    'admin@vncssd.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.a5J0mKqQoXYfHi',
    'System Administrator',
    'admin',
    TRUE
) ON DUPLICATE KEY UPDATE id=id;

-- ============================================
-- Views for common queries
-- ============================================

-- Active recordings view
CREATE OR REPLACE VIEW v_active_recordings AS
SELECT 
    r.id,
    r.name,
    r.file_size_bytes,
    r.started_at,
    n.id AS node_id,
    n.uuid AS node_uuid,
    n.name AS node_name,
    n.device_type,
    n.status AS node_status
FROM recordings r
JOIN nodes n ON r.node_id = n.id
WHERE r.status = 'recording';

-- Node summary view
CREATE OR REPLACE VIEW v_node_summary AS
SELECT 
    n.id,
    n.uuid,
    n.name,
    n.device_type,
    n.status,
    n.location_name,
    n.last_seen_at,
    (SELECT COUNT(*) FROM recordings r WHERE r.node_id = n.id) AS total_recordings,
    (SELECT COUNT(*) FROM recordings r WHERE r.node_id = n.id AND r.status = 'recording') AS active_recordings,
    (SELECT COALESCE(SUM(warning_count), 0) FROM recordings r WHERE r.node_id = n.id) AS total_warnings,
    (SELECT COUNT(*) FROM alerts a WHERE a.node_id = n.id AND a.is_acknowledged = FALSE) AS unack_alerts
FROM nodes n;

-- Alert summary view
CREATE OR REPLACE VIEW v_alert_summary AS
SELECT 
    a.id,
    a.severity,
    a.title,
    a.is_acknowledged,
    a.created_at,
    n.id AS node_id,
    n.name AS node_name,
    n.uuid AS node_uuid,
    r.name AS recording_name
FROM alerts a
JOIN nodes n ON a.node_id = n.id
LEFT JOIN recordings r ON a.recording_id = r.id
ORDER BY a.created_at DESC;
