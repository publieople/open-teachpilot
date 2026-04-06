# TeachPilot - 多模态 AI 互动式教学智能体

> 服务外包大赛 A04 题目参赛作品 - 基于 Open WebUI 二次开发

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

## 项目简介

TeachPilot 是一个面向计算机学科 Python 入门教学的多模态 AI 互动式教学智能体。本项目基于 Open WebUI 进行深度定制化开发，旨在帮助教师高效完成课件设计与教学准备。

### 核心功能

- 🎯 **智能意图理解** - 通过多轮对话深度理解教师的教学目标、知识点、讲授逻辑
- 📚 **本地知识库 RAG** - 支持计算机学科资料的向量化存储与智能检索
- 📄 **多模态输入** - 支持语音/文字双输入方式，可上传 PDF、Word、PPT、图片、视频等参考资料
- 📑 **课件自动生成** - 根据教学意图自动生成 PPT 课件和 Word 教案
- 🔄 **迭代优化** - 支持基于反馈的课件修改和重新生成

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 20GB+ 可用磁盘空间

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url> open-teachpilot
cd open-teachpilot
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.teachpilot .env

# 编辑 .env 文件，填入您的 OpenRouter API Key
# OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
```

3. **启动服务**
```bash
# 使用 Docker Compose 启动
docker-compose -f docker-compose.teachpilot.yaml up -d

# 查看日志
docker-compose -f docker-compose.teachpilot.yaml logs -f
```

4. **访问应用**
打开浏览器访问：http://localhost:3000

### 默认配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 服务端口 | 3000 | 可通过 OPEN_WEBUI_PORT 修改 |
| 默认模型 | qwen/qwen3.6-plus:free | OpenRouter 提供的免费模型 |
| 知识库路径 | ./knowledge-base | 计算机学科资料目录 |

## 目录结构

```
open-teachpilot/
├── docker-compose.teachpilot.yaml  # Docker Compose 配置
├── .env.teachpilot                 # 环境变量模板
├── knowledge-base/                 # 知识库目录
│   ├── README.md
│   ├── python-basics/             # Python 入门资料
│   ├── data-structures/           # 数据结构资料
│   └── algorithms/                # 算法资料
├── src/                           # 前端源码 (SvelteKit)
│   ├── lib/
│   │   ├── constants.ts           # 应用常量（品牌化配置）
│   │   ├── components/            # UI 组件
│   │   └── i18n/                  # 国际化
│   └── routes/                    # 路由
├── backend/                       # 后端源码 (FastAPI)
│   └── open_webui/
│       ├── env.py                 # 环境配置
│       └── config.py              # 运行时配置
└── static/                        # 静态资源
    ├── favicon.png                # TeachPilot 图标
    └── splash.png                 # 启动画面
```

## 品牌化说明

本项目已完成以下品牌化改造：

- ✅ 应用名称：Open WebUI → TeachPilot
- ✅ 界面所有文本替换为 TeachPilot
- ✅ Logo 和 Favicon 使用 TeachPilot 标识
- ✅ 右下角保留 "Powered by Open WebUI" 标识

## 比赛要求对齐

| 比赛要求 | 实现状态 | 说明 |
|----------|----------|------|
| 本地知识库 RAG | ✅ 已实现 | ChromaDB + 计算机学科资料 |
| 语音/文字输入 | ✅ 已有 | Open WebUI 内置支持 |
| 多轮对话澄清 | ✅ 已有 | LLM 驱动对话 |
| 参考资料上传 | ✅ 已有 | 支持 PDF/Word/PPT/图片/视频 |
| 教学意图结构化 | 🔄 开发中 | Prompt Engineering |
| PPT 生成 | 🔄 开发中 | python-pptx 库 |
| Word 教案生成 | 🔄 开发中 | python-docx 库 |
| 迭代优化 | 🔄 开发中 | 对话式修改 |

## 开发指南

### 本地开发

```bash
# 安装依赖
npm install
pip install -r backend/requirements.txt

# 启动开发服务器
npm run dev
```

### Docker 开发

```bash
# 重新构建镜像
docker-compose -f docker-compose.teachpilot.yaml build

# 清理并重启
docker-compose -f docker-compose.teachpilot.yaml down
docker-compose -f docker-compose.teachpilot.yaml up -d
```

## 技术栈

- **前端**: SvelteKit, TypeScript, TailwindCSS
- **后端**: FastAPI, Python 3.11
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量库**: ChromaDB
- **AI 模型**: OpenRouter API (Qwen3.6-Plus)

## 许可证

本项目基于 MIT 许可证开源

## 致谢

- [Open WebUI](https://openwebui.com) - 提供基础框架
- 服务外包大赛 A04 题目 - 锐捷网络

---

**TeachPilot** - 让教学更智能，让备课更高效
