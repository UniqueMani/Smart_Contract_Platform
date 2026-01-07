<template>
  <div>
    <PageHeader title="合同审核" subtitle="法务审核待审核的合同，审核通过后合同生效" />

    <el-table :data="rows" border>
      <el-table-column prop="contract_no" label="合同号" width="140" />
      <el-table-column prop="contract_name" label="合同名称" />
      <el-table-column prop="project_name" label="项目名称" />
      <el-table-column prop="contractor_org" label="承包方" width="140" />
      <el-table-column prop="tender_price" label="中标价" width="120">
        <template #default="{ row }">
          {{ row.tender_price.toLocaleString() }} 元
        </template>
      </el-table-column>
      <el-table-column prop="contract_price" label="合同价" width="120">
        <template #default="{ row }">
          {{ row.contract_price.toLocaleString() }} 元
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="created_at" label="提交时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push('/contracts/' + row.id)">查看详情</el-button>
          <el-button size="small" type="success" @click="approve(row)">审核通过</el-button>
          <el-button size="small" type="danger" @click="reject(row)">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'
import { useRouter } from 'vue-router'
import { formatDateTime } from '../utils/dateTime'

const auth = useAuthStore()
const router = useRouter()
const rows = ref([])

async function load(){
  try {
    const { data } = await http.get('/contracts/pending/legal')
    rows.value = data
  } catch (error) {
    ElMessage.error('加载失败')
    console.error('加载待审核合同失败:', error)
  }
}

async function approve(row){
  try {
    await http.post(`/contracts/${row.id}/review/legal`)
    ElMessage.success('审核通过，合同已生效')
    await load()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '审核失败')
  }
}

async function reject(row){
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '法务驳回', { 
      inputPlaceholder: '如：合同条款不符合规范要求',
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消'
    })
    await http.post(`/contracts/${row.id}/reject/legal`, { reason: value })
    ElMessage.success('已驳回，合同已退回草稿状态')
    await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || '驳回失败')
    }
  }
}

onMounted(load)
</script>

