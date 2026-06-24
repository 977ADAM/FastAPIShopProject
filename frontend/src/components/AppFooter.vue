<template>
  <footer class="bg-ink px-6 py-12 text-white md:px-12">
    <div class="mx-auto flex max-w-[1440px] flex-wrap items-start justify-between gap-6">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-accent font-black text-lg text-white">S</div>
          <div class="font-black text-2xl tracking-tight">FastAPI <span class="text-accent">Shop</span></div>
        </div>
        <div class="mt-3 font-mono text-[11px] leading-[1.9] tracking-wide text-neutral-400">
          BUILT WITH FASTAPI + VUE<br />OPEN 24/7
        </div>
      </div>
      <div class="flex gap-12 font-mono text-xs tracking-wide text-neutral-300">
        <div class="flex flex-col gap-2">
          <span class="text-white">SHOP</span><span>Catalog</span><span>New</span><span>Cart</span>
        </div>
        <div class="flex flex-col gap-2">
          <span class="text-white">HELP</span><span>Shipping</span><span>Returns</span><span>Sizes</span>
        </div>
      </div>
    </div>
  </footer>
</template>
