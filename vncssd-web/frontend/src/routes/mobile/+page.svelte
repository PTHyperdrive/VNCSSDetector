<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";

    interface MobileToken {
        id: number;
        token: string;
        name: string;
        created_at: string;
        last_used_at: string | null;
        is_active: boolean;
    }

    let tokens = $state<MobileToken[]>([]);
    let loading = $state(true);
    let error = $state("");

    // Add token modal
    let showAddModal = $state(false);
    let tokenName = $state("");
    let addingToken = $state(false);

    // Generated token display
    let showTokenModal = $state(false);
    let generatedToken = $state("");
    let generatedTokenName = $state("");

    onMount(async () => {
        await loadTokens();
    });

    async function loadTokens() {
        loading = true;
        error = "";
        try {
            // API endpoint sẽ được tạo sau
            const response = await fetch("/api/mobile/tokens", {
                credentials: "include",
            });
            if (response.ok) {
                tokens = await response.json();
            } else {
                // Fallback - hiện tại chưa có API
                tokens = [];
            }
        } catch (e) {
            tokens = [];
        } finally {
            loading = false;
        }
    }

    async function generateToken() {
        addingToken = true;
        try {
            const response = await fetch("/api/mobile/tokens", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ name: tokenName }),
            });

            if (response.ok) {
                const result = await response.json();
                generatedToken = result.token;
                generatedTokenName = tokenName;
                showAddModal = false;
                showTokenModal = true;
                tokenName = "";
                await loadTokens();
            } else {
                error = "Lỗi tạo token";
            }
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tạo token";
        } finally {
            addingToken = false;
        }
    }

    async function revokeToken(id: number) {
        if (
            !confirm(
                "Bạn có chắc muốn thu hồi token này? Thiết bị sử dụng token sẽ không thể kết nối.",
            )
        )
            return;
        try {
            await fetch(`/api/mobile/tokens/${id}`, {
                method: "DELETE",
                credentials: "include",
            });
            await loadTokens();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi thu hồi token";
        }
    }

    function copyToken() {
        navigator.clipboard.writeText(generatedToken);
    }
</script>

<svelte:head>
    <title>Mobile Tokens - VNCSSDetector</title>
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
                        Mobile Tokens
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400">
                        Tạo token để ứng dụng mobile nhận thông báo từ hệ thống
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
                    Tạo Token Mới
                </button>
            </div>

            <!-- Info Card -->
            <div
                class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-6"
            >
                <div class="flex items-start">
                    <svg
                        class="w-6 h-6 text-blue-600 mt-0.5 mr-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    <div>
                        <h3
                            class="font-medium text-blue-900 dark:text-blue-200 mb-1"
                        >
                            Hướng dẫn sử dụng
                        </h3>
                        <ol
                            class="text-sm text-blue-700 dark:text-blue-300 list-decimal list-inside space-y-1"
                        >
                            <li>Tạo token mới cho mỗi thiết bị mobile</li>
                            <li>Mở ứng dụng VNCSSDetector trên điện thoại</li>
                            <li>Nhập token vào phần "Kết nối Server"</li>
                            <li>
                                Điện thoại sẽ tự động nhận thông báo khi có cảnh
                                báo mới
                            </li>
                        </ol>
                    </div>
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
            {:else if tokens.length === 0}
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
                            d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                        />
                    </svg>
                    <h3
                        class="text-lg font-medium text-gray-900 dark:text-white mb-2"
                    >
                        Chưa có token nào
                    </h3>
                    <p class="text-gray-500 mb-4">
                        Tạo token đầu tiên để kết nối ứng dụng mobile
                    </p>
                    <button
                        onclick={() => (showAddModal = true)}
                        class="btn-primary"
                    >
                        Tạo Token
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
                                    >Tên thiết bị</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Trạng thái</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Ngày tạo</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Lần dùng cuối</th
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
                            {#each tokens as token}
                                <tr
                                    class="hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    <td class="px-6 py-4">
                                        <div class="flex items-center">
                                            <div
                                                class="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mr-3"
                                            >
                                                <svg
                                                    class="w-5 h-5 text-green-600 dark:text-green-400"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                                                    />
                                                </svg>
                                            </div>
                                            <span
                                                class="font-medium text-gray-900 dark:text-white"
                                                >{token.name}</span
                                            >
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {token.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-gray-100 text-gray-800'}"
                                        >
                                            {token.is_active
                                                ? "Hoạt động"
                                                : "Đã thu hồi"}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {new Date(
                                            token.created_at,
                                        ).toLocaleDateString("vi-VN")}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {token.last_used_at
                                            ? new Date(
                                                  token.last_used_at,
                                              ).toLocaleString("vi-VN")
                                            : "Chưa sử dụng"}
                                    </td>
                                    <td class="px-6 py-4 text-right">
                                        {#if token.is_active}
                                            <button
                                                onclick={() =>
                                                    revokeToken(token.id)}
                                                class="text-red-600 hover:text-red-900"
                                                title="Thu hồi token"
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
                                                        d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
                                                    />
                                                </svg>
                                            </button>
                                        {/if}
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

<!-- Add Token Modal -->
{#if showAddModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4"
        >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Tạo Token Mới
                </h2>
            </div>
            <form
                onsubmit={(e) => {
                    e.preventDefault();
                    generateToken();
                }}
                class="p-6 space-y-4"
            >
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Tên thiết bị
                    </label>
                    <input
                        type="text"
                        bind:value={tokenName}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="VD: iPhone của Minh"
                        required
                    />
                    <p class="text-xs text-gray-500 mt-1">
                        Đặt tên dễ nhớ để quản lý sau này
                    </p>
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
                        disabled={addingToken}
                        class="flex-1 btn-primary"
                    >
                        {addingToken ? "Đang tạo..." : "Tạo Token"}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

<!-- Token Display Modal -->
{#if showTokenModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg mx-4"
        >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Token cho: {generatedTokenName}
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
                            lần. Hãy sao chép và nhập vào ứng dụng mobile ngay!
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
