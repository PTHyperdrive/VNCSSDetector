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

        const result = await auth.login(email, password);

        if (result.success) {
            goto("/");
        } else {
            error = result.error || "Đăng nhập thất bại";
        }

        loading = false;
    }
</script>

<svelte:head>
    <title>Đăng Nhập - VNCSSDetector</title>
</svelte:head>

<div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900 px-4"
>
    <div class="max-w-md w-full">
        <!-- Logo -->
        <div class="text-center mb-8">
            <div
                class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4"
            >
                <svg
                    class="w-10 h-10 text-primary-600"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                >
                    <path
                        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
                    />
                </svg>
            </div>
            <h1 class="text-3xl font-bold text-white">VNCSSDetector</h1>
            <p class="text-primary-200 mt-2">
                Hệ thống phát hiện trạm thu phát giả mạo
            </p>
        </div>

        <!-- Login Form -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
            <h2
                class="text-2xl font-bold text-gray-900 dark:text-white text-center mb-6"
            >
                Đăng Nhập
            </h2>

            {#if error}
                <div
                    class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 animate-fade-in"
                >
                    <p class="text-red-800 dark:text-red-200 text-sm">
                        {error}
                    </p>
                </div>
            {/if}

            <form onsubmit={handleSubmit} class="space-y-6">
                <div>
                    <label for="email" class="label">Email</label>
                    <input
                        type="email"
                        id="email"
                        bind:value={email}
                        class="input"
                        placeholder="admin@vncssd.local"
                        required
                        disabled={loading}
                    />
                </div>

                <div>
                    <label for="password" class="label">Mật khẩu</label>
                    <input
                        type="password"
                        id="password"
                        bind:value={password}
                        class="input"
                        placeholder="••••••••"
                        required
                        disabled={loading}
                    />
                </div>

                <button
                    type="submit"
                    class="w-full btn-primary py-3 text-base"
                    disabled={loading}
                >
                    {#if loading}
                        <svg
                            class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                        Đang đăng nhập...
                    {:else}
                        Đăng Nhập
                    {/if}
                </button>
            </form>

            <div class="mt-6 text-center">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                    Tài khoản mặc định: <code class="text-primary-600"
                        >admin@vncssd.local</code
                    >
                </p>
            </div>
        </div>

        <!-- Footer -->
        <p class="text-center text-primary-200 text-sm mt-8">
            © 2024 VNCSSDetector. HUTECH University.
        </p>
    </div>
</div>
