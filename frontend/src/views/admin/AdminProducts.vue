<template>
  <div class="admin">
    <header class="admin-header">
      <h1>Админка — товары</h1>
      <button class="link" @click="onLogout">Выйти</button>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <section class="grid">
      <!-- Форма создания/редактирования -->
      <form class="card" @submit.prevent="onSubmit">
        <h2>{{ editingId ? 'Редактировать товар' : 'Новый товар' }}</h2>

        <label>Название<input v-model="form.name" required minlength="5" /></label>
        <label>Описание<textarea v-model="form.description" rows="2" /></label>
        <label>Цена<input v-model.number="form.price" type="number" step="0.01" min="0.01" required /></label>
        <label>
          Категория
          <select v-model.number="form.category_id" required>
            <option :value="null" disabled>— выберите —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </label>

        <label>
          Изображение
          <input type="file" accept="image/*" @change="onFileChange" />
        </label>
        <small v-if="uploading">Загрузка изображения…</small>
        <img v-if="form.image_url" :src="form.image_url" alt="preview" class="preview" />

        <div class="row">
          <button type="submit" :disabled="saving">
            {{ saving ? 'Сохранение…' : editingId ? 'Сохранить' : 'Создать' }}
          </button>
          <button v-if="editingId" type="button" class="ghost" @click="resetForm">Отмена</button>
        </div>
      </form>

      <!-- Управление категориями -->
      <form class="card" @submit.prevent="onCreateCategory">
        <h2>Новая категория</h2>
        <label>Название<input v-model="categoryForm.name" required minlength="5" /></label>
        <label>Slug<input v-model="categoryForm.slug" required minlength="5" /></label>
        <button type="submit">Добавить категорию</button>

        <ul class="cat-list">
          <li v-for="c in categories" :key="c.id">
            <span>{{ c.name }}</span>
            <button type="button" class="link danger" @click="onDeleteCategory(c.id)">×</button>
          </li>
        </ul>
      </form>
    </section>

    <!-- Список товаров -->
    <section class="card">
      <h2>Товары ({{ products.length }})</h2>
      <p v-if="loading">Загрузка…</p>
      <table v-else>
        <thead>
          <tr><th>ID</th><th>Название</th><th>Категория</th><th>Цена</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>{{ p.id }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.category?.name }}</td>
            <td>${{ p.price.toFixed(2) }}</td>
            <td class="actions">
              <button class="link" @click="onEdit(p)">ред.</button>
              <button class="link danger" @click="onDelete(p.id)">удал.</button>
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

const auth = useAuthStore()
const router = useRouter()

const products = ref([])
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const error = ref(null)
const editingId = ref(null)

const emptyForm = () => ({ name: '', description: '', price: null, category_id: null, image_url: '' })
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
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 16px 0;
}
.card {
  border: 2px solid #111;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}
.card h2 {
  margin-top: 0;
  font-size: 16px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  margin-bottom: 10px;
}
input,
textarea,
select {
  padding: 8px;
  border: 1px solid #999;
  border-radius: 4px;
}
.row {
  display: flex;
  gap: 8px;
}
button {
  padding: 8px 14px;
  border: none;
  border-radius: 4px;
  background: #111;
  color: #fff;
  cursor: pointer;
}
button.ghost {
  background: #eee;
  color: #111;
}
.link {
  background: none;
  color: #2563eb;
  padding: 2px 6px;
}
.link.danger {
  color: #c0392b;
}
.preview {
  max-width: 120px;
  border-radius: 4px;
  margin-bottom: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  text-align: left;
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
}
.actions {
  display: flex;
  gap: 4px;
}
.cat-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
}
.cat-list li {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}
.error {
  color: #c0392b;
}
@media (max-width: 700px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
