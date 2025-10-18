// src/theme.js
import { extendTheme } from '@chakra-ui/react'
import colors from 'tailwindcss/colors'

const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  fonts: {
    heading: 'var(--font-sans), ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
    body: 'var(--font-sans), ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \\"Liberation Mono\\", \\"Courier New\\", monospace',
  },
  colors: {
    ...colors,
    // Deprecated Tailwind colors removed, using updated color names (sky, stone, neutral, gray, slate) per Tailwind v3+
    light: {
      bg: 'white',
      text: 'neutral.950',
    },
    dark: {
      bg: 'neutral.950',
      text: 'white',
    },
  },
})

export default theme
