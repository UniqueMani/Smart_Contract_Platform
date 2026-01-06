<template>
  <div>
    <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:8px;">
      <div />
      <el-button v-if="['SUPERVISOR','ADMIN'].includes(auth.role)" size="small" type="primary" @click="openCreate = true">
        录入完工比例
      </el-button>
    </div>

    <el-table :data="rows" border>
      <el-table-column prop="period" label="期次" width="120" />
      <el-table-column prop="completion_ratio" label="完工比例" width="120" />
      <el-table-column prop="note" label="备注" />
      <el-table-column prop="created_by" label="录入人" width="120" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <el-dialog v-model="openCreate" title="录入完工比例" width="600px">
      <el-form label-position="top">
        <el-form-item label="期次">
          <el-input v-model="form.period" />
        </el-form-item>
        <el-form-item label="完工比例（0~1）">
          <el-input-number v-model="form.completion_ratio" :min="0" :max="1" :step="0.01" style="width:100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="openCreate=false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="create">提交</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { onMounted, ref, reactive, watch } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'

const props = defineProps({ contractId: Number })
const auth = useAuthStore()

const rows = ref([])
const openCreate = ref(false)
const loading = ref(false)
const form = reactive({ period: '2025-12', completion_ratio: 0.4, note: '月度计量确认' })

async function load(){
  const { data } = await http.get('/quantities/contract/' + props.contractId)
  rows.value = data
}

async function create(){
  try{
    loading.value = true
    await http.post('/quantities', { ...form, contract_id: props.contractId })
    ElMessage.success('已录入')
    openCreate.value = false
    await load()
  }catch(e){
    // 提取详细的错误信息
    let errorMsg = '提交失败'
    if (e?.response?.data?.detail) {
      errorMsg = e.response.data.detail
    } else if (e?.response?.data?.message) {
      errorMsg = e.response.data.message
    } else if (e?.message) {
      errorMsg = e.message
    } else if (typeof e?.response?.data === 'string') {
      errorMsg = e.response.data
    }
    ElMessage.error(errorMsg)
    console.error('录入完工比例失败:', e)
  }finally{
    loading.value = false
  }
}

onMounted(load)
watch(() => props.contractId, load)
</script>
