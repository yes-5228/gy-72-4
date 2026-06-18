<template>
  <div class="orders-layout">
    <section class="panel full-panel">
      <div class="panel-title">
        <h2>我的订单</h2>
        <span>{{ orders.length }} 条订单</span>
      </div>

      <div class="order-filter">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          :class="{ selected: currentStatus === tab.value }"
          type="button"
          @click="currentStatus = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="loading" class="loading">订单加载中...</div>
      <div v-else-if="filteredOrders.length === 0" class="empty-state">暂无相关订单</div>
      <div v-else class="order-list">
        <article
          v-for="order in filteredOrders"
          :key="order.id"
          class="order-card"
          :class="{ expanded: expandedId === order.id, abnormal: order.status === 'abnormal' }"
          @click="toggleExpand(order.id)"
        >
          <div class="order-header">
            <div>
              <strong>订单 #{{ order.id }}</strong>
              <span class="status-badge" :class="order.status">{{ order.status_label }}</span>
            </div>
            <div class="order-meta">
              <span>￥{{ order.total_amount }}</span>
              <small>{{ formatDate(order.created_at) }}</small>
            </div>
          </div>

          <div class="order-summary">
            <span>{{ order.items.length }} 类菜品</span>
            <span v-if="order.delivery_info" class="delivery-status">
              配送：{{ order.delivery_info.status_label || '待分配' }}
            </span>
          </div>

          <div v-if="expandedId === order.id" class="order-detail">
            <div class="detail-section">
              <h4>配送信息</h4>
              <p><span>收货人：</span>{{ order.student_name }}</p>
              <p><span>联系电话：</span>{{ order.phone }}</p>
              <p><span>配送地址：</span>{{ order.delivery_address }}</p>
              <p><span>预约送达：</span>{{ formatDate(order.pickup_time) }}</p>
              <p v-if="order.note"><span>备注：</span>{{ order.note }}</p>
            </div>

            <div v-if="order.delivery_info" class="detail-section">
              <h4>配送状态</h4>
              <p>
                <span>当前状态：</span>
                <span class="status-badge" :class="order.delivery_info.status">
                  {{ order.delivery_info.status_label }}
                </span>
              </p>
              <p v-if="order.delivery_info.courier_name">
                <span>配送员：</span>{{ order.delivery_info.courier_name }}
              </p>
              <p v-if="order.delivery_info.courier_phone">
                <span>配送电话：</span>{{ order.delivery_info.courier_phone }}
              </p>
              <p v-if="order.delivery_info.estimated_arrival">
                <span>预计送达：</span>{{ formatDate(order.delivery_info.estimated_arrival) }}
              </p>
              <p v-if="order.delivery_info.delivered_at">
                <span>实际送达：</span>{{ formatDate(order.delivery_info.delivered_at) }}
              </p>
            </div>

            <div v-if="order.status === 'abnormal'" class="abnormal-notice">
              <p>该订单配送出现异常，暂时无法评价。请联系食堂或配送员处理，异常解决并送达后将可以评价。</p>
            </div>

            <div class="detail-section">
              <h4>菜品明细</h4>
              <div class="order-items">
                <div v-for="item in order.items" :key="item.id" class="order-item">
                  <span>{{ item.dish_detail.name }}</span>
                  <span>x {{ item.quantity }}</span>
                  <span>￥{{ (item.quantity * item.unit_price).toFixed(2) }}</span>
                </div>
              </div>
              <div class="order-total">
                <span>合计</span>
                <strong>￥{{ order.total_amount }}</strong>
              </div>
            </div>

            <div v-if="order.status === 'completed'" class="detail-actions">
              <button class="primary-button" type="button" @click.stop="goReview(order)">
                去评价
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { fetchOrders } from '../api/canteen'

const props = defineProps({
  reloadKey: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['navigate-review'])

const orders = ref([])
const loading = ref(false)
const expandedId = ref(null)
const currentStatus = ref('')

const statusTabs = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待确认' },
  { value: 'delivering', label: '配送中' },
  { value: 'completed', label: '已完成' },
  { value: 'abnormal', label: '异常' },
]

const filteredOrders = computed(() => {
  if (!currentStatus.value) return orders.value
  return orders.value.filter((o) => o.status === currentStatus.value)
})

async function loadOrders() {
  loading.value = true
  try {
    orders.value = await fetchOrders({ ordering: '-created_at' })
  } finally {
    loading.value = false
  }
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function goReview(order) {
  emit('navigate-review', order)
}

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

onMounted(loadOrders)
watch(() => props.reloadKey, loadOrders)
</script>

<style scoped>
.orders-layout {
  min-width: 0;
}

.order-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.order-filter button {
  padding: 8px 16px;
  border: 1px solid #d6ded8;
  border-radius: 999px;
  background: #fff;
  color: #445248;
  cursor: pointer;
  font-size: 14px;
}

.order-filter button.selected {
  background: #2f7d57;
  border-color: #2f7d57;
  color: #fff;
}

.order-list {
  display: grid;
  gap: 12px;
}

.order-card {
  border: 1px solid #dfe7e1;
  border-radius: 8px;
  background: #fff;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.06);
}

.order-card.expanded {
  border-color: #2f7d57;
}

.order-card.abnormal {
  border-color: #e8a090;
  background: #fffbfa;
}

.order-card.abnormal.expanded {
  border-color: #b45134;
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.order-header strong {
  font-size: 16px;
}

.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  margin-left: 8px;
}

.status-badge.pending {
  background: #fff2dc;
  color: #9a5b00;
}

.status-badge.confirmed,
.status-badge.preparing {
  background: #e0edff;
  color: #1e5c9e;
}

.status-badge.delivering,
.status-badge.picked,
.status-badge.assigned {
  background: #dcefe5;
  color: #1e5c3e;
}

.status-badge.completed,
.status-badge.delivered {
  background: #dcefe5;
  color: #1e5c3e;
}

.status-badge.cancelled {
  background: #f1f5f2;
  color: #66746b;
}

.status-badge.abnormal {
  background: #ffe0e0;
  color: #b45134;
  font-weight: 700;
}

.status-badge.failed,
.status-badge.waiting {
  background: #ffe0e0;
  color: #b45134;
}

.order-meta {
  text-align: right;
}

.order-meta span {
  display: block;
  font-weight: 700;
  color: #2f7d57;
}

.order-meta small {
  color: #66746b;
  font-size: 12px;
}

.order-summary {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #edf1ee;
  color: #66746b;
  font-size: 14px;
}

.delivery-status {
  color: #2f7d57;
}

.order-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #edf1ee;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #17201a;
}

.detail-section p {
  margin: 6px 0;
  font-size: 14px;
  color: #445248;
  display: flex;
  gap: 8px;
}

.detail-section p span:first-child {
  color: #66746b;
  min-width: 70px;
}

.order-items {
  display: grid;
  gap: 8px;
}

.order-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px dashed #edf1ee;
  font-size: 14px;
}

.order-item:last-child {
  border-bottom: none;
}

.order-total {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #edf1ee;
  font-size: 15px;
}

.order-total strong {
  color: #2f7d57;
  font-size: 18px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #edf1ee;
}

.detail-actions button {
  padding: 10px 24px;
}

.abnormal-notice {
  border: 1px solid #e8a090;
  border-radius: 8px;
  background: #fff5f3;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.abnormal-notice p {
  margin: 0;
  color: #b45134;
  font-size: 14px;
  line-height: 1.6;
}
</style>
