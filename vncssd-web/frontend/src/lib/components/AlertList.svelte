<script lang="ts">
    import type { RecentAlert } from "$lib/api";

    interface Props {
        alerts: RecentAlert[];
        compact?: boolean;
    }

    let { alerts, compact = false }: Props = $props();

    function getSeverityBadge(severity: string): string {
        switch (severity) {
            case "critical":
                return "badge-danger";
            case "high":
                return "badge-warning";
            case "medium":
                return "badge-info";
            default:
                return "badge-gray";
        }
    }

    function formatTime(dateStr: string): string {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        if (diff < 60000) return "Vừa xong";
        if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
        return date.toLocaleDateString("vi-VN");
    }
</script>

{#if alerts.length === 0}
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
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
        </svg>
        <p>Không có cảnh báo</p>
    </div>
{:else}
    <div class="space-y-3">
        {#each alerts as alert}
            <a
                href="/alerts/{alert.id}"
                class="block p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
                <div class="flex items-start gap-3">
                    <div class="flex-shrink-0 mt-0.5">
                        {#if alert.severity === "critical"}
                            <div
                                class="w-2 h-2 bg-red-500 rounded-full animate-pulse"
                            ></div>
                        {:else if alert.severity === "high"}
                            <div
                                class="w-2 h-2 bg-yellow-500 rounded-full"
                            ></div>
                        {:else}
                            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                        {/if}
                    </div>
                    <div class="flex-1 min-w-0">
                        <p
                            class="text-sm font-medium text-gray-900 dark:text-white truncate"
                        >
                            {alert.title}
                        </p>
                        <div class="flex items-center gap-2 mt-1">
                            <span
                                class="text-xs text-gray-500 dark:text-gray-400"
                            >
                                {alert.node_name}
                            </span>
                            <span class="text-gray-300 dark:text-gray-600"
                                >•</span
                            >
                            <span
                                class="text-xs text-gray-500 dark:text-gray-400"
                            >
                                {formatTime(alert.created_at)}
                            </span>
                        </div>
                    </div>
                    <span class="{getSeverityBadge(alert.severity)} capitalize">
                        {alert.severity}
                    </span>
                </div>
            </a>
        {/each}
    </div>
{/if}
