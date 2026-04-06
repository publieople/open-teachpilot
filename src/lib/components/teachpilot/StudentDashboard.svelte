<script lang="ts">
	import { onMount } from 'svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	
	// 图标组件
	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import Clock from '$lib/components/icons/Clock.svelte';
	import Trophy from '$lib/components/icons/Trophy.svelte';
	import ChartBar from '$lib/components/icons/ChartBar.svelte';
	
	// 数据类型
	interface Course {
		id: number;
		title: string;
		subject: string;
		progress_percentage: number;
		completed_lessons: number;
		total_lessons: number;
		enrolled_at: string;
	}
	
	interface LearningStats {
		total_courses: number;
		completed_courses: number;
		total_time_hours: number;
		average_score: number;
		total_lessons_progress: number;
	}
	
	// 状态
	let loading = true;
	let courses: Course[] = [];
	let stats: LearningStats = {
		total_courses: 0,
		completed_courses: 0,
		total_time_hours: 0,
		average_score: 0,
		total_lessons_progress: 0
	};
	
	// API 调用
	async function fetchCourses() {
		try {
			const response = await fetch(`${WEBUI_BASE_URL}/api/v1/teachpilot/progress/courses`, {
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				}
			});
			if (response.ok) {
				courses = await response.json();
			}
		} catch (error) {
			console.error('获取课程列表失败:', error);
		}
	}
	
	async function fetchStats() {
		try {
			const response = await fetch(`${WEBUI_BASE_URL}/api/v1/teachpilot/progress/stats`, {
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				}
			});
			if (response.ok) {
				stats = await response.json();
			}
		} catch (error) {
			console.error('获取学习统计失败:', error);
		}
	}
	
	function getProgressColor(percentage: number): string {
		if (percentage >= 80) return 'bg-green-500';
		if (percentage >= 50) return 'bg-blue-500';
		if (percentage >= 20) return 'bg-yellow-500';
		return 'bg-gray-400';
	}
	
	onMount(async () => {
		await fetchCourses();
		await fetchStats();
		loading = false;
	});
</script>

<div class="p-6 max-w-7xl mx-auto">
	<!-- 页面头部 -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-gray-900 dark:text-white">学习中心</h1>
		<p class="text-gray-500 dark:text-gray-400 mt-1">跟踪学习进度，管理作业提交</p>
	</div>
	
	<!-- 学习统计 -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
					<BookOpen className="size-6 text-blue-600 dark:text-blue-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">学习中课程</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_courses}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
					<Trophy className="size-6 text-green-600 dark:text-green-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">已完成课程</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.completed_courses}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
					<Clock className="size-6 text-purple-600 dark:text-purple-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">学习时长</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_time_hours}h</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
					<ChartBar className="size-6 text-yellow-600 dark:text-yellow-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">平均成绩</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.average_score}</p>
				</div>
			</div>
		</div>
	</div>
	
	<!-- 我的课程 -->
	<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
		<div class="p-4 border-b border-gray-200 dark:border-gray-700">
			<h2 class="text-lg font-semibold text-gray-900 dark:text-white">我的课程</h2>
		</div>
		
		{#if loading}
			<div class="p-8 text-center">
				<p class="text-gray-500 dark:text-gray-400">加载中...</p>
			</div>
		{:else if courses.length === 0}
			<div class="p-8 text-center">
				<p class="text-gray-500 dark:text-gray-400">暂无课程</p>
				<p class="text-sm text-gray-400 dark:text-gray-500 mt-2">
					请联系教师获取课程邀请码
				</p>
			</div>
		{:else}
			<div class="divide-y divide-gray-200 dark:divide-gray-700">
				{#each courses as course}
					<div class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
						<div class="flex justify-between items-start mb-3">
							<div class="flex-1">
								<h3 class="font-medium text-gray-900 dark:text-white">{course.title}</h3>
								<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
									{course.subject} • 已加入 {new Date(course.enrolled_at).toLocaleDateString('zh-CN')}
								</p>
							</div>
							<div class="text-right">
								<p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
									{course.progress_percentage}%
								</p>
								<p class="text-xs text-gray-500 dark:text-gray-400">
									{course.completed_lessons}/{course.total_lessons} 课时
								</p>
							</div>
						</div>
						
						<!-- 进度条 -->
						<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
							<div
								class="h-2 rounded-full transition-all duration-300 {getProgressColor(course.progress_percentage)}"
								style="width: {course.progress_percentage}%"
							></div>
						</div>
						
						<div class="mt-3 flex gap-2">
							<button
								class="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
							>
								继续学习
							</button>
							<button
								class="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
							>
								查看作业
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
