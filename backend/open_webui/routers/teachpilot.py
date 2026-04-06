"""
TeachPilot API 路由
服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体

提供教师端和学生端的核心功能接口：
- 课程大纲自动生成
- 学习进度追踪
- 多模态作业批改
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from open_webui.internal.db import get_db
from open_webui.models.teachpilot import (
    CourseOutline, Lesson, LearningProgress,
    Assignment, AssignmentSubmission, TeachingIntent, CourseEnrollment
)
from open_webui.models.auths import Auth
from open_webui.utils.auth import get_current_user, get_verified_user, get_admin_user
from open_webui.teachpilot.intent.intent_extractor import extract_teaching_intent
from open_webui.teachpilot.generators.outline_generator import generate_course_outline
from open_webui.teachpilot.multimodal.assignment_grader import grade_assignment_multimodal

log = logging.getLogger(__name__)

router = APIRouter(prefix="/teachpilot", tags=["teachpilot"])


# ==================== Pydantic 模型 ====================

class OutlineGenerateRequest(BaseModel):
    """课程大纲生成请求"""
    prompt: str = Field(..., description="教师输入的教学需求")
    subject: str = Field(default="computer_science", description="学科领域")
    target_audience: Optional[str] = Field(default=None, description="目标学员")
    required_duration: Optional[int] = Field(default=None, description="预计课时（分钟）")
    reference_material_ids: Optional[List[str]] = Field(default=None, description="参考资料 ID 列表")
    learning_objectives: Optional[List[str]] = Field(default=None, description="学习目标")
    key_knowledge_points: Optional[List[str]] = Field(default=None, description="关键知识点")


class OutlineUpdateRequest(BaseModel):
    """课程大纲更新请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    chapters: Optional[List[Dict]] = None
    learning_objectives: Optional[List[str]] = None
    key_knowledge_points: Optional[List[str]] = None
    teaching_difficulties: Optional[List[str]] = None


class LessonCreateRequest(BaseModel):
    """课时创建请求"""
    title: str
    order: int = 0
    objectives: Optional[List[str]] = None
    content: Optional[str] = None
    activities: Optional[List[Dict]] = None
    assignments: Optional[List[Dict]] = None


class AssignmentCreateRequest(BaseModel):
    """作业创建请求"""
    lesson_id: int
    title: str
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    rubric: Optional[Dict] = None
    max_score: int = 100
    due_date: Optional[datetime] = None
    allowed_file_types: Optional[List[str]] = None


class AssignmentSubmitRequest(BaseModel):
    """作业提交请求"""
    content: Optional[str] = None
    files: Optional[List[Dict]] = None
    code_snippet: Optional[str] = None


class ProgressUpdateRequest(BaseModel):
    """学习进度更新请求"""
    lesson_id: Optional[int] = None
    progress_percentage: float = Field(ge=0, le=100)
    status: Optional[str] = None
    interaction_data: Optional[Dict] = None


# ==================== 课程大纲管理 ====================

@router.post("/outlines/generate", response_model=Dict)
async def generate_outline(
    request: OutlineGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【教师端】生成课程大纲
    
    基于教师输入的教学需求，利用 LLM 自动生成结构化的课程大纲
    """
    try:
        # 1. 提取教学意图
        intent_result = extract_teaching_intent(
            prompt=request.prompt,
            user_id=user.id
        )
        
        # 2. 生成课程大纲
        outline_data = await generate_course_outline(
            intent=intent_result,
            subject=request.subject,
            target_audience=request.target_audience,
            required_duration=request.required_duration,
            reference_material_ids=request.reference_material_ids
        )
        
        # 3. 保存到数据库
        new_outline = CourseOutline(
            user_id=user.id,
            title=outline_data.get("title", "未命名课程"),
            description=outline_data.get("description", ""),
            subject=request.subject,
            target_audience=request.target_audience,
            learning_objectives=request.learning_objectives or outline_data.get("learning_objectives", []),
            key_knowledge_points=request.key_knowledge_points or outline_data.get("key_knowledge_points", []),
            teaching_difficulties=outline_data.get("teaching_difficulties", []),
            required_duration=request.required_duration,
            chapters=outline_data.get("chapters", []),
            generated_by=outline_data.get("model", "qwen/qwen3.6-plus:free"),
            generation_prompt=request.prompt,
            reference_materials=request.reference_material_ids or [],
            status="draft"
        )
        
        db.add(new_outline)
        db.commit()
        db.refresh(new_outline)
        
        # 4. 记录教学意图
        intent_record = TeachingIntent(
            user_id=user.id,
            session_id=f"outline_{new_outline.id}",
            intent_type="create_outline",
            extracted_elements=intent_result,
            conversation_history=[{"role": "user", "content": request.prompt}],
            generated_content={"outline_id": new_outline.id},
            confidence_score=intent_result.get("confidence", 0.0)
        )
        db.add(intent_record)
        db.commit()
        
        return {
            "success": True,
            "outline_id": new_outline.id,
            "outline": {
                "id": new_outline.id,
                "title": new_outline.title,
                "chapters": new_outline.chapters,
                "created_at": new_outline.created_at.isoformat()
            }
        }
        
    except Exception as e:
        log.exception(f"生成课程大纲失败：{e}")
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")


@router.get("/outlines", response_model=List[Dict])
async def list_outlines(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】获取课程大纲列表"""
    query = db.query(CourseOutline).filter(CourseOutline.user_id == user.id)
    if status:
        query = query.filter(CourseOutline.status == status)
    outlines = query.order_by(CourseOutline.created_at.desc()).all()
    
    return [{
        "id": o.id,
        "title": o.title,
        "subject": o.subject,
        "status": o.status,
        "version": o.version,
        "created_at": o.created_at.isoformat(),
        "updated_at": o.updated_at.isoformat()
    } for o in outlines]


@router.get("/outlines/{outline_id}", response_model=Dict)
async def get_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】获取课程大纲详情"""
    outline = db.query(CourseOutline).filter(
        CourseOutline.id == outline_id,
        CourseOutline.user_id == user.id
    ).first()
    
    if not outline:
        raise HTTPException(status_code=404, detail="课程大纲不存在")
    
    return {
        "id": outline.id,
        "title": outline.title,
        "description": outline.description,
        "subject": outline.subject,
        "target_audience": outline.target_audience,
        "learning_objectives": outline.learning_objectives,
        "key_knowledge_points": outline.key_knowledge_points,
        "teaching_difficulties": outline.teaching_difficulties,
        "required_duration": outline.required_duration,
        "chapters": outline.chapters,
        "lessons": [{
            "id": l.id,
            "title": l.title,
            "order": l.order,
            "objectives": l.objectives,
            "ppt_path": l.ppt_path,
            "doc_path": l.doc_path
        } for l in outline.lessons],
        "status": outline.status,
        "version": outline.version,
        "created_at": outline.created_at.isoformat(),
        "updated_at": outline.updated_at.isoformat()
    }


@router.put("/outlines/{outline_id}", response_model=Dict)
async def update_outline(
    outline_id: int,
    request: OutlineUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】更新课程大纲"""
    outline = db.query(CourseOutline).filter(
        CourseOutline.id == outline_id,
        CourseOutline.user_id == user.id
    ).first()
    
    if not outline:
        raise HTTPException(status_code=404, detail="课程大纲不存在")
    
    # 更新字段
    if request.title:
        outline.title = request.title
    if request.description:
        outline.description = request.description
    if request.chapters:
        outline.chapters = request.chapters
    if request.learning_objectives:
        outline.learning_objectives = request.learning_objectives
    if request.key_knowledge_points:
        outline.key_knowledge_points = request.key_knowledge_points
    if request.teaching_difficulties:
        outline.teaching_difficulties = request.teaching_difficulties
    
    outline.version += 1
    outline.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(outline)
    
    return {
        "success": True,
        "outline_id": outline.id,
        "version": outline.version
    }


@router.delete("/outlines/{outline_id}")
async def delete_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】删除课程大纲"""
    outline = db.query(CourseOutline).filter(
        CourseOutline.id == outline_id,
        CourseOutline.user_id == user.id
    ).first()
    
    if not outline:
        raise HTTPException(status_code=404, detail="课程大纲不存在")
    
    db.delete(outline)
    db.commit()
    
    return {"success": True}


# ==================== 课时管理 ====================

@router.post("/outlines/{outline_id}/lessons", response_model=Dict)
async def create_lesson(
    outline_id: int,
    request: LessonCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】创建课时"""
    outline = db.query(CourseOutline).filter(
        CourseOutline.id == outline_id,
        CourseOutline.user_id == user.id
    ).first()
    
    if not outline:
        raise HTTPException(status_code=404, detail="课程大纲不存在")
    
    lesson = Lesson(
        course_id=outline_id,
        title=request.title,
        order=request.order,
        objectives=request.objectives,
        content=request.content,
        activities=request.activities,
        assignments=request.assignments
    )
    
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    
    return {
        "success": True,
        "lesson_id": lesson.id
    }


# ==================== 学习进度追踪 ====================

@router.get("/progress/courses", response_model=List[Dict])
async def get_student_courses(
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【学生端】获取我的课程列表
    
    返回学生已注册的课程及学习进度概览
    """
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == user.id,
        CourseEnrollment.status == "active"
    ).all()
    
    course_ids = [e.course_id for e in enrollments]
    courses = db.query(CourseOutline).filter(CourseOutline.id.in_(course_ids)).all()
    
    result = []
    for course in courses:
        # 计算总体进度
        lessons = db.query(Lesson).filter(Lesson.course_id == course.id).all()
        progress_records = db.query(LearningProgress).filter(
            LearningProgress.user_id == user.id,
            LearningProgress.course_id == course.id
        ).all()
        
        total_lessons = len(lessons)
        completed_lessons = sum(1 for p in progress_records if p.status == "completed")
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        result.append({
            "id": course.id,
            "title": course.title,
            "subject": course.subject,
            "progress_percentage": round(overall_progress, 1),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "enrolled_at": next(e.enrolled_at.isoformat() for e in enrollments if e.course_id == course.id)
        })
    
    return result


@router.get("/progress/{course_id}", response_model=Dict)
async def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【学生端】获取课程详细进度
    
    返回每课时的学习进度、测验成绩、学习笔记等
    """
    course = db.query(CourseOutline).filter(CourseOutline.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == user.id,
        LearningProgress.course_id == course_id
    ).all()
    
    progress_map = {p.lesson_id: p for p in progress_records}
    
    lesson_progress = []
    for lesson in lessons:
        progress = progress_map.get(lesson.id)
        lesson_progress.append({
            "lesson_id": lesson.id,
            "title": lesson.title,
            "order": lesson.order,
            "progress_percentage": progress.progress_percentage if progress else 0,
            "status": progress.status if progress else "not_started",
            "time_spent": progress.time_spent if progress else 0,
            "quiz_scores": progress.quiz_scores if progress else [],
            "last_accessed_at": progress.last_accessed_at.isoformat() if progress and progress.last_accessed_at else None,
            "completed_at": progress.completed_at.isoformat() if progress and progress.completed_at else None
        })
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "overall_progress": sum(lp["progress_percentage"] for lp in lesson_progress) / len(lesson_progress) if lesson_progress else 0,
        "lessons": lesson_progress
    }


@router.post("/progress/update", response_model=Dict)
async def update_progress(
    request: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【学生端】更新学习进度
    
    记录学生的学习行为，包括进度、时间、交互数据等
    """
    if not request.lesson_id:
        raise HTTPException(status_code=400, detail="lesson_id 是必填项")
    
    lesson = db.query(Lesson).filter(Lesson.id == request.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课时不存在")
    
    # 查找或创建进度记录
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == user.id,
        LearningProgress.lesson_id == request.lesson_id
    ).first()
    
    if not progress:
        progress = LearningProgress(
            user_id=user.id,
            course_id=lesson.course_id,
            lesson_id=request.lesson_id,
            progress_percentage=request.progress_percentage,
            status=request.status or "in_progress",
            last_accessed_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.progress_percentage = request.progress_percentage
        if request.status:
            progress.status = request.status
        progress.last_accessed_at = datetime.utcnow()
        
        if request.progress_percentage >= 100 and progress.status != "completed":
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
        
        if request.interaction_data:
            existing_data = progress.interaction_data or {}
            existing_data.update(request.interaction_data)
            progress.interaction_data = existing_data
    
    db.commit()
    db.refresh(progress)
    
    return {
        "success": True,
        "progress_id": progress.id,
        "status": progress.status,
        "completed": progress.status == "completed"
    }


@router.get("/progress/stats", response_model=Dict)
async def get_progress_stats(
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【学生端】获取学习统计
    
    返回学习时长、完成课程数、平均成绩等统计数据
    """
    progress_records = db.query(LearningProgress).filter(
        LearningProgress.user_id == user.id
    ).all()
    
    total_time = sum(p.time_spent for p in progress_records)
    completed_count = sum(1 for p in progress_records if p.status == "completed")
    
    # 计算平均成绩
    all_scores = []
    for p in progress_records:
        if p.quiz_scores:
            all_scores.extend(p.quiz_scores)
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return {
        "total_courses": len(set(p.course_id for p in progress_records)),
        "completed_courses": completed_count,
        "total_time_seconds": total_time,
        "total_time_hours": round(total_time / 3600, 1),
        "average_score": round(avg_score, 1),
        "total_lessons_progress": len(progress_records)
    }


# ==================== 多模态作业批改 ====================

@router.post("/assignments", response_model=Dict)
async def create_assignment(
    request: AssignmentCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】创建作业"""
    lesson = db.query(Lesson).filter(Lesson.id == request.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课时不存在")
    
    # 验证教师权限
    course = db.query(CourseOutline).filter(
        CourseOutline.id == lesson.course_id,
        CourseOutline.user_id == user.id
    ).first()
    if not course:
        raise HTTPException(status_code=403, detail="无权为此课程创建作业")
    
    assignment = Assignment(
        lesson_id=request.lesson_id,
        title=request.title,
        description=request.description,
        requirements=request.requirements,
        rubric=request.rubric,
        max_score=request.max_score,
        due_date=request.due_date,
        allowed_file_types=request.allowed_file_types or ["pdf", "docx", "txt", "py", "jpg", "png"],
        support_multimodal=True
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return {
        "success": True,
        "assignment_id": assignment.id
    }


@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    content: Optional[str] = Form(None),
    files: Optional[str] = Form(None),
    code_snippet: Optional[str] = Form(None),
    upload_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【学生端】提交作业
    
    支持多模态提交：文本、文件、代码片段
    """
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 处理上传文件
    file_list = []
    if upload_files:
        for file in upload_files:
            # 这里应该实际保存文件，简化处理
            file_list.append({
                "name": file.filename,
                "type": file.content_type,
                "size": file.size
            })
    
    # 解析 files JSON
    files_data = None
    if files:
        files_data = json.loads(files)
        file_list.extend(files_data)
    
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        user_id=user.id,
        content=content,
        files=file_list,
        code_snippet=code_snippet,
        status="submitted"
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # 触发自动批改（后台任务）
    if assignment.support_multimodal:
        # 这里可以添加后台任务进行自动批改
        pass
    
    return {
        "success": True,
        "submission_id": submission.id,
        "submitted_at": submission.submitted_at.isoformat()
    }


@router.post("/assignments/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    auto_grade: bool = True,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """
    【教师端/AI】批改作业
    
    支持 AI 自动批改和教师手动批改
    """
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    assignment = db.query(Assignment).filter(
        Assignment.id == submission.assignment_id
    ).first()
    
    result = {
        "success": True,
        "submission_id": submission_id,
        "auto_grade": None,
        "ai_feedback": None
    }
    
    # AI 自动批改
    if auto_grade and assignment.support_multimodal:
        grading_result = await grade_assignment_multimodal(
            submission=submission,
            assignment=assignment,
            rubric=assignment.rubric
        )
        
        submission.auto_grade = grading_result.get("score")
        submission.ai_feedback = grading_result.get("feedback")
        submission.multimodal_analysis = grading_result.get("multimodal_analysis")
        submission.status = "graded"
        
        result["auto_grade"] = grading_result.get("score")
        result["ai_feedback"] = grading_result.get("feedback")
    
    db.commit()
    db.refresh(submission)
    
    return result


@router.get("/assignments/{assignment_id}/submissions", response_model=List[Dict])
async def list_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端】获取作业提交列表"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 验证教师权限
    lesson = db.query(Lesson).filter(Lesson.id == assignment.lesson_id).first()
    course = db.query(CourseOutline).filter(
        CourseOutline.id == lesson.course_id,
        CourseOutline.user_id == user.id
    ).first()
    if not course:
        raise HTTPException(status_code=403, detail="无权查看此作业的提交")
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    
    return [{
        "id": s.id,
        "user_id": s.user_id,
        "status": s.status,
        "submitted_at": s.submitted_at.isoformat(),
        "auto_grade": s.auto_grade,
        "teacher_grade": s.teacher_grade,
        "has_feedback": s.feedback is not None or s.ai_feedback is not None
    } for s in submissions]


@router.get("/assignments/submissions/{submission_id}", response_model=Dict)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_verified_user)
):
    """【教师端/学生端】获取作业提交详情"""
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    # 权限检查：只有提交者或教师可以查看
    assignment = db.query(Assignment).filter(
        Assignment.id == submission.assignment_id
    ).first()
    lesson = db.query(Lesson).filter(Lesson.id == assignment.lesson_id).first()
    course = db.query(CourseOutline).filter(CourseOutline.id == lesson.course_id).first()
    
    is_owner = submission.user_id == user.id
    is_teacher = course.user_id == user.id
    
    if not is_owner and not is_teacher:
        raise HTTPException(status_code=403, detail="无权查看此提交")
    
    return {
        "id": submission.id,
        "assignment_id": submission.assignment_id,
        "assignment_title": assignment.title,
        "content": submission.content,
        "files": submission.files,
        "code_snippet": submission.code_snippet,
        "status": submission.status,
        "auto_grade": submission.auto_grade,
        "teacher_grade": submission.teacher_grade,
        "feedback": submission.feedback,
        "ai_feedback": submission.ai_feedback,
        "multimodal_analysis": submission.multimodal_analysis,
        "submitted_at": submission.submitted_at.isoformat(),
        "graded_at": submission.graded_at.isoformat() if submission.graded_at else None
    }
