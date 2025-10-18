"use client";

import { Button as ChakraButton } from "@chakra-ui/react";
import Link from "next/link";
import { useColorMode, useColorModeValue } from '@chakra-ui/react'

const Button = ({ invert, href, className, children, ...props }) => {
  const { colorMode } = useColorMode()
  const bgColor = useColorModeValue('neutral.950', 'white')
  const textColor = useColorModeValue('white', 'neutral.950')

  const buttonProps = {
    ...props,
    bg: invert ? 'white' : bgColor,
    color: invert ? 'neutral.950' : textColor,
    _hover: { bg: invert ? 'neutral.200' : colorMode === 'light' ? 'neutral.800' : 'neutral.200' },
    borderRadius: 'full',
    px: 4,
    py: 1.5,
    fontSize: 'sm',
    fontWeight: 'semibold',
    transition: 'all 0.2s',
  };

  if (href) {
    return (
      <ChakraButton as={Link} href={href} {...buttonProps}>
        {children}
      </ChakraButton>
    );
  }

  return <ChakraButton {...buttonProps}>{children}</ChakraButton>;
};

export default Button;