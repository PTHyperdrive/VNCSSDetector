/**
 * API client for VNCSSDetector Web Service
 */

const API_BASE = '/api';

interface ApiError {
    detail: string;
}

class ApiClient {
    private token: string | null = null;

    setToken(token: string | null) {
        this.token = token;
        if (token) {
            localStorage.setItem('access_token', token);
        } else {
            localStorage.removeItem('access_token');
        }
    }

    getToken(): string | null {
        if (!this.token) {
            this.token = localStorage.getItem('access_token');
        }
        return this.token;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const token = this.getToken();

        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Don't redirect here - let the auth store/layout handle it
                // This prevents redirect loops
                this.setToken(null);
                throw new Error('Unauthorized');
            }

            const errorData = await response.json().catch(() => ({
                detail: 'An error occurred'
            }));
            // Handle various error formats from FastAPI
            let errorMessage = 'An error occurred';
            if (typeof errorData.detail === 'string') {
                errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail.map((e: any) => e.msg || e.message || String(e)).join(', ');
            } else if (typeof errorData.detail === 'object' && errorData.detail?.msg) {
                errorMessage = errorData.detail.msg;
            } else if (errorData.message) {
                errorMessage = errorData.message;
            }
            throw new Error(errorMessage);
        }

        if (response.status === 204) {
            return undefined as T;
        }

        return response.json();
    }

    // Authentication
    async login(email: string, password: string) {
        const data = await this.request<{
            access_token: string;
            refresh_token: string;
        }>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.setToken(data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return data;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' }).catch(() => { });
        this.setToken(null);
        localStorage.removeItem('refresh_token');
    }

    async getCurrentUser() {
        return this.request<User>('/auth/me');
    }

    // Dashboard
    async getDashboardStats() {
        return this.request<DashboardStats>('/dashboard/stats');
    }

    async getRecentAlerts(limit = 10) {
        return this.request<RecentAlert[]>(`/dashboard/recent-alerts?limit=${limit}`);
    }

    async getNodeMap() {
        return this.request<NodeMapItem[]>('/dashboard/node-map');
    }

    // Nodes
    async getNodes(params?: { status?: string; device_type?: string }) {
        const query = new URLSearchParams(params as Record<string, string>);
        return this.request<Node[]>(`/nodes?${query}`);
    }

    async getNode(id: number) {
        return this.request<Node>(`/nodes/${id}`);
    }

    async createNode(data: CreateNodeRequest) {
        return this.request<NodeApiKeyResponse>('/nodes', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateNode(id: number, data: Partial<Node>) {
        return this.request<Node>(`/nodes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteNode(id: number) {
        return this.request<void>(`/nodes/${id}`, { method: 'DELETE' });
    }

    async getNodeStats(id: number) {
        return this.request<NodeStats>(`/nodes/${id}/stats`);
    }

    // Recordings
    async getRecordings(params?: { node_id?: number; status?: string }) {
        const query = new URLSearchParams();
        if (params?.node_id) query.set('node_id', String(params.node_id));
        if (params?.status) query.set('status', params.status);
        return this.request<Recording[]>(`/recordings?${query}`);
    }

    async getRecording(id: number) {
        return this.request<Recording>(`/recordings/${id}`);
    }

    async stopRecording(id: number) {
        return this.request<Recording>(`/recordings/${id}/stop`, { method: 'POST' });
    }

    async triggerAnalysis(id: number) {
        return this.request<Recording>(`/recordings/${id}/analyze`, { method: 'POST' });
    }

    async getAnalysisResults(recordingId: number) {
        return this.request<AnalysisResult[]>(`/recordings/${recordingId}/analysis`);
    }

    async deleteRecording(id: number) {
        return this.request<void>(`/recordings/${id}`, { method: 'DELETE' });
    }

    // Alerts
    async getAlerts(params?: {
        node_id?: number;
        severity?: string;
        is_acknowledged?: boolean;
    }) {
        const query = new URLSearchParams();
        if (params?.node_id) query.set('node_id', String(params.node_id));
        if (params?.severity) query.set('severity', params.severity);
        if (params?.is_acknowledged !== undefined) {
            query.set('is_acknowledged', String(params.is_acknowledged));
        }
        return this.request<Alert[]>(`/alerts?${query}`);
    }

    async acknowledgeAlert(id: number) {
        return this.request<Alert>(`/alerts/${id}/acknowledge`, { method: 'PUT' });
    }

    async acknowledgeAllAlerts(params?: { node_id?: number; severity?: string }) {
        const query = new URLSearchParams(params as Record<string, string>);
        return this.request<{ acknowledged_count: number }>(
            `/alerts/acknowledge-all?${query}`,
            { method: 'PUT' }
        );
    }

    async dismissAlert(id: number) {
        return this.request<void>(`/alerts/${id}`, { method: 'DELETE' });
    }

    // Users
    async getUsers() {
        return this.request<User[]>('/users');
    }

    async createUser(data: CreateUserRequest) {
        return this.request<User>('/users', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateUser(id: number, data: Partial<User>) {
        return this.request<User>(`/users/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteUser(id: number) {
        return this.request<void>(`/users/${id}`, { method: 'DELETE' });
    }
}

// Types
export interface User {
    id: number;
    email: string;
    full_name: string | null;
    role: 'admin' | 'operator' | 'viewer';
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface CreateUserRequest {
    email: string;
    password: string;
    full_name?: string;
    role?: 'admin' | 'operator' | 'viewer';
}

export interface Node {
    id: number;
    uuid: string;
    name: string;
    device_type: string;
    status: 'online' | 'offline' | 'warning' | 'error';
    ip_address: string | null;
    location_lat: number | null;
    location_lng: number | null;
    location_name: string | null;
    last_seen_at: string | null;
    config: Record<string, unknown> | null;
    created_at: string;
    updated_at: string;
}

export interface CreateNodeRequest {
    name: string;
    device_type: string;
    ip_address?: string;
    location_lat?: number;
    location_lng?: number;
    location_name?: string;
}

export interface NodeApiKeyResponse {
    node_id: number;
    uuid: string;
    api_key: string;
    message: string;
}

export interface NodeStats {
    node_id: number;
    node_uuid: string;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    battery_level: number | null;
    signal_strength: number | null;
    is_recording: boolean;
    current_recording_name: string | null;
    uptime_seconds: number;
    last_updated: string;
}

export interface Recording {
    id: number;
    node_id: number;
    name: string;
    file_path: string;
    file_size_bytes: number;
    status: 'recording' | 'stopped' | 'analyzing' | 'analyzed' | 'error';
    started_at: string;
    stopped_at: string | null;
    analysis_status: 'pending' | 'running' | 'completed' | 'failed';
    warning_count: number;
    created_at: string;
    node_name?: string;
    node_uuid?: string;
}

export interface AnalysisResult {
    id: number;
    recording_id: number;
    timestamp: string;
    event_type: 'informational' | 'warning' | 'critical';
    analyzer_name: string;
    message: string;
    details: Record<string, unknown> | null;
    created_at: string;
}

export interface Alert {
    id: number;
    node_id: number;
    recording_id: number | null;
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string | null;
    is_acknowledged: boolean;
    acknowledged_by_id: number | null;
    acknowledged_at: string | null;
    created_at: string;
    node_name?: string;
    node_uuid?: string;
}

export interface DashboardStats {
    total_nodes: number;
    online_nodes: number;
    offline_nodes: number;
    warning_nodes: number;
    total_recordings: number;
    active_recordings: number;
    total_alerts: number;
    unacknowledged_alerts: number;
    critical_alerts: number;
    total_warnings_detected: number;
    storage_used_bytes: number;
    storage_used_formatted: string;
}

export interface RecentAlert {
    id: number;
    node_id: number;
    node_name: string;
    severity: string;
    title: string;
    created_at: string;
    is_acknowledged: boolean;
}

export interface NodeMapItem {
    id: number;
    uuid: string;
    name: string;
    status: string;
    location_lat: number | null;
    location_lng: number | null;
    location_name: string | null;
    is_recording: boolean;
    warning_count: number;
    last_seen_at: string | null;
}

export const api = new ApiClient();
