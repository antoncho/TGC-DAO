"use client";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { motion, MotionConfig, useReducedMotion } from "framer-motion";
import Container from "./Container";
import Link from "next/link";
import { useColorMode, useColorModeValue, IconButton, Flex, Box, VStack, Text } from "@chakra-ui/react";
import { MoonIcon, SunIcon, HamburgerIcon, CloseIcon } from "@chakra-ui/icons";
import { HiMenuAlt4 } from "react-icons/hi";
import { IoMdClose } from "react-icons/io";
import Footer from "./Footer";
import clsx from "clsx";
import Offices from "./Offices";
import SocialMedia from "./SocialMedia";
import Logo from "./Logo";
import ContactButton from "./ContactButton";
import MainNavigation from "./MainNavigation";
import FloatingNavbar from '../components/FloatingNavbar';
import { FaDiscord, FaLinkedin } from 'react-icons/fa';


const Header = ({
  panelId,
  expanded,
  onToggle,
  toggleRef,
}) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const bgColor = useColorModeValue("white", "gray.800");
  const textColor = useColorModeValue("gray.800", "white");
  const isInverted = expanded;

  const getButtonColor = () => {
    if (expanded) {
      return colorMode === 'dark' ? 'black' : 'white';
    } else {
      return colorMode === 'dark' ? 'white' : 'black';
    }
  };

  const getButtonBgColor = () => {
    if (expanded) {
      return colorMode === 'dark' ? 'white' : 'black';
    } else {
      return 'transparent';
    }
  };

  return (
    <Box 
      as="header" 
      bg={expanded ? (colorMode === 'dark' ? 'white' : 'black') : bgColor} 
      color={expanded ? (colorMode === 'dark' ? 'black' : 'white') : textColor}
      transition="background-color 0.3s, color 0.3s"
    >
      <Container className="absolute top-0 left-0 right-0 z-50">
        <Flex justify="space-between" align="center" py={2} >
          <Link href={"/"} aria-label="Home">
            <Logo invert={isInverted} />
          </Link>
          <Flex align="center" gap="4">
          <IconButton
              as="a"
              href="https://discord.gg/thegenuinecollective"
              target="_blank"
              rel="noopener noreferrer"
              size="sm"
              variant="ghost"
              color={getButtonColor()}
              icon={<FaDiscord />}
              aria-label="Join our Discord"
              rounded="full"
            />
            <IconButton
              as="a"
              href="https://www.linkedin.com/company/thegenuinecollective/"
              target="_blank"
              rel="noopener noreferrer"
              size="sm"
              variant="ghost"
              color={getButtonColor()}
              icon={<FaLinkedin />}
              aria-label="Visit our LinkedIn"
              rounded="full"
            />
            <ContactButton 
              href="/contact" 
              invert={isInverted}
              fillOnHover={true}
            >
              Contact us
            </ContactButton>
            
            <IconButton 
              onClick={toggleColorMode} 
              size="sm" 
              variant="ghost"
              color={getButtonColor()}
              icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
              aria-label={`Switch to ${colorMode === "light" ? "dark" : "light"} mode`}
            />
            <IconButton
              ref={toggleRef}
              onClick={onToggle}
              rounded="full"
              aria-expanded={expanded}
              aria-controls={panelId}
              color={getButtonColor()}
              bg={getButtonBgColor()}
              aria-label="Toggle navigation"
              icon={expanded ? <CloseIcon /> : <HamburgerIcon />}
              variant="ghost"
              _hover={{
                bg: expanded ? (colorMode === 'dark' ? 'gray.200' : 'gray.700') : 'gray.100',
              }}
              _active={{
                bg: expanded ? (colorMode === 'dark' ? 'gray.300' : 'gray.600') : 'gray.200',
              }}
            />
          </Flex>
        </Flex>
      </Container>
    </Box>
  );
};

const RootLayoutInner = ({ children }) => {
  const [expanded, setExpanded] = useState(false);
  const { colorMode } = useColorMode();
  const bgColor = useColorModeValue("white", "black");
  const textColor = useColorModeValue("gray.800", "white");
  const toggleRef = useRef(null);
  const panelId = useId();

  const toggleNavigation = () => {
    setExpanded((prev) => !prev);
  };

  return (
    <Box>
      <Header
        panelId={panelId}
        expanded={expanded}
        onToggle={toggleNavigation}
        toggleRef={toggleRef}
      />
      <MainNavigation expanded={expanded} onToggle={toggleNavigation} panelId={panelId} />
      <Box 
        bg={expanded ? (colorMode === 'dark' ? 'white' : 'black') : bgColor} 
        color={expanded ? (colorMode === 'dark' ? 'black' : 'white') : textColor}
        transition="background-color 0.3s, color 0.3s"
      >
        {children}
      </Box>
    </Box>
  );
};

const RootLayout = ({ children }) => {
  const pathName = usePathname();
  return <RootLayoutInner key={pathName}>{children}<FloatingNavbar /></RootLayoutInner>;
};

export default RootLayout;
