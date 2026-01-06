<template>
  <div>
    <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:8px;">
      <div />
      <el-button v-if="['CONTRACTOR','ADMIN'].includes(auth.role)" size="small" type="primary" @click="openCreate = true">
        发起支付申请
      </el-button>
    </div>

    <el-table :data="rows" border>
      <el-table-column prop="code" label="单号" width="130" />
      <el-table-column prop="amount" label="金额" width="120" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="purpose" label="事由" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="viewCalc(row)">额度</el-button>
          <el-button v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role) && row.status==='SUBMITTED'" size="small" type="primary" @click="toFinance(row)">合同审核通过</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="openCreate" title="发起支付申请" width="600px">
      <el-form label-position="top">
        <el-form-item label="申请金额（元）">
          <el-input-number v-model="form.amount" :min="0" style="width:100%;" />
        </el-form-item>
        <el-form-item label="支付事由">
          <el-input v-model="form.purpose" />
        </el-form-item>
        <el-form-item label="工程进度说明">
          <el-input v-model="form.progress_desc" />
        </el-form-item>
        <el-form-item label="期次（例如 2025-12）">
          <el-input v-model="form.period" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="openCreate=false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="create">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="openCalc" title="支付额度计算（demo）" width="700px">
      <el-descriptions border :column="2" v-if="calc">
        <el-descriptions-item label="批复概算">{{ calc.approved_budget }}</el-descriptions-item>
        <el-descriptions-item label="完工比例">{{ calc.completion_ratio }}</el-descriptions-item>
        <el-descriptions-item label="可支付额度">{{ calc.payable_limit }}</el-descriptions-item>
        <el-descriptions-item label="已支付累计">{{ calc.paid_total }}</el-descriptions-item>
        <el-descriptions-item label="可申请最大金额">{{ calc.max_apply }}</el-descriptions-item>
      </el-descriptions>
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
const openCalc = ref(false)
const calc = ref(null)
const loading = ref(false)

const form = reactive({
  amount: 9000000,
  purpose: '工程进度款',
  progress_desc: '按月度工程量计量单申请',
  period: '2025-12',
})

async function load(){
  const { data } = await http.get('/payments')
  rows.value = data.filter(x => x.contract_id === props.contractId)
}

async function create(){
  try{
    loading.value = true
    await http.post('/payments', { ...form, contract_id: props.contractId })
    ElMessage.success('已提交支付申请')
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
    console.error('支付申请提交失败:', e)
  }finally{
    loading.value = false
  }
}

async function viewCalc(row){
  const { data } = await http.get(`/payments/${row.id}/calc`)
  calc.value = data
  openCalc.value = true
}

async function toFinance(row){
  await http.post(`/payments/${row.id}/review/contract`)
  ElMessage.success('已流转到财务审核')
  await load()
}

onMounted(load)
watch(() => props.contractId, load)
</script>
