import React from "react";
import Container from "./Container";
import FadeIn from "./FadeIn";
import FooterNavigation from "./FooterNavigation";
import Logo from "./Logo";
import Link from "next/link";
import { useColorMode, useColorModeValue, Box, Text, Input, Button, Flex } from "@chakra-ui/react";

const ArrowIcon = (props) => {
  return (
    <svg viewBox="0 0 16 6" aria-hidden="true" {...props}>
      <path
        fill="currentColor"
        fillRule="evenodd"
        clipRule="evenodd"
        d="M16 3 10 .5v2H0v1h10v2L16 3Z"
      />
    </svg>
  );
};

const NewsletterForm = () => {
  const { colorMode } = useColorMode();
  const bgColor = useColorModeValue('white', 'neutral.950');
  const textColor = useColorModeValue('neutral.950', 'white');
  const borderColor = useColorModeValue('neutral.300', 'neutral.800');
  const placeholderColor = useColorModeValue('neutral.500', 'neutral.500');
  const focusBorderColor = useColorModeValue('neutral.950', 'white');
  const focusRingColor = useColorModeValue('neutral.950/5', 'neutral.800');

  return (
    <form className="max-w-sm">
      <Text as="h2" fontSize="sm" fontWeight="semibold" letterSpacing="wider" color={colorMode === 'dark' ? 'white' : 'neutral.950'}>
        Sign up for our newsletter
      </Text>
      <Text mt={4} fontSize="sm" color={colorMode === 'dark' ? 'neutral.400' : 'neutral.700'}>
        Subscribe to get the latest design news, articles, resources and
        inspiration.
      </Text>
      <Box position="relative" mt={6}>
        <Input
          type="email"
          placeholder="Email address"
          autoComplete="email"
          aria-label="Email address"
          bg="transparent"
          borderColor={borderColor}
          color={textColor}
          _placeholder={{ color: placeholderColor }}
          _focus={{ borderColor: focusBorderColor, ring: focusRingColor }}
        />
        <Box position="absolute" right={1} top={1} bottom={1}>
          <Button
            type="submit"
            aria-label="Submit"
            bg={bgColor}
            color={colorMode === 'dark' ? 'neutral.950' : 'white'}
            _hover={{ bg: colorMode === 'dark' ? 'neutral.200' : 'neutral.800' }}
          >
            <ArrowIcon className="w-4" />
          </Button>
        </Box>
      </Box>
    </form>
  );
};

const XIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" {...props}>
    <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z" />
  </svg>
);

const Footer = () => {
  const { colorMode } = useColorMode();
  const textColor = useColorModeValue('gray.700', 'gray.300');
  const linkColor = useColorModeValue('blue.600', 'blue.300');
  const iconColor = useColorModeValue('gray.600', 'gray.400');
  const borderColor = useColorModeValue('neutral.200', 'neutral.800');

  return (
    <Container as="footer" className="relative mt-24 w-full sm:mt-32 lg:mt-40 z-50">
      <FadeIn>
        <div className="grid grid-cols-1 gap-x-8 gap-y-16 lg:grid-cols-2">
          <FooterNavigation />
          <div className="flex lg:justify-end">
            <NewsletterForm />
          </div>
        </div>
        <Box
          mt={24}
          mb={20}
          pt={12}
          borderTopWidth={1}
          borderTopColor={borderColor}
          display="flex"
          flexWrap="wrap"
          alignItems="flex-end"
          justifyContent="space-between"
        >
          <Link href={"/"} aria-label="Home">
            <Logo className="h-8" fillOnHover invert={colorMode === 'dark'}>
              the Genuine Collective
            </Logo>
          </Link>
          <Flex alignItems="center" justifyContent="space-between" width="100%" mt={6}>
            <Text fontSize="sm" color={textColor}>
              {new Date().getFullYear()} The Genuine Collective. All rights reserved.
            </Text>
            <Flex gap={4}>
              <Link href="https://x.com/thegenuineco" aria-label="TGC on X (Twitter)">
                <XIcon fill={iconColor} className="h-6 w-6 transition-colors hover:fill-current hover:text-blue-400" />
              </Link>
              {/* Add other social media links similarly */}
            </Flex>
          </Flex>
        </Box>
      </FadeIn>
    </Container>
  );
};

export default Footer;
