import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";

interface CacheItem {
  data: any;
  timestamp: number;
  ttl: number;
}

class MemoryCache {
  private cache: Map<string, CacheItem> = new Map();

  get(key: string): any {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key: string, data: any, ttl: number = 3600000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  clear(): void {
    this.cache.clear();
  }

  delete(key: string): void {
    this.cache.delete(key);
  }
}

@Injectable()
export class OrgService {
  private cache = new MemoryCache();
  private readonly CACHE_TTL = 3600000; // 1 hour

  constructor(private readonly prisma: PrismaService) {}

  async getSchools() {
    const cacheKey = 'schools';
    const cachedData = this.cache.get(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const validClassIds = await this.prisma.graphNode.findMany({
      where: {
        OR: [
          { nodeType: "Student" },
          { nodeType: "Teacher" }
        ],
        classId: { not: null }
      },
      select: { classId: true }
    }).then(nodes => nodes.map(node => node.classId).filter(Boolean) as string[]);

    const schools = await this.prisma.school.findMany({
      where: {
        grades: {
          some: {
            classes: {
              some: {
                id: { in: validClassIds }
              }
            }
          }
        }
      },
      select: { id: true, name: true },
      orderBy: { name: "asc" },
    });

    const result = {
      data: schools,
      meta: null,
      error: null,
    };

    this.cache.set(cacheKey, result, this.CACHE_TTL);
    return result;
  }

  async getGrades(schoolId: string) {
    const cacheKey = `grades:${schoolId}`;
    const cachedData = this.cache.get(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const validClassIds = await this.prisma.graphNode.findMany({
      where: {
        OR: [
          { nodeType: "Student" },
          { nodeType: "Teacher" }
        ],
        classId: { not: null }
      },
      select: { classId: true }
    }).then(nodes => nodes.map(node => node.classId).filter(Boolean) as string[]);

    const grades = await this.prisma.grade.findMany({
      where: {
        schoolId,
        classes: {
          some: {
            id: { in: validClassIds }
          }
        }
      },
      select: {
        id: true,
        gradeName: true,
      },
      orderBy: { gradeName: "asc" },
    });

    const result = {
      data: grades,
      meta: null,
      error: null,
    };

    this.cache.set(cacheKey, result, this.CACHE_TTL);
    return result;
  }

  async getClasses(gradeId: string) {
    const cacheKey = `classes:${gradeId}`;
    const cachedData = this.cache.get(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const validClassIds = await this.prisma.graphNode.findMany({
      where: {
        OR: [
          { nodeType: "Student" },
          { nodeType: "Teacher" }
        ],
        classId: { not: null }
      },
      select: { classId: true }
    }).then(nodes => nodes.map(node => node.classId).filter(Boolean) as string[]);

    const classes = await this.prisma.schoolClass.findMany({
      where: {
        gradeId,
        id: { in: validClassIds }
      },
      select: {
        id: true,
        className: true,
      },
      orderBy: { className: "asc" },
    });

    const result = {
      data: classes,
      meta: null,
      error: null,
    };

    this.cache.set(cacheKey, result, this.CACHE_TTL);
    return result;
  }

  async getOrgHierarchy() {
    const cacheKey = 'org:hierarchy';
    const cachedData = this.cache.get(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const validClassIds = await this.prisma.graphNode.findMany({
      where: {
        OR: [
          { nodeType: "Student" },
          { nodeType: "Teacher" }
        ],
        classId: { not: null }
      },
      select: { classId: true }
    }).then(nodes => nodes.map(node => node.classId).filter(Boolean) as string[]);

    const schools = await this.prisma.school.findMany({
      where: {
        grades: {
          some: {
            classes: {
              some: {
                id: { in: validClassIds }
              }
            }
          }
        }
      },
      select: {
        id: true,
        name: true,
        grades: {
          where: {
            classes: {
              some: {
                id: { in: validClassIds }
              }
            }
          },
          select: {
            id: true,
            gradeName: true,
            classes: {
              where: {
                id: { in: validClassIds }
              },
              select: {
                id: true,
                className: true
              },
              orderBy: { className: "asc" }
            }
          },
          orderBy: { gradeName: "asc" }
        }
      },
      orderBy: { name: "asc" }
    });

    const result = {
      data: schools,
      meta: null,
      error: null,
    };

    this.cache.set(cacheKey, result, this.CACHE_TTL);
    return result;
  }
}
