<script lang="ts">
    import { onMount } from "svelte";
    import { api, type Alert } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";

    let alerts = $state<Alert[]>([]);
    let loading = $state(true);
    let error = $state("");
    let filterSeverity = $state("");
    let filterNodeId = $state<number | null>(null);

    onMount(async () => {
        await loadAlerts();
    });

    async function loadAlerts() {
        loading = true;
        error = "";
        try {
            const params: any = {};
            if (filterSeverity) params.severity = filterSeverity;
            if (filterNodeId) params.node_id = filterNodeId;
            alerts = await api.getAlerts(params);
        } catch (e) {
            error =
                e instanceof Error ? e.message : "Lỗi tải danh sách cảnh báo";
        } finally {
            loading = false;
        }
    }

    async function acknowledgeAlert(id: number) {
        try {
            await api.acknowledgeAlert(id);
            await loadAlerts();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi xác nhận cảnh báo";
        }
    }

    async function dismissAlert(id: number) {
        if (!confirm("Bạn có chắc muốn xóa cảnh báo này?")) return;
        try {
            await api.dismissAlert(id);
            await loadAlerts();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi xóa cảnh báo";
        }
    }

    function getSeverityColor(severity: string) {
        switch (severity) {
            case "critical":
                return "bg-red-100 text-red-800 border-red-300";
            case "high":
                return "bg-orange-100 text-orange-800 border-orange-300";
            case "medium":
                return "bg-yellow-100 text-yellow-800 border-yellow-300";
            default:
                return "bg-blue-100 text-blue-800 border-blue-300";
        }
    }

    function getSeverityText(severity: string) {
        switch (severity) {
            case "critical":
                return "Nghiêm trọng";
            case "high":
                return "Cao";
            case "medium":
                return "Trung bình";
            default:
                return "Thấp";
        }
    }

    // Group alerts by node
    function groupByNode(alerts: Alert[]) {
        const groups: { [key: string]: Alert[] } = {};
        for (const alert of alerts) {
            const nodeName = alert.node_name || `Node ${alert.node_id}`;
            if (!groups[nodeName]) groups[nodeName] = [];
            groups[nodeName].push(alert);
        }
        return Object.entries(groups);
    }
</script>

<svelte:head>
    <title>Cảnh báo - VNCSSDetector</title>
</svelte:head>

<div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <Sidebar />

    <main class="flex-1 overflow-auto">
        <div class="p-8">
            <!-- Header -->
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h1
                        class="text-2xl font-bold text-gray-900 dark:text-white"
                    >
                        Cảnh báo
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400">
                        Theo dõi và xử lý các cảnh báo từ nodes
                    </p>
                </div>
                <div class="flex gap-3">
                    <select
                        bind:value={filterSeverity}
                        onchange={() => loadAlerts()}
                        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                    >
                        <option value="">Tất cả mức độ</option>
                        <option value="critical">Nghiêm trọng</option>
                        <option value="high">Cao</option>
                        <option value="medium">Trung bình</option>
                        <option value="low">Thấp</option>
                    </select>
                    <button onclick={() => loadAlerts()} class="btn-secondary">
                        <svg
                            class="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                            />
                        </svg>
                    </button>
                </div>
            </div>

            {#if error}
                <div class="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
                    {error}
                </div>
            {/if}

            {#if loading}
                <div class="flex justify-center py-12">
                    <div
                        class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
                    ></div>
                </div>
            {:else if alerts.length === 0}
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow p-12 text-center"
                >
                    <svg
                        class="w-16 h-16 mx-auto text-green-400 mb-4"
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
                    <h3
                        class="text-lg font-medium text-gray-900 dark:text-white mb-2"
                    >
                        Không có cảnh báo
                    </h3>
                    <p class="text-gray-500">
                        Hệ thống đang hoạt động bình thường
                    </p>
                </div>
            {:else}
                <!-- Grouped by Node -->
                <div class="space-y-6">
                    {#each groupByNode(alerts) as [nodeName, nodeAlerts]}
                        <div
                            class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden"
                        >
                            <div
                                class="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600"
                            >
                                <div class="flex items-center gap-3">
                                    <div
                                        class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center"
                                    >
                                        <svg
                                            class="w-5 h-5 text-primary-600 dark:text-primary-400"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2"
                                            />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3
                                            class="font-semibold text-gray-900 dark:text-white"
                                        >
                                            {nodeName}
                                        </h3>
                                        <p class="text-sm text-gray-500">
                                            {nodeAlerts.length} cảnh báo
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div
                                class="divide-y divide-gray-200 dark:divide-gray-600"
                            >
                                {#each nodeAlerts as alert}
                                    <div
                                        class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                                    >
                                        <div
                                            class="flex items-start justify-between"
                                        >
                                            <div class="flex-1">
                                                <div
                                                    class="flex items-center gap-3 mb-2"
                                                >
                                                    <span
                                                        class="px-2 py-1 text-xs font-semibold rounded-full border {getSeverityColor(
                                                            alert.severity,
                                                        )}"
                                                    >
                                                        {getSeverityText(
                                                            alert.severity,
                                                        )}
                                                    </span>
                                                    <span
                                                        class="text-sm text-gray-500"
                                                    >
                                                        {new Date(
                                                            alert.created_at,
                                                        ).toLocaleString(
                                                            "vi-VN",
                                                        )}
                                                    </span>
                                                    {#if alert.is_acknowledged}
                                                        <span
                                                            class="text-xs text-green-600 flex items-center gap-1"
                                                        >
                                                            <svg
                                                                class="w-4 h-4"
                                                                fill="none"
                                                                stroke="currentColor"
                                                                viewBox="0 0 24 24"
                                                            >
                                                                <path
                                                                    stroke-linecap="round"
                                                                    stroke-linejoin="round"
                                                                    stroke-width="2"
                                                                    d="M5 13l4 4L19 7"
                                                                />
                                                            </svg>
                                                            Đã xác nhận
                                                        </span>
                                                    {/if}
                                                </div>
                                                <h4
                                                    class="font-medium text-gray-900 dark:text-white"
                                                >
                                                    {alert.title}
                                                </h4>
                                                {#if alert.description}
                                                    <p
                                                        class="text-sm text-gray-500 mt-1"
                                                    >
                                                        {alert.description}
                                                    </p>
                                                {/if}
                                            </div>
                                            <div
                                                class="flex items-center gap-2 ml-4"
                                            >
                                                {#if !alert.is_acknowledged}
                                                    <button
                                                        onclick={() =>
                                                            acknowledgeAlert(
                                                                alert.id,
                                                            )}
                                                        class="text-green-600 hover:text-green-800 p-2"
                                                        title="Xác nhận"
                                                    >
                                                        <svg
                                                            class="w-5 h-5"
                                                            fill="none"
                                                            stroke="currentColor"
                                                            viewBox="0 0 24 24"
                                                        >
                                                            <path
                                                                stroke-linecap="round"
                                                                stroke-linejoin="round"
                                                                stroke-width="2"
                                                                d="M5 13l4 4L19 7"
                                                            />
                                                        </svg>
                                                    </button>
                                                {/if}
                                                <button
                                                    onclick={() =>
                                                        dismissAlert(alert.id)}
                                                    class="text-red-600 hover:text-red-800 p-2"
                                                    title="Xóa"
                                                >
                                                    <svg
                                                        class="w-5 h-5"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        viewBox="0 0 24 24"
                                                    >
                                                        <path
                                                            stroke-linecap="round"
                                                            stroke-linejoin="round"
                                                            stroke-width="2"
                                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                                        />
                                                    </svg>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </main>
</div>
