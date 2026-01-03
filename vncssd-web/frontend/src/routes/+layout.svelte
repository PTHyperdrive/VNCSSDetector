<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let { children } = $props();

	const publicRoutes = ['/login', '/register'];

	onMount(() => {
		auth.initialize();
	});

	$effect(() => {
		if ($auth.initialized && !$auth.loading) {
			const isPublicRoute = publicRoutes.includes($page.url.pathname);
			
			if (!$auth.user && !isPublicRoute) {
				goto('/login');
			} else if ($auth.user && isPublicRoute) {
				goto('/');
			}
		}
	});
</script>

{#if $auth.loading && !$auth.initialized}
	<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
		<div class="text-center">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
			<p class="mt-4 text-gray-600 dark:text-gray-400">Đang tải...</p>
		</div>
	</div>
{:else}
	{@render children()}
{/if}
