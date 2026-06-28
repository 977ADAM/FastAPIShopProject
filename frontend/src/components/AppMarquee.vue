<template>
  <div class="flex h-12 items-center overflow-hidden border-y-2 border-ink bg-accent">
    <div
      class="flex animate-marquee whitespace-nowrap font-sans text-[13px] font-bold tracking-wide text-ink"
    >
      <span>{{ line }}&nbsp;</span>
      <span>{{ line }}&nbsp;</span>
    </div>
  </div>
</template>

<script setup>
const items = [
  'СВЕЖИЕ ПОСТАВКИ КАЖДУЮ НЕДЕЛЮ',
  'ЦЕНЫ ОПТ И РОЗНИЦА',
  'ВСЁ ДЛЯ ШКОЛЫ И ОФИСА',
  'БЫСТРАЯ ДОСТАВКА',
]
const line = items.map((i) => `✦ ${i} `).join('')
</script>
