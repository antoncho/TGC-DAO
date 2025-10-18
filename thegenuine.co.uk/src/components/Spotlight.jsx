import React from "react";
import { cn } from "../../lib/utils";  // Corrected import path
import { useColorModeValue } from '@chakra-ui/react';

export const Spotlight = ({ className }) => {
  const gradientId = useColorModeValue('spotlightGradientLight', 'spotlightGradientDark');
  const opacity = useColorModeValue(0.15, 0.3); // Adjust these values as needed

  return (
    <svg
      className={cn(
        "animate-spotlight pointer-events-none absolute z-0",
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 3787 2842"
      fill="none"
    >
      <defs>
        <radialGradient id="spotlightGradientLight" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(0 2194.66 -2910.97 0 1893.5 647.664)">
          <stop stopColor="#7775D6"/>
          <stop offset="1" stopColor="#E935C1" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="spotlightGradientDark" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(0 2194.66 -2910.97 0 1893.5 647.664)">
          <stop stopColor="#7775D6"/>
          <stop offset="1" stopColor="#E935C1" stopOpacity="0"/>
        </radialGradient>
      </defs>
      <g opacity={opacity}>
        <ellipse
          cx="1893.5"
          cy="647.664"
          rx="2910.97"
          ry="2194.66"
          transform="rotate(-90 1893.5 647.664)"
          fill={`url(#${gradientId})`}
        />
      </g>
    </svg>
  );
};