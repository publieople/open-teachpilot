"""
教学意图提取模块
服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体

负责从教师的自然语言输入中结构化提取教学要素
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

log = logging.getLogger(__name__)

# 教学意图类型
INTENT_TYPES = {
    "create_outline": "创建课程大纲",
    "generate_lesson": "生成课时内容",
    "create_quiz": "创建测验题目",
    "generate_ppt": "生成 PPT 课件",
    "generate_doc": "生成 Word 教案",
    "create_assignment": "创建作业",
    "explain_concept": "解释概念",
    "design_activity": "设计教学活动"
}


def extract_teaching_intent(
    prompt: str,
    user_id: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    提取教学意图
    
    从教师的输入中识别意图类型并提取结构化的教学要素
    
    Args:
        prompt: 教师输入的文本
        user_id: 用户 ID
        conversation_history: 对话历史（用于多轮对话澄清）
    
    Returns:
        包含提取结果的结构化字典
    """
    # 使用 LLM 进行意图识别和要素提取
    # 这里使用预设的 prompt 模板，实际应该调用 LLM API
    
    intent_prompt = f"""
你是一个专业的教学助手，专门帮助教师设计课程。请分析以下教师输入，提取结构化的教学要素。

教师输入：
{prompt}

请按照以下 JSON 格式返回提取结果：
{{
    "intent_type": "识别的意图类型（create_outline/generate_lesson/create_quiz 等）",
    "confidence": 0.0-1.0 的置信度，
    "subject": "学科领域（如 computer_science, python_programming）",
    "topic": "具体主题",
    "target_audience": "目标学员描述（如'Python 零基础初学者'）",
    "learning_objectives": ["学习目标 1", "学习目标 2", ...],
    "key_knowledge_points": ["知识点 1", "知识点 2", ...],
    "teaching_difficulties": ["难点 1", "难点 2", ...],
    "required_duration": 预计课时（分钟，如不确定则为 null）,
    "teaching_style": "教学风格偏好（如'实践导向'、'理论为主'）",
    "prerequisites": ["前置知识要求 1", ...],
    "clarification_questions": ["需要向教师确认的问题 1", ...]
}}

如果某些信息无法从输入中确定，请在对应字段填入 null 或空数组。
如果有模糊或不确定的地方，请在 clarification_questions 中列出需要进一步确认的问题。
"""
    
    # 模拟 LLM 调用结果（实际应该调用 OpenRouter API）
    # 这里使用简单的规则匹配作为示例
    result = _mock_intent_extraction(prompt)
    
    log.info(f"教学意图提取结果：{result}")
    
    return result


def _mock_intent_extraction(prompt: str) -> Dict[str, Any]:
    """
    模拟意图提取（用于开发测试）
    实际应该调用 LLM API
    """
    prompt_lower = prompt.lower()
    
    # 简单的关键词匹配
    intent_type = "create_outline"
    if "课时" in prompt or "节课" in prompt:
        intent_type = "generate_lesson"
    elif "测验" in prompt or "题目" in prompt or "测试" in prompt:
        intent_type = "create_quiz"
    elif "PPT" in prompt or "课件" in prompt:
        intent_type = "generate_ppt"
    elif "作业" in prompt or "练习" in prompt:
        intent_type = "create_assignment"
    elif "解释" in prompt or "什么是" in prompt:
        intent_type = "explain_concept"
    
    # 提取可能的主题
    topic = None
    python_keywords = ["python", "变量", "函数", "循环", "列表", "字典", "类", "对象"]
    for kw in python_keywords:
        if kw in prompt_lower:
            topic = f"Python: {kw}"
            break
    
    # 构建结果
    result = {
        "intent_type": intent_type,
        "confidence": 0.85,
        "subject": "computer_science",
        "topic": topic or "Python 编程基础",
        "target_audience": "Python 零基础初学者",
        "learning_objectives": [
            "理解核心概念",
            "掌握基本用法",
            "能够独立完成简单练习"
        ],
        "key_knowledge_points": [
            "概念定义",
            "语法规则",
            "实际应用"
        ],
        "teaching_difficulties": [
            "概念抽象理解",
            "实际场景应用"
        ],
        "required_duration": 45,
        "teaching_style": "实践导向",
        "prerequisites": [
            "了解计算机基本操作"
        ],
        "clarification_questions": []
    }
    
    return result


async def clarify_intent(
    user_id: str,
    session_id: str,
    user_response: str,
    previous_intent: Dict[str, Any]
) -> Dict[str, Any]:
    """
    多轮对话澄清意图
    
    根据用户对澄清问题的回答，完善教学意图
    """
    # 更新之前的意图结果
    updated_intent = previous_intent.copy()
    
    # 这里应该调用 LLM 来理解用户的回答并更新意图
    # 简化处理：直接合并
    
    log.info(f"意图澄清：{user_response}")
    
    return updated_intent


def get_intent_template(intent_type: str) -> Dict[str, Any]:
    """
    获取特定意图类型的模板
    """
    templates = {
        "create_outline": {
            "required_fields": ["topic", "target_audience"],
            "optional_fields": ["learning_objectives", "required_duration", "teaching_style"],
            "output_format": "course_outline"
        },
        "generate_lesson": {
            "required_fields": ["outline_id", "lesson_topic"],
            "optional_fields": ["teaching_activities", "assignments"],
            "output_format": "lesson_plan"
        },
        "create_quiz": {
            "required_fields": ["topic", "question_count"],
            "optional_fields": ["difficulty_level", "question_types"],
            "output_format": "quiz"
        },
        "generate_ppt": {
            "required_fields": ["topic", "slide_count"],
            "optional_fields": ["style", "include_notes"],
            "output_format": "ppt_structure"
        },
        "create_assignment": {
            "required_fields": ["topic", "assignment_type"],
            "optional_fields": ["difficulty", "estimated_time", "rubric"],
            "output_format": "assignment"
        }
    }
    
    return templates.get(intent_type, templates["create_outline"])
