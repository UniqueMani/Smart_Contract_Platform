<template>
  <div>
    <PageHeader 
      :title="isLegalRole ? '合同审核' : '审核（合同/财务）'" 
      :subtitle="isLegalRole ? '法务审核待审核的合同，审核通过后合同生效' : '变更申请审核（按职级显示）→ 合同审核 → 财务审核 → 支付；系统自动计算额度并执行超概算拦截'" 
    />

    <el-tabs>
      <el-tab-pane v-if="!isLegalRole" label="变更申请审核">
        <el-table :data="changeRows" border>
          <el-table-column prop="change.code" label="变更单号" width="130" />
          <el-table-column prop="change.contract_id" label="合同ID" width="100" />
          <el-table-column prop="change.amount" label="金额" width="120">
            <template #default="{ row }">
              {{ row.change.amount.toLocaleString() }} 元
            </template>
          </el-table-column>
          <el-table-column prop="change.schedule_impact_days" label="工期影响" width="100">
            <template #default="{ row }">
              <span v-if="row.change.schedule_impact_days > 0">
                {{ row.change.schedule_impact_days }} 天
              </span>
              <span v-else style="color: #999;">无</span>
            </template>
          </el-table-column>
          <el-table-column prop="change.reason" label="变更原因" />
          <el-table-column prop="task.step_name" label="当前审核步骤" width="120">
            <template #default="{ row }">
              {{ row.task.step_name === '科员' ? '合同管理员' : row.task.step_name }}
            </template>
          </el-table-column>
          <el-table-column prop="task.required_level" label="所需级别" width="100">
            <template #default="{ row }">
              <span v-if="row.task.required_level">
                {{ row.task.required_level === 'SECTION_CHIEF' ? '科长' : 
                   row.task.required_level === 'DIRECTOR' ? '处长' : 
                   row.task.required_level === 'BUREAU_CHIEF' ? '局长' : row.task.required_level }}
              </span>
              <span v-else style="color: #999;">无要求</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="approveChange(row)">通过</el-button>
              <el-button size="small" type="danger" @click="rejectChange(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="isLegalRole" label="合同审核">
        <el-table :data="contractRows" border>
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
              <el-button size="small" type="success" @click="approveContract(row)">审核通过</el-button>
              <el-button size="small" type="danger" @click="rejectContract(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="!isLegalRole" label="待合同审核">
        <el-table :data="submitted" border>
          <el-table-column prop="code" label="单号" width="130" />
          <el-table-column prop="amount" label="金额" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role)" size="small" type="primary" @click="toFinance(row)">
                合同审核通过
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="!isLegalRole" label="待财务审核">
        <el-table :data="finance" border>
          <el-table-column prop="code" label="单号" width="130" />
          <el-table-column prop="amount" label="金额" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column label="操作" width="260">
            <template #default="{ row }">
              <el-button size="small" @click="viewCalc(row)">额度</el-button>
              <el-button v-if="['OWNER_FINANCE','ADMIN'].includes(auth.role)" size="small" type="success" @click="approve(row)">通过并支付</el-button>
              <el-button v-if="['OWNER_FINANCE','ADMIN'].includes(auth.role)" size="small" type="danger" @click="reject(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-dialog v-model="openCalc" title="支付额度计算（demo）" width="700px">
          <el-descriptions border :column="2" v-if="calc">
            <el-descriptions-item label="批复概算">{{ calc.approved_budget }}</el-descriptions-item>
            <el-descriptions-item label="完工比例">{{ calc.completion_ratio }}</el-descriptions-item>
            <el-descriptions-item label="可支付额度">{{ calc.payable_limit }}</el-descriptions-item>
            <el-descriptions-item label="已支付累计">{{ calc.paid_total }}</el-descriptions-item>
            <el-descriptions-item label="可申请最大金额">{{ calc.max_apply }}</el-descriptions-item>
          </el-descriptions>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>

    <!-- 变更申请审核对话框 -->
    <el-dialog v-model="openChangeDialog" :title="changeDialogTitle" width="500px">
      <el-form>
        <el-form-item label="审核意见">
          <el-input v-model="changeComment" type="textarea" :rows="4" placeholder="请输入审核意见（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="openChangeDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmChangeAction">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'
import { useRouter } from 'vue-router'
import { formatDateTime } from '../utils/dateTime'

const auth = useAuthStore()
const router = useRouter()
const rows = ref([])
const calc = ref(null)
const openCalc = ref(false)
const changeRows = ref([])
const contractRows = ref([])
const openChangeDialog = ref(false)
const changeDialogTitle = ref('')
const changeComment = ref('')
const currentChangeAction = ref(null) // 'approve' or 'reject'
const currentChangeRow = ref(null)

const isLegalRole = computed(() => auth.role === 'OWNER_LEGAL')
const submitted = computed(() => rows.value.filter(x => x.status === 'SUBMITTED'))
const finance = computed(() => rows.value.filter(x => x.status === 'FINANCE_REVIEW'))

async function load(){
  const { data } = await http.get('/payments')
  rows.value = data
}

async function loadChanges(){
  try {
    const { data } = await http.get('/changes/pending/my')
    changeRows.value = data
  } catch (error) {
    // 如果接口不存在或用户无权限，忽略错误
    console.log('无法加载变更申请:', error)
  }
}

async function loadContracts(){
  if (isLegalRole.value) {
    try {
      const { data } = await http.get('/contracts/pending/legal')
      contractRows.value = data
    } catch (error) {
      console.log('无法加载待审核合同:', error)
    }
  }
}

async function approveContract(row){
  try {
    await http.post(`/contracts/${row.id}/review/legal`)
    ElMessage.success('审核通过，合同已生效')
    await loadContracts()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '审核失败')
  }
}

async function rejectContract(row){
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '法务驳回', { 
      inputPlaceholder: '如：合同条款不符合规范要求',
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消'
    })
    await http.post(`/contracts/${row.id}/reject/legal`, { reason: value })
    ElMessage.success('已驳回，合同已退回草稿状态')
    await loadContracts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || '驳回失败')
    }
  }
}

async function toFinance(row){
  await http.post(`/payments/${row.id}/review/contract`)
  ElMessage.success('已流转')
  await load()
}

async function viewCalc(row){
  const { data } = await http.get(`/payments/${row.id}/calc`)
  calc.value = data
  openCalc.value = true
}

async function approve(row){
  const { data } = await http.post(`/payments/${row.id}/review/finance/approve`)
  if(data.ok){
    ElMessage.success('已支付')
  }else{
    ElMessage.error('被拦截：' + (data.reason || '超额'))
  }
  await load()
}

async function reject(row){
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '财务驳回', { 
      inputPlaceholder: '如：申请材料不完整',
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消'
    })
    await http.post(`/payments/${row.id}/review/finance/reject`, { reject_reason: value })
    ElMessage.success('已驳回')
    await load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || '驳回失败')
    }
  }
}

function approveChange(row){
  currentChangeRow.value = row
  currentChangeAction.value = 'approve'
  changeDialogTitle.value = '审核通过'
  changeComment.value = ''
  openChangeDialog.value = true
}

function rejectChange(row){
  currentChangeRow.value = row
  currentChangeAction.value = 'reject'
  changeDialogTitle.value = '驳回变更申请'
  changeComment.value = ''
  openChangeDialog.value = true
}

async function confirmChangeAction(){
  if (!currentChangeRow.value || !currentChangeAction.value) return
  
  try {
    const taskId = currentChangeRow.value.task.id
    const url = `/changes/tasks/${taskId}/${currentChangeAction.value}`
    await http.post(url, { comment: changeComment.value || null })
    
    if (currentChangeAction.value === 'approve') {
      ElMessage.success('审核通过')
    } else {
      ElMessage.success('已驳回')
    }
    
    openChangeDialog.value = false
    await loadChanges()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  if (!isLegalRole.value) {
    load()
    loadChanges()
  } else {
    loadContracts()
  }
})
</script>
