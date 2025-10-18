import RootLayout from "@/components/RootLayout";
import { Providers } from "@/components/Providers";
import { Space_Grotesk } from "next/font/google";
export const metadata = {
  metadataBase: new URL("https://thegenuine.co.uk"),
  title: {
    default: "The Genuine Collective",
    template: "%s | The Genuine Collective",
  },
  description: "We craft genuine technology solutions for authentic brands.",
  openGraph: {
    title: "The Genuine Collective",
    description: "We craft genuine technology solutions for authentic brands.",
    url: "https://thegenuine.co.uk",
    siteName: "The Genuine Collective",
    images: [
      {
        url: "/genuine-collective.PNG",
      },
    ],
    locale: "en_GB",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "The Genuine Collective",
    description: "We craft genuine technology solutions for authentic brands.",
    creator: "@thegenuineco",
    images: ["/genuine-collective.PNG"],
  },
  icons: {
    icon: "/favicon.ico",
  },
};
import "./globals.css";

export const viewport = {
  themeColor: "#ffffff",
};

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export default function Layout({ children }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} antialiased`}>
      <body>
        <Providers>
          <RootLayout>{children}</RootLayout>
        </Providers>
      </body>
    </html>
  );
}
