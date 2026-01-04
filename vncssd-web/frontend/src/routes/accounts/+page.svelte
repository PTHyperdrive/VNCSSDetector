<script lang="ts">
    import { onMount } from "svelte";
    import { api, type User } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { isAdmin } from "$lib/stores/auth";

    let users = $state<User[]>([]);
    let loading = $state(true);
    let error = $state("");

    // Add user modal
    let showAddModal = $state(false);
    let newUser = $state({
        email: "",
        password: "",
        full_name: "",
        role: "viewer" as "admin" | "operator" | "viewer",
    });
    let addingUser = $state(false);

    onMount(async () => {
        await loadUsers();
    });

    async function loadUsers() {
        loading = true;
        error = "";
        try {
            users = await api.getUsers();
        } catch (e) {
            error =
                e instanceof Error ? e.message : "Lỗi tải danh sách tài khoản";
        } finally {
            loading = false;
        }
    }

    async function addUser() {
        addingUser = true;
        try {
            await api.createUser({
                email: newUser.email,
                password: newUser.password,
                full_name: newUser.full_name,
                role: newUser.role,
            });
            showAddModal = false;
            newUser = {
                email: "",
                password: "",
                full_name: "",
                role: "viewer",
            };
            await loadUsers();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tạo tài khoản";
        } finally {
            addingUser = false;
        }
    }

    async function toggleUserStatus(user: User) {
        try {
            await api.updateUser(user.id, { is_active: !user.is_active });
            await loadUsers();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi cập nhật tài khoản";
        }
    }

    async function deleteUser(id: number) {
        if (!confirm("Bạn có chắc muốn xóa tài khoản này?")) return;
        try {
            await api.deleteUser(id);
            await loadUsers();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi xóa tài khoản";
        }
    }

    function getRoleColor(role: string) {
        switch (role) {
            case "admin":
                return "bg-red-100 text-red-800";
            case "operator":
                return "bg-blue-100 text-blue-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function getRoleName(role: string) {
        switch (role) {
            case "admin":
                return "Quản trị viên";
            case "operator":
                return "Vận hành viên";
            default:
                return "Người xem";
        }
    }
</script>

<svelte:head>
    <title>Tài khoản - VNCSSDetector</title>
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
                        Quản lý Tài khoản
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400">
                        Quản lý người dùng trong hệ thống
                    </p>
                </div>
                {#if $isAdmin}
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
                        Thêm Tài khoản
                    </button>
                {/if}
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
            {:else}
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden"
                >
                    <table class="w-full">
                        <thead class="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Người dùng</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Email</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Vai trò</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Trạng thái</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                    >Ngày tạo</th
                                >
                                {#if $isAdmin}
                                    <th
                                        class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                                        >Thao tác</th
                                    >
                                {/if}
                            </tr>
                        </thead>
                        <tbody
                            class="divide-y divide-gray-200 dark:divide-gray-600"
                        >
                            {#each users as user}
                                <tr
                                    class="hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    <td class="px-6 py-4">
                                        <div class="flex items-center">
                                            <div
                                                class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mr-3"
                                            >
                                                <span
                                                    class="text-primary-600 dark:text-primary-400 font-medium"
                                                >
                                                    {user.full_name?.[0] ||
                                                        user.email[0].toUpperCase()}
                                                </span>
                                            </div>
                                            <span
                                                class="font-medium text-gray-900 dark:text-white"
                                            >
                                                {user.full_name ||
                                                    "Chưa đặt tên"}
                                            </span>
                                        </div>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {user.email}
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {getRoleColor(
                                                user.role,
                                            )}"
                                        >
                                            {getRoleName(user.role)}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {user.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-gray-100 text-gray-800'}"
                                        >
                                            {user.is_active
                                                ? "Hoạt động"
                                                : "Đã khóa"}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-gray-500 dark:text-gray-400"
                                    >
                                        {new Date(
                                            user.created_at,
                                        ).toLocaleDateString("vi-VN")}
                                    </td>
                                    {#if $isAdmin}
                                        <td
                                            class="px-6 py-4 text-right space-x-2"
                                        >
                                            <button
                                                onclick={() =>
                                                    toggleUserStatus(user)}
                                                class="text-yellow-600 hover:text-yellow-900"
                                                title={user.is_active
                                                    ? "Khóa tài khoản"
                                                    : "Mở khóa tài khoản"}
                                            >
                                                <svg
                                                    class="w-5 h-5 inline"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    {#if user.is_active}
                                                        <path
                                                            stroke-linecap="round"
                                                            stroke-linejoin="round"
                                                            stroke-width="2"
                                                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                                        />
                                                    {:else}
                                                        <path
                                                            stroke-linecap="round"
                                                            stroke-linejoin="round"
                                                            stroke-width="2"
                                                            d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"
                                                        />
                                                    {/if}
                                                </svg>
                                            </button>
                                            <button
                                                onclick={() =>
                                                    deleteUser(user.id)}
                                                class="text-red-600 hover:text-red-900"
                                                title="Xóa tài khoản"
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
                                    {/if}
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </main>
</div>

<!-- Add User Modal -->
{#if showAddModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4"
        >
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    Thêm Tài khoản Mới
                </h2>
            </div>
            <form
                onsubmit={(e) => {
                    e.preventDefault();
                    addUser();
                }}
                class="p-6 space-y-4"
            >
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Họ và tên
                    </label>
                    <input
                        type="text"
                        bind:value={newUser.full_name}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="VD: Nguyễn Văn A"
                    />
                </div>
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Email
                    </label>
                    <input
                        type="email"
                        bind:value={newUser.email}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="email@example.com"
                        required
                    />
                </div>
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Mật khẩu
                    </label>
                    <input
                        type="password"
                        bind:value={newUser.password}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                        placeholder="••••••••"
                        required
                    />
                </div>
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                        Vai trò
                    </label>
                    <select
                        bind:value={newUser.role}
                        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                    >
                        <option value="viewer">Người xem</option>
                        <option value="operator">Vận hành viên</option>
                        <option value="admin">Quản trị viên</option>
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
                        disabled={addingUser}
                        class="flex-1 btn-primary"
                    >
                        {addingUser ? "Đang tạo..." : "Tạo Tài khoản"}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}
