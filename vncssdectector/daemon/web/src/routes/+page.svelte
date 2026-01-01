<script lang="ts">
    import { ManifestEntry } from '$lib/manifest.svelte';
    import { get_manifest, get_system_stats } from '$lib/utils.svelte';
    import ManifestTable from '$lib/components/ManifestTable.svelte';
    import Card from '$lib/components/ManifestCard.svelte';
    import type { SystemStats } from '$lib/systemStats';
    import { AnalysisManager } from '$lib/analysisManager.svelte';
    import SystemStatsTable from '$lib/components/SystemStatsTable.svelte';
    import DeleteAllButton from '$lib/components/DeleteAllButton.svelte';
    import RecordingControls from '$lib/components/RecordingControls.svelte';
    import ConfigForm from '$lib/components/ConfigForm.svelte';
    import ActionErrors from '$lib/components/ActionErrors.svelte';
    import LogView from '$lib/components/LogView.svelte';
    import NodeModePanel from '$lib/components/NodeModePanel.svelte';
    import ModeStatusBadge from '$lib/components/ModeStatusBadge.svelte';
    import SwarmModeView from '$lib/components/SwarmModeView.svelte';

    interface ModeStatus {
        running_mode: 'standalone' | 'node' | 'swarm';
        connection_status: 'disconnected' | 'connecting' | 'connected' | 'error';
        server_ip: string | null;
        is_heuristic_passed: boolean;
        last_error: string | null;
    }

    let manager: AnalysisManager = new AnalysisManager();
    let loaded = $state(false);
    let filter_threshold: boolean = $state(false);
    let entries: ManifestEntry[] = $state([]);
    let current_entry: ManifestEntry | undefined = $state(undefined);
    let system_stats: SystemStats | undefined = $state(undefined);
    let update_error: string | undefined = $state(undefined);
    let logview_shown: boolean = $state(false);
    let node_panel_shown: boolean = $state(false);
    let mode_status: ModeStatus | null = $state(null);

    $effect(() => {
        const interval = setInterval(async () => {
            try {
                // Don't update UI if browser tab isn't visible
                if (document.hidden) {
                    return;
                }

                await manager.update();
                let new_manifest = await get_manifest();
                await new_manifest.set_analysis_status(manager);
                entries = filter_threshold
                    ? new_manifest.entries.filter((e) => e.get_num_warnings())
                    : new_manifest.entries;

                current_entry = new_manifest.current_entry;

                system_stats = await get_system_stats();

                // Fetch mode status
                try {
                    const res = await fetch('/api/mode');
                    if (res.ok) {
                        mode_status = await res.json();
                    }
                } catch (e) {
                    // Ignore mode fetch errors
                }

                update_error = undefined;
                loaded = true;
            } catch (error) {
                if (error instanceof Error) {
                    update_error = error.message;
                } else {
                    update_error = '';
                }
            }
        }, 1000);

        return () => clearInterval(interval);
    });
</script>

<!-- Show Swarm mode locked view if in Swarm mode -->
{#if mode_status?.running_mode === 'swarm'}
    <SwarmModeView />
{:else}
    <LogView bind:shown={logview_shown} />
    <NodeModePanel bind:shown={node_panel_shown} />
    <div
        class="p-4 xl:px-8 bg-gray-100 border-gray-100 drop-shadow flex flex-row justify-between items-center"
    >
        <!-- https://www.w3.org/WAI/tutorials/images/decorative/ -->
        <img src="/vncssdetector_text.png" alt="" class="h-10 xl:h-12" />
        <div class="flex flex-row gap-4 items-center">
            <!-- Mode Status Badge -->
            <ModeStatusBadge status={mode_status} />

            <!-- Node Config Button (only show in Node mode or when not in standalone) -->
            {#if mode_status?.running_mode === 'node' || mode_status?.running_mode === 'swarm'}
                <button
                    onclick={() => (node_panel_shown = true)}
                    class="flex flex-row gap-1 group"
                    title="Cấu hình Node"
                >
                    <svg
                        class="w-6 h-6 text-gray-800 group-hover:text-gray-500"
                        aria-hidden="true"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                        <path
                            fill-rule="evenodd"
                            d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z"
                            clip-rule="evenodd"
                        />
                    </svg>
                </button>
            {/if}

            <button onclick={() => (logview_shown = true)} class="flex flex-row gap-1 group">
                <span class="hidden text-gray-800 group-hover:text-gray-500 lg:flex">Nhật ký</span>
                <svg
                    class="w-6 h-6 text-gray-800 group-hover:text-gray-500"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        d="M10 14H3"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                    />
                    <path
                        d="M10 18H3"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                    />
                    <path
                        d="M14 15L17.5 18L21 15"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M3 6L13.5 6M20 6L17.75 6"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                    />
                    <path
                        d="M20 10L9.5 10M3 10H5.25"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                    />
                </svg>
            </button>
        </div>
    </div>
    <div class="m-4 xl:mx-8 flex flex-col gap-4">
        {#if update_error !== undefined}
            <div
                class="bg-red-100 border-red-100 drop-shadow p-4 flex flex-col gap-2 border rounded-md flex-1 justify-between"
            >
                <span class="text-2xl font-bold mb-2 flex flex-row items-center gap-2 text-red-600">
                    <svg
                        class="w-8 h-8 text-red-600"
                        aria-hidden="true"
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm11-4a1 1 0 1 0-2 0v5a1 1 0 1 0 2 0V8Zm-1 7a1 1 0 1 0 0 2h.01a1 1 0 1 0 0-2H12Z"
                            clip-rule="evenodd"
                        />
                    </svg>
                    Lỗi Kết Nối
                </span>
                <span
                    >Trang web này hiện không nhận được cập nhật từ thiết bị VNCSSdetector của bạn.
                    Điều này có thể do mất kết nối hoặc sự cố với thiết bị của bạn.</span
                >
                {#if update_error}
                    <details>
                        <summary>Lỗi</summary>
                        <code>{update_error}</code>
                    </details>
                {/if}
            </div>
        {/if}
        <ActionErrors />
        {#if loaded}
            <div class="flex flex-col lg:flex-row gap-4">
                {#if current_entry}
                    <Card
                        entry={current_entry}
                        current={true}
                        server_is_recording={!!current_entry}
                        {manager}
                    />
                {:else}
                    <div
                        class="bg-red-100 border-red-100 drop-shadow p-4 flex flex-col gap-2 border rounded-md flex-1 justify-between"
                    >
                        <span
                            class="text-2xl font-bold mb-2 flex flex-row items-center gap-2 text-red-600"
                        >
                            <svg
                                class="w-8 h-8 text-red-600"
                                aria-hidden="true"
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm11-4a1 1 0 1 0-2 0v5a1 1 0 1 0 2 0V8Zm-1 7a1 1 0 1 0 0 2h.01a1 1 0 1 0 0-2H12Z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                            CẢNH BÁO: Chưa Chạy
                        </span>
                        <span>
                            VNCSSdetector hiện không chạy và sẽ không phát hiện hành vi bất thường!
                        </span>
                        <div class="flex flex-row justify-end mt-2">
                            <RecordingControls server_is_recording={!!current_entry} />
                        </div>
                    </div>
                {/if}
                <SystemStatsTable stats={system_stats!} {mode_status} />
            </div>
            <div class="flex flex-col gap-2">
                <div class="flex flex-row gap-2">
                    <div class="text-xl flex-1">Lịch Sử</div>
                    <div class="flex flex-row items-center gap-2 px-3">
                        <label
                            for="filter_threshold"
                            class="block text-md font-medium text-gray-700 mb-1"
                        >
                            Lọc Cảnh Báo
                        </label>
                        <input
                            type="checkbox"
                            id="filter_threshold"
                            bind:checked={filter_threshold}
                            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vncssdetector-blue"
                        />
                    </div>
                </div>
                <ManifestTable {entries} server_is_recording={!!current_entry} {manager} />
            </div>
            <DeleteAllButton />
            <ConfigForm />
        {:else}
            <div class="flex flex-col justify-center items-center">
                <!-- https://www.w3.org/WAI/tutorials/images/decorative/ -->
                <img src="/vncssdetector_orca_only.png" alt="" class="h-48 animate-spin" />
                <p class="text-xl">Đang Tải...</p>
            </div>
        {/if}
    </div>
{/if}
