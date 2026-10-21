// Root UnoCSS config, used by the ESLint plugin and editor tooling.
// Each frontend app has its own uno.config.ts for builds.
import { defineConfig } from 'unocss'
import { appyUnoConfig } from './packages/ui/src/unocss'

export default defineConfig(appyUnoConfig())
