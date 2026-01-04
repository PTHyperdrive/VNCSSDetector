<script lang="ts">
    import { auth } from "$lib/stores/auth";
    import { goto } from "$app/navigation";

    let email = $state("");
    let password = $state("");
    let error = $state("");
    let loading = $state(false);

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = "";
        loading = true;

        try {
            const result = await auth.login(email, password);

            if (result.success) {
                // Cookie is automatically set by the server
                // Use window.location for reliable redirect with full page reload
                window.location.href = "/";
            } else {
                // Display error message (Vietnamese)
                if (
                    result.error?.includes("Incorrect") ||
                    result.error?.includes("401")
                ) {
                    error = "Email hoặc mật khẩu không đúng";
                } else if (
                    result.error?.includes("not a valid email") ||
                    result.error?.includes("422")
                ) {
                    error = "Email không hợp lệ";
                } else {
                    error = result.error || "Đăng nhập thất bại";
                }
            }
        } catch (err) {
            error = "Đã xảy ra lỗi. Vui lòng thử lại.";
            console.error("Login error:", err);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Đăng Nhập - VNCSSDetector</title>
</svelte:head>

<div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-800"
>
    <div class="w-full max-w-md">
        <!-- Logo & Title -->
        <div class="text-center mb-8">
            <div
                class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4 shadow-lg"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-8 w-8 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                </svg>
            </div>
            <h1 class="text-3xl font-bold text-white">VNCSSDetector</h1>
            <p class="text-blue-200 mt-2">
                Hệ thống phát hiện trạm thu phát giả mạo
            </p>
        </div>

        <!-- Login Card -->
        <div class="bg-white rounded-xl shadow-2xl p-8">
            <h2 class="text-2xl font-semibold text-gray-800 text-center mb-6">
                Đăng Nhập
            </h2>

            {#if error}
                <div
                    class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4"
                >
                    {error}
                </div>
            {/if}

            <form onsubmit={handleSubmit} class="space-y-5">
                <div>
                    <label
                        for="email"
                        class="block text-sm font-medium text-gray-700 mb-1"
                    >
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        bind:value={email}
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                        placeholder="admin@vncssd.notrespond.com"
                        required
                    />
                </div>

                <div>
                    <label
                        for="password"
                        class="block text-sm font-medium text-gray-700 mb-1"
                    >
                        Mật khẩu
                    </label>
                    <input
                        type="password"
                        id="password"
                        bind:value={password}
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                        placeholder="••••••••"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {#if loading}
                        <span class="inline-flex items-center">
                            <svg
                                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                            >
                                <circle
                                    class="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    stroke-width="4"
                                ></circle>
                                <path
                                    class="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                ></path>
                            </svg>
                            Đang xử lý...
                        </span>
                    {:else}
                        Đăng Nhập
                    {/if}
                </button>
            </form>

            <div class="mt-6 text-center text-sm text-gray-500">
                Tài khoản mặc định: <span class="text-blue-600"
                    >admin@vncssd.notrespond.com</span
                >
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-6 text-center text-blue-200 text-sm">
            <p>VNCSSDetector &copy; 2026</p>
        </div>
    </div>
</div>
