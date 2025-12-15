<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-head">
        <div class="mark" aria-hidden="true"></div>
        <div>
          <h1>政企工程合同平台（Demo）</h1>
          <p>合规审查 · 变更分级审批 · 进度款支付控制</p>
        </div>
      </div>

      <el-form label-position="top" style="padding: 10px 14px 14px;" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" autocomplete="current-password" />
        </el-form-item>

        <el-button type="primary" :loading="loading" style="width:100%;" @click="doLogin">
          登录
        </el-button>

        <div class="muted" style="margin-top: 10px;">
          预置账号见根目录 README.md（建议先用 owner_contract / Owner123!）
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const username = ref('owner_contract')
const password = ref('Owner123!')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function doLogin(){
  try{
    loading.value = true
    await auth.login(username.value, password.value)
    router.push('/')
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  }finally{
    loading.value = false
  }
}
</script>
