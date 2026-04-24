import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Sidebar } from "@/components/sidebar";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Forge — Control Panel",
  description: "Autonomous 3D-printing micro-business operator dashboard",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased`}>
        <Sidebar />
        <main className="min-h-screen pt-14 px-4 pb-6 lg:pt-0 lg:ml-56 lg:p-6">
          {children}
        </main>
      </body>
    </html>
  );
}
