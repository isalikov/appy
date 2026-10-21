<script setup lang="ts">
import { appLink } from '@appy/config'
import { AppLogo } from '@appy/ui'
import { useHead } from '@unhead/vue'

useHead({
  title: 'Home',
  meta: [{ name: 'description', content: 'Appy — a full-stack application boilerplate.' }],
})

// Cross-app links come from PUBLIC_*_URL, never from hard-coded hosts.
const openAppHref = appLink('web')
</script>

<template>
  <main class="text-fg p-6 bg-bg grid place-items-center min-h-dvh">
    <section class="text-center flex flex-col gap-5 max-w-xl items-center">
      <AppLogo size="lg" />
      <h1 class="text-3xl tracking-tight font-bold sm:text-5xl">
        Hello from Appy
      </h1>
      <p class="text-lg text-muted">
        A statically generated landing page. Edit
        <code class="font-mono">apps/landing/src/pages/IndexPage.vue</code>.
      </p>
      <a
        :href="openAppHref"
        class="text-white font-medium px-5 py-2.5 appy-focus rounded-lg bg-primary inline-flex gap-2 transition-opacity items-center hover:opacity-90"
      >
        Open the app
        <span class="i-lucide-arrow-right" aria-hidden="true" />
      </a>
    </section>
  </main>
</template>
