import type { Preset, UserConfig } from 'unocss'
import type { Theme } from 'unocss/preset-wind4'
import {
  definePreset,
  presetIcons,
  presetTypography,
  presetWind4,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

/**
 * Design tokens shared by every frontend app. Colours are CSS variables so a
 * theme (light/dark or per-app brand) only redefines variables, never classes.
 * Build real palettes with the ui-ux-pro-max skill before shipping a product UI.
 */
export const presetAppy = definePreset((): Preset<Theme> => ({
  name: 'appy',
  theme: {
    colors: {
      bg: 'var(--appy-bg)',
      fg: 'var(--appy-fg)',
      muted: 'var(--appy-muted)',
      border: 'var(--appy-border)',
      primary: 'var(--appy-primary)',
    },
    font: {
      sans: 'Inter, ui-sans-serif, system-ui, sans-serif',
      mono: 'ui-monospace, SFMono-Regular, Menlo, monospace',
    },
  },
  shortcuts: {
    'appy-container': 'mx-auto w-full max-w-6xl px-4 sm:px-6',
    'appy-focus': 'outline-none focus-visible:(ring-2 ring-primary ring-offset-2 ring-offset-bg)',
  },
  preflights: [
    {
      getCSS: () => `
:root {
  color-scheme: light dark;
  --appy-bg: oklch(100% 0 0);
  --appy-fg: oklch(20.8% 0.042 265.8);
  --appy-muted: oklch(55.4% 0.046 257.4);
  --appy-border: oklch(92.9% 0.013 255.5);
  --appy-primary: oklch(51.1% 0.262 276.97);
}
@media (prefers-color-scheme: dark) {
  :root {
    --appy-bg: oklch(12.9% 0.042 264.7);
    --appy-fg: oklch(96.8% 0.007 247.9);
    --appy-muted: oklch(70.4% 0.04 256.8);
    --appy-border: oklch(27.9% 0.041 260);
    --appy-primary: oklch(67.3% 0.182 276.9);
  }
}
html, body { background: var(--appy-bg); color: var(--appy-fg); }
`,
    },
  ],
}))

/** Base UnoCSS config for apps; extend it in each app's `uno.config.ts`. */
export function appyUnoConfig(overrides: UserConfig<Theme> = {}): UserConfig<Theme> {
  return {
    ...overrides,
    presets: [
      presetWind4(),
      presetIcons({ scale: 1.2 }),
      presetTypography(),
      presetAppy(),
      ...(overrides.presets ?? []),
    ],
    transformers: [
      transformerDirectives(),
      transformerVariantGroup(),
      ...(overrides.transformers ?? []),
    ],
    content: {
      ...overrides.content,
      pipeline: {
        include: [/\.(vue|ts|html)($|\?)/, /packages\/ui\/src\/.+\.(vue|ts)$/],
      },
    },
  }
}
