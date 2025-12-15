<template>
  <div>
    <PageHeader
      title="仪表盘"
      subtitle="合同起草、变更分级审批、进度款额度计算与超概算拦截的演示总览"
    />
    <el-alert type="info" show-icon :closable="false">
      这是一个演示 demo：合同起草、变更审批分级、进度款额度计算与超额拦截、通知与审计留痕。
    </el-alert>

    <div class="grid-cards">
      <el-card>
        <h3 style="margin:0 0 8px;">快速开始</h3>
        <ol style="margin:0; padding-left: 18px; line-height: 1.9;">
          <li>合同管理员：新建合同 → 提交</li>
          <li>承包方：提交变更/进度款申请</li>
          <li>监理：录入完工比例</li>
          <li>财务：审核支付（超额会拦截）</li>
        </ol>
      </el-card>

      <el-card>
        <h3 style="margin:0 0 8px;">当前用户</h3>
        <div>username: {{ auth.username }}</div>
        <div>role: {{ auth.role }}</div>
        <div>company: {{ auth.me?.company || '-' }}</div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import PageHeader from '../components/PageHeader.vue'
const auth = useAuthStore()
</script>
