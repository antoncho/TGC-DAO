import React from "react";
import GridPattern from "./GridPattern";
import clsx from "clsx";
import Container from "./Container";
import FadeIn from "./FadeIn";
import Image from "next/image";
import { Box, useColorModeValue } from "@chakra-ui/react";

const Testimonials = ({ children, client, className }) => {
  const bgColor = useColorModeValue("white", "black");

  return (
    <Box
      className={clsx(
        "relative isolate bg-white dark:bg-black py-16 sm:py-28 md:py-32",
        className
      )}
      style={{ backgroundColor: bgColor }}
    >
      <GridPattern
        className="absolute inset-0 -z-10 h-full w-full fill-neutral-100 stroke-neutral-950/5 [mask-image:linear-gradient(to_bottom_left,white_50%,transparent_60%)]"
        yOffset={-256}
      />
      <Container>
        <FadeIn>
          <figure className="mx-auto max-w-4xl">
            <blockquote className="relative font-display text-3xl sm:text-4xl">
              <p className="before:content-['“'] after:content-['”'] sm:before:absolute sm:before:right-full  font-medium text-black dark:text-white tracking-tight">
                {children}
              </p>
            </blockquote>
            <figcaption className="mt-10">
              {client.logo ? (
                <Image src={client.logo} alt={client.name} unoptimized />
              ) : (
                <div style={{ width: 120, height: 60, background: '#eee' }} />
              )}
            </figcaption>
          </figure>
        </FadeIn>
      </Container>
    </Box>
  );
};

export default Testimonials;
