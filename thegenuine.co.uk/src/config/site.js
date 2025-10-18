import { useColorMode } from '@chakra-ui/react'

export function constructMetadata({
  title = "The Genuine Collective",
  description = "We craft genuine technology solutions for authentic brands.",
  image = "/genuine-collective.PNG",
  icons = "/favicon.ico",
  noIndex = false,
}) {
  // themeColor is now static; cannot use colorMode hook here
  const themeColor = "#FFF";

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      images: [
        {
          url: image,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
      creator: "@thegenuineco",
    },
    icons,
    metadataBase: new URL("https://thegenuine.co.uk"),
    themeColor,
    ...(noIndex && {
      robots: {
        index: false,
        follow: false,
      },
    }),
  };
}
