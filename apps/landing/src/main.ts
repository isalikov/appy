import type { RouteRecordRaw } from 'vue-router'
import { ViteSSG } from 'vite-ssg'
import App from './App.vue'
import 'virtual:uno.css'

// Every route listed here is pre-rendered to static HTML at build time.
const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: () => import('./pages/IndexPage.vue') },
]

export const createApp = ViteSSG(App, { routes })
