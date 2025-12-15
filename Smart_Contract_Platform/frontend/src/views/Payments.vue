<template>
  <div>
    <PageHeader title="进度款" subtitle="支付申请列表（超概算会在财务审核环节拦截）" />
    <el-table :data="rows" border>
      <el-table-column prop="code" label="单号" width="130" />
      <el-table-column prop="contract_id" label="合同ID" width="80" />
      <el-table-column prop="amount" label="金额" width="120" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="purpose" label="事由" />
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import PageHeader from '../components/PageHeader.vue'
const rows = ref([])
onMounted(async () => {
  const { data } = await http.get('/payments')
  rows.value = data
})
</script>
