<script lang="ts">
    import { get_config, set_config, type Config } from '../utils.svelte';

    let config = $state<Config | null>(null);

    let loading = $state(false);
    let saving = $state(false);
    let message = $state('');
    let messageType = $state<'success' | 'error' | null>(null);
    let showConfig = $state(false);

    async function loadConfig() {
        try {
            loading = true;
            config = await get_config();
            message = '';
            messageType = null;
        } catch (error) {
            message = `Không thể tải cấu hình: ${error}`;
            messageType = 'error';
        } finally {
            loading = false;
        }
    }

    async function saveConfig() {
        if (!config) return;

        try {
            saving = true;
            await set_config(config);
            message =
                'Cấu hình đã được lưu thành công! VNCSSdetector đang khởi động lại. Tải lại trang sau vài giây.';
            messageType = 'success';
        } catch (error) {
            message = `Không thể lưu cấu hình: ${error}`;
            messageType = 'error';
        } finally {
            saving = false;
        }
    }

    // Load config when first shown
    $effect(() => {
        if (showConfig && !config) {
            loadConfig();
        }
    });
</script>

<div class="bg-white rounded-lg shadow-md p-6 m-4">
    <button
        class="w-full flex justify-between items-center text-xl font-bold mb-4 text-vncssdetector-dark-blue hover:text-vncssdetector-blue"
        onclick={() => (showConfig = !showConfig)}
    >
        <span>Cấu Hình</span>
        <svg
            class="w-6 h-6 transition-transform {showConfig ? 'rotate-180' : ''}"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
        >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"
            ></path>
        </svg>
    </button>

    {#if showConfig}
        {#if loading}
            <div class="text-center py-4">Đang tải cấu hình...</div>
        {:else if config}
            <form
                class="space-y-4"
                onsubmit={(e) => {
                    e.preventDefault();
                    saveConfig();
                }}
            >
                <div>
                    <label for="ui_level" class="block text-sm font-medium text-gray-700 mb-1">
                        Mức Giao Diện Thiết Bị
                    </label>
                    <select
                        id="ui_level"
                        bind:value={config.ui_level}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vncssdetector-blue"
                    >
                        <option value={0}>0 - Chế độ ẩn</option>
                        <option value={1}>1 - Chế độ tinh tế (dòng màu)</option>
                        <option value={2}>2 - Chế độ demo (gif cá voi)</option>
                        <option value={3}>3 - Logo PT.Hyperdrive</option>
                    </select>
                </div>

                <div>
                    <label
                        for="key_input_mode"
                        class="block text-sm font-medium text-gray-700 mb-1"
                    >
                        Chế Độ Nhập Liệu Thiết Bị
                    </label>
                    <select
                        id="key_input_mode"
                        bind:value={config.key_input_mode}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vncssdetector-blue"
                    >
                        <option value={0}>0 - Tắt điều khiển bằng nút</option>
                        <option value={1}
                            >1 - Nhấn đúp nút nguồn để bắt đầu/dừng ghi</option
                        >
                    </select>
                </div>

                <div class="space-y-3">
                    <div class="flex items-center">
                        <input
                            id="colorblind_mode"
                            type="checkbox"
                            bind:checked={config.colorblind_mode}
                            class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                        />
                        <label for="colorblind_mode" class="ml-2 block text-sm text-gray-700">
                            Chế Độ Mù Màu
                        </label>
                    </div>
                </div>

                <div class="border-t pt-4 mt-6 space-y-3">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Cài Đặt Thông Báo</h3>
                    <div>
                        <label for="ntfy_url" class="block text-sm font-medium text-gray-700 mb-1">
                            URL ntfy để gửi thông báo (nếu không đặt, bạn sẽ không nhận được
                            thông báo)
                        </label>
                        <input
                            id="ntfy_url"
                            type="url"
                            bind:value={config.ntfy_url}
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vncssdetector-blue"
                        />
                    </div>

                    <div class="space-y-2">
                        <div class="block text-sm font-medium text-gray-700 mb-1">
                            Loại Thông Báo Được Bật
                        </div>
                        <div class="flex items-center">
                            <input
                                type="checkbox"
                                id="enable_warning_notifications"
                                value="Warning"
                                bind:group={config.enabled_notifications}
                            />
                            <label
                                for="enable_warning_notifications"
                                class="ml-2 block text-sm text-gray-700"
                            >
                                Cảnh Báo
                            </label>
                        </div>
                        <div class="flex items-center">
                            <input
                                type="checkbox"
                                id="enable_lowbattery_notifications"
                                value="LowBattery"
                                bind:group={config.enabled_notifications}
                            />
                            <label
                                for="enable_lowbattery_notifications"
                                class="ml-2 block text-sm text-gray-700"
                            >
                                Pin Yếu
                            </label>
                        </div>
                    </div>
                </div>

                <div class="border-t pt-4 mt-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">
                        Cài Đặt Analyzer Heuristic
                    </h3>
                    <div class="space-y-3">
                        <div class="flex items-center">
                            <input
                                id="imsi_requested"
                                type="checkbox"
                                bind:checked={config.analyzers.imsi_requested}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label for="imsi_requested" class="ml-2 block text-sm text-gray-700">
                                IMSI Requested Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="connection_redirect_2g_downgrade"
                                type="checkbox"
                                bind:checked={config.analyzers.connection_redirect_2g_downgrade}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label
                                for="connection_redirect_2g_downgrade"
                                class="ml-2 block text-sm text-gray-700"
                            >
                                Connection Redirect 2G Downgrade Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="lte_sib6_and_7_downgrade"
                                type="checkbox"
                                bind:checked={config.analyzers.lte_sib6_and_7_downgrade}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label
                                for="lte_sib6_and_7_downgrade"
                                class="ml-2 block text-sm text-gray-700"
                            >
                                LTE SIB6 and SIB7 Downgrade Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="null_cipher"
                                type="checkbox"
                                bind:checked={config.analyzers.null_cipher}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label for="null_cipher" class="ml-2 block text-sm text-gray-700">
                                Null Cipher Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="nas_null_cipher"
                                type="checkbox"
                                bind:checked={config.analyzers.nas_null_cipher}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label for="nas_null_cipher" class="ml-2 block text-sm text-gray-700">
                                NAS Null Cipher Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="incomplete_sib"
                                type="checkbox"
                                bind:checked={config.analyzers.incomplete_sib}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label for="incomplete_sib" class="ml-2 block text-sm text-gray-700">
                                Incomplete SIB Heuristic
                            </label>
                        </div>

                        <div class="flex items-center">
                            <input
                                id="test_analyzer"
                                type="checkbox"
                                bind:checked={config.analyzers.test_analyzer}
                                class="h-4 w-4 text-vncssdetector-blue focus:ring-vncssdetector-blue border-gray-300 rounded"
                            />
                            <label for="test_analyzer" class="ml-2 block text-sm text-gray-700">
                                Test Heuristic (ồn ào!)
                            </label>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 pt-4">
                    <button
                        type="submit"
                        disabled={saving}
                        class="bg-blue-500 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded-md flex flex-row gap-1 items-center"
                    >
                        {#if saving}
                            <div
                                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                            ></div>
                            Saving...
                        {:else}
                            <svg
                                class="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M5 13l4 4L19 7"
                                ></path>
                            </svg>
                            Áp dụng và khởi động lại
                        {/if}
                    </button>
                </div>
            </form>
            {#if message}
                <div
                    class="mt-4 p-3 rounded {messageType === 'error'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-green-100 text-green-700'}"
                >
                    {message}
                </div>
            {/if}
        {:else}
            <div class="text-center py-4 text-red-600">
                Không thể tải cấu hình. Vui lòng tải lại trang.
            </div>
        {/if}
    {/if}
</div>
