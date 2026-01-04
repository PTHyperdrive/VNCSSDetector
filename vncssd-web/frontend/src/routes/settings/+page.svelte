<script lang="ts">
    import { onMount } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";

    // Settings state
    let theme = $state<"light" | "dark" | "system">("system");
    let notificationCooldown = $state(60); // seconds
    let soundEnabled = $state(true);
    let saving = $state(false);
    let saved = $state(false);

    onMount(() => {
        // Load settings from localStorage
        const savedTheme = localStorage.getItem("vncssd_theme");
        if (savedTheme) theme = savedTheme as "light" | "dark" | "system";

        const savedCooldown = localStorage.getItem(
            "vncssd_notification_cooldown",
        );
        if (savedCooldown) notificationCooldown = parseInt(savedCooldown);

        const savedSound = localStorage.getItem("vncssd_sound_enabled");
        if (savedSound) soundEnabled = savedSound === "true";

        applyTheme();
    });

    function applyTheme() {
        if (
            theme === "dark" ||
            (theme === "system" &&
                window.matchMedia("(prefers-color-scheme: dark)").matches)
        ) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    }

    function saveSettings() {
        saving = true;

        // Save to localStorage
        localStorage.setItem("vncssd_theme", theme);
        localStorage.setItem(
            "vncssd_notification_cooldown",
            notificationCooldown.toString(),
        );
        localStorage.setItem("vncssd_sound_enabled", soundEnabled.toString());

        applyTheme();

        setTimeout(() => {
            saving = false;
            saved = true;
            setTimeout(() => (saved = false), 3000);
        }, 500);
    }
</script>

<svelte:head>
    <title>Cài đặt - VNCSSDetector</title>
</svelte:head>

<div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <Sidebar />

    <main class="flex-1 overflow-auto">
        <div class="p-8 max-w-3xl">
            <!-- Header -->
            <div class="mb-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                    Cài đặt
                </h1>
                <p class="text-gray-500 dark:text-gray-400">
                    Tùy chỉnh giao diện và thông báo
                </p>
            </div>

            <!-- Theme Settings -->
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-6">
                <h2
                    class="text-lg font-semibold text-gray-900 dark:text-white mb-4"
                >
                    Giao diện
                </h2>

                <div class="space-y-4">
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                            Chế độ hiển thị
                        </label>
                        <div class="grid grid-cols-3 gap-3">
                            <button
                                onclick={() => (theme = "light")}
                                class="p-4 border-2 rounded-lg text-center transition-colors {theme ===
                                'light'
                                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'}"
                            >
                                <svg
                                    class="w-8 h-8 mx-auto mb-2 text-yellow-500"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                                    />
                                </svg>
                                <span
                                    class="text-sm font-medium text-gray-900 dark:text-white"
                                    >Sáng</span
                                >
                            </button>
                            <button
                                onclick={() => (theme = "dark")}
                                class="p-4 border-2 rounded-lg text-center transition-colors {theme ===
                                'dark'
                                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'}"
                            >
                                <svg
                                    class="w-8 h-8 mx-auto mb-2 text-gray-600 dark:text-gray-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                                    />
                                </svg>
                                <span
                                    class="text-sm font-medium text-gray-900 dark:text-white"
                                    >Tối</span
                                >
                            </button>
                            <button
                                onclick={() => (theme = "system")}
                                class="p-4 border-2 rounded-lg text-center transition-colors {theme ===
                                'system'
                                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'}"
                            >
                                <svg
                                    class="w-8 h-8 mx-auto mb-2 text-gray-600 dark:text-gray-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                    />
                                </svg>
                                <span
                                    class="text-sm font-medium text-gray-900 dark:text-white"
                                    >Hệ thống</span
                                >
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Notification Settings -->
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-6">
                <h2
                    class="text-lg font-semibold text-gray-900 dark:text-white mb-4"
                >
                    Thông báo
                </h2>

                <div class="space-y-6">
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                            Thời gian chờ giữa các thông báo (giây)
                        </label>
                        <div class="flex items-center gap-4">
                            <input
                                type="range"
                                bind:value={notificationCooldown}
                                min="10"
                                max="300"
                                step="10"
                                class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                            />
                            <span
                                class="w-16 text-center font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded"
                            >
                                {notificationCooldown}s
                            </span>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">
                            Ngăn spam thông báo bằng cách đặt thời gian chờ tối
                            thiểu
                        </p>
                    </div>

                    <div class="flex items-center justify-between">
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700 dark:text-gray-300"
                            >
                                Âm thanh thông báo
                            </label>
                            <p class="text-xs text-gray-500">
                                Phát âm thanh khi có cảnh báo mới
                            </p>
                        </div>
                        <button
                            onclick={() => (soundEnabled = !soundEnabled)}
                            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors {soundEnabled
                                ? 'bg-primary-600'
                                : 'bg-gray-300 dark:bg-gray-600'}"
                        >
                            <span
                                class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform {soundEnabled
                                    ? 'translate-x-6'
                                    : 'translate-x-1'}"
                            />
                        </button>
                    </div>
                </div>
            </div>

            <!-- Save Button -->
            <div class="flex items-center gap-4">
                <button
                    onclick={saveSettings}
                    disabled={saving}
                    class="btn-primary"
                >
                    {saving ? "Đang lưu..." : "Lưu cài đặt"}
                </button>
                {#if saved}
                    <span class="text-green-600 flex items-center gap-1">
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
                        Đã lưu!
                    </span>
                {/if}
            </div>
        </div>
    </main>
</div>
