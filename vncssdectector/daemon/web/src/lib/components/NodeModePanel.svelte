<script lang="ts">
    import { onMount } from 'svelte';

    interface ModeStatus {
        running_mode: 'standalone' | 'node' | 'swarm';
        connection_status: 'disconnected' | 'connecting' | 'connected' | 'error';
        server_ip: string | null;
        is_heuristic_passed: boolean;
        last_error: string | null;
    }

    let { shown = $bindable() }: { shown: boolean } = $props();

    let server_ip: string = $state('');
    let api_key: string = $state('');
    let loading: boolean = $state(false);
    let error: string | null = $state(null);
    let mode_status: ModeStatus | null = $state(null);

    onMount(() => {
        fetch_mode_status();
    });

    async function fetch_mode_status() {
        try {
            const res = await fetch('/api/mode');
            if (res.ok) {
                mode_status = await res.json();
                if (mode_status?.server_ip) {
                    server_ip = mode_status.server_ip;
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
                shown = false;
                // Reload page to apply changes
                setTimeout(() => window.location.reload(), 500);
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
</script>

{#if shown}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-40" onclick={() => (shown = false)}></div>
    <div
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-lg shadow-lg p-6 w-96 max-w-[90vw]"
    >
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Cấu hình Node</h2>
            <button onclick={() => (shown = false)} class="text-gray-500 hover:text-gray-700">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                    />
                </svg>
            </button>
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
                <p class="text-xs text-gray-500 mt-1">Địa chỉ IP hoặc hostname của VNCSSD Server</p>
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
                <p class="text-xs text-gray-500 mt-1">API Key được tạo từ VNCSSD Server</p>
            </div>

            {#if mode_status}
                <div class="bg-gray-100 p-3 rounded-md">
                    <p class="text-sm">
                        <span class="font-medium">Trạng thái: </span>
                        {#if mode_status.connection_status === 'connected'}
                            <span class="text-green-600">Đã kết nối</span>
                        {:else if mode_status.connection_status === 'connecting'}
                            <span class="text-yellow-600">Đang kết nối...</span>
                        {:else if mode_status.connection_status === 'error'}
                            <span class="text-red-600">Lỗi</span>
                        {:else}
                            <span class="text-gray-600">Chưa kết nối</span>
                        {/if}
                    </p>
                    {#if mode_status.last_error}
                        <p class="text-xs text-red-500 mt-1">{mode_status.last_error}</p>
                    {/if}
                </div>
            {/if}

            <button
                onclick={save_config}
                disabled={loading}
                class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
                {loading ? 'Đang lưu...' : 'Lưu và Kết nối'}
            </button>
        </div>
    </div>
{/if}
