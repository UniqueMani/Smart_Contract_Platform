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

### 发包方角色
- **科员**： `owner_staff` / `Staff123!` - 变更申请审批流程第一步（所有金额都需要科员审核）
- **发包方合同管理员**： `owner_contract` / `Owner123!` - **唯一有权限创建合同**的角色，创建合同后提交给法务审核
- **发包方财务**： `owner_finance` / `Finance123!` - 负责财务审核和支付
- **发包方法务**： `owner_legal` / `Legal123!` - 审核合同，审核通过后合同变为 ACTIVE 状态
- **发包方领导（局长）**： `owner_leader` / `Leader123!` - 局长级别，可审核所有金额的变更申请
- **发包方领导（处长）**： `owner_leader_director` / `Director123!` - 处长级别，可审核≤100万元的变更申请
- **发包方领导（科长）**： `owner_leader_section` / `Section123!` - 科长级别，可审核≤20万元的变更申请

### 其他角色
- **承包方**： `contractor` / `Contractor123!` - 可提交变更申请和进度款申请
- **监理**： `supervisor` / `Supervisor123!` - 可录入完工比例
- **审计**： `auditor` / `Auditor123!` - 可查看审计日志
- **系统管理员**： `admin` / `Admin123!` - 拥有所有权限

### 变更申请审批规则（按金额分级）
- **≤5万元**：科员审核 → 科长审核
- **5-20万元**：科员审核 → 科长审核 → 处长审核
- **20-100万元**：科员审核 → 科长审核 → 处长审核 → 局长审核
- **>100万元**：科员审核 → 科长审核 → 处长审核 → 局长审核 → 特批

> **测试建议**：
> - 使用 `contractor` 账号提交不同金额的变更申请（如3万、15万、50万、150万）
> - 使用不同级别的领导账号登录，在"审核（合同/财务）"页面的"变更申请审核"标签页查看和审核
> - 只有符合职级要求的领导才能看到并审核对应的变更申请

## 核心功能

### 1. 合同管理流程
- **合同创建**：只有 `OWNER_CONTRACT` 角色（合同管理员）可以创建合同
- **合同提交**：合同管理员创建合同后，提交给法务审核（状态变为 APPROVING）
- **法务审核**：法务可以审核通过（合同变为 ACTIVE）或驳回（退回 DRAFT 状态）
- **合同生效**：只有法务审核通过后，合同才变为 ACTIVE 状态，才能进行后续的变更和支付操作

### 2. 变更申请分级审批
- 系统根据变更金额自动匹配审批层级
- 不同职级的领导只能看到和审核符合其权限范围的变更申请
- 审批流程：科员 → 科长 → 处长 → 局长 → 特批（根据金额）

### 3. 审核界面
- 在"审核（合同/财务）"页面新增"变更申请审核"标签页
- 显示待审核的变更申请列表，包括：
  - 变更单号、合同ID、金额、变更原因
  - 当前审核步骤（科员/科长/处长/局长/特批）
  - 所需级别要求
- 支持审核通过和驳回操作，可填写审核意见

### 4. 首页通知
- 登录后首页显示通知列表
- 关键节点提醒（审批流转、支付结果、超概算拦截等）

## 目录结构（MVC 思路）
- backend/app/models：Model（SQLAlchemy ORM）
- backend/app/api/routers：Controller（路由/接口）
- backend/app/services：Service（业务规则/流程/校验）
- frontend/src/views：View（页面）
- frontend/src/components：Component（组件）

## 测试流程示例

1. **合同创建和审核**：
   - 使用 `owner_contract` 账号登录，创建新合同（只有这个角色可以创建）
   - 创建后点击"提交给法务审核"，合同状态变为 APPROVING
   - 使用 `owner_legal` 账号登录，在合同详情页可以看到"法务审核通过"和"法务驳回"按钮
   - 法务审核通过后，合同状态变为 ACTIVE，才能进行后续操作

2. **提交变更申请**：
   - 使用 `contractor` 账号登录
   - 进入合同详情页的"变更"标签，创建变更申请（选择不同金额测试不同审批流程）

3. **审核变更申请**：
   - 使用 `owner_staff` 账号登录，审核科员级别的变更申请（审批流程第一步）
   - 使用 `owner_leader_section` 账号登录，审核科长级别的变更申请
   - 使用 `owner_leader_director` 账号登录，审核处长级别的变更申请
   - 使用 `owner_leader` 账号登录，审核局长级别的变更申请

4. **查看通知**：
   - 各角色登录后，在首页查看相关通知信息
