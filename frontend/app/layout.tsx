import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export const metadata: Metadata = {
  title: "教育知识图谱系统",
  description: "基于知识图谱的教育数据分析平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="antialiased">
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
