import { useColorMode } from '@chakra-ui/react'

export function useColorModeValue(lightValue, darkValue, invert = false) {
  const { colorMode } = useColorMode()
  
  if (invert) {
    return colorMode === 'light' ? darkValue : lightValue
  }
  
  return colorMode === 'light' ? lightValue : darkValue
}