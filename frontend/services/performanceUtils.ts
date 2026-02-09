/**
 * 缓存工具类
 */
export class Cache {
  private cache: Map<string, { data: any; timestamp: number }>;
  private defaultTTL: number;

  constructor(defaultTTL: number = 5 * 60 * 1000) { // 默认5分钟
    this.cache = new Map();
    this.defaultTTL = defaultTTL;
  }

  /**
   * 设置缓存
   */
  set(key: string, data: any, _ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * 获取缓存
   */
  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // 检查是否过期
    if (Date.now() - item.timestamp > this.defaultTTL) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  /**
   * 删除缓存
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 获取缓存大小
   */
  size(): number {
    return this.cache.size;
  }
}

// 创建全局缓存实例
export const graphDataCache = new Cache(5 * 60 * 1000); // 5分钟缓存

/**
 * 生成缓存键
 */
export const generateCacheKey = (prefix: string, params: Record<string, any>): string => {
  const sortedParams = Object.keys(params)
    .sort()
    .map(key => `${key}:${params[key]}`)
    .join('|');
  return `${prefix}:${sortedParams}`;
};

/**
 * 防抖函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate: boolean = false
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return function(this: any, ...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };

    const callNow = immediate && !timeout;

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func.apply(this, args);
  };
};

/**
 * 节流函数
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle = false;

  return function(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * 带缓存的异步函数包装器
 */
export const withCache = async <T>(
  key: string,
  fn: () => Promise<T>,
  cache: Cache = graphDataCache
): Promise<T> => {
  // 尝试从缓存获取
  const cachedData = cache.get(key);
  if (cachedData) {
    console.log(`从缓存获取数据: ${key}`);
    return cachedData as T;
  }

  // 缓存未命中，执行函数
  console.log(`缓存未命中，执行函数: ${key}`);
  const data = await fn();

  // 设置缓存
  cache.set(key, data);
  return data;
};
