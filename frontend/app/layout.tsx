import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export const metadata: Metadata = {
  title: "交互网络可视化系统",
  description: "基于交互网络的可视化分析平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <QueryProvider>
          {children}
          {/* Theme Toggle */}
          <div className="fixed bottom-4 right-4 z-50">
            <ThemeToggle />
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
