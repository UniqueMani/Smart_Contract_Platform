<template>
  <div>
    <PageHeader title="审计日志" subtitle="关键操作留痕（合同、变更、支付、通知等）">
      <el-button size="small" @click="load">刷新</el-button>
    </PageHeader>
    <el-table :data="rows" border>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="actor" label="操作人" width="120" />
      <el-table-column prop="action" label="动作" width="100" />
      <el-table-column prop="entity_type" label="对象" width="120" />
      <el-table-column prop="entity_id" label="ID" width="80" />
      <el-table-column prop="detail" label="详情" />
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import PageHeader from '../components/PageHeader.vue'
import { formatDateTime } from '../utils/dateTime'
const rows = ref([])
async function load(){
  const { data } = await http.get('/audits')
  rows.value = data
}
onMounted(load)
</script>
