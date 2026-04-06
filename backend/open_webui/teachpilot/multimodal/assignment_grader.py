"""
多模态作业批改模块
服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体

支持文本、代码、图片等多种作业类型的 AI 自动批改
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

log = logging.getLogger(__name__)


async def grade_assignment_multimodal(
    submission: Any,
    assignment: Any,
    rubric: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    多模态作业批改
    
    Args:
        submission: 作业提交对象
        assignment: 作业对象
        rubric: 评分标准
    
    Returns:
        批改结果，包含分数、反馈和多模态分析
    """
    result = {
        "score": 0,
        "feedback": {},
        "multimodal_analysis": {}
    }
    
    # 分析提交内容类型
    content_types = _analyze_submission_types(submission)
    
    # 根据作业类型选择批改策略
    if _is_code_assignment(submission, assignment):
        # 代码作业批改
        result = await _grade_code_submission(submission, assignment, rubric)
    elif _is_text_assignment(submission, assignment):
        # 文本回答批改
        result = await _grade_text_submission(submission, assignment, rubric)
    elif _is_multimodal_assignment(submission, assignment):
        # 多模态作业批改
        result = await _grade_multimodal_submission(submission, assignment, rubric)
    
    return result


def _analyze_submission_types(submission: Any) -> List[str]:
    """分析提交内容的类型"""
    types = []
    
    if submission.content:
        types.append("text")
    if submission.code_snippet:
        types.append("code")
    if submission.files:
        for f in submission.files:
            file_type = f.get("type", "")
            if "image" in file_type:
                types.append("image")
            elif "pdf" in file_type:
                types.append("pdf")
            elif "video" in file_type:
                types.append("video")
    
    return types


def _is_code_assignment(submission: Any, assignment: Any) -> bool:
    """判断是否为代码作业"""
    if submission.code_snippet:
        return True
    if assignment.allowed_file_types:
        code_extensions = ["py", "java", "cpp", "js", "ts"]
        for ext in code_extensions:
            if ext in assignment.allowed_file_types:
                return True
    return False


def _is_text_assignment(submission: Any, assignment: Any) -> bool:
    """判断是否为文本回答作业"""
    return bool(submission.content) and not submission.code_snippet


def _is_multimodal_assignment(submission: Any, assignment: Any) -> bool:
    """判断是否为多模态作业"""
    types = _analyze_submission_types(submission)
    return len(types) > 1


async def _grade_code_submission(
    submission: Any,
    assignment: Any,
    rubric: Optional[Dict]
) -> Dict[str, Any]:
    """
    代码作业批改
    
    评估维度：
    1. 代码正确性（是否能通过测试用例）
    2. 代码规范（命名、注释、格式）
    3. 代码效率（时间复杂度、空间复杂度）
    4. 代码创新（解决方案的巧妙程度）
    """
    code = submission.code_snippet or ""
    
    # 构建评分 prompt
    prompt = f"""
请作为编程助教批改以下 Python 代码作业。

## 作业要求
{assignment.description or "完成指定的编程任务"}

## 评分标准
{json.dumps(rubric, ensure_ascii=False) if rubric else "默认评分标准：正确性 40% + 规范性 30% + 效率 20% + 创新性 10%"}

## 学生代码
```python
{code}
```

请按照以下 JSON 格式返回批改结果：
{{
    "score": 0-100 的分数，
    "correctness_score": 正确性得分，
    "style_score": 规范性得分，
    "efficiency_score": 效率得分，
    "creativity_score": 创新性得分，
    "feedback": {{
        "strengths": ["优点 1", "优点 2"],
        "weaknesses": ["不足 1", "不足 2"],
        "suggestions": ["改进建议 1", "改进建议 2"]
    }},
    "code_analysis": {{
        "syntax_errors": ["语法错误列表"],
        "style_issues": ["规范问题列表"],
        "complexity": "时间复杂度分析",
        "test_results": "测试用例通过情况"
    }},
    "overall_comment": "总体评价（100 字以内）"
}}
"""
    
    # 模拟批改结果（实际应调用 LLM）
    result = {
        "score": 85,
        "correctness_score": 90,
        "style_score": 80,
        "efficiency_score": 85,
        "creativity_score": 75,
        "feedback": {
            "strengths": [
                "代码逻辑正确，能够完成基本功能",
                "变量命名清晰，易于理解"
            ],
            "weaknesses": [
                "缺少必要的注释",
                "部分代码可以进一步优化"
            ],
            "suggestions": [
                "建议为函数添加 docstring 说明",
                "可以考虑使用列表推导式简化代码"
            ]
        },
        "code_analysis": {
            "syntax_errors": [],
            "style_issues": [
                "第 5 行：建议添加空行分隔逻辑块",
                "第 10 行：变量名可以更具体"
            ],
            "complexity": "时间复杂度 O(n)，空间复杂度 O(1)",
            "test_results": "5/5 测试用例通过"
        },
        "overall_comment": "代码完成度较高，功能实现正确。建议在代码规范和注释方面继续改进，提高代码可读性。"
    }
    
    return result


async def _grade_text_submission(
    submission: Any,
    assignment: Any,
    rubric: Optional[Dict]
) -> Dict[str, Any]:
    """
    文本回答批改
    
    评估维度：
    1. 内容完整性
    2. 逻辑清晰度
    3. 表达准确性
    4. 创新性思考
    """
    content = submission.content or ""
    
    prompt = f"""
请批改以下文本回答作业。

## 作业要求
{assignment.description or "回答指定问题"}

## 评分标准
{json.dumps(rubric, ensure_ascii=False) if rubric else "默认评分标准：完整性 30% + 逻辑性 30% + 准确性 25% + 创新性 15%"}

## 学生回答
{content}

请按照以下 JSON 格式返回批改结果：
{{
    "score": 0-100 的分数，
    "completeness_score": 完整性得分，
    "logic_score": 逻辑性得分，
    "accuracy_score": 准确性得分，
    "creativity_score": 创新性得分，
    "feedback": {{
        "strengths": ["优点 1", "优点 2"],
        "weaknesses": ["不足 1", "不足 2"],
        "suggestions": ["改进建议 1", "改进建议 2"]
    }},
    "content_analysis": {{
        "key_points_covered": ["覆盖的要点"],
        "missing_points": ["遗漏的要点"],
        "factual_errors": ["事实错误"],
        "word_count": 字数统计
    }},
    "overall_comment": "总体评价"
}}
"""
    
    # 模拟批改结果
    result = {
        "score": 78,
        "completeness_score": 80,
        "logic_score": 75,
        "accuracy_score": 85,
        "creativity_score": 70,
        "feedback": {
            "strengths": [
                "回答内容基本完整",
                "概念理解准确"
            ],
            "weaknesses": [
                "逻辑结构可以更清晰",
                "缺少具体例子支撑论点"
            ],
            "suggestions": [
                "建议使用总分总结构组织答案",
                "可以添加实际案例增强说服力"
            ]
        },
        "content_analysis": {
            "key_points_covered": ["核心概念定义", "基本特点说明"],
            "missing_points": ["实际应用场景", "与其他概念的比较"],
            "factual_errors": [],
            "word_count": len(content)
        },
        "overall_comment": "回答基本准确，但可以在逻辑组织和举例说明方面加强。"
    }
    
    return result


async def _grade_multimodal_submission(
    submission: Any,
    assignment: Any,
    rubric: Optional[Dict]
) -> Dict[str, Any]:
    """
    多模态作业批改
    
    综合评估文本、代码、图片等多种内容
    """
    types = _analyze_submission_types(submission)
    
    # 分别批改各类型内容
    results = {}
    weights = {}
    
    if "text" in types:
        text_result = await _grade_text_submission(submission, assignment, rubric)
        results["text"] = text_result
        weights["text"] = 0.4
    
    if "code" in types:
        code_result = await _grade_code_submission(submission, assignment, rubric)
        results["code"] = code_result
        weights["code"] = 0.4
    
    if "image" in types:
        # 图片分析（需要视觉模型）
        image_result = await _analyze_image_submission(submission)
        results["image"] = image_result
        weights["image"] = 0.2
    
    # 计算综合分数
    total_score = sum(
        results[key].get("score", 0) * weights[key]
        for key in results.keys()
    )
    
    # 整合反馈
    all_feedback = {
        "strengths": [],
        "weaknesses": [],
        "suggestions": []
    }
    for result in results.values():
        feedback = result.get("feedback", {})
        all_feedback["strengths"].extend(feedback.get("strengths", []))
        all_feedback["weaknesses"].extend(feedback.get("weaknesses", []))
        all_feedback["suggestions"].extend(feedback.get("suggestions", []))
    
    return {
        "score": round(total_score, 1),
        "feedback": all_feedback,
        "multimodal_analysis": {
            "content_types": types,
            "type_scores": {
                key: result.get("score", 0)
                for key, result in results.items()
            },
            "integration_quality": "良好" if total_score > 80 else "一般"
        },
        "overall_comment": f"多模态作业完成度{total_score/100:.0%}，各类型内容配合{'默契' if total_score > 80 else '需要加强'}。"
    }


async def _analyze_image_submission(submission: Any) -> Dict[str, Any]:
    """
    分析图片类作业
    
    需要视觉模型支持，这里提供框架
    """
    # 实际应该调用视觉模型 API 分析图片内容
    return {
        "score": 80,
        "analysis": {
            "image_count": len([f for f in submission.files if "image" in f.get("type", "")]),
            "quality_assessment": "良好",
            "relevance": "与作业主题相关"
        }
    }


async def provide_detailed_feedback(
    submission: Any,
    grading_result: Dict[str, Any]
) -> str:
    """
    生成详细的批改反馈
    
    将结构化批改结果转换为自然语言反馈
    """
    score = grading_result.get("score", 0)
    feedback = grading_result.get("feedback", {})
    overall = grading_result.get("overall_comment", "")
    
    feedback_text = f"""
## 作业批改反馈

**得分：{score}/100**

### 优点
"""
    for strength in feedback.get("strengths", []):
        feedback_text += f"- {strength}\n"
    
    feedback_text += "\n### 需要改进\n"
    for weakness in feedback.get("weaknesses", []):
        feedback_text += f"- {weakness}\n"
    
    feedback_text += "\n### 建议\n"
    for suggestion in feedback.get("suggestions", []):
        feedback_text += f"- {suggestion}\n"
    
    feedback_text += f"\n### 总体评价\n{overall}"
    
    return feedback_text
