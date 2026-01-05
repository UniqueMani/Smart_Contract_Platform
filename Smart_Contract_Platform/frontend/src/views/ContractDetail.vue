<template>
  <div v-if="c">
    <PageHeader :title="`合同详情：${c.contract_no}`" subtitle="合同-变更-进度款-完工比例在此聚合展示">
      <div style="display: flex; gap: 8px;">
        <el-button v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role) && c.status==='DRAFT'" type="primary" @click="submit">
          提交给法务审核
        </el-button>
        <el-button v-if="['OWNER_LEGAL','ADMIN'].includes(auth.role) && c.status==='APPROVING'" type="success" @click="legalApprove">
          法务审核通过
        </el-button>
        <el-button v-if="['OWNER_LEGAL','ADMIN'].includes(auth.role) && c.status==='APPROVING'" type="danger" @click="legalReject">
          法务驳回
        </el-button>
      </div>
    </PageHeader>

    <el-descriptions :column="2" border>
      <el-descriptions-item label="合同名称">{{ c.contract_name }}</el-descriptions-item>
      <el-descriptions-item label="项目">{{ c.project_name }}</el-descriptions-item>
      <el-descriptions-item label="发包方">{{ c.owner_org }}</el-descriptions-item>
      <el-descriptions-item label="承包方">{{ c.contractor_org }}</el-descriptions-item>
      <el-descriptions-item label="中标价">{{ c.tender_price }}</el-descriptions-item>
      <el-descriptions-item label="合同价">{{ c.contract_price }}</el-descriptions-item>
      <el-descriptions-item label="履约保证金">{{ c.performance_bond }}</el-descriptions-item>
      <el-descriptions-item label="批复概算">{{ c.approved_budget }}</el-descriptions-item>
      <el-descriptions-item label="合同开始日期">{{ c.start_date ? new Date(c.start_date).toLocaleDateString('zh-CN') : '-' }}</el-descriptions-item>
      <el-descriptions-item label="合同结束日期">{{ c.end_date ? new Date(c.end_date).toLocaleDateString('zh-CN') : '-' }}</el-descriptions-item>
      <el-descriptions-item label="完工比例">{{ c.completion_ratio }}</el-descriptions-item>
      <el-descriptions-item label="已支付">{{ c.paid_total }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ c.status }}</el-descriptions-item>
    </el-descriptions>

    <el-card style="margin-top: 12px;" shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-weight: 500;">详细条款</div>
          <el-button 
            v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role) && c.status==='DRAFT' && !isEditingClauses" 
            size="small" 
            @click="isEditingClauses = true"
          >
            编辑
          </el-button>
        </div>
      </template>
      <div v-if="!isEditingClauses" style="white-space: pre-wrap; line-height: 1.6; min-height: 60px;">
        {{ c.clauses || '暂无详细条款' }}
      </div>
      <div v-else>
        <el-input
          v-model="editingClauses"
          type="textarea"
          :rows="8"
          placeholder="请输入合同详细条款..."
        />
        <div style="margin-top: 12px; text-align: right;">
          <el-button size="small" @click="cancelEditClauses">取消</el-button>
          <el-button type="primary" size="small" :loading="savingClauses" @click="saveClauses">保存</el-button>
        </div>
      </div>
    </el-card>

    <el-tabs style="margin-top: 12px;">
      <el-tab-pane label="变更">
        <ChangeList :contractId="c.id" />
      </el-tab-pane>
      <el-tab-pane label="进度款">
        <PaymentList :contractId="c.id" />
      </el-tab-pane>
      <el-tab-pane label="完工比例">
        <QuantityList :contractId="c.id" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

import ChangeList from '../components/ChangeList.vue'
import PaymentList from '../components/PaymentList.vue'
import QuantityList from '../components/QuantityList.vue'

const auth = useAuthStore()
const route = useRoute()
const c = ref(null)
const isEditingClauses = ref(false)
const editingClauses = ref('')
const savingClauses = ref(false)

async function load(){
  const { data } = await http.get('/contracts/' + route.params.id)
  c.value = data
  editingClauses.value = c.value?.clauses || ''
}

async function submit(){
  try{
    await http.post(`/contracts/${c.value.id}/submit`)
    ElMessage.success('已提交给法务审核')
    await load()
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '提交失败')
  }
}

async function legalApprove(){
  try{
    await http.post(`/contracts/${c.value.id}/review/legal`)
    ElMessage.success('法务审核通过，合同已生效')
    await load()
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '审核失败')
  }
}

async function legalReject(){
  try{
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '法务驳回', { 
      inputPlaceholder: '如：合同条款不符合规范要求',
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消'
    })
    await http.post(`/contracts/${c.value.id}/reject/legal`, { reason: value })
    ElMessage.success('已驳回，合同已退回草稿状态')
    await load()
  }catch(e){
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || '驳回失败')
    }
  }
}

function cancelEditClauses(){
  isEditingClauses.value = false
  editingClauses.value = c.value?.clauses || ''
}

async function saveClauses(){
  try{
    savingClauses.value = true
    await http.put(`/contracts/${c.value.id}`, { clauses: editingClauses.value })
    ElMessage.success('条款已保存')
    isEditingClauses.value = false
    await load()
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  }finally{
    savingClauses.value = false
  }
}

onMounted(load)
</script>
