import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
  typescript: true,
  unocss: true,
  ignores: [
    'apps/api/**',
    'apps/cli/**',
    'target/**',
    'packages/api-client/src/schema.d.ts',
    'packages/api-client/openapi.json',
    '.claude/skills/**',
  ],
})
