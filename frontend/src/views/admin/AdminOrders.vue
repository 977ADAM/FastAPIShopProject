<template>
  <div class="admin">
    <header class="admin-header">
      <h1>Админка — заказы</h1>
      <nav>
        <router-link to="/admin">Товары</router-link>
        <button class="link" @click="onLogout">Выйти</button>
      </nav>
    </header>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading">Загрузка…</p>

    <table v-else class="card">
      <thead>
        <tr>
          <th>ID</th><th>Покупатель</th><th>Email</th><th>Сумма</th><th>Позиции</th><th>Статус</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id">
          <td>{{ o.id }}</td>
          <td>{{ o.customer_name }}</td>
          <td>{{ o.customer_email }}</td>
          <td>${{ o.total.toFixed(2) }}</td>
          <td>
            <span v-for="it in o.items" :key="it.product_id" class="item">
              {{ it.product_name }} ×{{ it.quantity }}
            </span>
          </td>
          <td>
            <select :value="o.status" @change="onStatusChange(o, $event.target.value)">
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
        </tr>
        <tr v-if="!orders.length">
          <td colspan="6" class="empty">Заказов пока нет</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ordersAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const orders = ref([])
const loading = ref(false)
const error = ref(null)
const statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await ordersAPI.getAll()
    orders.value = res.data.orders
  } catch {
    error.value = 'Не удалось загрузить заказы'
  } finally {
    loading.value = false
  }
}

async function onStatusChange(order, status) {
  try {
    const res = await ordersAPI.updateStatus(order.id, status)
    order.status = res.data.status
  } catch {
    error.value = 'Не удалось изменить статус'
  }
}

function onLogout() {
  auth.logout()
  router.push('/admin/login')
}

onMounted(load)
</script>

<style scoped>
.admin {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 16px;
}
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
nav {
  display: flex;
  gap: 16px;
  align-items: center;
}
.card {
  width: 100%;
  border-collapse: collapse;
  border: 2px solid #111;
  border-radius: 8px;
  overflow: hidden;
}
th,
td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}
.item {
  display: inline-block;
  margin-right: 8px;
  color: #555;
}
select {
  padding: 4px;
  border: 1px solid #999;
  border-radius: 4px;
}
.link {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
}
.error {
  color: #c0392b;
}
.empty {
  text-align: center;
  color: #888;
}
a {
  color: #2563eb;
}
</style>
