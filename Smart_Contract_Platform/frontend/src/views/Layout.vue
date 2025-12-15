<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true"></div>
        <div class="brand-title">
          <strong>政企工程合同平台</strong>
          <span>合规 · 变更 · 支付一体化（Demo）</span>
        </div>
      </div>

      <div class="user-card">
        <div class="u1">当前用户</div>
        <div class="u2">{{ auth.username || '-' }}</div>
        <div class="pill">角色：{{ auth.role || '-' }}</div>
      </div>

      <el-menu class="side-menu" :default-active="$route.path" router>
        <el-menu-item index="/">仪表盘</el-menu-item>
        <el-menu-item index="/contracts">合同</el-menu-item>
        <el-menu-item index="/changes">变更</el-menu-item>
        <el-menu-item index="/payments">进度款</el-menu-item>

        <el-menu-item v-if="['OWNER_FINANCE','OWNER_CONTRACT','ADMIN'].includes(auth.role)" index="/finance">
          审核（合同/财务）
        </el-menu-item>

        <el-menu-item v-if="['SUPERVISOR','ADMIN'].includes(auth.role)" index="/quantity">
          工程量/完工比例
        </el-menu-item>

        <el-menu-item index="/notifications">通知</el-menu-item>
        <el-menu-item v-if="['ADMIN','AUDITOR','OWNER_CONTRACT','OWNER_FINANCE','OWNER_LEGAL','OWNER_LEADER'].includes(auth.role)" index="/audits">
          审计日志
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button size="small" plain @click="logout">退出</el-button>
        <span class="muted">v0.1</span>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="hint">{{ auth.me?.company || '' }}</div>
      </header>
      <main class="content">
        <div class="page">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout(){
  auth.logout()
  router.push('/login')
}
</script>
