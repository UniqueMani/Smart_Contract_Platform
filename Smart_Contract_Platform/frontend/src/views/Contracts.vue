<template>
  <div>
    <PageHeader title="合同" subtitle="合同台账（含批复概算、完工比例、已支付汇总）">
      <el-button v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role)" type="primary" @click="$router.push('/contracts/new')">
        新建合同
      </el-button>
    </PageHeader>

    <div style="margin-bottom: 16px;">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索合同名称或合同号"
        clearable
        style="width: 300px;"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <el-table :data="rows" border style="width:100%;">
      <el-table-column prop="contract_no" label="合同号" width="140" />
      <el-table-column prop="contract_name" label="合同名称" />
      <el-table-column prop="contractor_org" label="承包方" width="140" />
      <el-table-column prop="approved_budget" label="批复概算" width="120" />
      <el-table-column prop="completion_ratio" label="完工比例" width="100" />
      <el-table-column prop="paid_total" label="已支付" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push('/contracts/'+row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const auth = useAuthStore()
const rows = ref([])
const searchKeyword = ref('')

async function load(){
  try{
    const params = {}
    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim()
    }
    const { data } = await http.get('/contracts', { params })
    rows.value = data
  }catch(e){
    ElMessage.error('加载失败')
  }
}

function handleSearch() {
  load()
}

onMounted(load)
</script>
