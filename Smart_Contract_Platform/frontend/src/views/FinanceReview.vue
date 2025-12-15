<template>
  <div>
    <PageHeader title="审核（合同/财务）" subtitle="合同审核 → 财务审核 → 支付；系统自动计算额度并执行超概算拦截" />

    <el-tabs>
      <el-tab-pane label="待合同审核">
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

      <el-tab-pane label="待财务审核">
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
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

const auth = useAuthStore()
const rows = ref([])
const calc = ref(null)
const openCalc = ref(false)

const submitted = computed(() => rows.value.filter(x => x.status === 'SUBMITTED'))
const finance = computed(() => rows.value.filter(x => x.status === 'FINANCE_REVIEW'))

async function load(){
  const { data } = await http.get('/payments')
  rows.value = data
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
  await http.post(`/payments/${row.id}/review/finance/reject`)
  ElMessage.success('已驳回')
  await load()
}

onMounted(load)
</script>
