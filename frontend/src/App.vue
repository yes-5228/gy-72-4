<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">食</span>
        <div>
          <strong>校园订餐</strong>
          <small>School Canteen</small>
        </div>
      </div>
      <nav>
        <button
          v-for="item in navItems"
          :key="item.key"
          :class="{ active: currentPage === item.key }"
          type="button"
          @click="navigateTo(item.key)"
        >
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <main class="main-panel">
      <header class="topbar">
        <div>
          <p class="eyebrow">提前订餐 · 营养分析 · 配送闭环</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <button class="ghost-button" type="button" @click="triggerReload">刷新数据</button>
      </header>

      <div v-show="currentPage === 'menu'" class="page-wrapper">
        <MenuPage :reload-key="reloadKey" @order-created="handleOrderCreated" />
      </div>
      <div v-show="currentPage === 'orders'" class="page-wrapper">
        <OrdersPage
          :reload-key="reloadKey"
          @navigate-review="handleNavigateReview"
        />
      </div>
      <div v-show="currentPage === 'delivery'" class="page-wrapper">
        <DeliveryPage :reload-key="reloadKey" @status-updated="handleStatusUpdated" />
      </div>
      <div v-show="currentPage === 'reviews'" class="page-wrapper">
        <ReviewsPage :reload-key="reloadKey" :selected-order="selectedOrder" />
      </div>
    </main>

    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.visible" class="toast" :class="toast.type">
          <span class="toast-icon">{{ toast.icon }}</span>
          <span class="toast-text">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import DeliveryPage from './pages/DeliveryPage.vue'
import MenuPage from './pages/MenuPage.vue'
import OrdersPage from './pages/OrdersPage.vue'
import ReviewsPage from './pages/ReviewsPage.vue'

const currentPage = ref('menu')
const reloadKey = ref(0)
const selectedOrder = ref(null)

const toast = reactive({
  visible: false,
  message: '',
  type: 'success',
  icon: '✓',
})
let toastTimer = null

const navItems = [
  { key: 'menu', label: '菜品订餐', icon: '🍱' },
  { key: 'orders', label: '我的订单', icon: '📋' },
  { key: 'delivery', label: '配送管理', icon: '🚚' },
  { key: 'reviews', label: '评价反馈', icon: '★' },
]

const pageTitle = computed(() => navItems.find((item) => item.key === currentPage.value)?.label)

function showToast(message, type = 'success') {
  const icons = { success: '✓', error: '✕', info: 'ℹ' }
  toast.message = message
  toast.type = type
  toast.icon = icons[type] || 'ℹ'
  toast.visible = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.visible = false
  }, 2500)
}

function triggerReload() {
  reloadKey.value++
  showToast('数据已刷新', 'info')
}

function navigateTo(key) {
  currentPage.value = key
  if (key !== 'reviews') {
    selectedOrder.value = null
  }
}

function handleNavigateReview(order) {
  selectedOrder.value = order
  currentPage.value = 'reviews'
}

function handleOrderCreated(order) {
  reloadKey.value++
  showToast(`订单 #${order.id} 已提交，金额 ￥${order.total_amount}`, 'success')
}

function handleStatusUpdated(detail) {
  reloadKey.value++
  if (detail) {
    const orderText = detail.order_id ? `订单 #${detail.order_id}` : '订单'
    showToast(`${orderText}已标记为「${detail.status_label}」`, 'success')
  } else {
    showToast('配送状态已更新', 'success')
  }
}
</script>

<style scoped>
.page-wrapper {
  min-width: 0;
}
</style>
