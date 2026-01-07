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
      <el-table-column prop="completion_description" label="完工情况描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="note" label="备注" />
      <el-table-column prop="created_by" label="录入人" width="120" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="签章状态" width="150">
        <template #default="{ row }">
          <div v-if="row.sealed">
            <el-tag type="success" size="small">已签章</el-tag>
            <div style="font-size: 12px; color: #909399; margin-top: 4px;">
              {{ row.sealed_by }}<br/>
              {{ formatDateTime(row.sealed_at) }}
            </div>
          </div>
          <el-tag v-else type="info" size="small">未签章</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="openCreate" title="录入完工比例" width="600px">
      <el-form ref="formRef" :model="form" label-position="top" :rules="rules">
        <el-form-item label="期次" prop="period">
          <el-input v-model="form.period" />
        </el-form-item>
        <el-form-item label="完工比例（0~1）" prop="completion_ratio">
          <el-input-number v-model="form.completion_ratio" :min="0" :max="1" :step="0.01" style="width:100%;" />
        </el-form-item>
        <el-form-item label="完工情况描述" prop="completion_description">
          <el-input 
            v-model="form.completion_description" 
            type="textarea" 
            :rows="4" 
            placeholder="请详细描述当前进度的实际完成情况"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" />
        </el-form-item>
        <el-divider />
        <el-form-item label="电子签章确认" prop="seal_password">
          <el-alert type="info" :closable="false" style="margin-bottom: 12px;">
            请输入您的密码进行电子签章确认
          </el-alert>
          <el-input 
            v-model="form.seal_password" 
            type="password" 
            placeholder="请输入您的密码"
            show-password
          />
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
import { formatDateTime } from '../utils/dateTime'

const props = defineProps({ contractId: Number })
const auth = useAuthStore()

const rows = ref([])
const openCreate = ref(false)
const loading = ref(false)
const formRef = ref(null)
const form = reactive({ 
  period: '2025-12', 
  completion_ratio: 0.4, 
  completion_description: '',
  note: '月度计量确认',
  seal_password: ''
})

const rules = {
  period: [{ required: true, message: '请输入期次', trigger: 'blur' }],
  completion_ratio: [{ required: true, message: '请输入完工比例', trigger: 'blur' }],
  completion_description: [{ required: true, message: '请输入完工情况描述', trigger: 'blur' }],
  seal_password: [{ required: true, message: '请输入签章密码', trigger: 'blur' }]
}

async function load(){
  const { data } = await http.get('/quantities/contract/' + props.contractId)
  rows.value = data
}

async function create(){
  // 表单验证
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try{
    loading.value = true
    const response = await http.post('/quantities', { ...form, contract_id: props.contractId })
    // 检查响应状态码和数据（axios 成功响应会自动返回 response 对象）
    if (response && response.data) {
      ElMessage.success('已录入')
      openCreate.value = false
      // 重置表单
      form.period = '2025-12'
      form.completion_ratio = 0.4
      form.completion_description = ''
      form.note = '月度计量确认'
      form.seal_password = ''
      await load()
    } else {
      ElMessage.error('提交失败：响应格式异常')
    }
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
