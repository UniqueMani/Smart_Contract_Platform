# 政企工程合同合规变更与支付一体化智慧管理平台

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0-4FC08D.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于 Vue3 + FastAPI 的政企工程合同管理平台，提供合同起草、变更审批、支付管理、AI智能审查等核心功能。

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [核心功能](#核心功能)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

### 核心业务功能

- **📝 合同管理**
  - 合同创建、编辑、审核
  - 合同状态流转（草稿 → 审核中 → 生效）
  - 合同详情查看和条款管理
  - AI智能合同审查

- **🔄 变更管理**
  - 变更申请提交
  - 多级审批流程（按金额和工期自动匹配审批层级）
  - 变更审批历史追踪
  - 合同价格和工期自动更新

- **💰 支付管理**
  - 进度款支付申请
  - 支付额度自动计算（批复概算 × 完工比例）
  - 超额拦截和预警
  - 支付审核流程

- **📊 工程量管理**
  - 完工比例录入
  - 电子签章确认
  - 工程量历史记录

- **🔔 通知系统**
  - 实时通知推送
  - 角色化通知过滤
  - 审批流转提醒

- **📜 审计日志**
  - 关键操作记录
  - 操作历史查询
  - 审计追踪

### AI智能审查

- **🤖 RAG增强的合同审查**
  - 基于法律文档知识库的智能检索
  - DeepSeek API驱动的条款分析
  - 合规性评分和问题识别
  - 改进建议生成

## 🛠 技术栈

### 后端

- **框架**: FastAPI 0.115.6
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT (python-jose)
- **AI服务**: 
  - DeepSeek API (合同审查)
  - ChromaDB (向量数据库)
  - LangChain (RAG框架)
  - Sentence Transformers (文本嵌入)

### 前端

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI组件**: Element Plus
- **HTTP客户端**: Axios

## 📁 项目结构

```
Smart_Contract_Platform/
├── backend/                 # 后端服务
│   ├── app/                # 应用主目录
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── crud/           # CRUD操作
│   │   ├── db/             # 数据库配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   └── services/       # 业务服务
│   ├── knowledge_base/     # AI知识库
│   ├── scripts/            # 工具脚本
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由配置
│   │   ├── store/         # 状态管理
│   │   └── views/         # 页面视图
│   └── package.json       # 前端依赖
└── README.md              # 项目说明
```

详细结构说明请参考：
- [后端文档](./backend/README.md)
- [前端文档](./frontend/README.md)

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/Smart_Contract_Platform.git
cd Smart_Contract_Platform
```

#### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DeepSeek API Key

# 初始化数据库
python -m app.db.init_db

# 初始化AI知识库（可选）
python scripts/init_knowledge_base.py

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端服务将在 `http://localhost:8000` 启动

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

### 访问系统

- **前端应用**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **API交互式文档**: http://localhost:8000/redoc

## 🏗 系统架构

```
┌─────────────────┐
│   前端 (Vue3)   │
│  Element Plus   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  后端 (FastAPI) │
│   JWT认证       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│SQLite │ │ChromaDB │
│数据库  │ │向量数据库│
└───────┘ └─────────┘
              │
         ┌────▼────┐
         │DeepSeek │
         │  API    │
         └─────────┘
```

## 📖 核心功能

### 1. 合同管理

- 合同创建（仅合同管理员）
- 法务审核流程
- 合同状态管理
- AI智能审查

### 2. 变更审批

- 自动匹配审批层级
- 多级审批流程
- 金额和时间双重审批规则
- 审批历史追踪

### 3. 支付管理

- 支付额度自动计算
- 超额拦截机制
- 支付审核流程
- 支付历史记录

### 4. 角色权限

系统支持以下角色：

- **发包方**: 合同管理员、财务、法务、领导（局长/处长/科长）、科员
- **承包方**: 承包商
- **监理**: 监理单位
- **审计**: 审计人员
- **系统管理员**: 系统管理员

详细角色权限请参考 [后端文档](./backend/README.md#角色权限)

## 📚 API文档

API文档通过 Swagger UI 自动生成：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要API端点：

- `/api/auth/*` - 认证相关
- `/api/contracts/*` - 合同管理
- `/api/changes/*` - 变更管理
- `/api/payments/*` - 支付管理
- `/api/quantities/*` - 工程量管理
- `/api/contracts/{id}/ai-review` - AI合同审查

## 🧪 测试账号

系统预置了多个测试账号，详见 [测试账号说明](./backend/README.md#测试账号)

## 🔧 开发指南

### 代码规范

- **Python**: 遵循 PEP 8
- **JavaScript/Vue**: 遵循 ESLint 规则
- **提交信息**: 使用约定式提交格式

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📦 部署指南

### 开发环境

参考 [快速开始](#快速开始) 部分

### 生产环境

详细部署指南请参考：

- [后端部署文档](./backend/README.md#部署)
- [服务器部署指南](./docs/deployment.md) (待补充)

推荐配置：

- **操作系统**: Ubuntu 22.04 LTS
- **Web服务器**: Nginx
- **应用服务器**: Gunicorn/Uvicorn
- **数据库**: PostgreSQL
- **进程管理**: Supervisor

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [DeepSeek](https://www.deepseek.com/) - AI 服务提供商
- [ChromaDB](https://www.trychroma.com/) - 向量数据库

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
