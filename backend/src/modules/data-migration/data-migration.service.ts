import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../../shared/utils/prisma.service';
import { ExcelReaderUtil } from '../../shared/utils/excel-reader.util';
import * as path from 'path';
import * as fs from 'fs';

/**
 * 数据迁移服务
 */
@Injectable()
export class DataMigrationService {
  private readonly logger = new Logger(DataMigrationService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * 执行全量数据迁移
   */
  async executeFullMigration() {
    this.logger.log('开始执行全量数据迁移');

    const result = {
      totalRecords: 0,
      successfulRecords: 0,
      failedRecords: 0,
      errors: [] as string[],
    };

    try {
      // 1. 迁移问卷数据到学生表
      const studentResult = await this.migrateQuestionnaireData();
      result.totalRecords += studentResult.total;
      result.successfulRecords += studentResult.successful;
      result.failedRecords += studentResult.failed;
      result.errors = [...result.errors, ...studentResult.errors];

      // 2. 迁移作品数据到交互表
      const workResult = await this.migrateWorkData();
      result.totalRecords += workResult.total;
      result.successfulRecords += workResult.successful;
      result.failedRecords += workResult.failed;
      result.errors = [...result.errors, ...workResult.errors];

      // 3. 迁移AI助手使用数据到交互表
      const aiResult = await this.migrateAiUsageData();
      result.totalRecords += aiResult.total;
      result.successfulRecords += aiResult.successful;
      result.failedRecords += aiResult.failed;
      result.errors = [...result.errors, ...aiResult.errors];

      // 4. 迁移知识点数据
      const knowledgeResult = await this.migrateKnowledgeData();
      result.totalRecords += knowledgeResult.total;
      result.successfulRecords += knowledgeResult.successful;
      result.failedRecords += knowledgeResult.failed;
      result.errors = [...result.errors, ...knowledgeResult.errors];

      this.logger.log(`数据迁移完成: 总计 ${result.totalRecords} 条记录, 成功 ${result.successfulRecords} 条, 失败 ${result.failedRecords} 条`);
    } catch (error) {
      this.logger.error('数据迁移过程中发生错误', error);
      result.errors.push(`迁移过程中发生错误: ${error.message}`);
    }

    return result;
  }

  /**
   * 迁移知识点数据
   */
  private async migrateKnowledgeData() {
    this.logger.log('开始迁移知识点数据');

    const result = {
      total: 0,
      successful: 0,
      failed: 0,
      errors: [] as string[],
    };

    const filePath = path.join(
      __dirname, '../../../../Real Data/知识点_处理后.json',
    );

    try {
      const knowledgeData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      result.total = knowledgeData.length;

      for (const item of knowledgeData) {
        try {
          // 检查知识点是否已存在
          const existingKnowledge = await this.prisma.knowledge.findFirst({
            where: {
              knowledgePoint: item.knowledge_point,
              grade: item.grade,
            },
          });

          // 转换相关知识点ID和名称为字符串
          const relatedKnowledgeIds = JSON.stringify(item.related_knowledge_ids);
          const relatedKnowledgeNames = JSON.stringify(item.related_knowledge_names);

          if (existingKnowledge) {
            // 更新现有知识点
            await this.prisma.knowledge.update({
              where: { id: existingKnowledge.id },
              data: {
                content: item.content || '',
                knowledgePoint: item.knowledge_point || '',
                grade: item.grade || '',
                type: item.type || '知识点',
                parentId: item.parent_id || null,
                parentName: item.parent_name || null,
                relatedKnowledgeIds,
                relatedKnowledgeNames,
              },
            });
          } else {
            // 创建新知识点
            await this.prisma.knowledge.create({
              data: {
                content: item.content || '',
                knowledgePoint: item.knowledge_point || '',
                grade: item.grade || '',
                type: item.type || '知识点',
                parentId: item.parent_id || null,
                parentName: item.parent_name || null,
                relatedKnowledgeIds,
                relatedKnowledgeNames,
              },
            });
          }

          result.successful++;
        } catch (error) {
          this.logger.error(`处理知识点数据失败: ${error.message}`);
          result.failed++;
          result.errors.push(`处理知识点数据失败: ${error.message}`);
        }
      }
    } catch (error) {
      this.logger.error(`读取知识点文件失败: ${error.message}`);
      result.errors.push(`读取知识点文件失败: ${error.message}`);
    }

    this.logger.log(`知识点数据迁移完成: 总计 ${result.total} 条记录, 成功 ${result.successful} 条, 失败 ${result.failed} 条`);
    return result;
  }

  /**
   * 迁移问卷数据到学生表
   */
  private async migrateQuestionnaireData() {
    this.logger.log('开始迁移问卷数据');

    const result = {
      total: 0,
      successful: 0,
      failed: 0,
      errors: [] as string[],
    };

    const filePath = path.join(
      __dirname, '../../../../Real Data/调研问卷明细 0115.xls',
    );

    try {
      const sheets = ExcelReaderUtil.readExcelFile(filePath);

      for (const [sheetName, data] of Object.entries(sheets)) {
        this.logger.log(`处理工作表: ${sheetName}, 记录数: ${data.length}`);
        result.total += data.length;

        for (const row of data) {
          try {
            // 解析学生数据
            const studentData = this.parseQuestionnaireRow(row);
            if (!studentData) {
              result.failed++;
              continue;
            }

            // 检查学生是否已存在
            const existingStudent = await this.prisma.student.findFirst({
              where: {
                name: studentData.name,
                school: studentData.school,
                grade: studentData.grade,
                classId: studentData.classId,
              },
            });

            if (existingStudent) {
              // 更新现有学生
              await this.prisma.student.update({
                where: { id: existingStudent.id },
                data: studentData,
              });
            } else {
              // 创建新学生
              await this.prisma.student.create({
                data: studentData,
              });
            }

            result.successful++;
          } catch (error) {
            this.logger.error(`处理问卷数据失败: ${error.message}`);
            result.failed++;
            result.errors.push(`处理问卷数据失败: ${error.message}`);
          }
        }
      }
    } catch (error) {
      this.logger.error(`读取问卷文件失败: ${error.message}`);
      result.errors.push(`读取问卷文件失败: ${error.message}`);
    }

    this.logger.log(`问卷数据迁移完成: 总计 ${result.total} 条记录, 成功 ${result.successful} 条, 失败 ${result.failed} 条`);
    return result;
  }

  /**
   * 解析问卷数据行
   */
  private parseQuestionnaireRow(row: any) {
    // 解析Sheet1的数据结构
    if (row['陆雨欣'] !== undefined) {
      return {
        name: row['陆雨欣'] || row['项目'] || '',
        school: row['湖州市爱山小学教育集团常溪小学'] || row['学校'] || '',
        grade: row['5年级'] || row['年级'] || '',
        classId: row['新五年级2班'] || row['班级'] || '',
        knowledgeReserve: this.calculateScore(row, [14, 15, 16, 17, 18, 19]),
        learningMotivation: this.calculateScore(row, [20, 21, 22]),
        learningAttitude: this.calculateScore(row, [23, 24, 25]),
        learningEngagement: this.calculateScore(row, [26, 27, 28]),
        computationalThinking: this.calculateScore(row, [29, 30, 31]),
        learningMethod: this.calculateScore(row, [32, 33, 34]),
        cognitiveLoad: this.calculateScore(row, [35, 36, 37]),
        humanAiTrust: this.calculateScore(row, [38, 39, 40]),
      };
    }

    return null;
  }

  /**
   * 计算得分
   */
  private calculateScore(row: any, columnIndices: number[]) {
    const scores = columnIndices.map(index => {
      const value = row[index] || row[`${index}`] || row[`${index}.1`];
      return this.mapAnswerToScore(value);
    });

    const validScores = scores.filter(score => score !== null);
    if (validScores.length === 0) {
      return 0;
    }

    return validScores.reduce((sum, score) => sum + score, 0) / validScores.length;
  }

  /**
   * 将答案映射为得分
   */
  private mapAnswerToScore(answer: string): number {
    const answerMap: Record<string, number> = {
      '非常同意': 5,
      '同意': 4,
      '一般': 3,
      '不同意': 2,
      '非常不同意': 1,
    };

    return answerMap[answer] || 0;
  }

  /**
   * 迁移作品数据到交互表
   */
  private async migrateWorkData() {
    this.logger.log('开始迁移作品数据');

    const result = {
      total: 0,
      successful: 0,
      failed: 0,
      errors: [] as string[],
    };

    // 处理作品评论数据
    const commentFilePath = path.join(
      __dirname, '../../../../Real Data/260115作品评论明细.xls',
    );

    try {
      const commentSheets = ExcelReaderUtil.readExcelFile(commentFilePath);
      for (const [sheetName, data] of Object.entries(commentSheets)) {
        this.logger.log(`处理评论工作表: ${sheetName}, 记录数: ${data.length}`);
        result.total += data.length;

        for (const row of data) {
          try {
            // 解析评论数据并创建交互记录
            await this.createWorkInteraction(row, 'comment');
            result.successful++;
          } catch (error) {
            result.failed++;
            result.errors.push(`处理评论数据失败: ${error.message}`);
          }
        }
      }
    } catch (error) {
      this.logger.error(`读取评论文件失败: ${error.message}`);
      result.errors.push(`读取评论文件失败: ${error.message}`);
    }

    // 处理作品点赞数据
    const likeFilePath = path.join(
      __dirname, '../../../../Real Data/260115作品点赞明细查询.xls',
    );

    try {
      const likeSheets = ExcelReaderUtil.readExcelFile(likeFilePath);
      for (const [sheetName, data] of Object.entries(likeSheets)) {
        this.logger.log(`处理点赞工作表: ${sheetName}, 记录数: ${data.length}`);
        result.total += data.length;

        for (const row of data) {
          try {
            // 解析点赞数据并创建交互记录
            await this.createWorkInteraction(row, 'like');
            result.successful++;
          } catch (error) {
            result.failed++;
            result.errors.push(`处理点赞数据失败: ${error.message}`);
          }
        }
      }
    } catch (error) {
      this.logger.error(`读取点赞文件失败: ${error.message}`);
      result.errors.push(`读取点赞文件失败: ${error.message}`);
    }

    this.logger.log(`作品数据迁移完成: 总计 ${result.total} 条记录, 成功 ${result.successful} 条, 失败 ${result.failed} 条`);
    return result;
  }

  /**
   * 创建作品交互记录
   */
  private async createWorkInteraction(row: any, interactionType: 'comment' | 'like') {
    const workId = row['作品id'] || row['作品ID'];
    const studentId = row['点赞学生id'] || row['学生ID'];
    const studentSchoolId = row['点赞学生学校id'] || row['学校ID'];

    if (!workId || !studentId) {
      throw new Error('缺少必要字段');
    }

    // 创建交互记录
    await this.prisma.interaction.create({
      data: {
        sourceId: studentId,
        targetId: workId.toString(),
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: interactionType === 'like' ? 1 : 2,
        type: 'PLATFORM',
        interactionType: interactionType,
      },
    });
  }

  /**
   * 迁移AI助手使用数据到交互表
   */
  private async migrateAiUsageData() {
    this.logger.log('开始迁移AI助手使用数据');

    const result = {
      total: 0,
      successful: 0,
      failed: 0,
      errors: [] as string[],
    };

    const filePath = path.join(
      __dirname, '../../../../Real Data/260119学生AI助手使用数据.xlsx',
    );

    try {
      const sheets = ExcelReaderUtil.readExcelFile(filePath);

      for (const [sheetName, data] of Object.entries(sheets)) {
        this.logger.log(`处理工作表: ${sheetName}, 记录数: ${data.length}`);
        result.total += data.length;

        for (const row of data) {
          try {
            // 解析AI助手使用数据
            const aiData = this.parseAiUsageRow(row);
            if (!aiData) {
              result.failed++;
              continue;
            }

            // 创建交互记录
            await this.prisma.interaction.create({
              data: aiData,
            });

            result.successful++;
          } catch (error) {
            result.failed++;
            result.errors.push(`处理AI助手使用数据失败: ${error.message}`);
          }
        }
      }
    } catch (error) {
      this.logger.error(`读取AI助手使用文件失败: ${error.message}`);
      result.errors.push(`读取AI助手使用文件失败: ${error.message}`);
    }

    this.logger.log(`AI助手使用数据迁移完成: 总计 ${result.total} 条记录, 成功 ${result.successful} 条, 失败 ${result.failed} 条`);
    return result;
  }

  /**
   * 解析AI助手使用数据行
   */
  private parseAiUsageRow(row: any) {
    const content = row['content'] || '';
    const userId = row['channel_user_id'] || '';
    const role = row['角色'] || '';
    const schoolId = row['学校Id'] || '';

    if (!content || !userId || !role) {
      return null;
    }

    return {
      sourceId: userId,
      targetId: schoolId,
      sourceType: role.toUpperCase() === 'TEACHER' ? 'TEACHER' : 'STUDENT',
      targetType: 'KNOWLEDGE',
      value: 1,
      type: 'PLATFORM',
      interactionType: 'ai_usage',
    };
  }

  /**
   * 验证迁移结果
   */
  async verifyMigration() {
    this.logger.log('开始验证迁移结果');

    const result = {
      students: 0,
      teachers: 0,
      knowledge: 0,
      interactions: 0,
      issues: [] as string[],
    };

    try {
      // 统计各表数据量
      result.students = await this.prisma.student.count();
      result.teachers = await this.prisma.teacher.count();
      result.knowledge = await this.prisma.knowledge.count();
      result.interactions = await this.prisma.interaction.count();

      this.logger.log(`验证结果: 学生 ${result.students}, 教师 ${result.teachers}, 知识点 ${result.knowledge}, 交互 ${result.interactions}`);

      // 检查数据质量
      const invalidStudents = await this.prisma.student.findMany({
        where: {
          OR: [
            { name: '' },
            { school: '' },
            { grade: '' },
            { classId: '' },
          ],
        },
      });

      if (invalidStudents.length > 0) {
        result.issues.push(`发现 ${invalidStudents.length} 个无效学生记录`);
      }

      const invalidInteractions = await this.prisma.interaction.findMany({
        where: {
          OR: [
            { sourceId: '' },
            { targetId: '' },
            { sourceType: '' },
            { targetType: '' },
          ],
        },
      });

      if (invalidInteractions.length > 0) {
        result.issues.push(`发现 ${invalidInteractions.length} 个无效交互记录`);
      }
    } catch (error) {
      this.logger.error('验证过程中发生错误', error);
      result.issues.push(`验证过程中发生错误: ${error.message}`);
    }

    return result;
  }

  /**
   * 导入数据
   */
  async importData(data: { fileType?: string; fileUrl?: string }) {
    this.logger.log(`开始导入数据: ${data.fileType} from ${data.fileUrl}`);
    
    // 这里可以根据fileType和fileUrl执行相应的导入逻辑
    const result = await this.executeFullMigration();
    
    return {
      message: '数据导入成功',
      importedCount: result.successfulRecords,
      updatedCount: 0,
      errors: result.errors
    };
  }
}
