import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthGuard } from "@/components/AuthGuard";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sistema de Detección de Infracciones - Dashboard",
  description: "Dashboard en tiempo real para monitoreo de infracciones de tránsito",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50`}>
        <AuthGuard>
          <div className="min-h-full">
            {children}
          </div>
        </AuthGuard>
      </body>
    </html>
  );
}
