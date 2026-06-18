<template>
  <section class="panel full-panel">
    <div class="panel-title">
      <h2>配送任务</h2>
      <span>{{ deliveries.length }} 条任务</span>
    </div>

    <div v-if="loading" class="loading">配送数据加载中...</div>
    <div v-else class="delivery-list">
      <article v-for="task in deliveries" :key="task.id" class="delivery-card">
        <div class="delivery-info">
          <div class="delivery-header">
            <strong>订单 #{{ task.order }}</strong>
            <span class="status-badge" :class="task.status">{{ task.status_label }}</span>
          </div>
          <p class="delivery-contact">
            {{ task.order_detail.student_name }} · {{ task.order_detail.phone }}
          </p>
          <p class="delivery-address">{{ task.order_detail.delivery_address }}</p>
          <div class="delivery-footer">
            <small>预计送达：{{ formatTime(task.estimated_arrival) }}</small>
            <span class="order-status-tag">
              订单状态：{{ task.order_detail.status_label }}
            </span>
          </div>
        </div>
        <div class="delivery-meta">
          <span class="courier-name">{{ task.courier_name || '待分配' }}</span>
          <select :value="task.status" @change="changeStatus(task, $event.target.value)">
            <option value="waiting">待分配</option>
            <option value="assigned">已分配</option>
            <option value="picked">已取餐</option>
            <option value="delivered">已送达</option>
            <option value="failed">异常</option>
          </select>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { fetchDeliveries, updateDelivery } from '../api/canteen'

const props = defineProps({
  reloadKey: {
    type: Number,
    default: 0,
  },
})

const deliveries = ref([])
const loading = ref(false)

async function loadDeliveries() {
  loading.value = true
  try {
    deliveries.value = await fetchDeliveries()
  } finally {
    loading.value = false
  }
}

async function changeStatus(task, status) {
  const payload = { status }
  if (status === 'delivered') {
    payload.delivered_at = new Date().toISOString()
  }
  const updated = await updateDelivery(task.id, payload)
  Object.assign(task, updated)
}

function formatTime(value) {
  if (!value) return '待确认'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

onMounted(loadDeliveries)
watch(() => props.reloadKey, loadDeliveries)
</script>

<style scoped>
.delivery-card {
  align-items: stretch;
}

.delivery-info {
  flex: 1;
  min-width: 0;
}

.delivery-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.delivery-header strong {
  font-size: 16px;
}

.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.status-badge.waiting {
  background: #f1f5f2;
  color: #66746b;
}

.status-badge.assigned {
  background: #e0edff;
  color: #1e5c9e;
}

.status-badge.picked {
  background: #dcefe5;
  color: #1e5c3e;
}

.status-badge.delivered {
  background: #dcefe5;
  color: #1e5c3e;
}

.status-badge.failed {
  background: #ffe0e0;
  color: #b45134;
}

.delivery-contact {
  margin: 4px 0;
  color: #445248;
  font-size: 14px;
}

.delivery-address {
  margin: 4px 0;
  color: #66746b;
  font-size: 13px;
}

.delivery-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  gap: 10px;
}

.delivery-footer small {
  color: #66746b;
}

.order-status-tag {
  font-size: 12px;
  color: #2f7d57;
  font-weight: 600;
}

.courier-name {
  font-size: 14px;
  color: #445248;
}
</style>
