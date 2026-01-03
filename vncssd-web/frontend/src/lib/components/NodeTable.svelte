<script lang="ts">
    import type { Node } from "$lib/api";

    interface Props {
        nodes: Node[];
        compact?: boolean;
    }

    let { nodes, compact = false }: Props = $props();

    function getStatusBadge(status: string): string {
        switch (status) {
            case "online":
                return "badge-success";
            case "warning":
                return "badge-warning";
            case "error":
                return "badge-danger";
            default:
                return "badge-gray";
        }
    }

    function getStatusLabel(status: string): string {
        switch (status) {
            case "online":
                return "Trực tuyến";
            case "offline":
                return "Ngoại tuyến";
            case "warning":
                return "Cảnh báo";
            case "error":
                return "Lỗi";
            default:
                return status;
        }
    }

    function formatLastSeen(dateStr: string | null): string {
        if (!dateStr) return "Chưa kết nối";

        const date = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        if (diff < 60000) return "Vừa xong";
        if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
        return date.toLocaleDateString("vi-VN");
    }
</script>

{#if nodes.length === 0}
    <div class="text-center py-8 text-gray-500 dark:text-gray-400">
        <svg
            class="w-12 h-12 mx-auto mb-3 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
        >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"
            />
        </svg>
        <p>Chưa có node nào</p>
    </div>
{:else}
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                    <th
                        class="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400"
                        >Node</th
                    >
                    <th
                        class="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400"
                        >Loại</th
                    >
                    <th
                        class="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400"
                        >Trạng thái</th
                    >
                    {#if !compact}
                        <th
                            class="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400"
                            >Vị trí</th
                        >
                    {/if}
                    <th
                        class="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400"
                        >Cập nhật</th
                    >
                </tr>
            </thead>
            <tbody>
                {#each nodes as node}
                    <tr
                        class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                    >
                        <td class="py-3 px-4">
                            <a
                                href="/nodes/{node.id}"
                                class="flex items-center gap-3 group"
                            >
                                <div
                                    class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center"
                                >
                                    <svg
                                        class="w-4 h-4 text-gray-500 dark:text-gray-400"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"
                                        />
                                    </svg>
                                </div>
                                <div>
                                    <p
                                        class="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 transition-colors"
                                    >
                                        {node.name}
                                    </p>
                                    <p
                                        class="text-xs text-gray-500 dark:text-gray-400 font-mono"
                                    >
                                        {node.uuid.slice(0, 8)}...
                                    </p>
                                </div>
                            </a>
                        </td>
                        <td class="py-3 px-4">
                            <span
                                class="text-sm text-gray-600 dark:text-gray-300 capitalize"
                            >
                                {node.device_type}
                            </span>
                        </td>
                        <td class="py-3 px-4">
                            <span class={getStatusBadge(node.status)}>
                                {getStatusLabel(node.status)}
                            </span>
                        </td>
                        {#if !compact}
                            <td class="py-3 px-4">
                                <span
                                    class="text-sm text-gray-600 dark:text-gray-300"
                                >
                                    {node.location_name || "-"}
                                </span>
                            </td>
                        {/if}
                        <td class="py-3 px-4">
                            <span
                                class="text-sm text-gray-500 dark:text-gray-400"
                            >
                                {formatLastSeen(node.last_seen_at)}
                            </span>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
{/if}
