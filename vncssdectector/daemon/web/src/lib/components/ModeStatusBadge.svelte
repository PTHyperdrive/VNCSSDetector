<script lang="ts">
    interface ModeStatus {
        running_mode: 'standalone' | 'node' | 'swarm';
        connection_status: 'disconnected' | 'connecting' | 'connected' | 'error';
        server_ip: string | null;
        is_heuristic_passed: boolean;
        last_error: string | null;
    }

    let { status }: { status: ModeStatus | null } = $props();

    let status_text = $derived.by(() => {
        if (!status) return 'Đang tải...';

        if (status.running_mode === 'standalone') {
            return 'Standalone';
        }

        if (status.connection_status === 'connected') {
            return `Đã kết nối ${status.server_ip || ''}`;
        }

        if (status.connection_status === 'connecting') {
            return 'Đang kết nối...';
        }

        if (status.connection_status === 'error') {
            return 'Lỗi kết nối';
        }

        return 'Chưa kết nối';
    });

    let status_color = $derived.by(() => {
        if (!status) return 'text-gray-500';

        if (status.running_mode === 'standalone') {
            return 'text-blue-600';
        }

        if (status.connection_status === 'connected') {
            return 'text-green-600';
        }

        if (status.connection_status === 'connecting') {
            return 'text-yellow-600';
        }

        if (status.connection_status === 'error') {
            return 'text-red-600';
        }

        return 'text-gray-500';
    });

    let dot_color = $derived.by(() => {
        if (!status) return 'bg-gray-400';

        if (status.running_mode === 'standalone') {
            return 'bg-blue-500';
        }

        if (status.connection_status === 'connected') {
            return 'bg-green-500';
        }

        if (status.connection_status === 'connecting') {
            return 'bg-yellow-500 animate-pulse';
        }

        if (status.connection_status === 'error') {
            return 'bg-red-500';
        }

        return 'bg-gray-400';
    });
</script>

<div class="flex items-center gap-2">
    <span class={`w-2 h-2 rounded-full ${dot_color}`}></span>
    <span class={`text-sm font-medium ${status_color}`}>{status_text}</span>
</div>
