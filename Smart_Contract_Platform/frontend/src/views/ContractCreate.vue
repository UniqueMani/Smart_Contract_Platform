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
      <el-form-item label="承包方名称">
        <el-input v-model="f.contractor_org" />
      </el-form-item>

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

      <el-button type="primary" :loading="loading" @click="save">保存</el-button>
      <el-button @click="$router.back()">取消</el-button>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'

const loading = ref(false)
const f = reactive({
  contract_no: 'HT-2025-002',
  contract_name: '市政道路工程施工合同（二期）',
  project_name: '市政道路工程二期',
  owner_org: '发包方A',
  contractor_org: '承包方B',
  tender_price: 10000000,
  contract_price: 10000000,
  approved_budget: 20000000,
})

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
</script>
