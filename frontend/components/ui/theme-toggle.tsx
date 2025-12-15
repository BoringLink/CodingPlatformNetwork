"use client";

import React, { useEffect } from "react";
import { Button } from "./button";
import { Moon, Sun } from "lucide-react";
import { useUIStore } from "@/store/ui-store";

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useUIStore();

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    const isDark = theme === "dark" || 
                  (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      aria-label="切换主题"
      className="h-8 w-8"
    >
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">切换主题</span>
    </Button>
  );
};