<script lang="ts">
    import { onMount } from "svelte";
    import { api, type Node } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";

    let nodes = $state<Node[]>([]);
    let loading = $state(true);
    let error = $state("");

    // Add node modal
    let showAddModal = $state(false);
    let newNode = $state({
        name: "",
        device_type: "android",
        location_name: "",
    });
    let addingNode = $state(false);

    // Token modal
    let showTokenModal = $state(false);
    let generatedToken = $state("");
    let tokenNodeName = $state("");

    onMount(async () => {
        await loadNodes();
    });

    async function loadNodes() {
        loading = true;
        error = "";
        try {
            nodes = await api.getNodes();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tải danh sách nodes";
        } finally {
            loading = false;
        }
    }

    async function addNode() {
        addingNode = true;
        try {
            const result = await api.createNode({
                name: newNode.name,
                device_type: newNode.device_type,
                location_name: newNode.location_name,
            });

            // Show the generated token
            generatedToken = result.api_key;
            tokenNodeName = newNode.name;
            showAddModal = false;
            showTokenModal = true;

            // Reset form
            newNode = { name: "", device_type: "android", location_name: "" };

            // Reload nodes
            await loadNodes();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tạo node";
        } finally {
            addingNode = false;
        }
    }

    async function generateToken(node: Node) {
        try {
            const result = await api.createNode({
                name: node.name,
                device_type: node.device_type,
            });
            generatedToken = result.api_key;
            tokenNodeName = node.name;
            showTokenModal = true;
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tạo token";
        }
    }

    async function deleteNode(id: number) {
        if (!confirm("Bạn có chắc muốn xóa node này?")) return;
        try {
            await api.deleteNode(id);
            await loadNodes();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi xóa node";
        }
    }

    function copyToken() {
        navigator.clipboard.writeText(generatedToken);
    }

    function getStatusColor(status: string) {
        switch (status) {
            case "online":
                return "bg-green-100 text-green-800";
            case "offline":
                return "bg-gray-100 text-gray-800";
            case "warning":
                return "bg-yellow-100 text-yellow-800";
            case "error":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function getStatusText(status: string) {
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
</script>

<svelte:head>
    <title>Nodes - VNCSSDetector</title>
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
                        Quản lý Nodes
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400">
                        Quản lý các thiết bị phát hiện trong hệ thống
                    </p>
                </div>
                <button
                    onclick={() => (showAddModal = true)}
                    class="btn-primary flex items-center gap-2"
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
                            d="M12 4v16m8-8H4"
                        />
                    </svg>
                    Thêm Node
                </button>
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
            {:else if nodes.length === 0}
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
                            d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"
                        />
                    </svg>
                    <h3
                        class="text-lg font-medium text-gray-900 dark:text-white mb-2"
                    >
                        Chưa có node nào
                    </h3>
                    <p class="text-gray-500 mb-4">
                        Thêm node đầu tiên để bắt đầu giám sát
                    </p>
                    <button
                        onclick={() => (showAddModal = true)}
                        class="btn-primary"
                    >
                        Thêm Node
                    </button>
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
                                    >Node</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Trạng thái</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Vị trí</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Loại thiết bị</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Lần cuối online</th
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
                            {#each nodes as node}
                                <tr
                                    class="hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    <td class="px-6 py-4">
                                        <div class="flex items-center">
                                            <div
                                                class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mr-3"
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
                                                <div
                                                    class="font-medium text-gray-900 dark:text-white"
                                                >
                                                    {node.name}
                                                </div>
                                                <div
                                                    class="text-sm text-gray-500"
                                                >
                                                    {node.uuid}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {getStatusColor(
                                                node.status,
                                            )}"
                                        >
                                            {getStatusText(node.status)}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {node.location_name || "-"}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400 capitalize"
                                    >
                                        {node.device_type}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {node.last_seen_at
                                            ? new Date(
                                                  node.last_seen_at,
                                              ).toLocaleString("vi-VN")
                                            : "-"}
                                    </td>
                                    <td class="px-6 py-4 text-right space-x-2">
                                        <button
                                            onclick={() => generateToken(node)}
                                            class="text-primary-600 hover:text-primary-900 dark:text-primary-400"
                                            title="Tạo token mới"
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
                                                    d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                                                />
                                            </svg>
                                        </button>
                                        <button
                                            onclick={() => deleteNode(node.id)}
                                            class="text-red-600 hover:text-red-900"
                                            title="Xóa node"
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

<!-- Add Node Modal -->
{#if showAddModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4"
        >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Thêm Node Mới
                </h2>
            </div>
            <form
                onsubmit={(e) => {
                    e.preventDefault();
                    addNode();
                }}
                class="p-6 space-y-4"
            >
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Tên Node
                    </label>
                    <input
                        type="text"
                        bind:value={newNode.name}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="VD: Node HCM-Q1-001"
                        required
                    />
                </div>
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Địa chỉ đặt Node
                    </label>
                    <input
                        type="text"
                        bind:value={newNode.location_name}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="VD: 123 Nguyễn Huệ, Q1, HCM"
                    />
                </div>
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Loại thiết bị
                    </label>
                    <select
                        bind:value={newNode.device_type}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                    >
                        <option value="android">Android</option>
                        <option value="pixel">Pixel</option>
                        <option value="raspberry_pi">Raspberry Pi</option>
                        <option value="linux_pc">Linux PC</option>
                    </select>
                </div>
                <div class="flex gap-3 pt-4">
                    <button
                        type="button"
                        onclick={() => (showAddModal = false)}
                        class="flex-1 btn-secondary"
                    >
                        Hủy
                    </button>
                    <button
                        type="submit"
                        disabled={addingNode}
                        class="flex-1 btn-primary"
                    >
                        {addingNode ? "Đang tạo..." : "Tạo Node"}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

<!-- Token Modal -->
{#if showTokenModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg mx-4"
        >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Token cho Node: {tokenNodeName}
                </h2>
            </div>
            <div class="p-6">
                <div
                    class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4"
                >
                    <div class="flex items-start">
                        <svg
                            class="w-5 h-5 text-yellow-600 mt-0.5 mr-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
                        </svg>
                        <p class="text-sm text-yellow-700 dark:text-yellow-300">
                            <strong>Quan trọng:</strong> Token này chỉ hiển thị một
                            lần. Hãy sao chép và lưu lại ngay!
                        </p>
                    </div>
                </div>
                <div
                    class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 font-mono text-sm break-all"
                >
                    {generatedToken}
                </div>
                <div class="flex gap-3 mt-6">
                    <button
                        onclick={copyToken}
                        class="flex-1 btn-secondary flex items-center justify-center gap-2"
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
                                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                            />
                        </svg>
                        Sao chép
                    </button>
                    <button
                        onclick={() => (showTokenModal = false)}
                        class="flex-1 btn-primary"
                    >
                        Đã lưu, đóng
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
