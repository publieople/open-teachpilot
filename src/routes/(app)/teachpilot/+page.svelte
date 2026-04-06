<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { user } from '$lib/stores';
	
	// TeachPilot 主页面 - 根据用户角色显示不同内容
	import TeacherDashboard from '$lib/components/teachpilot/TeacherDashboard.svelte';
	import StudentDashboard from '$lib/components/teachpilot/StudentDashboard.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	
	let loading = true;
	let userRole = 'student'; // 默认学生角色
	
	onMount(async () => {
		// 获取用户角色
		if ($user) {
			userRole = $user?.role || 'student';
		}
		loading = false;
	});
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	{#if loading}
		<div class="flex items-center justify-center h-screen">
			<Spinner size="40" />
		</div>
	{:else}
		{#if userRole === 'teacher' || userRole === 'admin'}
			<TeacherDashboard />
		{:else}
			<StudentDashboard />
		{/if}
	{/if}
</div>
