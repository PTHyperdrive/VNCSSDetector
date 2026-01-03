<script lang="ts">
    interface Props {
        title: string;
        value: number;
        total?: number;
        icon: "server" | "record" | "alert" | "warning";
        color: "green" | "blue" | "yellow" | "red" | "purple";
    }

    let { title, value, total, icon, color }: Props = $props();

    const colorClasses = {
        green: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
        blue: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
        yellow: "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400",
        red: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
        purple: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
    };
</script>

<div class="card p-6">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
                {title}
            </p>
            <div class="mt-2 flex items-baseline gap-2">
                <p class="text-3xl font-bold text-gray-900 dark:text-white">
                    {value}
                </p>
                {#if total !== undefined}
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                        / {total}
                    </p>
                {/if}
            </div>
        </div>
        <div
            class="w-12 h-12 rounded-xl flex items-center justify-center {colorClasses[
                color
            ]}"
        >
            {#if icon === "server"}
                <svg
                    class="w-6 h-6"
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
            {:else if icon === "record"}
                <svg
                    class="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <circle
                        cx="12"
                        cy="12"
                        r="4"
                        stroke-width="2"
                        fill="currentColor"
                    />
                    <circle cx="12" cy="12" r="8" stroke-width="2" />
                </svg>
            {:else if icon === "alert"}
                <svg
                    class="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                </svg>
            {:else if icon === "warning"}
                <svg
                    class="w-6 h-6"
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
            {/if}
        </div>
    </div>

    {#if total !== undefined && total > 0}
        <div class="mt-4">
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                    class="h-2 rounded-full transition-all duration-500 {color ===
                    'green'
                        ? 'bg-green-500'
                        : color === 'blue'
                          ? 'bg-blue-500'
                          : color === 'yellow'
                            ? 'bg-yellow-500'
                            : color === 'red'
                              ? 'bg-red-500'
                              : 'bg-purple-500'}"
                    style="width: {(value / total) * 100}%"
                ></div>
            </div>
        </div>
    {/if}
</div>
