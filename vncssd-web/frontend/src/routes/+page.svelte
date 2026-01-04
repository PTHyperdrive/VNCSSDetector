<script lang="ts">
    import { onMount } from "svelte";
    import {
        api,
        type DashboardStats,
        type RecentAlert,
        type Node,
    } from "$lib/api";
    import { auth, isOperator } from "$lib/stores/auth";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import StatsCard from "$lib/components/StatsCard.svelte";
    import AlertList from "$lib/components/AlertList.svelte";
    import NodeTable from "$lib/components/NodeTable.svelte";

    let stats: DashboardStats | null = $state(null);
    let recentAlerts: RecentAlert[] = $state([]);
    let nodes: Node[] = $state([]);
    let loading = $state(true);
    let error: string | null = $state(null);

    async function loadData() {
        try {
            const [statsData, alertsData, nodesData] = await Promise.all([
                api.getDashboardStats(),
                api.getRecentAlerts(5),
                api.getNodes(),
            ]);
            stats = statsData;
            recentAlerts = alertsData;
            nodes = nodesData;
            error = null;
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load data";
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadData();

        // Refresh every 30 seconds
        const interval = setInterval(loadData, 30000);
        return () => clearInterval(interval);
    });

    function getStatusColor(status: string): string {
        switch (status) {
            case "online":
                return "text-green-500";
            case "offline":
                return "text-gray-400";
            case "warning":
                return "text-yellow-500";
            case "error":
                return "text-red-500";
            default:
                return "text-gray-400";
        }
    }
</script>

<svelte:head>
    <title>Dashboard - VNCSSDetector</title>
</svelte:head>

<div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <Sidebar />

    <main class="flex-1 overflow-auto">
        <div class="p-6 lg:p-8">
            <!-- Header -->
            <div class="flex items-center justify-between mb-8">
                <div>
                    <h1
                        class="text-2xl font-bold text-gray-900 dark:text-white"
                    >
                        Dashboard
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400">
                        Tổng quan hệ thống VNCSSDetector
                    </p>
                </div>
                <button
                    onclick={loadData}
                    class="btn-secondary"
                    disabled={loading}
                >
                    <svg
                        class="w-4 h-4 mr-2"
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
                    Làm mới
                </button>
            </div>

            {#if error}
                <div
                    class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6"
                >
                    <p class="text-red-800 dark:text-red-200">{error}</p>
                </div>
            {/if}

            {#if loading && !stats}
                <div class="flex items-center justify-center h-64">
                    <div
                        class="animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"
                    ></div>
                </div>
            {:else if stats}
                <!-- Stats Grid -->
                <div
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
                >
                    <StatsCard
                        title="Nodes Trực Tuyến"
                        value={stats.online_nodes}
                        total={stats.total_nodes}
                        icon="server"
                        color="green"
                    />
                    <StatsCard
                        title="Đang Ghi"
                        value={stats.active_recordings}
                        total={stats.total_recordings}
                        icon="record"
                        color="blue"
                    />
                    <StatsCard
                        title="Cảnh Báo Chưa Xử Lý"
                        value={stats.unacknowledged_alerts}
                        total={stats.total_alerts}
                        icon="alert"
                        color={stats.critical_alerts > 0 ? "red" : "yellow"}
                    />
                    <StatsCard
                        title="Phát Hiện Bất Thường"
                        value={stats.total_warnings_detected}
                        icon="warning"
                        color="purple"
                    />
                </div>

                <!-- Main Content Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Nodes Table -->
                    <div class="lg:col-span-2 card p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h2
                                class="text-lg font-semibold text-gray-900 dark:text-white"
                            >
                                Danh Sách Nodes
                            </h2>
                            {#if $isOperator}
                                <a href="/nodes" class="btn-primary text-sm">
                                    + Thêm Node
                                </a>
                            {/if}
                        </div>
                        <NodeTable {nodes} compact />
                    </div>

                    <!-- Recent Alerts -->
                    <div class="card p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h2
                                class="text-lg font-semibold text-gray-900 dark:text-white"
                            >
                                Cảnh Báo Gần Đây
                            </h2>
                            <a
                                href="/alerts"
                                class="text-sm text-primary-600 hover:text-primary-700"
                            >
                                Xem tất cả →
                            </a>
                        </div>
                        <AlertList alerts={recentAlerts} compact />
                    </div>
                </div>

                <!-- Storage Info -->
                <div class="mt-6 card p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3
                                class="text-sm font-medium text-gray-500 dark:text-gray-400"
                            >
                                Dung Lượng Sử Dụng
                            </h3>
                            <p
                                class="text-2xl font-bold text-gray-900 dark:text-white"
                            >
                                {stats.storage_used_formatted}
                            </p>
                        </div>
                        <div class="text-right">
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                Tổng ghi âm: {stats.total_recordings}
                            </p>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    </main>
</div>
