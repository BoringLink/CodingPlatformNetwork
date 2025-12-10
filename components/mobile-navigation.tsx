"use client";

import React from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { Menu, X, ChevronRight } from "lucide-react";

interface NavigationItem {
  label: string;
  href: string;
}

const navigationItems: NavigationItem[] = [
  { label: "首页", href: "/" },
  { label: "图可视化", href: "/graph" },
  { label: "数据导入", href: "/import" },
  { label: "报告生成", href: "/reports" },
];

export function MobileNavigation() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-6 w-6" />
          <span className="sr-only">打开菜单</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[240px] sm:w-[300px]">
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between py-4">
            <h2 className="text-xl font-bold">教育知识图谱</h2>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <X className="h-5 w-5" />
                <span className="sr-only">关闭菜单</span>
              </Button>
            </SheetTrigger>
          </div>
          
          <nav className="flex-1 space-y-2">
            {navigationItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-accent transition-colors"
              >
                <span className="font-medium">{item.label}</span>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            ))}
          </nav>
          
          <div className="border-t pt-4">
            <p className="text-sm text-muted-foreground text-center">
              © 2025 教育知识图谱系统
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}