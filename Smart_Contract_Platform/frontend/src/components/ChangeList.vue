<template>
  <div>
    <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:8px;">
      <div />
      <el-button v-if="['CONTRACTOR','ADMIN'].includes(auth.role)" size="small" type="primary" @click="openCreate = true">
        发起变更
      </el-button>
    </div>

    <el-table :data="rows" border>
      <el-table-column prop="code" label="编号" width="130" />
      <el-table-column prop="amount" label="金额" width="120" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="reason" label="原因" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="viewTasks(row)">审批流</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="openCreate" title="发起变更" width="600px">
      <el-form label-position="top">
        <el-form-item label="变更金额（元）">
          <el-input-number v-model="form.amount" :min="0" style="width:100%;" />
        </el-form-item>
        <el-form-item label="变更原因">
          <el-input v-model="form.reason" />
        </el-form-item>
        <el-form-item label="范围描述">
          <el-input v-model="form.scope_desc" />
        </el-form-item>
        <el-form-item label="工期影响（天）">
          <el-input-number v-model="form.schedule_impact_days" :min="0" style="width:100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="openCreate=false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="create">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="openTasks" title="变更审批任务" width="700px">
      <el-table :data="tasks" border>
        <el-table-column prop="step_order" label="顺序" width="60" />
        <el-table-column prop="step_name" label="节点" width="120">
          <template #default="{ row }">
            {{ row.step_name === '科员' ? '合同管理员' : row.step_name }}
          </template>
        </el-table-column>
        <el-table-column prop="assignee_role" label="角色" width="140" />
        <el-table-column prop="status" label="状态" width="110" />
        <el-table-column prop="comment" label="意见" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button v-if="row.status==='PENDING' && canAct(row)" size="small" type="success" @click="approve(row)">通过</el-button>
            <el-button v-if="row.status==='PENDING' && canAct(row)" size="small" type="danger" @click="reject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

  </div>
</template>

<script setup>
import { onMounted, ref, reactive, watch } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({ contractId: Number })
const auth = useAuthStore()

const rows = ref([])
const tasks = ref([])
const openCreate = ref(false)
const openTasks = ref(false)
const loading = ref(false)

const form = reactive({
  amount: 0,
  reason: '',
  scope_desc: '',
  schedule_impact_days: 0,
})

async function load(){
  const { data } = await http.get('/changes')
  rows.value = data.filter(x => x.contract_id === props.contractId)
}

function canAct(task){
  // 管理员可以操作所有任务
  if (auth.role === 'ADMIN') {
    return true
  }
  // 检查角色是否匹配
  if (auth.role !== task.assignee_role) {
    return false
  }
  // 如果任务需要特定级别，检查用户级别是否匹配
  if (task.required_level) {
    return auth.level === task.required_level
  }
  // 如果任务不需要级别，只要角色匹配就可以
  return true
}

async function create(){
  // 表单验证
  if (!props.contractId) {
    ElMessage.error('合同ID缺失，请刷新页面重试')
    return
  }
  if (form.amount === undefined || form.amount === null || form.amount < 0) {
    ElMessage.error('变更金额不能为负数')
    return
  }
  // 允许金额为0（可以只变更时间），但需要至少金额或时间有变更
  if (form.amount === 0 && (!form.schedule_impact_days || form.schedule_impact_days === 0)) {
    ElMessage.error('变更金额和时间不能同时为0，至少需要变更其中一项')
    return
  }
  if (!form.reason || !form.reason.trim()) {
    ElMessage.error('请输入变更原因')
    return
  }
  if (!form.scope_desc || !form.scope_desc.trim()) {
    ElMessage.error('请输入范围描述')
    return
  }
  
  try{
    loading.value = true
    await http.post('/changes', { 
      contract_id: props.contractId,
      amount: form.amount,
      reason: form.reason.trim(),
      scope_desc: form.scope_desc.trim(),
      schedule_impact_days: form.schedule_impact_days || 0
    })
    ElMessage.success('已提交变更申请')
    openCreate.value = false
    // 重置表单
    form.amount = 0
    form.reason = ''
    form.scope_desc = ''
    form.schedule_impact_days = 0
    await load()
  }catch(e){
    const errorMsg = e?.response?.data?.detail || e?.message || '提交失败'
    ElMessage.error(errorMsg)
    console.error('提交变更申请失败:', e)
  }finally{
    loading.value = false
  }
}

async function viewTasks(row){
  const { data } = await http.get(`/changes/${row.id}/tasks`)
  tasks.value = data
  openTasks.value = true
}

async function approve(task){
  await http.post(`/changes/tasks/${task.id}/approve`, { comment: '同意（demo）' })
  ElMessage.success('已通过')
  await viewTasks({ id: task.change_id })
  await load()
}

async function reject(task){
  const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回', { inputPlaceholder: '如：缺少造价核算报告' })
  await http.post(`/changes/tasks/${task.id}/reject`, { comment: value })
  ElMessage.success('已驳回')
  await viewTasks({ id: task.change_id })
  await load()
}

onMounted(load)
watch(() => props.contractId, load)
</script>
