"""
课程大纲生成模块
服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体

基于教学意图生成结构化的课程大纲
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

log = logging.getLogger(__name__)


async def generate_course_outline(
    intent: Dict[str, Any],
    subject: str = "computer_science",
    target_audience: Optional[str] = None,
    required_duration: Optional[int] = None,
    reference_material_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    生成课程大纲
    
    Args:
        intent: 教学意图提取结果
        subject: 学科领域
        target_audience: 目标学员
        required_duration: 预计课时
        reference_material_ids: 参考资料 ID 列表
    
    Returns:
        课程大纲数据结构
    """
    # 构建 LLM 提示词
    prompt = _build_outline_prompt(
        intent=intent,
        subject=subject,
        target_audience=target_audience,
        required_duration=required_duration
    )
    
    # 调用 LLM 生成大纲（这里使用模拟结果）
    outline_data = await _call_llm_for_outline(prompt)
    
    return outline_data


def _build_outline_prompt(
    intent: Dict[str, Any],
    subject: str,
    target_audience: Optional[str],
    required_duration: Optional[int]
) -> str:
    """构建生成大纲的提示词"""
    
    return f"""
你是一位经验丰富的教学设计师，请根据以下信息生成一份完整的课程大纲。

## 教学意图
- 主题：{intent.get('topic', 'Python 编程基础')}
- 学科：{subject}
- 目标学员：{target_audience or intent.get('target_audience', '初学者')}
- 预计课时：{required_duration or intent.get('required_duration', 45)} 分钟
- 学习目标：{intent.get('learning_objectives', [])}
- 关键知识点：{intent.get('key_knowledge_points', [])}
- 教学难点：{intent.get('teaching_difficulties', [])}

## 输出要求

请按照以下 JSON 格式返回课程大纲：
{{
    "title": "课程标题",
    "description": "课程简介（200 字以内）",
    "learning_objectives": ["目标 1", "目标 2", "目标 3"],
    "key_knowledge_points": ["知识点 1", "知识点 2", "知识点 3"],
    "teaching_difficulties": ["难点 1", "难点 2"],
    "chapters": [
        {{
            "title": "章节标题",
            "order": 1,
            "content": "章节内容概述",
            "lessons": [
                {{
                    "title": "课时标题",
                    "objectives": ["课时目标 1", "课时目标 2"],
                    "content": "详细教学内容",
                    "activities": ["教学活动 1", "教学活动 2"],
                    "assignments": ["课后作业"]
                }}
            ]
        }}
    ],
    "assessment": "考核方式",
    "resources": "推荐学习资源"
}}

确保内容结构清晰、难度递进合理、适合目标学员。
"""


async def _call_llm_for_outline(prompt: str) -> Dict[str, Any]:
    """
    调用 LLM 生成大纲
    实际应该调用 OpenRouter API
    """
    # 模拟返回结果
    return {
        "title": "Python 编程入门：变量与数据类型",
        "description": "本课程面向零基础学员，系统讲解 Python 编程中的变量概念和基本数据类型。通过实践案例帮助学员理解变量的命名规则、赋值方式，掌握整数、浮点数、字符串、布尔值等常用数据类型的使用方法。",
        "learning_objectives": [
            "理解变量的概念和命名规则",
            "掌握 Python 的基本数据类型",
            "能够进行简单的类型转换",
            "学会使用 print() 和 input() 函数"
        ],
        "key_knowledge_points": [
            "变量定义与命名规则",
            "整数 (int) 和浮点数 (float)",
            "字符串 (str) 的基本操作",
            "布尔类型 (bool) 和空值 (None)",
            "类型转换方法"
        ],
        "teaching_difficulties": [
            "变量引用的概念理解",
            "字符串的不可变性",
            "类型转换的边界情况"
        ],
        "chapters": [
            {
                "title": "第一章：变量基础",
                "order": 1,
                "content": "介绍变量的概念、命名规则和赋值方式",
                "lessons": [
                    {
                        "title": "1.1 什么是变量",
                        "objectives": ["理解变量的概念", "学会变量赋值"],
                        "content": "变量是存储数据的容器，可以想象成一个带标签的盒子...",
                        "activities": ["互动演示：变量盒子游戏", "小组讨论：生活中的变量类比"],
                        "assignments": ["完成变量定义练习题"]
                    },
                    {
                        "title": "1.2 变量命名规则",
                        "objectives": ["掌握命名规范", "避免常见错误"],
                        "content": "Python 变量命名需要遵循以下规则：只能包含字母、数字和下划线...",
                        "activities": ["命名改错练习", "最佳实践讨论"],
                        "assignments": ["为给定场景设计合适的变量名"]
                    }
                ]
            },
            {
                "title": "第二章：数据类型",
                "order": 2,
                "content": "系统讲解 Python 的基本数据类型及其特点",
                "lessons": [
                    {
                        "title": "2.1 数值类型",
                        "objectives": ["区分 int 和 float", "掌握数值运算"],
                        "content": "Python 支持整数 (int) 和浮点数 (float) 两种数值类型...",
                        "activities": ["数值运算练习", "类型判断游戏"],
                        "assignments": ["编写简单计算器程序"]
                    },
                    {
                        "title": "2.2 字符串基础",
                        "objectives": ["掌握字符串定义", "学会常用字符串操作"],
                        "content": "字符串是用来表示文本的数据类型，可以用单引号或双引号包裹...",
                        "activities": ["字符串拼接比赛", "格式化输出练习"],
                        "assignments": ["编写个人信息展示程序"]
                    },
                    {
                        "title": "2.3 布尔类型和类型转换",
                        "objectives": ["理解布尔值", "掌握类型转换方法"],
                        "content": "布尔类型只有 True 和 False 两个值，常用于条件判断...",
                        "activities": ["真假判断游戏", "类型转换挑战"],
                        "assignments": ["完成类型转换练习题"]
                    }
                ]
            }
        ],
        "assessment": "平时练习 40% + 期末项目 60%",
        "resources": [
            "Python 官方文档：https://docs.python.org/zh-cn/3/",
            "菜鸟教程 Python 专栏：https://www.runoob.com/python3/"
        ],
        "model": "qwen/qwen3.6-plus:free"
    }


async def regenerate_outline(
    original_outline: Dict[str, Any],
    feedback: str,
    intent: Dict[str, Any]
) -> Dict[str, Any]:
    """
    根据反馈重新生成大纲
    
    Args:
        original_outline: 原始大纲
        feedback: 修改反馈
        intent: 教学意图
    
    Returns:
        修改后的大纲
    """
    prompt = f"""
请根据以下反馈修改课程大纲。

## 原始大纲
{json.dumps(original_outline, ensure_ascii=False, indent=2)}

## 修改反馈
{feedback}

## 原始教学意图
- 主题：{intent.get('topic', '')}
- 目标学员：{intent.get('target_audience', '')}

请在保持原有结构的基础上，根据反馈进行针对性修改。
返回修改后的完整 JSON 大纲。
"""
    
    # 调用 LLM 重新生成
    # 这里返回原始大纲作为示例
    return original_outline
