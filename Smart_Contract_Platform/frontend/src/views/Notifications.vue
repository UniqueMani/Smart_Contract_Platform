<template>
  <div>
    <PageHeader title="首页通知" subtitle="关键节点提醒（审批流转、支付结果、超概算拦截等）">
      <el-button size="small" @click="load">刷新</el-button>
    </PageHeader>

    <el-table :data="rows" border>
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column prop="title" label="标题" width="220" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="is_read" label="已读" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_read" type="success">是</el-tag>
          <el-tag v-else type="warning">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button v-if="!row.is_read" size="small" @click="read(row)">标为已读</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

const rows = ref([])

async function load(){
  const { data } = await http.get('/notifications')
  rows.value = data
}
async function read(row){
  await http.post(`/notifications/${row.id}/read`)
  ElMessage.success('已读')
  await load()
}
onMounted(load)
</script>
