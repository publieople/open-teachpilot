<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { WEBUI_BASE_URL } from '$lib/constants';
	
	// 图标组件
	import Plus from '$lib/components/icons/Plus.svelte';
	import Document from '$lib/components/icons/Document.svelte';
	import ChartBar from '$lib/components/icons/ChartBar.svelte';
	import Assignment from '$lib/components/icons/Assignment.svelte';
	
	// 数据类型
	interface CourseOutline {
		id: number;
		title: string;
		subject: string;
		status: string;
		version: number;
		created_at: string;
		updated_at: string;
	}
	
	interface CourseStats {
		total_courses: number;
		total_students: number;
	 pending_grading: number;
		avg_progress: number;
	}
	
	// 状态
	let loading = true;
	let courses: CourseOutline[] = [];
	let stats: CourseStats = {
		total_courses: 0,
		total_students: 0,
		pending_grading: 0,
		avg_progress: 0
	};
	
	// 生成大纲表单
	let showGenerateModal = false;
	let generating = false;
	let promptInput = '';
	let subjectInput = 'computer_science';
	let targetAudienceInput = 'Python 零基础初学者';
	let durationInput = 45;
	
	// API 调用
	async function fetchCourses() {
		try {
			const response = await fetch(`${WEBUI_BASE_URL}/api/v1/teachpilot/outlines`, {
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
		// 模拟统计数据
		stats = {
			total_courses: courses.length,
			total_students: 24,
			pending_grading: 5,
			avg_progress: 68
		};
	}
	
	// 生成课程大纲
	async function generateOutline() {
		if (!promptInput.trim()) {
			toast.error('请输入教学需求描述');
			return;
		}
		
		generating = true;
		
		try {
			const response = await fetch(`${WEBUI_BASE_URL}/api/v1/teachpilot/outlines/generate`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				},
				body: JSON.stringify({
					prompt: promptInput,
					subject: subjectInput,
					target_audience: targetAudienceInput,
					required_duration: durationInput
				})
			});
			
			if (response.ok) {
				const result = await response.json();
				toast.success(`课程大纲生成成功！ID: ${result.outline_id}`);
				showGenerateModal = false;
				promptInput = '';
				await fetchCourses();
			} else {
				const error = await response.json();
				toast.error(`生成失败：${error.detail}`);
			}
		} catch (error) {
			toast.error('生成失败，请重试');
			console.error(error);
		} finally {
			generating = false;
		}
	}
	
	onMount(async () => {
		await fetchCourses();
		await fetchStats();
		loading = false;
	});
</script>

<div class="p-6 max-w-7xl mx-auto">
	<!-- 页面头部 -->
	<div class="flex justify-between items-center mb-8">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">教师工作台</h1>
			<p class="text-gray-500 dark:text-gray-400 mt-1">管理课程、跟踪学生学习进度</p>
		</div>
		<button
			on:click={() => showGenerateModal = true}
			class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
		>
			<Plus className="size-5" />
			生成课程大纲
		</button>
	</div>
	
	<!-- 统计卡片 -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
					<Document className="size-6 text-blue-600 dark:text-blue-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">我的课程</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_courses}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
					<ChartBar className="size-6 text-green-600 dark:text-green-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">学生总数</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_students}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
					<Assignment className="size-6 text-yellow-600 dark:text-yellow-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">待批改作业</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.pending_grading}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
					<ChartBar className="size-6 text-purple-600 dark:text-purple-400" />
				</div>
				<div>
					<p class="text-sm text-gray-500 dark:text-gray-400">平均进度</p>
					<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.avg_progress}%</p>
				</div>
			</div>
		</div>
	</div>
	
	<!-- 课程列表 -->
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
				<p class="text-gray-500 dark:text-gray-400 mb-4">暂无课程</p>
				<button
					on:click={() => showGenerateModal = true}
					class="text-blue-600 hover:text-blue-700"
				>
					创建第一个课程
				</button>
			</div>
		{:else}
			<div class="divide-y divide-gray-200 dark:divide-gray-700">
				{#each courses as course}
					<div class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
						<div class="flex justify-between items-start">
							<div>
								<h3 class="font-medium text-gray-900 dark:text-white">{course.title}</h3>
								<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
									{course.subject} • 版本 {course.version}
								</p>
								<p class="text-xs text-gray-400 dark:text-gray-500 mt-2">
									创建于 {new Date(course.created_at).toLocaleDateString('zh-CN')}
								</p>
							</div>
							<div class="flex items-center gap-2">
								<span class="px-2 py-1 text-xs rounded-full {
									course.status === 'published' 
										? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
										: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
								}">
									{course.status === 'published' ? '已发布' : '草稿'}
								</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<!-- 生成课程大纲模态框 -->
{#if showGenerateModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="bg-white dark:bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6 border-b border-gray-200 dark:border-gray-700">
				<h2 class="text-xl font-semibold text-gray-900 dark:text-white">生成课程大纲</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
					描述您的教学需求，AI 将自动生成结构化的课程大纲
				</p>
			</div>
			
			<div class="p-6 space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						教学需求描述 *
					</label>
					<textarea
						bind:value={promptInput}
						rows="4"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						placeholder="例如：我想为零基础学员设计一个 Python 入门课程，涵盖变量、数据类型、控制结构等基础知识，希望以实践案例为主..."
					></textarea>
				</div>
				
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							学科领域
						</label>
						<select
							bind:value={subjectInput}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
						>
							<option value="computer_science">计算机科学</option>
							<option value="python_programming">Python 编程</option>
							<option value="data_structures">数据结构</option>
							<option value="algorithms">算法</option>
						</select>
					</div>
					
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							预计课时（分钟）
						</label>
						<input
							type="number"
							bind:value={durationInput}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
						/>
					</div>
				</div>
				
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						目标学员
					</label>
					<input
						type="text"
						bind:value={targetAudienceInput}
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
						placeholder="例如：Python 零基础初学者"
					/>
				</div>
			</div>
			
			<div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
				<button
					on:click={() => showGenerateModal = false}
					class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
				>
					取消
				</button>
				<button
					on:click={generateOutline}
					disabled={generating}
					class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center gap-2"
				>
					{#if generating}
						<Spinner size="16" />
						生成中...
					{:else}
						生成大纲
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
