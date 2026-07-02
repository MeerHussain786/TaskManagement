import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono, Orbitron } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-geist-sans", // keeping the variable name so we don't have to change tailwind.config
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const orbitron = Orbitron({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["400", "700", "900"],
});

export const metadata: Metadata = {
  title: "Task Management SaaS",
  description: "Enterprise Task Management Frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${jetbrainsMono.variable} ${orbitron.variable} antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans antialiased">
          <Providers
            attribute="class"
            defaultTheme="dark"
            enableSystem={false}
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
