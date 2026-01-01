<script lang="ts">
    interface ModeStatus {
        running_mode: 'standalone' | 'node' | 'swarm';
        connection_status: 'disconnected' | 'connecting' | 'connected' | 'error';
        server_ip: string | null;
        is_heuristic_passed: boolean;
        last_error: string | null;
    }

    let server_ip: string = $state('');
    let api_key: string = $state('');
    let loading: boolean = $state(false);
    let error: string | null = $state(null);
    let mode_status: ModeStatus | null = $state(null);
    let heuristic_status: string = $state('idle');

    // Fetch mode status on mount and every 3 seconds
    $effect(() => {
        fetch_mode_status();
        const interval = setInterval(fetch_mode_status, 3000);
        return () => clearInterval(interval);
    });

    async function fetch_mode_status() {
        try {
            const res = await fetch('/api/mode');
            if (res.ok) {
                mode_status = await res.json();
                if (mode_status?.server_ip) {
                    server_ip = mode_status.server_ip;
                }
                // Check if heuristic passed
                if (mode_status?.is_heuristic_passed) {
                    heuristic_status = 'passed';
                }
            }
        } catch (e) {
            console.error('Failed to fetch mode status:', e);
        }
    }

    async function save_config() {
        if (!server_ip.trim() || !api_key.trim()) {
            error = 'Vui lòng nhập cả Server IP và API Key';
            return;
        }

        loading = true;
        error = null;

        try {
            const res = await fetch('/api/node-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ server_ip, api_key }),
            });

            if (res.ok) {
                // Start heuristic test
                heuristic_status = 'checking';
                await fetch('/api/heuristic-test', { method: 'POST' });
            } else {
                const text = await res.text();
                error = text || 'Lỗi khi lưu cấu hình';
            }
        } catch (e) {
            error = 'Lỗi kết nối đến server';
        } finally {
            loading = false;
        }
    }

    async function unlock_to_node_mode() {
        try {
            await fetch('/api/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ running_mode: 'node' }),
            });
            // Reload page
            window.location.reload();
        } catch (e) {
            error = 'Lỗi khi chuyển chế độ';
        }
    }
</script>

<div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <img src="/vncssdetector_text.png" alt="" class="h-12 mx-auto mb-4" />
            <h1 class="text-2xl font-bold text-gray-800">Chế độ Swarm</h1>
            <p class="text-gray-600 text-sm mt-2">
                Giao diện web đã bị khóa. Nhập thông tin kết nối để tiếp tục.
            </p>
        </div>

        {#if error}
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
                {error}
            </div>
        {/if}

        <div class="space-y-4">
            <div>
                <label for="server_ip" class="block text-sm font-medium text-gray-700 mb-1">
                    Server IP
                </label>
                <input
                    type="text"
                    id="server_ip"
                    bind:value={server_ip}
                    placeholder="192.168.1.100:3000"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            <div>
                <label for="api_key" class="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                </label>
                <input
                    type="password"
                    id="api_key"
                    bind:value={api_key}
                    placeholder="vnc_xxxxxxxxxxxxx"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            <!-- Connection Status -->
            <div class="bg-gray-50 p-4 rounded-md">
                <div class="flex items-center justify-between">
                    <span class="font-medium">Trạng thái:</span>
                    {#if mode_status?.connection_status === 'connected'}
                        <span class="flex items-center gap-2 text-green-600">
                            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                            Đã kết nối
                        </span>
                    {:else if mode_status?.connection_status === 'connecting'}
                        <span class="flex items-center gap-2 text-yellow-600">
                            <span class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
                            Đang kết nối...
                        </span>
                    {:else}
                        <span class="flex items-center gap-2 text-gray-500">
                            <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                            Chưa kết nối
                        </span>
                    {/if}
                </div>

                <!-- Heuristic Test Status -->
                <div class="flex items-center justify-between mt-2">
                    <span class="font-medium">Kiểm tra VNCSSDetector:</span>
                    {#if heuristic_status === 'passed'}
                        <span class="flex items-center gap-2 text-green-600">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path
                                    fill-rule="evenodd"
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                            Đang hoạt động
                        </span>
                    {:else if heuristic_status === 'checking'}
                        <span class="flex items-center gap-2 text-yellow-600">
                            <span
                                class="w-4 h-4 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin"
                            ></span>
                            Đang kiểm tra...
                        </span>
                    {:else}
                        <span class="text-gray-500">Chưa kiểm tra</span>
                    {/if}
                </div>

                {#if mode_status?.last_error}
                    <p class="text-xs text-red-500 mt-2">{mode_status.last_error}</p>
                {/if}
            </div>

            <button
                onclick={save_config}
                disabled={loading}
                class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
                {loading ? 'Đang lưu...' : 'Lưu và Kết nối'}
            </button>

            <hr class="my-4" />

            <button
                onclick={unlock_to_node_mode}
                class="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
            >
                🔓 Mở khóa (Chuyển về chế độ Node)
            </button>
        </div>
    </div>
</div>
