# 政企工程合同合规变更与支付一体化智慧管理平台 — Demo（Vue3 + Python/FastAPI）

这是一个**可运行的 demo**，用于演示你们规格说明书里的核心流程闭环：
- 合同起草：模板选择/自动填充（合同价=中标价、履约保证金=中标价×10%）、保存草稿、合规校验（demo 版为规则模拟）
- 变更：承包方提交变更申请，按金额自动匹配审批层级并流转（demo 内置默认规则）
- 支付：承包方提交进度款支付申请；系统按 **可支付额度 = 批复概算 × 完工比例** 计算，并在财务审核时执行**超额拦截**，生成预警与通知
- 工程量：监理录入“完工比例”，用于支付额度计算
- RBAC：多角色登录，不同角色看到不同菜单；后端接口也做权限校验
- 审计日志：关键操作留痕

> 技术栈：
- 前端：Vue 3 + Vite + Pinia + Vue Router + Element Plus + Axios
- 后端：FastAPI + SQLAlchemy + SQLite + JWT

## 运行方式

### 1) 启动后端
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

访问：
- Swagger 文档： http://localhost:8000/docs

### 2) 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问：
- 前端： http://localhost:5173

## 预置账号（密码均满足>=8位）
- 发包方合同： owner_contract / Owner123!
- 发包方财务： owner_finance / Finance123!
- 发包方法务： owner_legal / Legal123!
- 发包方领导： owner_leader / Leader123!
- 承包方： contractor / Contractor123!
- 监理： supervisor / Supervisor123!
- 审计： auditor / Auditor123!
- 系统管理员： admin / Admin123!

## 目录结构（MVC 思路）
- backend/app/models：Model（SQLAlchemy ORM）
- backend/app/api/routers：Controller（路由/接口）
- backend/app/services：Service（业务规则/流程/校验）
- frontend/src/views：View（页面）
- frontend/src/components：Component（组件）
