<template>
  <div class="login-wrap">
    <form class="login-card" @submit.prevent="onSubmit">
      <h1>Вход администратора</h1>

      <label>
        Логин
        <input v-model="username" type="text" autocomplete="username" required />
      </label>

      <label>
        Пароль
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>

      <p v-if="auth.error" class="error">{{ auth.error }}</p>

      <button type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Вход…' : 'Войти' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')

async function onSubmit() {
  const ok = await auth.login(username.value, password.value)
  if (ok) {
    router.push('/admin')
  }
}
</script>

<style scoped>
.login-wrap {
  display: flex;
  justify-content: center;
  padding: 64px 16px;
}
.login-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 320px;
  padding: 32px;
  border: 2px solid #111;
  border-radius: 8px;
  background: #fff;
}
.login-card h1 {
  margin: 0;
  font-size: 20px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}
input {
  padding: 8px;
  border: 1px solid #999;
  border-radius: 4px;
}
button {
  padding: 10px;
  border: none;
  border-radius: 4px;
  background: #111;
  color: #fff;
  cursor: pointer;
}
button:disabled {
  opacity: 0.6;
  cursor: default;
}
.error {
  margin: 0;
  color: #c0392b;
  font-size: 14px;
}
</style>
