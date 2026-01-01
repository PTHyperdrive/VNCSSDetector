-- Initial database setup script
-- This runs automatically when the PostgreSQL container starts

-- Create initial roles
INSERT INTO roles (name, permissions) VALUES 
    ('admin', '{"all": true}'),
    ('operator', '{"nodes.read": true, "nodes.command": true, "events.read": true, "notifications.read": true}'),
    ('viewer', '{"nodes.read": true, "events.read": true, "notifications.read": true}')
ON CONFLICT (name) DO NOTHING;
