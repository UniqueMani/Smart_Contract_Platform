<template>
  <div v-if="c">
    <PageHeader :title="`合同详情：${c.contract_no}`" subtitle="合同-变更-进度款-完工比例在此聚合展示">
      <el-button v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role) && c.status==='DRAFT'" type="primary" @click="submit">
        提交（demo：直接生效）
      </el-button>
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
      <el-descriptions-item label="完工比例">{{ c.completion_ratio }}</el-descriptions-item>
      <el-descriptions-item label="已支付">{{ c.paid_total }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ c.status }}</el-descriptions-item>
    </el-descriptions>

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
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

import ChangeList from '../components/ChangeList.vue'
import PaymentList from '../components/PaymentList.vue'
import QuantityList from '../components/QuantityList.vue'

const auth = useAuthStore()
const route = useRoute()
const c = ref(null)

async function load(){
  const { data } = await http.get('/contracts/' + route.params.id)
  c.value = data
}

async function submit(){
  try{
    await http.post(`/contracts/${c.value.id}/submit`)
    ElMessage.success('已提交/生效')
    await load()
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '提交失败')
  }
}

onMounted(load)
</script>
