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
          <div style="display: flex; gap: 8px;">
            <el-button 
              v-if="['OWNER_CONTRACT','OWNER_LEGAL','ADMIN'].includes(auth.role) && c.clauses && !isEditingClauses" 
              size="small" 
              type="primary"
              :loading="reviewing"
              @click="startAIReview"
            >
              AI审查
            </el-button>
            <el-button 
              v-if="['OWNER_CONTRACT','ADMIN'].includes(auth.role) && c.status==='DRAFT' && !isEditingClauses" 
              size="small" 
              @click="isEditingClauses = true"
            >
              编辑
            </el-button>
          </div>
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

    <!-- AI审查结果对话框 -->
    <el-dialog v-model="showReviewResult" title="AI审查结果" width="800px">
      <div v-if="reviewResult">
        <!-- 合规性评分 -->
        <div style="margin-bottom: 20px; text-align: center;">
          <div style="font-size: 14px; color: #666; margin-bottom: 8px;">合规性评分</div>
          <el-progress 
            :percentage="reviewResult.compliance_score" 
            :color="getScoreColor(reviewResult.compliance_score)"
            :stroke-width="20"
            :format="(percentage) => `${percentage.toFixed(1)}分`"
          />
        </div>

        <!-- 问题列表 -->
        <div v-if="reviewResult.issues && reviewResult.issues.length > 0" style="margin-bottom: 20px;">
          <h3 style="margin-bottom: 12px; font-size: 16px;">发现的问题</h3>
          <el-table :data="reviewResult.issues" border>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === '违规' ? 'danger' : row.type === '风险' ? 'warning' : 'info'">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === '高' ? 'danger' : row.severity === '中' ? 'warning' : 'success'">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="description" label="问题描述" />
            <el-table-column prop="suggestion" label="改进建议" />
          </el-table>
        </div>

        <!-- 改进建议 -->
        <div v-if="reviewResult.suggestions && reviewResult.suggestions.length > 0" style="margin-bottom: 20px;">
          <h3 style="margin-bottom: 12px; font-size: 16px;">总体改进建议</h3>
          <ul style="padding-left: 20px; line-height: 1.8;">
            <li v-for="(suggestion, index) in reviewResult.suggestions" :key="index" style="margin-bottom: 8px;">
              {{ suggestion }}
            </li>
          </ul>
        </div>

        <!-- 错误信息 -->
        <div v-if="reviewResult.error" style="color: #f56c6c; margin-top: 20px;">
          <el-alert type="error" :title="reviewResult.error" :closable="false" />
        </div>

        <!-- 空结果提示 -->
        <div v-if="!reviewResult.error && (!reviewResult.issues || reviewResult.issues.length === 0) && (!reviewResult.suggestions || reviewResult.suggestions.length === 0)" style="text-align: center; color: #999; padding: 40px;">
          未发现明显问题
        </div>
      </div>
      <div v-else style="text-align: center; padding: 40px;">
        <el-icon class="is-loading"><Loading /></el-icon>
        <div style="margin-top: 12px;">正在审查中...</div>
      </div>
      <template #footer>
        <el-button @click="showReviewResult = false">关闭</el-button>
      </template>
    </el-dialog>

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
import { Loading } from '@element-plus/icons-vue'
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
const reviewing = ref(false)
const showReviewResult = ref(false)
const reviewResult = ref(null)

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

async function startAIReview(){
  if (!c.value || !c.value.clauses || !c.value.clauses.trim()) {
    ElMessage.warning('合同条款为空，无法进行AI审查')
    return
  }
  
  try {
    reviewing.value = true
    showReviewResult.value = true
    reviewResult.value = null
    
    const { data } = await http.post(`/contracts/${c.value.id}/ai-review`, {})
    reviewResult.value = data
    
    if (data.error) {
      ElMessage.error(`AI审查失败: ${data.error}`)
    } else {
      ElMessage.success('AI审查完成')
    }
  } catch (e) {
    const errorMsg = e?.response?.data?.detail || e?.message || 'AI审查失败'
    ElMessage.error(errorMsg)
    reviewResult.value = {
      error: errorMsg,
      issues: [],
      suggestions: [],
      compliance_score: 0.0
    }
  } finally {
    reviewing.value = false
  }
}

function getScoreColor(score) {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

onMounted(load)
</script>
