import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Sidebar } from "@/components/sidebar";
import { QueryProvider } from "@/lib/query-provider";
import { AuthProvider } from "@/lib/auth-context";
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
        <AuthProvider>
          <QueryProvider>
            <Sidebar />
            <main className="min-h-screen pt-18 px-4 pb-8 lg:pt-8 lg:ml-56 lg:px-8 lg:pb-8">
              {children}
            </main>
          </QueryProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
