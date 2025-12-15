<template>
  <div>
    <PageHeader title="工程量/完工比例" subtitle="监理录入与签认（建议在合同详情页完成，这里提供快捷入口）" />
    <el-alert type="info" show-icon :closable="false">
      建议从「合同详情 → 完工比例」里录入；这里仅提供快捷入口。
    </el-alert>
    <div class="row" style="margin-top:12px;">
      <el-button @click="$router.push('/contracts')">去合同列表</el-button>
    </div>
  </div>
</template>

<script setup>
import PageHeader from '../components/PageHeader.vue'
</script>
