import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import Layout from '../views/Layout.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Contracts from '../views/Contracts.vue'
import ContractCreate from '../views/ContractCreate.vue'
import ContractDetail from '../views/ContractDetail.vue'
import Changes from '../views/Changes.vue'
import Payments from '../views/Payments.vue'
import FinanceReview from '../views/FinanceReview.vue'
import LegalReview from '../views/LegalReview.vue'
import Quantity from '../views/Quantity.vue'
import Notifications from '../views/Notifications.vue'
import Audits from '../views/Audits.vue'

const routes = [
  { path: '/login', component: Login },
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', component: Notifications },
      { path: 'dashboard', component: Dashboard },

      { path: 'contracts', component: Contracts },
      { path: 'contracts/new', component: ContractCreate, meta: { roles: ['OWNER_CONTRACT','ADMIN'] } },
      { path: 'contracts/:id', component: ContractDetail },

      { path: 'changes', component: Changes },
      { path: 'payments', component: Payments },
      { path: 'finance', component: FinanceReview, meta: { roles: ['OWNER_FINANCE','OWNER_CONTRACT','OWNER_LEGAL','OWNER_LEADER','ADMIN'] } },
      { path: 'legal', component: LegalReview, meta: { roles: ['OWNER_LEGAL','ADMIN'] } },
      { path: 'quantity', component: Quantity, meta: { roles: ['SUPERVISOR','ADMIN'] } },

      { path: 'audits', component: Audits, meta: { roles: ['ADMIN','AUDITOR','OWNER_CONTRACT','OWNER_FINANCE','OWNER_LEGAL','OWNER_LEADER'] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.isAuthed) {
    return '/login'
  }
  if (auth.isAuthed && !auth.me) {
    await auth.fetchMe()
  }
  const roles = to.meta?.roles
  if (roles && roles.length && !roles.includes(auth.role)) {
    return '/' // 简化：无权限就回首页（通知页面）
  }
})

export default router
