<template>
  <div>
    <PageHeader
      title="仪表盘"
      :subtitle="dashboardSubtitle"
    >
      <el-button size="small" @click="load">刷新</el-button>
    </PageHeader>

    <el-alert v-if="loading" type="info" show-icon :closable="false">
      正在加载数据...
    </el-alert>

    <el-alert v-else-if="error" type="error" show-icon :closable="false">
      {{ error }}
    </el-alert>

    <template v-else-if="dashboardData">
      <!-- 统计卡片区域 -->
      <div class="stats-section">
        <h2 style="margin: 24px 0 16px; font-size: 18px; font-weight: 600;">统计概览</h2>
        <div class="stats-grid">
          <el-card 
            v-for="(stat, index) in dashboardData.stats" 
            :key="index"
            class="stat-card"
            :class="`stat-card-${stat.color || 'default'}`"
          >
            <div class="stat-content">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">
                {{ formatValue(stat.value) }}{{ stat.unit || '' }}
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 待处理事项区域 -->
      <div v-if="dashboardData.pending_items && dashboardData.pending_items.length > 0" class="section">
        <h2 style="margin: 24px 0 16px; font-size: 18px; font-weight: 600;">待处理事项</h2>
        <el-table :data="dashboardData.pending_items" border>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="row.link" 
                size="small" 
                type="primary" 
                @click="$router.push(row.link)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 最近数据区域 -->
      <div v-if="dashboardData.recent_items && dashboardData.recent_items.length > 0" class="section">
        <h2 style="margin: 24px 0 16px; font-size: 18px; font-weight: 600;">最近数据</h2>
        <el-table :data="dashboardData.recent_items" border>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="row.link" 
                size="small" 
                type="primary" 
                @click="$router.push(row.link)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 快捷操作区域 -->
      <div v-if="dashboardData.quick_actions && dashboardData.quick_actions.length > 0" class="section">
        <h2 style="margin: 24px 0 16px; font-size: 18px; font-weight: 600;">快捷操作</h2>
        <div class="quick-actions">
          <el-button
            v-for="(action, index) in dashboardData.quick_actions"
            :key="index"
            :type="action.type || 'default'"
            @click="$router.push(action.link)"
          >
            {{ action.label }}
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="dashboardData.stats.length === 0 && 
              (!dashboardData.pending_items || dashboardData.pending_items.length === 0) &&
              (!dashboardData.recent_items || dashboardData.recent_items.length === 0)"
        description="暂无数据"
      />
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'
import http from '../api/http'
import PageHeader from '../components/PageHeader.vue'
import { formatDateTime } from '../utils/dateTime'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const error = ref(null)
const dashboardData = ref(null)

const dashboardSubtitle = computed(() => {
  const roleNames = {
    'OWNER_CONTRACT': '合同管理员',
    'OWNER_LEGAL': '法务',
    'OWNER_FINANCE': '财务',
    'OWNER_LEADER': '领导',
    'OWNER_STAFF': '科员',
    'CONTRACTOR': '承包方',
    'SUPERVISOR': '监理',
    'AUDITOR': '审计',
    'ADMIN': '系统管理员'
  }
  const roleName = roleNames[auth.role] || auth.role
  return `${roleName}工作台 - 查看您的统计数据和待处理事项`
})

function formatValue(value) {
  if (typeof value === 'number') {
    return value.toLocaleString('zh-CN')
  }
  return value
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/dashboard/stats')
    dashboardData.value = data
  } catch (err) {
    error.value = err.response?.data?.detail || '加载数据失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.stats-section {
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  padding: 8px 0;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-card-primary .stat-value {
  color: #409eff;
}

.stat-card-success .stat-value {
  color: #67c23a;
}

.stat-card-warning .stat-value {
  color: #e6a23c;
}

.stat-card-danger .stat-value {
  color: #f56c6c;
}

.stat-card-info .stat-value {
  color: #909399;
}

.section {
  margin-bottom: 32px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
