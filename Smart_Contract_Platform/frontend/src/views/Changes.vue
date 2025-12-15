<template>
  <div>
    <PageHeader title="变更" subtitle="变更单列表（含分级审批结果，demo 为汇总展示）" />
    <el-table :data="rows" border>
      <el-table-column prop="code" label="编号" width="130" />
      <el-table-column prop="contract_id" label="合同ID" width="80" />
      <el-table-column prop="amount" label="金额" width="120" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="reason" label="原因" />
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import PageHeader from '../components/PageHeader.vue'
const rows = ref([])
onMounted(async () => {
  const { data } = await http.get('/changes')
  rows.value = data
})
</script>
