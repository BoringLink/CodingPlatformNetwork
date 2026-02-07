import { PrismaClient } from "@prisma/client";

/**
 * 数据查询脚本
 * 抽样查询学生、教师、知识点表的内容
 */
async function runDataQuery() {
  console.log("开始执行数据抽样查询...");

  const prisma = new PrismaClient();

  try {
    // 查询学生表数据（抽样10条）
    console.log("\n=== 学生表抽样数据 ===");
    const students = await prisma.student.findMany({
      take: 10,
      orderBy: { createdAt: "desc" },
    });

    console.log(`学生表总记录数: ${students.length}`);
    students.forEach((student, index) => {
      console.log(
        `${index + 1}. ${student.name} - ${student.school} - ${student.grade}${
          student.classId
        }`,
      );
      console.log(
        `   知识储备: ${student.knowledgeReserve}, 学习动机: ${student.learningMotivation}`,
      );
      console.log(
        `   学习态度: ${student.learningAttitude}, 学习投入: ${student.learningEngagement}`,
      );
    });

    // 查询教师表数据（抽样10条）
    console.log("\n=== 教师表抽样数据 ===");
    const teachers = await prisma.teacher.findMany({
      take: 10,
      orderBy: { createdAt: "desc" },
    });

    console.log(`教师表总记录数: ${teachers.length}`);
    teachers.forEach((teacher, index) => {
      console.log(`${index + 1}. ${teacher.name} - ${teacher.school}`);
      console.log(
        `   教学年级: ${teacher.teachingGrade}, 教学班级: ${teacher.teachingClass}`,
      );
    });

    // 查询知识点表数据（抽样10条）
    console.log("\n=== 知识点表抽样数据 ===");
    const knowledgePoints = await prisma.knowledge.findMany({
      take: 10,
      orderBy: { createdAt: "desc" },
    });

    console.log(`知识点表总记录数: ${knowledgePoints.length}`);
    knowledgePoints.forEach((knowledge, index) => {
      console.log(
        `${index + 1}. ${knowledge.knowledgePoint} - 年级: ${knowledge.grade}`,
      );
      console.log(
        `   类型: ${knowledge.type}, 父知识点: ${knowledge.parentName}`,
      );
      console.log(`   内容: ${knowledge.content.substring(0, 50)}...`);
    });

    // 查询交互表数据（抽样10条）
    console.log("\n=== 交互表抽样数据 ===");
    const interactions = await prisma.interaction.findMany({
      take: 10,
      orderBy: { createdAt: "desc" },
    });

    console.log(`交互表总记录数: ${interactions.length}`);
    interactions.forEach((interaction, index) => {
      console.log(
        `${index + 1}. ${interaction.sourceType} -> ${interaction.targetType}`,
      );
      console.log(
        `   类型: ${interaction.interactionType}, 值: ${interaction.value}`,
      );
    });

    console.log("\n数据抽样查询完成！");
  } catch (error) {
    console.error("数据查询失败:", error);
  } finally {
    await prisma.$disconnect();
  }
}

// 运行查询脚本
runDataQuery();
