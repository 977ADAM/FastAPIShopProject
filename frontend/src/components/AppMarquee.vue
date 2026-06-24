<template>
  <div class="flex h-12 items-center overflow-hidden border-y-2 border-ink bg-accent">
    <div
      class="flex animate-marquee whitespace-nowrap font-mono text-[13px] font-bold tracking-wide text-white"
    >
      <span>{{ line }}&nbsp;</span>
      <span>{{ line }}&nbsp;</span>
    </div>
  </div>
</template>

<script setup>
const items = [
  'FREE SHIPPING NATIONWIDE',
  'EASY RETURNS',
  'SECURE CHECKOUT',
  'NEW ARRIVALS WEEKLY',
]
const line = items.map((i) => `✦ ${i} `).join('')
</script>
