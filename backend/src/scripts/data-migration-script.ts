import { PrismaClient } from "@prisma/client";
import * as XLSX from "xlsx";
import * as fs from "fs";
import * as path from "path";

/**
 * Excel文件读取工具类
 */
class ExcelReaderUtil {
  /**
   * 读取Excel文件
   * @param filePath 文件路径
   * @returns 工作表数据
   */
  static readExcelFile(filePath: string): Record<string, any[]> {
    if (!fs.existsSync(filePath)) {
      throw new Error(`文件不存在: ${filePath}`);
    }

    const workbook = XLSX.readFile(filePath);
    const sheets: Record<string, any[]> = {};

    workbook.SheetNames.forEach((sheetName) => {
      const worksheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(worksheet, {
        header: 1,
        defval: "",
      });

      if (data.length > 0) {
        const headers = data[0] as any[];
        const rows = data.slice(1);

        const formattedData = rows.map((row) => {
          const rowData: any = {};
          if (headers && Array.isArray(headers)) {
            headers.forEach((header: any, index: number) => {
              rowData[header] = row[index] || "";
            });
          }
          return rowData;
        });

        sheets[sheetName] = formattedData;
      }
    });

    return sheets;
  }
}

/**
 * 数据迁移脚本
 */
async function runDataMigration() {
  console.log("开始执行数据迁移...");

  const prisma = new PrismaClient();

  try {
    // 1. 迁移问卷数据到学生表
    console.log("\n=== 迁移问卷数据 ===");
    await migrateQuestionnaireData(prisma);

    // 2. 迁移作品数据到交互表
    console.log("\n=== 迁移作品数据 ===");
    await migrateWorkData(prisma);

    // 3. 迁移AI助手使用数据到交互表
    console.log("\n=== 迁移AI助手使用数据 ===");
    await migrateAiUsageData(prisma);

    // 4. 验证迁移结果
    console.log("\n=== 验证迁移结果 ===");
    await verifyMigration(prisma);

    console.log("\n数据迁移完成！");
  } catch (error) {
    console.error("数据迁移失败:", error);
  } finally {
    await prisma.$disconnect();
  }
}

/**
 * 迁移问卷数据到学生表
 */
async function migrateQuestionnaireData(prisma: PrismaClient) {
  const filePath = path.join(
    __dirname,
    "../../../Real Data/调研问卷明细 0115.xlsx",
  );

  try {
    const sheets = ExcelReaderUtil.readExcelFile(filePath);

    let total = 0;
    let successful = 0;
    let failed = 0;
    const batchSize = 200;
    let batchCount = 0;

    for (const [sheetName, data] of Object.entries(sheets)) {
      console.log(`处理工作表: ${sheetName}, 记录数: ${data.length}`);
      total += data.length;

      // 批量处理
      const batches = [];
      for (let i = 0; i < data.length; i += batchSize) {
        batches.push(data.slice(i, i + batchSize));
      }

      for (const batch of batches) {
        batchCount++;
        let batchSuccessful = 0;
        let batchFailed = 0;

        console.log(`开始处理第 ${batchCount} 批数据, 记录数: ${batch.length}`);

        for (const row of batch) {
          try {
            // 解析学生数据
            const studentData = parseQuestionnaireRow(row);
            if (!studentData) {
              batchFailed++;
              continue;
            }

            // 检查学生是否已存在
            const existingStudent = await prisma.student.findFirst({
              where: {
                name: studentData.name,
                school: studentData.school,
                grade: studentData.grade,
                classId: studentData.classId,
              },
            });

            if (existingStudent) {
              // 更新现有学生
              await prisma.student.update({
                where: { id: existingStudent.id },
                data: studentData,
              });
            } else {
              // 创建新学生
              await prisma.student.create({
                data: studentData,
              });
            }

            batchSuccessful++;
          } catch (error) {
            console.error(`处理问卷数据失败: ${error.message}`);
            batchFailed++;
          }
        }

        // 验证批次数据
        console.log(
          `第 ${batchCount} 批处理完成: 成功 ${batchSuccessful}, 失败 ${batchFailed}`,
        );

        // 验证数据库中的记录数
        const batchStudents = await prisma.student.findMany({
          take: batchSuccessful,
          orderBy: { createdAt: "desc" },
        });

        if (batchStudents.length === batchSuccessful) {
          console.log(`第 ${batchCount} 批数据验证通过`);
        } else {
          console.error(
            `第 ${batchCount} 批数据验证失败: 期望 ${batchSuccessful}, 实际 ${batchStudents.length}`,
          );
        }

        successful += batchSuccessful;
        failed += batchFailed;
      }
    }

    console.log(
      `问卷数据迁移完成: 总计 ${total} 条记录, 成功 ${successful} 条, 失败 ${failed} 条`,
    );
  } catch (error) {
    console.error(`读取问卷文件失败: ${error.message}`);
  }
}

/**
 * 解析问卷数据行
 */
function parseQuestionnaireRow(row: any) {
  // 解析Sheet1的数据结构
  if (row["陆雨欣"] !== undefined) {
    return {
      name: row["陆雨欣"] || row["项目"] || "",
      school: row["湖州市爱山小学教育集团常溪小学"] || row["学校"] || "",
      grade: row["5年级"] || row["年级"] || "",
      classId: row["新五年级2班"] || row["班级"] || "",
      knowledgeReserve: calculateScore(row, [14, 15, 16, 17, 18, 19]),
      learningMotivation: calculateScore(row, [20, 21, 22]),
      learningAttitude: calculateScore(row, [23, 24, 25]),
      learningEngagement: calculateScore(row, [26, 27, 28]),
      computationalThinking: calculateScore(row, [29, 30, 31]),
      learningMethod: calculateScore(row, [32, 33, 34]),
      cognitiveLoad: calculateScore(row, [35, 36, 37]),
      humanAiTrust: calculateScore(row, [38, 39, 40]),
    };
  }

  return null;
}

/**
 * 计算得分
 */
function calculateScore(row: any, columnIndices: number[]) {
  const scores = columnIndices.map((index) => {
    const value = row[index] || row[`${index}`] || row[`${index}.1`];
    return mapAnswerToScore(value);
  });

  const validScores = scores.filter((score) => score !== null);
  if (validScores.length === 0) {
    return 0;
  }

  return (
    validScores.reduce((sum, score) => sum + score, 0) / validScores.length
  );
}

/**
 * 将答案映射为得分
 */
function mapAnswerToScore(answer: string): number {
  const answerMap: Record<string, number> = {
    非常同意: 5,
    同意: 4,
    一般: 3,
    不同意: 2,
    非常不同意: 1,
  };

  return answerMap[answer] || 0;
}

/**
 * 迁移作品数据到交互表
 */
async function migrateWorkData(prisma: PrismaClient) {
  // 处理作品评论数据
  const commentFilePath = path.join(
    __dirname,
    "../../../Real Data/260115作品评论明细.xlsx",
  );

  // 处理作品点赞数据
  const likeFilePath = path.join(
    __dirname,
    "../../../Real Data/260115作品点赞明细查询.xlsx",
  );

  let total = 0;
  let successful = 0;
  let failed = 0;
  const batchSize = 200;

  async function processWorkBatch(
    data: any[],
    interactionType: "comment" | "like",
    batchCount: number,
  ) {
    let batchSuccessful = 0;
    let batchFailed = 0;

    console.log(
      `开始处理第 ${batchCount} 批 ${interactionType} 数据, 记录数: ${data.length}`,
    );

    for (const row of data) {
      try {
        await createWorkInteraction(prisma, row, interactionType);
        batchSuccessful++;
      } catch (error) {
        console.error(`处理${interactionType}数据失败: ${error.message}`);
        batchFailed++;
      }
    }

    // 验证批次数据
    console.log(
      `第 ${batchCount} 批 ${interactionType} 处理完成: 成功 ${batchSuccessful}, 失败 ${batchFailed}`,
    );

    // 验证数据库中的记录数
    const batchInteractions = await prisma.interaction.findMany({
      where: {
        interactionType: interactionType,
      },
      take: batchSuccessful,
      orderBy: { createdAt: "desc" },
    });

    if (batchInteractions.length >= batchSuccessful) {
      console.log(`第 ${batchCount} 批 ${interactionType} 数据验证通过`);
    } else {
      console.error(
        `第 ${batchCount} 批 ${interactionType} 数据验证失败: 期望 ${batchSuccessful}, 实际 ${batchInteractions.length}`,
      );
    }

    return { batchSuccessful, batchFailed };
  }

  try {
    const commentSheets = ExcelReaderUtil.readExcelFile(commentFilePath);
    for (const [sheetName, data] of Object.entries(commentSheets)) {
      console.log(`处理评论工作表: ${sheetName}, 记录数: ${data.length}`);
      total += data.length;

      // 批量处理
      const batches = [];
      for (let i = 0; i < data.length; i += batchSize) {
        batches.push(data.slice(i, i + batchSize));
      }

      for (let i = 0; i < batches.length; i++) {
        const { batchSuccessful, batchFailed } = await processWorkBatch(
          batches[i],
          "comment",
          i + 1,
        );
        successful += batchSuccessful;
        failed += batchFailed;
      }
    }
  } catch (error) {
    console.error(`读取评论文件失败: ${error.message}`);
  }

  try {
    const likeSheets = ExcelReaderUtil.readExcelFile(likeFilePath);
    for (const [sheetName, data] of Object.entries(likeSheets)) {
      console.log(`处理点赞工作表: ${sheetName}, 记录数: ${data.length}`);
      total += data.length;

      // 批量处理
      const batches = [];
      for (let i = 0; i < data.length; i += batchSize) {
        batches.push(data.slice(i, i + batchSize));
      }

      for (let i = 0; i < batches.length; i++) {
        const { batchSuccessful, batchFailed } = await processWorkBatch(
          batches[i],
          "like",
          i + 1,
        );
        successful += batchSuccessful;
        failed += batchFailed;
      }
    }
  } catch (error) {
    console.error(`读取点赞文件失败: ${error.message}`);
  }

  console.log(
    `作品数据迁移完成: 总计 ${total} 条记录, 成功 ${successful} 条, 失败 ${failed} 条`,
  );
}

/**
 * 创建作品交互记录
 */
async function createWorkInteraction(
  prisma: PrismaClient,
  row: any,
  interactionType: "comment" | "like",
) {
  const workId = row["作品id"] || row["作品ID"];
  const studentId = row["点赞学生id"] || row["学生ID"];

  if (!workId || !studentId) {
    throw new Error("缺少必要字段");
  }

  // 创建交互记录
  await prisma.interaction.create({
    data: {
      sourceId: studentId,
      targetId: workId.toString(),
      sourceType: "STUDENT",
      targetType: "KNOWLEDGE",
      value: interactionType === "like" ? 1 : 2,
      type: "PLATFORM",
      interactionType: interactionType,
    },
  });
}

/**
 * 迁移AI助手使用数据到交互表
 */
async function migrateAiUsageData(prisma: PrismaClient) {
  const filePath = path.join(
    __dirname,
    "../../../Real Data/260119学生AI助手使用数据.xlsx",
  );

  let total = 0;
  let successful = 0;
  let failed = 0;
  const batchSize = 200;
  let batchCount = 0;

  try {
    const sheets = ExcelReaderUtil.readExcelFile(filePath);

    for (const [sheetName, data] of Object.entries(sheets)) {
      console.log(`处理工作表: ${sheetName}, 记录数: ${data.length}`);
      total += data.length;

      // 批量处理
      const batches = [];
      for (let i = 0; i < data.length; i += batchSize) {
        batches.push(data.slice(i, i + batchSize));
      }

      for (const batch of batches) {
        batchCount++;
        let batchSuccessful = 0;
        let batchFailed = 0;

        console.log(
          `开始处理第 ${batchCount} 批AI助手使用数据, 记录数: ${batch.length}`,
        );

        for (const row of batch) {
          try {
            const aiData = parseAiUsageRow(row);
            if (!aiData) {
              batchFailed++;
              continue;
            }

            await prisma.interaction.create({
              data: aiData,
            });

            batchSuccessful++;
          } catch (error) {
            console.error(`处理AI助手使用数据失败: ${error.message}`);
            batchFailed++;
          }
        }

        // 验证批次数据
        console.log(
          `第 ${batchCount} 批AI助手使用数据处理完成: 成功 ${batchSuccessful}, 失败 ${batchFailed}`,
        );

        // 验证数据库中的记录数
        const batchInteractions = await prisma.interaction.findMany({
          where: {
            interactionType: "ai_usage",
          },
          take: batchSuccessful,
          orderBy: { createdAt: "desc" },
        });

        if (batchInteractions.length >= batchSuccessful) {
          console.log(`第 ${batchCount} 批AI助手使用数据验证通过`);
        } else {
          console.error(
            `第 ${batchCount} 批AI助手使用数据验证失败: 期望 ${batchSuccessful}, 实际 ${batchInteractions.length}`,
          );
        }

        successful += batchSuccessful;
        failed += batchFailed;
      }
    }
  } catch (error) {
    console.error(`读取AI助手使用文件失败: ${error.message}`);
  }

  console.log(
    `AI助手使用数据迁移完成: 总计 ${total} 条记录, 成功 ${successful} 条, 失败 ${failed} 条`,
  );
}

/**
 * 解析AI助手使用数据行
 */
function parseAiUsageRow(row: any) {
  const content = row["content"] || "";
  const userId = row["channel_user_id"] || "";
  const role = row["角色"] || "";
  const schoolId = row["学校Id"] || "";

  if (!content || !userId || !role) {
    return null;
  }

  return {
    sourceId: userId,
    targetId: schoolId,
    sourceType: role.toUpperCase() === "TEACHER" ? "TEACHER" : "STUDENT",
    targetType: "KNOWLEDGE",
    value: 1,
    type: "PLATFORM",
    interactionType: "ai_usage",
  };
}

/**
 * 验证迁移结果
 */
async function verifyMigration(prisma: PrismaClient) {
  const students = await prisma.student.count();
  const teachers = await prisma.teacher.count();
  const knowledge = await prisma.knowledge.count();
  const interactions = await prisma.interaction.count();

  console.log(
    `验证结果: 学生 ${students}, 教师 ${teachers}, 知识点 ${knowledge}, 交互 ${interactions}`,
  );

  // 检查数据质量
  const invalidStudents = await prisma.student.findMany({
    where: {
      OR: [{ name: "" }, { school: "" }, { grade: "" }, { classId: "" }],
    },
  });

  if (invalidStudents.length > 0) {
    console.warn(`发现 ${invalidStudents.length} 个无效学生记录`);
  }

  const invalidInteractions = await prisma.interaction.findMany({
    where: {
      OR: [
        { sourceId: "" },
        { targetId: "" },
        { sourceType: "" },
        { targetType: "" },
      ],
    },
  });

  if (invalidInteractions.length > 0) {
    console.warn(`发现 ${invalidInteractions.length} 个无效交互记录`);
  }
}

// 运行数据迁移
runDataMigration();
