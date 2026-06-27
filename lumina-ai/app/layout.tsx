import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-geist",
  display: "swap",
});

// JetBrains Mono from Google Fonts for mono labels
const jetbrainsMono = Inter({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Lumina AI — The AI Hiring Challenge",
  description:
    "Join the Lumina AI challenge — build the future of intelligent talent acquisition. Compete for ₹15 Lakhs in prizes across two tracks: Data & AI and Ideathon.",
  keywords: [
    "AI hiring",
    "machine learning challenge",
    "hackathon",
    "talent acquisition AI",
    "resume ranking",
    "data science competition",
    "Lumina AI",
  ],
  openGraph: {
    title: "Lumina AI — The AI Hiring Challenge",
    description:
      "Build the future of intelligent talent acquisition. Compete for ₹15 Lakhs in prizes.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-textPrimary antialiased">
        {children}
      </body>
    </html>
  );
}
