<template>
  <div class="mx-auto min-h-screen max-w-[1000px] bg-bg px-4 py-6">
    <header class="mb-4 flex items-center justify-between">
      <h1 class="font-black text-2xl uppercase tracking-tight">Админка — заказы</h1>
      <nav class="flex items-center gap-4 font-mono text-xs uppercase tracking-wide">
        <router-link to="/admin" class="text-ink hover:text-accent">Товары</router-link>
        <button type="button" class="cursor-pointer text-ink hover:text-accent" @click="onLogout">
          Выйти
        </button>
      </nav>
    </header>

    <p v-if="error" class="font-mono text-xs text-accent">{{ error }}</p>
    <p v-if="loading" class="font-mono text-xs text-muted">Загрузка…</p>

    <table v-else class="w-full border-collapse border border-border bg-white">
      <thead>
        <tr class="border-b border-ink font-mono text-xs uppercase tracking-wide text-muted">
          <th class="px-3 py-2 text-left">ID</th>
          <th class="px-3 py-2 text-left">Покупатель</th>
          <th class="px-3 py-2 text-left">Email</th>
          <th class="px-3 py-2 text-left">Сумма</th>
          <th class="px-3 py-2 text-left">Позиции</th>
          <th class="px-3 py-2 text-left">Статус</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id" class="border-b border-border text-sm">
          <td class="px-3 py-2">{{ o.id }}</td>
          <td class="px-3 py-2">{{ o.customer_name }}</td>
          <td class="px-3 py-2">{{ o.customer_email }}</td>
          <td class="px-3 py-2 font-mono">${{ o.total.toFixed(2) }}</td>
          <td class="px-3 py-2">
            <span
              v-for="it in o.items"
              :key="it.product_id"
              class="mr-2 inline-block font-mono text-xs text-muted"
            >
              {{ it.product_name }} ×{{ it.quantity }}
            </span>
          </td>
          <td class="px-3 py-2">
            <select
              :value="o.status"
              class="border border-ink px-2 py-1 font-mono text-xs focus:outline-none"
              :class="{
                'text-muted': o.status === 'pending',
                'text-ink': o.status === 'paid' || o.status === 'shipped',
                'text-success': o.status === 'completed',
                'text-accent': o.status === 'cancelled',
              }"
              @change="onStatusChange(o, $event.target.value)"
            >
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
        </tr>
        <tr v-if="!orders.length">
          <td colspan="6" class="px-3 py-6 text-center font-mono text-sm text-muted">
            Заказов пока нет
          </td>
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
