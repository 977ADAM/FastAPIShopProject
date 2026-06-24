<template>
  <Transition name="toast">
    <div
      v-if="ui.toast"
      data-test="toast"
      class="fixed bottom-7 left-1/2 z-[120] -translate-x-1/2 border-2 border-accent bg-ink px-6 py-3.5 font-mono text-sm font-bold tracking-wide text-accent"
    >
      ✦ {{ ui.toast }}
    </div>
  </Transition>
</template>

<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 8px);
}
</style>
