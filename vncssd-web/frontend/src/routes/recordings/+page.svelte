<script lang="ts">
    import { onMount } from "svelte";
    import { api, type Recording } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";

    let recordings = $state<Recording[]>([]);
    let loading = $state(true);
    let error = $state("");
    let filterStatus = $state("");

    onMount(async () => {
        await loadRecordings();
    });

    async function loadRecordings() {
        loading = true;
        error = "";
        try {
            const params: any = {};
            if (filterStatus) params.status = filterStatus;
            recordings = await api.getRecordings(params);
        } catch (e) {
            error =
                e instanceof Error ? e.message : "Lỗi tải danh sách bản ghi";
        } finally {
            loading = false;
        }
    }

    async function stopRecording(id: number) {
        try {
            await api.stopRecording(id);
            await loadRecordings();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi dừng ghi";
        }
    }

    async function triggerAnalysis(id: number) {
        try {
            await api.triggerAnalysis(id);
            await loadRecordings();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi phân tích";
        }
    }

    async function deleteRecording(id: number) {
        if (!confirm("Bạn có chắc muốn xóa bản ghi này?")) return;
        try {
            await api.deleteRecording(id);
            await loadRecordings();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi xóa bản ghi";
        }
    }

    function getStatusColor(status: string) {
        switch (status) {
            case "recording":
                return "bg-red-100 text-red-800";
            case "stopped":
                return "bg-gray-100 text-gray-800";
            case "analyzing":
                return "bg-yellow-100 text-yellow-800";
            case "analyzed":
                return "bg-green-100 text-green-800";
            case "error":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function getStatusText(status: string) {
        switch (status) {
            case "recording":
                return "Đang ghi";
            case "stopped":
                return "Đã dừng";
            case "analyzing":
                return "Đang phân tích";
            case "analyzed":
                return "Đã phân tích";
            case "error":
                return "Lỗi";
            default:
                return status;
        }
    }

    function formatFileSize(bytes: number) {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }
</script>

<svelte:head>
    <title>Bản ghi - VNCSSDetector</title>
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
                        Bản ghi
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400">
                        Quản lý các file QMDL từ nodes
                    </p>
                </div>
                <div class="flex gap-3">
                    <select
                        bind:value={filterStatus}
                        onchange={() => loadRecordings()}
                        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                    >
                        <option value="">Tất cả trạng thái</option>
                        <option value="recording">Đang ghi</option>
                        <option value="stopped">Đã dừng</option>
                        <option value="analyzing">Đang phân tích</option>
                        <option value="analyzed">Đã phân tích</option>
                    </select>
                    <button
                        onclick={() => loadRecordings()}
                        class="btn-secondary"
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
            {:else if recordings.length === 0}
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow p-12 text-center"
                >
                    <svg
                        class="w-16 h-16 mx-auto text-gray-300 mb-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                    <h3
                        class="text-lg font-medium text-gray-900 dark:text-white mb-2"
                    >
                        Chưa có bản ghi nào
                    </h3>
                    <p class="text-gray-500">
                        Các file QMDL từ nodes sẽ xuất hiện ở đây
                    </p>
                </div>
            {:else}
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden"
                >
                    <table class="w-full">
                        <thead class="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Tên file</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Node</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Trạng thái</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Kích thước</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Cảnh báo</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Thời gian</th
                                >
                                <th
                                    class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Thao tác</th
                                >
                            </tr>
                        </thead>
                        <tbody
                            class="divide-y divide-gray-200 dark:divide-gray-600"
                        >
                            {#each recordings as recording}
                                <tr
                                    class="hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    <td class="px-6 py-4">
                                        <div class="flex items-center">
                                            <div
                                                class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mr-3"
                                            >
                                                <svg
                                                    class="w-5 h-5 text-blue-600 dark:text-blue-400"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                                    />
                                                </svg>
                                            </div>
                                            <span
                                                class="font-medium text-gray-900 dark:text-white"
                                                >{recording.name}</span
                                            >
                                        </div>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {recording.node_name ||
                                            `Node ${recording.node_id}`}
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {getStatusColor(
                                                recording.status,
                                            )}"
                                        >
                                            {getStatusText(recording.status)}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {formatFileSize(
                                            recording.file_size_bytes,
                                        )}
                                    </td>
                                    <td class="px-6 py-4">
                                        {#if recording.warning_count > 0}
                                            <span
                                                class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800"
                                            >
                                                {recording.warning_count} cảnh báo
                                            </span>
                                        {:else}
                                            <span class="text-gray-400">-</span>
                                        {/if}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400 text-sm"
                                    >
                                        {new Date(
                                            recording.started_at,
                                        ).toLocaleString("vi-VN")}
                                    </td>
                                    <td class="px-6 py-4 text-right space-x-2">
                                        {#if recording.status === "recording"}
                                            <button
                                                onclick={() =>
                                                    stopRecording(recording.id)}
                                                class="text-red-600 hover:text-red-800"
                                                title="Dừng ghi"
                                            >
                                                <svg
                                                    class="w-5 h-5 inline"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                                    />
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
                                                    />
                                                </svg>
                                            </button>
                                        {:else if recording.status === "stopped" && recording.analysis_status === "pending"}
                                            <button
                                                onclick={() =>
                                                    triggerAnalysis(
                                                        recording.id,
                                                    )}
                                                class="text-blue-600 hover:text-blue-800"
                                                title="Phân tích"
                                            >
                                                <svg
                                                    class="w-5 h-5 inline"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                                    />
                                                </svg>
                                            </button>
                                        {/if}
                                        <button
                                            onclick={() =>
                                                deleteRecording(recording.id)}
                                            class="text-red-600 hover:text-red-800"
                                            title="Xóa"
                                        >
                                            <svg
                                                class="w-5 h-5 inline"
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
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </main>
</div>
