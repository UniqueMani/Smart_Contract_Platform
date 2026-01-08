# 前端应用文档

[![Vue](https://img.shields.io/badge/Vue-3.0-4FC08D.svg)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg)](https://vitejs.dev/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-2.4-409EFF.svg)](https://element-plus.org/)

前端应用基于 Vue 3 + Vite 构建，使用 Element Plus 作为 UI 组件库。

## 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [功能模块](#功能模块)
- [开发指南](#开发指南)
- [构建部署](#构建部署)

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装步骤

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

# 3. 构建生产版本
npm run build

# 4. 预览生产构建
npm run preview
```

应用将在 `http://localhost:5173` 启动

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口
│   │   └── http.js       # HTTP客户端配置
│   ├── components/        # 公共组件
│   │   ├── ChangeList.vue      # 变更列表
│   │   ├── PaymentList.vue    # 支付列表
│   │   ├── QuantityList.vue   # 工程量列表
│   │   └── PageHeader.vue      # 页面头部
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── store/            # 状态管理
│   │   └── auth.js       # 认证状态
│   ├── styles/           # 样式文件
│   │   └── app.css       # 全局样式
│   ├── utils/            # 工具函数
│   │   └── dateTime.js   # 日期时间工具
│   ├── views/            # 页面视图
│   │   ├── Login.vue           # 登录页
│   │   ├── Layout.vue          # 布局页
│   │   ├── Dashboard.vue       # 仪表盘
│   │   ├── Contracts.vue      # 合同列表
│   │   ├── ContractCreate.vue # 创建合同
│   │   ├── ContractDetail.vue # 合同详情
│   │   ├── Changes.vue         # 变更管理
│   │   ├── Payments.vue        # 支付管理
│   │   ├── Quantity.vue        # 工程量管理
│   │   ├── LegalReview.vue     # 法务审核
│   │   ├── FinanceReview.vue   # 财务审核
│   │   ├── Notifications.vue   # 通知中心
│   │   └── Audits.vue          # 审计日志
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html            # HTML模板
├── vite.config.js        # Vite配置
└── package.json          # 项目配置
```

## 🛠 技术栈

### 核心框架

- **Vue 3**: 渐进式 JavaScript 框架
  - Composition API
  - `<script setup>` 语法
  - 响应式系统

### 构建工具

- **Vite**: 下一代前端构建工具
  - 快速热更新
  - 按需编译
  - 优化的生产构建

### UI组件库

- **Element Plus**: Vue 3 组件库
  - 丰富的组件
  - 完善的文档
  - 主题定制

### 状态管理

- **Pinia**: Vue 官方状态管理库
  - 类型安全
  - 开发工具支持
  - 模块化设计

### 路由

- **Vue Router**: Vue 官方路由
  - 路由守卫
  - 动态路由
  - 嵌套路由

### HTTP客户端

- **Axios**: Promise 基础的 HTTP 客户端
  - 请求/响应拦截器
  - 自动错误处理
  - 请求取消

## 功能模块

### 1. 认证模块

- 用户登录
- JWT Token 管理
- 路由守卫
- 自动登出

### 2. 合同管理

- 合同列表
- 合同创建
- 合同详情
- 合同编辑
- 合同审核
- AI智能审查

### 3. 变更管理

- 变更申请列表
- 变更申请创建
- 变更审批流程
- 审批历史查看

### 4. 支付管理

- 支付申请列表
- 支付申请创建
- 支付额度计算
- 支付审核

### 5. 工程量管理

- 完工比例录入
- 工程量历史记录
- 电子签章

### 6. 审核中心

- 法务审核
- 财务审核
- 变更审批

### 7. 通知中心

- 通知列表
- 通知详情
- 通知标记

### 8. 审计日志

- 日志查询
- 日志筛选
- 日志详情

## 开发指南

### 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### 代码规范

- 使用 ESLint 进行代码检查
- 遵循 Vue 3 最佳实践
- 组件命名使用 PascalCase
- 文件命名使用 PascalCase（组件）或 kebab-case（工具）

### 组件开发

#### 组件结构

```vue
<template>
  <!-- 模板 -->
</template>

<script setup>
// 导入
import { ref, computed } from 'vue'

// 定义 props
const props = defineProps({
  // ...
})

// 定义 emits
const emit = defineEmits(['update'])

// 响应式数据
const data = ref(null)

// 计算属性
const computedValue = computed(() => {
  // ...
})

// 方法
const handleClick = () => {
  // ...
}
</script>

<style scoped>
/* 样式 */
</style>
```

### API调用

使用封装的 HTTP 客户端：

```javascript
import http from '@/api/http'

// GET 请求
const { data } = await http.get('/api/contracts')

// POST 请求
const { data } = await http.post('/api/contracts', {
  name: '合同名称',
  // ...
})

// PUT 请求
await http.put(`/api/contracts/${id}`, {
  // ...
})

// DELETE 请求
await http.delete(`/api/contracts/${id}`)
```

### 状态管理

使用 Pinia store：

```javascript
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const user = auth.user
const isAuthenticated = auth.isAuthenticated
```

### 路由配置

路由定义在 `src/router/index.js`：

```javascript
{
  path: '/contracts',
  name: 'Contracts',
  component: () => import('@/views/Contracts.vue'),
  meta: {
    requiresAuth: true,
    roles: ['OWNER_CONTRACT', 'ADMIN']
  }
}
```

### 路由守卫

路由守卫在 `src/router/index.js` 中配置，自动检查：

- 用户认证状态
- 角色权限
- 路由访问权限

## 样式指南

### 使用 Element Plus 主题

Element Plus 支持主题定制，可在 `vite.config.js` 中配置：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/variables.scss" as *;`
      }
    }
  }
})
```

### 全局样式

全局样式定义在 `src/styles/app.css` 中。

## 构建部署

### 开发构建

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 部署到 Nginx

1. 构建生产版本

```bash
npm run build
```

2. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 环境变量

创建 `.env.production` 文件：

```env
VITE_API_BASE_URL=https://api.example.com
```

## 相关文档

- [Vue 3 文档](https://vuejs.org/)
- [Vite 文档](https://vitejs.dev/)
- [Element Plus 文档](https://element-plus.org/)
- [Vue Router 文档](https://router.vuejs.org/)
- [Pinia 文档](https://pinia.vuejs.org/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
