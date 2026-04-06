"""
TeachPilot 数据模型
服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from open_webui.internal.db import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"


class CourseOutline(Base):
    """课程大纲表 - 教师端核心功能"""
    __tablename__ = "teachpilot_course_outline"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("auth.id"), nullable=False, index=True)  # 所属教师
    title = Column(String(255), nullable=False)  # 课程标题
    description = Column(Text)  # 课程描述
    subject = Column(String(100), default="computer_science")  # 学科领域
    target_audience = Column(String(255))  # 目标学员
    
    # 教学要素（结构化存储）
    learning_objectives = Column(JSON)  # 学习目标列表
    key_knowledge_points = Column(JSON)  # 关键知识点列表
    teaching_difficulties = Column(JSON)  # 教学难点列表
    required_duration = Column(Integer)  # 预计课时（分钟）
    
    # 大纲结构
    chapters = Column(JSON)  # 章节结构 [{"title": "", "content": "", "order": 1}]
    
    # 生成信息
    generated_by = Column(String(100))  # 生成模型
    generation_prompt = Column(Text)  # 生成提示词
    reference_materials = Column(JSON)  # 参考资料 ID 列表
    
    # 状态
    status = Column(String(50), default="draft")  # draft, published, archived
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("teachpilot_course_outline.id"))  # 版本继承
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    lessons = relationship("Lesson", back_populates="course_outline", cascade="all, delete-orphan")


class Lesson(Base):
    """课时表 - 课程大纲的子单元"""
    __tablename__ = "teachpilot_lesson"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("teachpilot_course_outline.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)  # 课时标题
    order = Column(Integer, default=0)  # 课时顺序
    
    # 教学内容
    objectives = Column(JSON)  # 本课时目标
    content = Column(Text)  # 教学内容
    activities = Column(JSON)  # 教学活动设计
    assignments = Column(JSON)  # 作业设计
    
    # 资源
    ppt_path = Column(String(512))  # PPT 文件路径
    doc_path = Column(String(512))  # Word 教案路径
    resources = Column(JSON)  # 附加资源
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    course_outline = relationship("CourseOutline", back_populates="lessons")


class LearningProgress(Base):
    """学习进度表 - 学生端核心功能"""
    __tablename__ = "teachpilot_learning_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("auth.id"), nullable=False, index=True)  # 学生 ID
    course_id = Column(Integer, ForeignKey("teachpilot_course_outline.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("teachpilot_lesson.id"))
    
    # 进度信息
    progress_percentage = Column(Float, default=0.0)  # 完成度 0-100
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    
    # 学习行为
    time_spent = Column(Integer, default=0)  # 花费时间（秒）
    last_accessed_at = Column(DateTime)  # 最后访问时间
    completed_at = Column(DateTime)  # 完成时间
    
    # 学习数据
    interaction_data = Column(JSON)  # 交互记录
    quiz_scores = Column(JSON)  # 测验成绩
    notes = Column(Text)  # 学习笔记
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Assignment(Base):
    """作业表 - 多模态作业批改"""
    __tablename__ = "teachpilot_assignment"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("teachpilot_lesson.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 作业要求
    requirements = Column(JSON)  # 作业要求列表
    rubric = Column(JSON)  # 评分标准
    max_score = Column(Integer, default=100)
    due_date = Column(DateTime)  # 截止时间
    
    # 多模态支持
    allowed_file_types = Column(JSON)  # 允许的文件类型
    support_multimodal = Column(Boolean, default=True)  # 是否支持多模态
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    """作业提交表 - 多模态作业批改"""
    __tablename__ = "teachpilot_assignment_submission"

    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("teachpilot_assignment.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("auth.id"), nullable=False, index=True)  # 提交学生
    
    # 提交内容
    content = Column(Text)  # 文本内容
    files = Column(JSON)  # 提交的文件列表 [{"id": "", "name": "", "type": "", "path": ""}]
    code_snippet = Column(Text)  # 代码片段（编程作业）
    
    # 批改信息
    status = Column(String(50), default="submitted")  # submitted, grading, graded, returned
    auto_grade = Column(Float)  # 自动评分
    teacher_grade = Column(Float)  # 教师评分
    feedback = Column(Text)  # 批改反馈
    ai_feedback = Column(JSON)  # AI 生成的详细反馈
    
    # 多模态分析结果
    multimodal_analysis = Column(JSON)  # 多模态分析结果
    
    # 时间戳
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)
    
    # 关联
    assignment = relationship("Assignment", back_populates="submissions")


class TeachingIntent(Base):
    """教学意图记录表 - 意图理解模块"""
    __tablename__ = "teachpilot_teaching_intent"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("auth.id"), nullable=False, index=True)
    session_id = Column(String(100), index=True)  # 对话会话 ID
    
    # 意图信息
    intent_type = Column(String(50))  # create_outline, generate_lesson, create_quiz, etc.
    extracted_elements = Column(JSON)  # 提取的教学要素
    
    # 对话历史
    conversation_history = Column(JSON)  # 多轮对话历史
    
    # 生成结果
    generated_content = Column(JSON)  # 生成的内容
    confidence_score = Column(Float)  # 意图识别置信度
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)


class CourseEnrollment(Base):
    """课程注册表"""
    __tablename__ = "teachpilot_course_enrollment"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("teachpilot_course_outline.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("auth.id"), nullable=False, index=True)
    role = Column(String(20), default="student")  # teacher, student, ta
    
    # 状态
    status = Column(String(20), default="active")  # active, dropped, completed
    
    # 时间戳
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
