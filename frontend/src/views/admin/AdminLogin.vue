<template>
  <div class="flex min-h-screen items-center justify-center bg-bg px-4 py-16">
    <form
      class="flex w-80 flex-col gap-5 border-2 border-ink bg-white p-8"
      @submit.prevent="onSubmit"
    >
      <h1 class="font-black text-2xl uppercase tracking-tight">ADMIN</h1>

      <label class="flex flex-col gap-1 font-mono text-xs uppercase tracking-wide text-muted">
        Логин
        <input
          v-model="username"
          type="text"
          autocomplete="username"
          required
          class="border border-ink px-3 py-2 font-sans text-sm text-ink focus:outline-none"
        />
      </label>

      <label class="flex flex-col gap-1 font-mono text-xs uppercase tracking-wide text-muted">
        Пароль
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
          class="border border-ink px-3 py-2 font-sans text-sm text-ink focus:outline-none"
        />
      </label>

      <p v-if="auth.error" class="font-mono text-xs text-accent">{{ auth.error }}</p>

      <button
        type="submit"
        :disabled="auth.loading"
        class="emp-press cursor-pointer bg-accent px-4 py-3 font-mono text-sm font-bold uppercase tracking-wide text-white disabled:cursor-default disabled:opacity-60"
      >
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
