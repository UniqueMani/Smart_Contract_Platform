<template>
  <div>
    <PageHeader title="新建合同" subtitle="合同价必须等于中标价；履约保证金按系统规则自动计算（demo）" />
    <el-form label-position="top" style="max-width: 760px;">
      <el-form-item label="合同号">
        <el-input v-model="f.contract_no" />
      </el-form-item>
      <el-form-item label="合同名称">
        <el-input v-model="f.contract_name" />
      </el-form-item>
      <el-form-item label="项目名称">
        <el-input v-model="f.project_name" />
      </el-form-item>
      <el-form-item label="发包方名称">
        <el-input v-model="f.owner_org" />
      </el-form-item>
      <el-form-item label="承包方">
        <el-select v-model="f.contractor_org" placeholder="请选择承包方" style="width:100%;" filterable>
          <el-option
            v-for="contractor in contractors"
            :key="contractor.company"
            :label="contractor.company"
            :value="contractor.company"
          />
        </el-select>
      </el-form-item>

      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="合同开始日期">
            <el-date-picker
              v-model="f.start_date"
              type="datetime"
              placeholder="选择开始日期"
              style="width:100%;"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="合同结束日期">
            <el-date-picker
              v-model="f.end_date"
              type="datetime"
              placeholder="选择结束日期"
              style="width:100%;"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="中标价">
            <el-input-number v-model="f.tender_price" :min="0" style="width:100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="合同价（必须=中标价）">
            <el-input-number v-model="f.contract_price" :min="0" style="width:100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="批复概算">
            <el-input-number v-model="f.approved_budget" :min="0" style="width:100%;" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="详细条款">
        <el-input
          v-model="f.clauses"
          type="textarea"
          :rows="8"
          placeholder="请输入合同详细条款..."
        />
      </el-form-item>

      <el-button type="primary" :loading="loading" @click="save">保存</el-button>
      <el-button @click="$router.back()">取消</el-button>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

const loading = ref(false)
const contractors = ref([])
const f = reactive({
  contract_no: 'HT-2025-002',
  contract_name: '市政道路工程施工合同（二期）',
  project_name: '市政道路工程二期',
  owner_org: '发包方A',
  contractor_org: '',
  tender_price: 10000000,
  contract_price: 10000000,
  approved_budget: 20000000,
  clauses: '',
  start_date: null,
  end_date: null,
})

async function loadContractors(){
  try{
    const { data } = await http.get('/users/contractors')
    contractors.value = data
    // 如果有承包方，默认选择第一个
    if (data.length > 0 && !f.contractor_org) {
      f.contractor_org = data[0].company
    }
  }catch(e){
    console.error('加载承包方列表失败', e)
  }
}

async function save(){
  try{
    loading.value = true
    const { data } = await http.post('/contracts', f)
    ElMessage.success('已创建')
    location.href = '/contracts/' + data.id
  }catch(e){
    ElMessage.error(e?.response?.data?.detail || '创建失败（注意：合同价必须=中标价）')
  }finally{
    loading.value = false
  }
}

onMounted(loadContractors)
</script>
