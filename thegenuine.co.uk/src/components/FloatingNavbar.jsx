import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { FiArrowUp } from "react-icons/fi";
import { Box, Flex, useColorModeValue, useColorMode, IconButton } from '@chakra-ui/react';
import { MoonIcon, SunIcon } from "@chakra-ui/icons";
import LogoSign from './LogoSign';
import Link from 'next/link';

const FloatingNavbar = () => {
  const [isVisible, setIsVisible] = useState(false);
  const bgColor = useColorModeValue("rgba(0, 0, 0, 0.8)", "rgba(255, 255, 255, 0.8)");
  const textColor = useColorModeValue("white", "black");
  const { colorMode, toggleColorMode } = useColorMode();

  useEffect(() => {
    const scrollPosition = window.scrollY;
    const viewportHeight = window.innerHeight;
    setIsVisible(scrollPosition > viewportHeight * 0.5);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const viewportHeight = window.innerHeight;
      setIsVisible(scrollPosition > viewportHeight * 0.5);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.3 }}
          style={{
            position: 'fixed',
            bottom: '20px',
            left: 'auto',
            right: '20px',
            transform: 'translateX(-50%)',
            zIndex: 1000,
          }}
        >
          <Flex
            alignItems="center"
            justifyContent="center"
            bg={bgColor}
            color={textColor}
            borderRadius="full"
            boxShadow="lg"
            px={4}
            py={2}
          >
            <Link href="/" passHref>
              <IconButton
                as="a"
                icon={<LogoSign size="20px" invert={colorMode === 'dark'} />}
                aria-label="Home"
                variant="ghost"
                rounded="full"
                mr={2}
              />
            </Link>
            <NavItem href="/work">Our Work</NavItem>
            <NavItem href="/about">About Us</NavItem>
            <NavItem href="/process">Our Process</NavItem>
            <NavItem href="/blog">Blog</NavItem>
            <IconButton
              onClick={toggleColorMode}
              size="sm"
              variant="ghost"
              color={textColor}
              icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
              aria-label={`Switch to ${colorMode === "light" ? "dark" : "light"} mode`}
              mr={2}
            />
            <IconButton
              onClick={scrollToTop}
              size="sm"
              variant="ghost"
              color={textColor}
              icon={<FiArrowUp />}
              aria-label="Scroll to top"
            />
          </Flex>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

const NavItem = ({ href, children }) => (
  <Box
    as="a"
    href={href}
    px={3}
    py={2}
    borderRadius="md"
    _hover={{ bg: useColorModeValue("rgba(255, 255, 255, 0.1)", "rgba(0, 0, 0, 0.1)") }}
  >
    {children}
  </Box>
);

export default FloatingNavbar;
