import { ThemeProvider } from 'next-themes'
import RootLayout from '../components/RootLayout'
import { useState } from 'react'

function MyApp({ Component, pageProps }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <ThemeProvider>
      <RootLayout expanded={expanded}>
        <Component {...pageProps} />
        <button onClick={() => setExpanded(!expanded)}>
          Toggle Menu
        </button>
      </RootLayout>
    </ThemeProvider>
  )
}

export default MyApp