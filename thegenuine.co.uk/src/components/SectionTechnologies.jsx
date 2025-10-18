import React from "react";
import { useAnimate, motion } from "framer-motion";
import { Box, useColorModeValue, Grid, Divider, Icon } from "@chakra-ui/react";
import { SiCardano, SiDogecoin, SiPolkadot, SiRipple, SiBitcoin, SiEthereum, SiLitecoin, SiMonero, SiTether } from "react-icons/si";

// Define the constants
const NO_CLIP = "polygon(0 0, 100% 0, 100% 100%, 0% 100%)";
const BOTTOM_RIGHT_CLIP = "polygon(0 0, 100% 0, 0 0, 0% 100%)";
const TOP_RIGHT_CLIP = "polygon(0 0, 0 100%, 100% 100%, 0% 100%)";
const BOTTOM_LEFT_CLIP = "polygon(100% 100%, 100% 0, 100% 100%, 0 100%)";
const TOP_LEFT_CLIP = "polygon(0 0, 100% 0, 100% 100%, 100% 0)";

const ENTRANCE_KEYFRAMES = {
  left: [BOTTOM_RIGHT_CLIP, NO_CLIP],
  bottom: [BOTTOM_RIGHT_CLIP, NO_CLIP],
  top: [BOTTOM_RIGHT_CLIP, NO_CLIP],
  right: [TOP_LEFT_CLIP, NO_CLIP],
};

const EXIT_KEYFRAMES = {
  left: [NO_CLIP, TOP_RIGHT_CLIP],
  bottom: [NO_CLIP, TOP_RIGHT_CLIP],
  top: [NO_CLIP, TOP_RIGHT_CLIP],
  right: [NO_CLIP, BOTTOM_LEFT_CLIP],
};

const LinkBox = ({ Icon, href }) => {
  const [scope, animate] = useAnimate();
  const bgColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");
  const iconColor = useColorModeValue("black", "gray.100");
  const hoverIconColor = useColorModeValue("black", "white");

  const getNearestSide = (e) => {
    const box = e.currentTarget.getBoundingClientRect();
    const { clientX, clientY } = e;

    const distances = [
      { side: "left", distance: Math.abs(box.left - clientX) },
      { side: "right", distance: Math.abs(box.right - clientX) },
      { side: "top", distance: Math.abs(box.top - clientY) },
      { side: "bottom", distance: Math.abs(box.bottom - clientY) },
    ];

    return distances.reduce((nearest, current) => 
      current.distance < nearest.distance ? current : nearest
    ).side;
  };

  const handleMouseEnter = (e) => {
    const side = getNearestSide(e);
    animate(scope.current, {
      clipPath: ENTRANCE_KEYFRAMES[side],
    });
  };

  const handleMouseLeave = (e) => {
    const side = getNearestSide(e);
    animate(scope.current, {
      clipPath: EXIT_KEYFRAMES[side],
    });
  };

  return (
    <Box
      as="a"
      href={href}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      position="relative"
      display="grid"
      placeContent="center"
      h={{ base: "7rem", sm: "9rem", md: "11rem" }}
      w="full"
    >
      <motion.div
        whileHover={{ scale: 1.1 }}
        transition={{ type: "spring", stiffness: 300, damping: 10 }}
      >
        <Icon 
          as={Icon} 
          boxSize={{ base: "40px", md: "56px", lg: "72px" }} 
          color={iconColor}
          transition="all 0.3s"
          _hover={{
            color: hoverIconColor,
            filter: "drop-shadow(0 0 8px currentColor)",
          }}
        />
      </motion.div>

      <Box
        ref={scope}
        style={{
          clipPath: BOTTOM_RIGHT_CLIP,
        }}
        position="absolute"
        inset={0}
        display="grid"
        placeContent="center"
        bg={bgColor}
      >
        <motion.div
          whileHover={{ scale: 1.1 }}
          transition={{ type: "spring", stiffness: 300, damping: 10 }}
        >
          <Icon 
            as={Icon} 
            boxSize={{ base: "40px", md: "56px", lg: "72px" }} 
            color={hoverIconColor}
            filter="drop-shadow(0 0 8px currentColor)"
            transition="all 0.3s"
          />
        </motion.div>
      </Box>
    </Box>
  );
};

export const ClipPathLinks = () => {
  const borderColor = useColorModeValue("gray.200", "gray.700");

  return (
    <Box borderWidth={1} borderColor={borderColor}>
      <Grid templateColumns="repeat(2, 1fr)" divider={<Divider orientation="vertical" />}>
        <LinkBox Icon={SiBitcoin} href="#" />
        <LinkBox Icon={SiEthereum} href="#" />
      </Grid>
      <Divider />
      <Grid templateColumns="repeat(4, 1fr)" divider={<Divider orientation="vertical" />}>
        <LinkBox Icon={SiLitecoin} href="#" />
        <LinkBox Icon={SiMonero} href="#" />
        <LinkBox Icon={SiDogecoin} href="#" />
        <LinkBox Icon={SiCardano} href="#" />
      </Grid>
      <Divider />
      <Grid templateColumns="repeat(3, 1fr)" divider={<Divider orientation="vertical" />}>
        <LinkBox Icon={SiPolkadot} href="#" />
        <LinkBox Icon={SiRipple} href="#" />
        <LinkBox Icon={SiTether} href="#" />
      </Grid>
    </Box>
  );
};

const SectionTechnologies = () => {
  const bgColor = useColorModeValue("white", "black");

  return (
    <Box bg={bgColor} px={4} py={12}>
      <Box maxW="7xl" mx="auto">
        <ClipPathLinks />
      </Box>
    </Box>
  );
};

export default SectionTechnologies;