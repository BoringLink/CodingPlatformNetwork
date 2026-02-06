import { PrismaClient } from '@prisma/client';
import * as dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

async function testDatabaseConnection() {
  const prisma = new PrismaClient();

  try {
    console.log('正在连接数据库...');
    // 测试连接
    await prisma.$connect();
    console.log('数据库连接成功！');

    // 测试基础查询
    console.log('测试基础查询...');
    const studentsCount = await prisma.student.count();
    console.log(`学生表中有 ${studentsCount} 条记录`);

    const teachersCount = await prisma.teacher.count();
    console.log(`教师表中有 ${teachersCount} 条记录`);

    const knowledgeCount = await prisma.knowledge.count();
    console.log(`知识点表中有 ${knowledgeCount} 条记录`);

    const interactionsCount = await prisma.interaction.count();
    console.log(`交互表中有 ${interactionsCount} 条记录`);

    console.log('数据库操作测试成功！');
  } catch (error) {
    console.error('数据库连接或操作失败:', error);
  } finally {
    // 关闭连接
    await prisma.$disconnect();
    console.log('数据库连接已关闭');
  }
}

testDatabaseConnection();