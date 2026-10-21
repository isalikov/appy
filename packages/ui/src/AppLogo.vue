<script setup lang="ts">
withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })
</script>

<template>
  <span
    class="tracking-tight font-semibold inline-flex gap-2 items-center"
    :class="{ 'text-base': size === 'sm', 'text-xl': size === 'md', 'text-4xl': size === 'lg' }"
  >
    <span class="i-lucide-sparkles text-primary" aria-hidden="true" />
    Appy
  </span>
</template>
