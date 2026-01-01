<script lang="ts">
    import { type ReportMetadata } from '$lib/analysis.svelte';
    import type { ManifestEntry } from '$lib/manifest.svelte';
    import { AnalysisManager } from '$lib/analysisManager.svelte';
    import AnalysisTable from './AnalysisTable.svelte';
    import ReAnalyzeButton from './ReAnalyzeButton.svelte';
    let {
        entry,
        manager,
        current,
    }: {
        entry: ManifestEntry;
        manager: AnalysisManager;
        current: boolean;
    } = $props();
</script>

<div class="container mt-2">
    {#if entry.analysis_report === undefined}
        <p>Báo cáo không khả dụng, hãy thử làm mới.</p>
    {:else if typeof entry.analysis_report === 'string'}
        <p>Lỗi khi lấy báo cáo phân tích: {entry.analysis_report}</p>
    {:else}
        {@const metadata: ReportMetadata = entry.analysis_report.metadata}
        <div class="flex flex-col gap-2">
            {#if !current}
                <div class="flex flex-row justify-end items-center">
                    <ReAnalyzeButton {entry} {manager} />
                </div>
            {/if}
            {#if entry.analysis_report.rows.length > 0}
                <AnalysisTable report={entry.analysis_report} />
            {:else}
                <p>Không có cảnh báo để hiển thị!</p>
            {/if}
            {#if metadata !== undefined && metadata.vncssdetector !== undefined}
                <div>
                    <p class="text-lg underline">Metadata</p>
                    <p>Phân tích bởi VNCSSdetector phiên bản {metadata.vncssdetector.vncssdetector_version}</p>
                    <p><b>Hệ điều hành thiết bị:</b> {metadata.vncssdetector.system_os}</p>
                </div>
                <div>
                    <p class="text-lg underline">Analyzers</p>
                    {#each metadata.analyzers as analyzer}
                        <p><b>{analyzer.name}:</b> {analyzer.description}</p>
                    {/each}
                </div>
            {:else}
                <p>Không có (phân tích được tạo bởi phiên bản cũ của vncssdetector)</p>
            {/if}
        </div>
    {/if}
</div>
