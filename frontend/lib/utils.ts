import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return ""; // 防 null/undefined
  const d = typeof date === "string" ? new Date(date) : date; // 转换字符串
  if (!(d instanceof Date) || isNaN(d.getTime())) return ""; // 守卫无效 Date
  return d.toLocaleDateString(); // 本地化格式
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
  options?: { immediate?: boolean }
) {
  let timer: NodeJS.Timeout | null = null;

  const debounced = function (...args: Parameters<T>) {
    const later = () => {
      timer = null;
      if (!options?.immediate) {
        fn(...args);
      }
    };

    const callNow = options?.immediate && !timer;

    if (timer) {
      clearTimeout(timer);
    }

    timer = setTimeout(later, delay);

    if (callNow) {
      fn(...args);
    }
  };

  debounced.cancel = () => {
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
  };

  return debounced;
}
