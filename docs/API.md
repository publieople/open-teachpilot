# TeachPilot API 文档

## 基础信息

- **基础 URL**: `http://localhost:3000/api/v1`
- **认证方式**: Bearer Token
- **内容类型**: `application/json`

## 认证

所有 API 请求（除登录注册外）需要在 Header 中包含认证 Token：

```
Authorization: Bearer <your_token>
```

---

## 教师端 API

### 课程大纲管理

#### 生成课程大纲

```http
POST /teachpilot/outlines/generate
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "prompt": "我想为零基础学员设计一个 Python 入门课程，涵盖变量、数据类型、控制结构等基础知识",
  "subject": "computer_science",
  "target_audience": "Python 零基础初学者",
  "required_duration": 45,
  "reference_material_ids": []
}
```

**响应**:
```json
{
  "success": true,
  "outline_id": 1,
  "outline": {
    "id": 1,
    "title": "Python 编程入门：变量与数据类型",
    "chapters": [...],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 获取课程大纲列表

```http
GET /teachpilot/outlines?status=draft
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": 1,
    "title": "Python 编程入门",
    "subject": "computer_science",
    "status": "draft",
    "version": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 获取课程大纲详情

```http
GET /teachpilot/outlines/{outline_id}
Authorization: Bearer <token>
```

#### 更新课程大纲

```http
PUT /teachpilot/outlines/{outline_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "更新后的课程标题",
  "chapters": [...],
  "learning_objectives": ["目标 1", "目标 2"]
}
```

#### 删除课程大纲

```http
DELETE /teachpilot/outlines/{outline_id}
Authorization: Bearer <token>
```

### 课时管理

#### 创建课时

```http
POST /teachpilot/outlines/{outline_id}/lessons
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "课时标题",
  "order": 1,
  "objectives": ["目标 1", "目标 2"],
  "content": "教学内容",
  "activities": ["活动 1", "活动 2"],
  "assignments": ["作业 1"]
}
```

### 作业管理

#### 创建作业

```http
POST /teachpilot/assignments
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "lesson_id": 1,
  "title": "Python 变量练习",
  "description": "完成以下变量定义练习",
  "requirements": ["要求 1", "要求 2"],
  "rubric": {"correctness": 40, "style": 30},
  "max_score": 100,
  "due_date": "2024-01-15T23:59:59Z",
  "allowed_file_types": ["py", "txt", "pdf"]
}
```

#### 获取作业提交列表

```http
GET /teachpilot/assignments/{assignment_id}/submissions
Authorization: Bearer <token>
```

#### 批改作业

```http
POST /teachpilot/assignments/submissions/{submission_id}/grade
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "auto_grade": true
}
```

---

## 学生端 API

### 学习进度

#### 获取我的课程

```http
GET /teachpilot/progress/courses
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": 1,
    "title": "Python 编程入门",
    "subject": "computer_science",
    "progress_percentage": 68.5,
    "completed_lessons": 5,
    "total_lessons": 8,
    "enrolled_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 获取课程详细进度

```http
GET /teachpilot/progress/{course_id}
Authorization: Bearer <token>
```

#### 更新学习进度

```http
POST /teachpilot/progress/update
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "lesson_id": 1,
  "progress_percentage": 75.0,
  "status": "in_progress",
  "interaction_data": {
    "video_watched": true,
    "quiz_completed": true
  }
}
```

#### 获取学习统计

```http
GET /teachpilot/progress/stats
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_courses": 3,
  "completed_courses": 1,
  "total_time_seconds": 7200,
  "total_time_hours": 2.0,
  "average_score": 85.5,
  "total_lessons_progress": 15
}
```

### 作业提交

#### 提交作业

```http
POST /teachpilot/assignments/{assignment_id}/submit
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**表单字段**:
- `content`: 文本回答（可选）
- `files`: 文件 JSON 数组（可选）
- `code_snippet`: 代码片段（可选）
- `upload_files`: 上传的文件（可选）

**响应**:
```json
{
  "success": true,
  "submission_id": 1,
  "submitted_at": "2024-01-10T10:00:00Z"
}
```

#### 获取作业提交详情

```http
GET /teachpilot/assignments/submissions/{submission_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "assignment_id": 1,
  "assignment_title": "Python 变量练习",
  "content": "学生回答内容",
  "files": [...],
  "code_snippet": "print('Hello')",
  "status": "graded",
  "auto_grade": 85.0,
  "teacher_grade": 90.0,
  "feedback": "教师反馈",
  "ai_feedback": {
    "strengths": ["代码逻辑正确"],
    "weaknesses": ["缺少注释"],
    "suggestions": ["建议添加 docstring"]
  },
  "submitted_at": "2024-01-10T10:00:00Z",
  "graded_at": "2024-01-11T09:00:00Z"
}
```

---

## 错误响应

所有 API 错误返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见状态码**:

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 速率限制

| 端点 | 限制 |
|------|------|
| /api/v1/teachpilot/outlines/generate | 10 次/分钟 |
| /api/v1/teachpilot/assignments/*/submit | 5 次/分钟 |
| 其他 API | 100 次/分钟 |

---

## 示例代码

### Python 示例

```python
import requests

BASE_URL = "http://localhost:3000/api/v1"
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 生成课程大纲
response = requests.post(
    f"{BASE_URL}/teachpilot/outlines/generate",
    headers=headers,
    json={
        "prompt": "创建一个 Python 入门课程",
        "subject": "computer_science",
        "target_audience": "零基础学员",
        "required_duration": 45
    }
)

if response.ok:
    result = response.json()
    print(f"课程大纲生成成功！ID: {result['outline_id']}")
else:
    print(f"错误：{response.json()['detail']}")
```

### JavaScript 示例

```javascript
const BASE_URL = 'http://localhost:3000/api/v1';
const TOKEN = 'your_token_here';

async function generateOutline(prompt) {
  const response = await fetch(`${BASE_URL}/teachpilot/outlines/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: prompt,
      subject: 'computer_science',
      target_audience: '零基础学员',
      required_duration: 45
    })
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log(`课程大纲生成成功！ID: ${result.outline_id}`);
    return result;
  } else {
    const error = await response.json();
    console.error(`错误：${error.detail}`);
    throw new Error(error.detail);
  }
}
```
