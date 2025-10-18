import { Button, css, useColorModeValue } from "@chakra-ui/react";
import { keyframes } from "@emotion/react";
import Link from "next/link";

const shimmer = keyframes`
  from { background-position: 0 0; }
  to { background-position: -200% 0; }
`;

const shimmerAnimation = css`
  animation: ${shimmer} 2s linear infinite;
`;

const ContactButton = ({ href, invert, fillOnHover, children, ...props }) => {
  const bgGradient = useColorModeValue(
    invert
      ? "linear-gradient(110deg, #ffffff 45%, #e0e0e0 55%, #ffffff)"
      : "linear-gradient(110deg, #000103 45%, #1e2631 55%, #000103)",
    invert
      ? "linear-gradient(110deg, #000103 45%, #1e2631 55%, #000103)"
      : "linear-gradient(110deg, #ffffff 45%, #e0e0e0 55%, #ffffff)"
  );
  const textColor = useColorModeValue(
    invert ? "black" : "white",
    invert ? "white" : "black"
  );
  const borderColor = useColorModeValue(
    invert ? "gray.200" : "gray.800",
    invert ? "gray.800" : "gray.200"
  );
  const hoverBg = useColorModeValue(
    invert ? "blackAlpha.200" : "whiteAlpha.200",
    invert ? "whiteAlpha.200" : "blackAlpha.200"
  );
  const hoverColor = useColorModeValue(
    invert ? "white" : "black",
    invert ? "black" : "white"
  );

  const hoverStyles = fillOnHover
    ? {
        bg: hoverBg,
        color: hoverColor,
      }
    : {};

  return (
    <Button
      as={Link}
      href={href}
      height="10"
      rounded="full"
      border="1px"
      borderColor={borderColor}
      bg={bgGradient}
      bgSize="200% 100%"
      px="5"
      fontWeight="medium"
      fontSize="xs"
      color={textColor}
      transition="colors 0.2s"
      _focus={{
        outline: "none",
        ringColor: borderColor,
        ring: "2px",
        ringOffset: "2px",
        ringOffsetColor: useColorModeValue(
          invert ? "gray.800" : "white",
          invert ? "white" : "gray.800"
        ),
      }}
      _hover={hoverStyles}
      css={shimmerAnimation}
      {...props}
    >
      {children}
    </Button>
  );
};

export default ContactButton;