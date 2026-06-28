<template>
  <div class="mx-auto min-h-screen max-w-[1000px] bg-bg px-4 py-6">
    <header class="flex items-center justify-between">
      <h1 class="font-extrabold text-2xl uppercase tracking-tight">Админка — товары</h1>
      <nav class="flex items-center gap-4 font-sans text-xs uppercase tracking-wide">
        <router-link to="/admin/orders" class="text-ink hover:text-accent">Заказы</router-link>
        <button type="button" class="cursor-pointer text-ink hover:text-accent" @click="onLogout">
          Выйти
        </button>
      </nav>
    </header>

    <p v-if="error" class="mt-4 font-sans text-xs text-accent">{{ error }}</p>

    <section class="my-4 grid grid-cols-1 gap-4 md:grid-cols-2">
      <!-- Форма создания/редактирования -->
      <form class="flex flex-col gap-3 border border-border bg-white p-4" @submit.prevent="onSubmit">
        <h2 class="font-extrabold text-base uppercase tracking-tight">
          {{ editingId ? 'Редактировать товар' : 'Новый товар' }}
        </h2>

        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Название
          <input
            v-model="form.name"
            required
            minlength="5"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Описание
          <textarea
            v-model="form.description"
            rows="2"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Цена
          <input
            v-model.number="form.price"
            type="number"
            step="0.01"
            min="0.01"
            required
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          Остаток
          <input
            v-model.number="form.stock"
            type="number"
            min="0"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          Бренд
          <input
            v-model="form.brand"
            placeholder="Бренд"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          Артикул
          <input
            v-model="form.sku"
            placeholder="Артикул"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          Единица
          <select
            v-model="form.unit"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          >
            <option value="шт">шт</option>
            <option value="упаковка">упаковка</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          В упаковке
          <input
            v-model.number="form.pack_qty"
            type="number"
            min="1"
            placeholder="В упаковке"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs font-bold uppercase tracking-wide text-muted">
          Категория
          <select
            v-model.number="form.category_id"
            required
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          >
            <option :value="null" disabled>— выберите —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Изображение
          <input
            type="file"
            accept="image/*"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
            @change="onFileChange"
          />
        </label>
        <small v-if="uploading" class="font-sans text-xs text-muted">Загрузка изображения…</small>
        <img
          v-if="form.image_url"
          :src="form.image_url"
          alt="preview"
          class="max-w-[120px] border border-border"
        />

        <div class="flex gap-2">
          <button
            type="submit"
            :disabled="saving"
            class="emp-press cursor-pointer bg-accent px-4 py-2 font-sans text-xs font-bold uppercase tracking-wide text-ink disabled:opacity-60"
          >
            {{ saving ? 'Сохранение…' : editingId ? 'Сохранить' : 'Создать' }}
          </button>
          <button
            v-if="editingId"
            type="button"
            class="emp-press cursor-pointer rounded-lg border border-border px-4 py-2 font-sans text-xs uppercase tracking-wide text-ink"
            @click="resetForm"
          >
            Отмена
          </button>
        </div>
      </form>

      <!-- Управление категориями -->
      <form class="flex flex-col gap-3 border border-border bg-white p-4" @submit.prevent="onCreateCategory">
        <h2 class="font-extrabold text-base uppercase tracking-tight">Новая категория</h2>
        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Название
          <input
            v-model="categoryForm.name"
            required
            minlength="5"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <label class="flex flex-col gap-1 font-sans text-xs uppercase tracking-wide text-muted">
          Slug
          <input
            v-model="categoryForm.slug"
            required
            minlength="5"
            class="rounded-lg border border-border px-3 py-2 font-sans text-sm text-ink focus:outline-none"
          />
        </label>
        <button
          type="submit"
          class="emp-press cursor-pointer self-start bg-accent px-4 py-2 font-sans text-xs font-bold uppercase tracking-wide text-ink"
        >
          Добавить категорию
        </button>

        <ul class="mt-3 list-none p-0">
          <li
            v-for="c in categories"
            :key="c.id"
            class="flex items-center justify-between border-b border-border py-1 font-sans text-sm"
          >
            <span>{{ c.name }}</span>
            <button
              type="button"
              class="cursor-pointer px-2 font-sans text-accent"
              @click="onDeleteCategory(c.id)"
            >
              ×
            </button>
          </li>
        </ul>
      </form>
    </section>

    <!-- Список товаров -->
    <section class="border border-border bg-white p-4">
      <h2 class="font-extrabold text-base uppercase tracking-tight">Товары ({{ products.length }})</h2>
      <p v-if="loading" class="mt-2 font-sans text-xs text-muted">Загрузка…</p>
      <table v-else class="mt-3 w-full border-collapse">
        <thead>
          <tr class="border-b border-ink font-sans text-xs uppercase tracking-wide text-muted">
            <th class="px-2 py-2 text-left">ID</th>
            <th class="px-2 py-2 text-left">Название</th>
            <th class="px-2 py-2 text-left">Категория</th>
            <th class="px-2 py-2 text-left">Цена</th>
            <th class="px-2 py-2 text-left">Остаток</th>
            <th class="px-2 py-2 text-left"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id" class="border-b border-border text-sm">
            <td class="px-2 py-2">{{ p.id }}</td>
            <td class="px-2 py-2">{{ p.name }}</td>
            <td class="px-2 py-2">{{ p.category?.name }}</td>
            <td class="px-2 py-2 font-sans">{{ formatPrice(p.price) }}</td>
            <td class="px-2 py-2 font-sans">{{ p.stock }}</td>
            <td class="px-2 py-2">
              <div class="flex gap-2 font-sans text-xs uppercase">
                <button type="button" class="cursor-pointer text-ink hover:text-accent" @click="onEdit(p)">
                  ред.
                </button>
                <button type="button" class="cursor-pointer text-accent" @click="onDelete(p.id)">
                  удал.
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productsAPI, categoriesAPI, uploadsAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatPrice } from '@/utils/format'

const auth = useAuthStore()
const router = useRouter()

const products = ref([])
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const error = ref(null)
const editingId = ref(null)

const emptyForm = () => ({
  name: '',
  description: '',
  price: null,
  category_id: null,
  image_url: '',
  stock: 0,
  brand: '',
  sku: '',
  unit: 'шт',
  pack_qty: 1,
})
const form = reactive(emptyForm())
const categoryForm = reactive({ name: '', slug: '' })

async function loadAll() {
  loading.value = true
  error.value = null
  try {
    const [pr, cat] = await Promise.all([productsAPI.getAll(), categoriesAPI.getAll()])
    products.value = pr.data.products
    categories.value = cat.data
  } catch {
    error.value = 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
}

function onEdit(p) {
  editingId.value = p.id
  Object.assign(form, {
    name: p.name,
    description: p.description || '',
    price: p.price,
    category_id: p.category_id,
    image_url: p.image_url || '',
    stock: p.stock ?? 0,
    brand: p.brand || '',
    sku: p.sku || '',
    unit: p.unit || 'шт',
    pack_qty: p.pack_qty ?? 1,
  })
}

async function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  uploading.value = true
  error.value = null
  try {
    const res = await uploadsAPI.uploadImage(file)
    form.image_url = res.data.image_url
  } catch {
    error.value = 'Не удалось загрузить изображение'
  } finally {
    uploading.value = false
  }
}

async function onSubmit() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    payload.brand = payload.brand || null
    payload.sku = payload.sku || null
    if (editingId.value) {
      await productsAPI.update(editingId.value, payload)
    } else {
      await productsAPI.create(payload)
    }
    resetForm()
    await loadAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось сохранить товар'
  } finally {
    saving.value = false
  }
}

async function onDelete(id) {
  if (!confirm('Удалить товар?')) return
  try {
    await productsAPI.remove(id)
    await loadAll()
  } catch {
    error.value = 'Не удалось удалить товар'
  }
}

async function onCreateCategory() {
  error.value = null
  try {
    await categoriesAPI.create({ ...categoryForm })
    categoryForm.name = ''
    categoryForm.slug = ''
    await loadAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось создать категорию'
  }
}

async function onDeleteCategory(id) {
  if (!confirm('Удалить категорию?')) return
  try {
    await categoriesAPI.remove(id)
    await loadAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось удалить категорию'
  }
}

function onLogout() {
  auth.logout()
  router.push('/admin/login')
}

onMounted(loadAll)
</script>
