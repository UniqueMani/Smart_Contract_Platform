# 后端服务文档

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)

后端服务基于 FastAPI 构建，提供 RESTful API 接口和 AI 智能审查功能。

## 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [环境配置](#环境配置)
- [数据库](#数据库)
- [API接口](#api接口)
- [AI智能审查](#ai智能审查)
- [角色权限](#角色权限)
- [测试账号](#测试账号)
- [开发指南](#开发指南)
- [部署](#部署)

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装步骤

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入配置信息

# 5. 初始化数据库
python -m app.db.init_db

# 6. 初始化AI知识库（可选）
python scripts/init_knowledge_base.py

# 7. 启动服务
uvicorn app.main:app --reload --port 8000
```

服务将在 `http://localhost:8000` 启动

## 项目结构

```
backend/
├── app/
│   ├── api/                 # API路由
│   │   ├── routers/         # 路由模块
│   │   │   ├── auth.py      # 认证
│   │   │   ├── contracts.py # 合同管理
│   │   │   ├── changes.py   # 变更管理
│   │   │   ├── payments.py   # 支付管理
│   │   │   ├── quantities.py # 工程量管理
│   │   │   ├── ai_review.py  # AI审查
│   │   │   └── ...
│   │   └── api.py           # 路由聚合
│   ├── core/                # 核心配置
│   │   ├── config.py        # 配置管理
│   │   ├── deps.py          # 依赖注入
│   │   └── security.py      # 安全相关
│   ├── crud/                # CRUD操作
│   │   ├── crud_contract.py
│   │   ├── crud_change.py
│   │   └── ...
│   ├── db/                  # 数据库
│   │   ├── base.py          # 基础模型
│   │   ├── session.py       # 数据库会话
│   │   └── init_db.py       # 初始化脚本
│   ├── models/              # 数据模型
│   │   ├── contract.py
│   │   ├── change.py
│   │   └── ...
│   ├── schemas/             # Pydantic模式
│   │   ├── contract.py
│   │   ├── change.py
│   │   └── ...
│   ├── services/            # 业务服务
│   │   ├── workflow.py      # 审批流程
│   │   ├── rules.py         # 业务规则
│   │   ├── rag_service.py   # RAG服务
│   │   └── ai_review.py     # AI审查服务
│   └── main.py              # 应用入口
├── knowledge_base/          # AI知识库
│   ├── pdfs/               # PDF文档
│   └── chroma_db/          # 向量数据库
├── scripts/                # 工具脚本
│   └── init_knowledge_base.py
├── requirements.txt        # Python依赖
└── .env                    # 环境变量（需创建）
```

## 环境配置

### 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# 应用配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXP_MINUTES=1440

# 数据库配置
SQLALCHEMY_DATABASE_URI=sqlite:///./demo.db

# DeepSeek API配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# RAG知识库配置
KNOWLEDGE_BASE_DIR=knowledge_base
CHROMA_DB_PATH=knowledge_base/chroma_db
PDFS_DIR=knowledge_base/pdfs
```

### 配置说明

- `SECRET_KEY`: JWT 令牌签名密钥（生产环境请使用强随机字符串）
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（用于 AI 审查功能）
- `SQLALCHEMY_DATABASE_URI`: 数据库连接字符串

## 🗄️ 数据库

### 数据库模型

主要数据模型：

- **User**: 用户信息
- **Contract**: 合同信息
- **ChangeRequest**: 变更申请
- **ChangeApprovalTask**: 变更审批任务
- **PaymentRequest**: 支付申请
- **Quantity**: 工程量记录
- **Notification**: 通知
- **AuditLog**: 审计日志

### 数据库初始化

```bash
# 初始化数据库（创建表结构和初始数据）
python -m app.db.init_db
```

### 数据库迁移

生产环境建议使用 PostgreSQL，迁移步骤：

1. 安装 PostgreSQL
2. 创建数据库
3. 修改 `config.py` 中的数据库连接字符串
4. 运行初始化脚本

## API接口

### 认证接口

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

### 合同管理

- `GET /api/contracts` - 获取合同列表
- `POST /api/contracts` - 创建合同
- `GET /api/contracts/{id}` - 获取合同详情
- `PUT /api/contracts/{id}` - 更新合同
- `POST /api/contracts/{id}/submit` - 提交合同审核
- `POST /api/contracts/{id}/legal-approve` - 法务审核通过
- `POST /api/contracts/{id}/legal-reject` - 法务审核驳回
- `POST /api/contracts/{id}/ai-review` - AI合同审查

### 变更管理

- `GET /api/changes` - 获取变更申请列表
- `POST /api/changes` - 创建变更申请
- `GET /api/changes/tasks` - 获取待审批任务
- `POST /api/changes/tasks/{id}/approve` - 审批通过
- `POST /api/changes/tasks/{id}/reject` - 审批驳回

### 支付管理

- `GET /api/payments` - 获取支付申请列表
- `POST /api/payments` - 创建支付申请
- `GET /api/payments/{id}/quota` - 获取支付额度
- `POST /api/payments/{id}/finance-approve` - 财务审核通过
- `POST /api/payments/{id}/finance-reject` - 财务审核驳回

### 工程量管理

- `GET /api/quantities` - 获取工程量记录
- `POST /api/quantities` - 创建工程量记录

### 其他接口

- `GET /api/notifications` - 获取通知列表
- `GET /api/audits` - 获取审计日志
- `GET /api/dashboard` - 获取仪表盘数据

详细API文档请访问：http://localhost:8000/docs

## AI智能审查

### 功能说明

AI合同审查功能基于 RAG（检索增强生成）技术，能够：

- 从法律文档知识库中检索相关条款
- 使用 DeepSeek API 进行智能分析
- 识别合同条款中的问题和风险
- 提供合规性评分和改进建议

### 使用步骤

1. **配置 API Key**

   在 `.env` 文件中配置 `DEEPSEEK_API_KEY`

2. **初始化知识库**

   ```bash
   python scripts/init_knowledge_base.py
   ```

3. **调用 API**

   ```bash
   POST /api/contracts/{contract_id}/ai-review
   ```

详细说明请参考 [AI审查功能使用说明](./AI审查功能使用说明.md)

## 角色权限

### 角色定义

| 角色 | 代码 | 权限说明 |
|------|------|----------|
| 合同管理员 | `OWNER_CONTRACT` | 创建合同、提交审核 |
| 法务 | `OWNER_LEGAL` | 审核合同 |
| 财务 | `OWNER_FINANCE` | 审核支付申请 |
| 领导 | `OWNER_LEADER` | 审批变更申请（按级别） |
| 科员 | `OWNER_STAFF` | 审批变更申请（第一步） |
| 承包方 | `CONTRACTOR` | 提交变更申请、支付申请 |
| 监理 | `SUPERVISOR` | 录入完工比例 |
| 审计 | `AUDITOR` | 查看审计日志 |
| 管理员 | `ADMIN` | 所有权限 |

### 权限控制

权限控制通过 `require_roles` 装饰器实现：

```python
from app.core.deps import require_roles

@router.post("/contracts")
@require_roles("OWNER_CONTRACT")
def create_contract(...):
    ...
```

## 测试账号

### 发包方角色

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| `owner_contract` | `Owner123!` | 合同管理员 | 可创建合同 |
| `owner_legal` | `Legal123!` | 法务 | 可审核合同 |
| `owner_finance` | `Finance123!` | 财务 | 可审核支付 |
| `owner_leader` | `Leader123!` | 局长 | 可审核所有变更 |
| `owner_leader_director` | `Director123!` | 处长 | 可审核≤100万变更 |
| `owner_leader_section` | `Section123!` | 科长 | 可审核≤20万变更 |
| `owner_staff` | `Staff123!` | 科员 | 变更审批第一步 |

### 其他角色

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| `contractor` | `Contractor123!` | 承包方 | 可提交变更和支付申请 |
| `supervisor` | `Supervisor123!` | 监理 | 可录入完工比例 |
| `auditor` | `Auditor123!` | 审计 | 可查看审计日志 |
| `admin` | `Admin123!` | 管理员 | 所有权限 |

## 开发指南

### 代码结构

项目采用 MVC 架构：

- **Models** (`app/models/`): 数据模型定义
- **Schemas** (`app/schemas/`): 数据验证和序列化
- **Routers** (`app/api/routers/`): API 路由处理
- **CRUD** (`app/crud/`): 数据库操作
- **Services** (`app/services/`): 业务逻辑

### 添加新功能

1. **定义数据模型** (`app/models/`)
2. **定义 Schema** (`app/schemas/`)
3. **实现 CRUD** (`app/crud/`)
4. **创建路由** (`app/api/routers/`)
5. **注册路由** (`app/api/api.py`)

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示
- 编写文档字符串
- 添加适当的错误处理

## 部署

### 开发环境

```bash
uvicorn app.main:app --reload --port 8000
```

### 生产环境

推荐使用 Gunicorn + Uvicorn：

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量

生产环境请确保设置：

- `SECRET_KEY`: 强随机字符串
- `SQLALCHEMY_DATABASE_URI`: 生产数据库连接
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥

## 相关文档

- [AI审查功能使用说明](./AI审查功能使用说明.md)
- [知识库文档](./knowledge_base/README.md)
- [脚本文档](./scripts/README.md)

## 贡献

欢迎提交 Issue 和 Pull Request！
