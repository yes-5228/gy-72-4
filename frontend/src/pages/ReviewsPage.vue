<template>
  <div class="reviews-layout">
    <section class="panel">
      <div class="panel-title">
        <h2>提交评价</h2>
      </div>

      <div v-if="completedOrders.length > 0" class="review-order-select">
        <p class="section-hint">选择要评价的订单：</p>
        <div class="order-mini-list">
          <div
            v-for="order in completedOrders"
            :key="order.id"
            class="order-mini-card"
            :class="{ selected: selectedOrderId === order.id }"
            @click="selectOrder(order)"
          >
            <span>订单 #{{ order.id }}</span>
            <small>{{ order.items.length }} 类菜品 · ￥{{ order.total_amount }}</small>
          </div>
        </div>
      </div>

      <div v-if="abnormalOrders.length > 0" class="review-abnormal-section">
        <p class="section-hint abnormal-hint">以下订单配送异常，暂不可评价：</p>
        <div class="order-mini-list">
          <div
            v-for="order in abnormalOrders"
            :key="order.id"
            class="order-mini-card abnormal"
          >
            <span>订单 #{{ order.id }}<em class="abnormal-tag">异常</em></span>
            <small>{{ order.items.length }} 类菜品 · ￥{{ order.total_amount }}</small>
          </div>
        </div>
        <p class="abnormal-tip">异常订单需等待配送问题解决并送达后，方可进行评价。如有疑问请联系食堂。</p>
      </div>

      <form class="order-form" @submit.prevent="submitReview">
        <label>
          菜品
          <select v-model="form.dish" required>
            <option value="">请选择菜品</option>
            <option
              v-for="dish in availableDishes"
              :key="dish.id"
              :value="dish.id"
            >{{ dish.name }}</option>
          </select>
        </label>
        <label>
          姓名
          <input v-model="form.student_name" required placeholder="评价人" />
        </label>
        <label>
          评分
          <input v-model.number="form.rating" max="5" min="1" required type="number" />
        </label>
        <label>
          评价内容
          <textarea v-model="form.content" required rows="5" placeholder="口味、分量、配送体验等"></textarea>
        </label>
        <button class="primary-button" type="submit" :disabled="!canSubmit">
          提交评价
        </button>
        <p v-if="hint" class="form-hint">{{ hint }}</p>
      </form>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>近期反馈</h2>
        <span>{{ reviews.length }} 条</span>
      </div>
      <div v-if="loading" class="loading">评价加载中...</div>
      <div v-else class="review-list">
        <article v-for="review in reviews" :key="review.id" class="review-card">
          <div>
            <strong>{{ review.dish_detail.name }}</strong>
            <span>{{ '★'.repeat(review.rating) }}</span>
          </div>
          <p>{{ review.content }}</p>
          <small>{{ review.student_name }} · {{ formatDate(review.created_at) }}</small>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { createReview, fetchDishes, fetchOrders, fetchReviews } from '../api/canteen'

const props = defineProps({
  reloadKey: {
    type: Number,
    default: 0,
  },
  selectedOrder: {
    type: Object,
    default: null,
  },
})

const dishes = ref([])
const reviews = ref([])
const allOrders = ref([])
const selectedOrderId = ref(null)
const loading = ref(false)

const form = reactive({
  dish: '',
  student_name: '',
  rating: 5,
  content: '',
})

const completedOrders = computed(() =>
  allOrders.value.filter((o) => o.status === 'completed'),
)

const abnormalOrders = computed(() =>
  allOrders.value.filter((o) => o.status === 'abnormal'),
)

const availableDishes = computed(() => {
  if (selectedOrderId.value) {
    const order = allOrders.value.find((o) => o.id === selectedOrderId.value)
    if (order) {
      return order.items.map((item) => ({
        id: item.dish,
        name: item.dish_detail.name,
      }))
    }
  }
  return dishes.value
})

const canSubmit = computed(() => {
  return form.dish && form.student_name && form.content && form.rating >= 1 && form.rating <= 5
})

const hint = computed(() => {
  if (completedOrders.value.length === 0 && abnormalOrders.value.length === 0) {
    return '暂无已完成的订单，订单送达后可进行评价。'
  }
  if (completedOrders.value.length === 0 && abnormalOrders.value.length > 0) {
    return '当前没有可评价的订单，存在异常订单需等待处理完成。'
  }
  if (selectedOrderId.value && !form.dish) {
    return '请选择要评价的菜品。'
  }
  return ''
})

function selectOrder(order) {
  selectedOrderId.value = order.id
  form.student_name = order.student_name
  form.dish = ''
}

async function loadData() {
  loading.value = true
  try {
    const [dishData, reviewData, orderData] = await Promise.all([
      fetchDishes(),
      fetchReviews(),
      fetchOrders({ ordering: '-created_at' }),
    ])
    dishes.value = dishData
    reviews.value = reviewData
    allOrders.value = orderData
  } finally {
    loading.value = false
  }
}

async function submitReview() {
  const payload = {
    dish: form.dish,
    student_name: form.student_name,
    rating: form.rating,
    content: form.content,
  }
  if (selectedOrderId.value) {
    payload.order = selectedOrderId.value
  }
  await createReview(payload)
  form.content = ''
  form.rating = 5
  await loadData()
}

function formatDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

onMounted(() => {
  loadData()
  if (props.selectedOrder) {
    selectOrder(props.selectedOrder)
  }
})

watch(() => props.reloadKey, loadData)

watch(
  () => props.selectedOrder,
  (newOrder) => {
    if (newOrder) {
      if (!allOrders.value.find((o) => o.id === newOrder.id)) {
        allOrders.value.unshift(newOrder)
      }
      selectOrder(newOrder)
    }
  },
)
</script>

<style scoped>
.review-order-select {
  margin-bottom: 16px;
}

.section-hint {
  margin: 0 0 8px;
  color: #66746b;
  font-size: 14px;
}

.order-mini-list {
  display: grid;
  gap: 8px;
}

.order-mini-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border: 1px solid #d6ded8;
  border-radius: 8px;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s;
}

.order-mini-card:hover {
  border-color: #2f7d57;
}

.order-mini-card.selected {
  border-color: #2f7d57;
  background: #dcefe5;
  color: #1e5c3e;
}

.order-mini-card span {
  font-weight: 600;
}

.order-mini-card small {
  color: #66746b;
  font-size: 12px;
}

.order-mini-card.selected small {
  color: #1e5c3e;
}

.form-hint {
  margin: 0;
  color: #9a5b00;
  font-size: 13px;
}

.review-abnormal-section {
  margin-bottom: 16px;
  padding: 14px;
  border: 1px solid #e8a090;
  border-radius: 8px;
  background: #fff5f3;
}

.abnormal-hint {
  color: #b45134 !important;
  font-weight: 600;
}

.order-mini-card.abnormal {
  border-color: #e8a090;
  background: #fff;
  cursor: default;
}

.order-mini-card.abnormal:hover {
  border-color: #e8a090;
}

.abnormal-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 999px;
  background: #ffe0e0;
  color: #b45134;
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
  margin-left: 6px;
  vertical-align: middle;
}

.abnormal-tip {
  margin: 10px 0 0;
  color: #b45134;
  font-size: 13px;
  line-height: 1.5;
}
</style>
