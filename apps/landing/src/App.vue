<script setup lang="ts">
import { useHead } from '@unhead/vue'

useHead({
  titleTemplate: title => (title ? `${title} · Appy` : 'Appy'),
  htmlAttrs: { lang: 'en' },
})
</script>

<template>
  <RouterView />
</template>
