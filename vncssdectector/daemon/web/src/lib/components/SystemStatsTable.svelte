<script lang="ts">
    import { type SystemStats } from '$lib/systemStats';

    interface ModeStatus {
        running_mode: 'standalone' | 'node' | 'swarm';
        connection_status: 'disconnected' | 'connecting' | 'connected' | 'error';
        server_ip: string | null;
        is_heuristic_passed: boolean;
        last_error: string | null;
    }

    let {
        stats,
        mode_status = null,
    }: {
        stats: SystemStats;
        mode_status?: ModeStatus | null;
    } = $props();

    const table_cell_classes = 'border p-1 lg:p-2';

    let battery_level = $derived(stats.battery_status ? stats.battery_status.level : 0);
    let bar_color = $derived.by(() => {
        if (stats.battery_status === undefined) {
            return '';
        }
        if (battery_level <= 10) {
            return 'fill-red-500';
        }
        if (battery_level <= 25) {
            return 'fill-yellow-300';
        }
        return 'fill-green-500';
    });
    let title_text = $derived.by(() => {
        if (stats.battery_status === undefined) {
            return 'VNCSSdetector chưa hỗ trợ hiển thị mức pin cho thiết bị này.';
        }

        let text = `Pin còn ${stats.battery_status.level}%`;

        if (stats.battery_status.is_plugged_in) {
            text += ' và đang sạc';
        }
        return text;
    });

    let mode_status_text = $derived.by(() => {
        if (!mode_status) return 'Standalone';

        if (mode_status.running_mode === 'standalone') {
            return 'Standalone';
        }

        if (mode_status.connection_status === 'connected') {
            return `Đã kết nối ${mode_status.server_ip || ''}`;
        }

        if (mode_status.connection_status === 'connecting') {
            return 'Đang kết nối...';
        }

        if (mode_status.connection_status === 'error') {
            return 'Lỗi kết nối';
        }

        return 'Chưa kết nối';
    });

    let mode_status_color = $derived.by(() => {
        if (!mode_status || mode_status.running_mode === 'standalone') {
            return 'text-blue-600';
        }

        if (mode_status.connection_status === 'connected') {
            return 'text-green-600';
        }

        if (mode_status.connection_status === 'connecting') {
            return 'text-yellow-600';
        }

        if (mode_status.connection_status === 'error') {
            return 'text-red-600';
        }

        return 'text-gray-600';
    });
</script>

<div
    class="flex-1 drop-shadow p-4 flex flex-col gap-2 border rounded-md bg-gray-100 border-gray-100"
>
    <p class="text-xl mb-2">Thông tin thiết bị</p>
    <table class="table-auto border">
        <tbody>
            <tr class="border">
                <th class={table_cell_classes}> Phiên bản VNCSSdetector </th>
                <td class={table_cell_classes}>{stats.runtime_metadata.vncssdetector_version}</td>
            </tr>
            <!-- Mode Status Row -->
            <tr class="border">
                <th class={table_cell_classes}> Chế độ </th>
                <td class={`${table_cell_classes} ${mode_status_color} font-medium`}>
                    {mode_status_text}
                </td>
            </tr>
            <tr class="border">
                <th class={table_cell_classes}> Bộ nhớ </th>
                <td class={table_cell_classes}>
                    {stats.disk_stats.used_percent} đã dùng ({stats.disk_stats.used_size} đã dùng / {stats
                        .disk_stats.available_size} khả dụng)
                </td>
            </tr>
            <tr class="border-b">
                <th class={table_cell_classes}> Bộ nhớ (RAM) </th>
                <td class={table_cell_classes}>
                    Trống: {stats.memory_stats.free}, Đã dùng: {stats.memory_stats.used}
                </td>
            </tr>
            <tr class="border-b">
                <th class={table_cell_classes}> Pin </th>
                <td class={table_cell_classes}>
                    <svg
                        width="80"
                        height="30"
                        viewBox="0 0 80 30"
                        role="img"
                        xmlns="http://www.w3.org/2000/svg"
                        class="battery-icon"
                    >
                        <title>{title_text}</title>
                        <!-- Battery body -->
                        <rect
                            class="fill-none stroke-neutral-800 stroke-2"
                            width="70"
                            height="30"
                            rx="3"
                            ry="3"
                        />
                        <!-- Battery terminal -->
                        <rect
                            class="fill-neutral-800"
                            x="70"
                            y="7"
                            width="8"
                            height="16"
                            rx="2"
                            ry="2"
                        />
                        <!-- Battery charge bar -->
                        <rect
                            class={bar_color}
                            x="2"
                            y="2"
                            height="26"
                            rx="2"
                            ry="2"
                            style="width: {battery_level * 0.66}px;"
                        />
                        {#if stats.battery_status && stats.battery_status.is_plugged_in}
                            <!-- Lightning bolt icon -->
                            <path
                                class="fill-yellow-300 stroke-neutral-800 stroke-1"
                                d="M38 3 L28 17 L34 17 L30 27 L40 13 L34 13 Z"
                            />
                        {/if}
                        {#if !stats.battery_status}
                            <!-- Question mark icon -->
                            <text
                                class="fill-neutral-500 text-[20px] font-bold [text-anchor:middle] [dominant-baseline:central]"
                                x="35"
                                y="15">?</text
                            >
                        {/if}
                    </svg>
                </td>
            </tr>
        </tbody>
    </table>
</div>
