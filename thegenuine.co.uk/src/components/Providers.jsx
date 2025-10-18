"use client";

import { ChakraProvider, ColorModeScript, useColorMode } from "@chakra-ui/react";
import theme from "@/theme";
import { useEffect } from "react";

function BodyColorModeClass() {
  const { colorMode } = useColorMode();
  useEffect(() => {
    if (colorMode === "dark") {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [colorMode]);
  return null;
}

export function Providers({ children }) {
  return (
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <BodyColorModeClass />
      {children}
    </ChakraProvider>
  );
}
