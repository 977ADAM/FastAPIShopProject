<template>
  <button type="button" class="emp-cat flex cursor-pointer flex-col items-center gap-3" @click="$emit('select', category.id)">
    <span
      class="emp-cat-circle placeholder-hatch flex h-24 w-24 items-center justify-center rounded-full border border-ink"
      :class="{ 'border-accent': active }"
    >
      <span class="font-mono text-[11px] tracking-wide text-muted">{{ short }}</span>
    </span>
    <span class="font-mono text-[11px] uppercase tracking-wide text-ink">{{ category.name }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  category: { type: Object, required: true },
  active: { type: Boolean, default: false },
})
defineEmits(['select'])
const short = computed(() => props.category.name.slice(0, 4).toUpperCase())
</script>

<style scoped>
.emp-cat-circle { transition: transform 0.25s ease, border-color 0.25s ease; }
.emp-cat:hover .emp-cat-circle { transform: translateY(-4px); border-color: var(--color-accent); }
</style>
