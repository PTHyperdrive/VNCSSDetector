<script lang="ts">
    import { onMount } from "svelte";
    import { api, type Node } from "$lib/api";
    import Sidebar from "$lib/components/Sidebar.svelte";

    let nodes = $state<Node[]>([]);
    let loading = $state(true);
    let error = $state("");
    let mapContainer: HTMLDivElement;
    let map: any;

    onMount(async () => {
        await loadNodes();
        await initMap();
    });

    async function loadNodes() {
        loading = true;
        try {
            nodes = await api.getNodes();
        } catch (e) {
            error = e instanceof Error ? e.message : "Lỗi tải nodes";
        } finally {
            loading = false;
        }
    }

    async function initMap() {
        // Load Leaflet dynamically
        const L = await import("leaflet");

        // @ts-ignore
        await import("leaflet/dist/leaflet.css");

        // Center on HCM City - Nguyễn Tri Phương area
        map = L.map(mapContainer).setView([10.765, 106.665], 15);

        // Add OpenStreetMap tiles
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution:
                '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        // Add node markers
        nodes.forEach((node) => {
            if (node.location_lat && node.location_lng) {
                const color = getMarkerColor(node.status);

                const icon = L.divIcon({
                    className: "custom-marker",
                    html: `<div style="
                        width: 24px;
                        height: 24px;
                        background: ${color};
                        border: 3px solid white;
                        border-radius: 50%;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                    "></div>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12],
                });

                const marker = L.marker(
                    [node.location_lat, node.location_lng],
                    { icon },
                ).addTo(map);

                marker.bindPopup(`
                    <div style="min-width: 200px">
                        <strong>${node.name}</strong><br/>
                        <span style="color: ${color}">● ${getStatusText(node.status)}</span><br/>
                        <small>${node.device_type}</small><br/>
                        <small>${node.location_name || "Không có địa chỉ"}</small>
                    </div>
                `);
            }
        });
    }

    function getMarkerColor(status: string) {
        switch (status) {
            case "online":
                return "#22c55e";
            case "offline":
                return "#6b7280";
            case "warning":
                return "#eab308";
            case "error":
                return "#ef4444";
            default:
                return "#6b7280";
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

    function getStatusCounts() {
        const counts = { online: 0, offline: 0, warning: 0, error: 0 };
        nodes.forEach((n) => {
            if (counts[n.status as keyof typeof counts] !== undefined) {
                counts[n.status as keyof typeof counts]++;
            }
        });
        return counts;
    }
</script>

<svelte:head>
    <title>Topology - VNCSSDetector</title>
    <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />
</svelte:head>

<div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <Sidebar />

    <main class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <div
            class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
        >
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-xl font-bold text-gray-900 dark:text-white">
                        Network Topology
                    </h1>
                    <p class="text-sm text-gray-500">
                        Bản đồ phân bố các nodes - TP.HCM
                    </p>
                </div>
                <div class="flex items-center gap-4">
                    {#if !loading}
                        {#each Object.entries(getStatusCounts()) as [status, count]}
                            <div class="flex items-center gap-1.5">
                                <span
                                    class="w-3 h-3 rounded-full"
                                    style="background: {getMarkerColor(status)}"
                                ></span>
                                <span
                                    class="text-sm text-gray-600 dark:text-gray-300"
                                >
                                    {count}
                                    {getStatusText(status)}
                                </span>
                            </div>
                        {/each}
                    {/if}
                    <button
                        onclick={() => {
                            loadNodes();
                            if (map) map.remove();
                            initMap();
                        }}
                        class="btn-secondary text-sm"
                    >
                        <svg
                            class="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                            />
                        </svg>
                        Làm mới
                    </button>
                </div>
            </div>
        </div>

        {#if error}
            <div class="bg-red-50 text-red-700 p-4 m-4 rounded-lg">{error}</div>
        {/if}

        {#if loading}
            <div class="flex-1 flex items-center justify-center">
                <div
                    class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"
                ></div>
            </div>
        {:else}
            <!-- Map Container -->
            <div class="flex-1 relative">
                <div bind:this={mapContainer} class="absolute inset-0"></div>
            </div>
        {/if}
    </main>
</div>

<style>
    :global(.leaflet-container) {
        height: 100%;
        width: 100%;
        z-index: 0;
    }

    :global(.custom-marker) {
        background: transparent !important;
        border: none !important;
    }
</style>
