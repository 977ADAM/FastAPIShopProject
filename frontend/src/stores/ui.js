import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const cartOpen = ref(false)
  const toast = ref(null)
  let timer = null

  function openCart() {
    cartOpen.value = true
  }
  function closeCart() {
    cartOpen.value = false
  }
  function showToast(message, duration = 1800) {
    toast.value = message
    clearTimeout(timer)
    timer = setTimeout(() => {
      toast.value = null
    }, duration)
  }

  return { cartOpen, toast, openCart, closeCart, showToast }
})
