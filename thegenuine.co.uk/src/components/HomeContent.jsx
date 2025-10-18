"use client";

import React from 'react';
import { useColorMode, useColorModeValue, IconButton, Box, VStack, Text } from "@chakra-ui/react";

import Clients from "@/components/Clients";
import ContactSection from "@/components/ContactSection";
import Container from "@/components/Container";
import FadeIn from "@/components/FadeIn";
import Services from "@/components/Services";
import Testimonials from "@/components/Testimonials";
import logoPhobiaDark from "@/images/clients/phobia/logo-dark.svg";
import HomeHero from '@/components/HomeHero';
import SectionTechnologies from './SectionTechnologies';
import HoverImageLinks from '@/components/SectionTechnologies';
import SectionAbout from '@/components/SectionAbout';
import Footer from '@/components/Footer';
export default function HomeContent() {

  return (
    <Box as="main" className="page-container max-w-9xl mx-auto overflow-hidden">
      
      
      <HomeHero />
      <SectionAbout />
      <Services />
      <Clients />
      <Testimonials
        className="mt-24 sm:mt-32 lg:mt-40"
        client={{ name: "Lora Gene", logo: logoPhobiaDark }}
      >
        The Genuine Collective helped us cut through complexity and ship value
        fast. Clear communication, thoughtful planning, and rock‑solid delivery.
        — Lora Nikolaeva, Director, Lora Gene Clothing
      </Testimonials>
      <ContactSection />
      <Footer />
    </Box>
  );
}
