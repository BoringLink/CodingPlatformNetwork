/**
 * 数据解析模块
 * 负责从Excel文件中读取并解析真实数据
 */

import * as XLSX from 'xlsx';
import {
    DATA_PATHS,
    LIKERT_SCALE_MAP,
    LEARNING_PREFERENCE_MAP,
    PERSONALITY_MAP,
    LEADERSHIP_MAP,
    SURVEY_COLUMN_INDEX,
    COGNITIVE_DIMENSION_MAPPING,
    WORKS_COLUMN_INDEX,
} from './dataConfig';
import { GraphNode, GraphLink, NodeType, InteractionType, Scenario, ClassInfo } from '../types';

// 缓存已加载的数据
let cachedSurveyData: any[] | null = null;
let cachedWorksData: any[] | null = null;
let cachedLikesData: any[] | null = null;
let cachedCommentsData: any[] | null = null;

/**
 * 从Excel文件路径读取数据
 */
async function readExcelFile(filePath: string): Promise<any[]> {
    try {
        const response = await fetch(filePath);
        const arrayBuffer = await response.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });

        // 读取第一个工作表
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];

        // 转换为JSON，使用header: 1来获取原始数组
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

        return data as any[];
    } catch (error) {
        console.error(`读取Excel文件失败: ${filePath}`, error);
        return [];
    }
}

/**
 * 转换李克特量表值为数字
 */
function convertLikertScale(value: any): number {
    if (typeof value === 'number') return value;

    const strValue = String(value).trim();
    return LIKERT_SCALE_MAP[strValue] || 3; // 默认返回3（一般）
}

/**
 * 计算认知维度的平均分
 */
function calculateCognitiveDimension(row: any[], columnIndices: number[]): number {
    const values = columnIndices.map(idx => convertLikertScale(row[idx]));
    const sum = values.reduce((acc, val) => acc + val, 0);
    return Math.round(sum / values.length); // 四舍五入到整数 (1-5)
}

/**
 * 加载并解析调研问卷数据
 */
export async function loadSurveyData(): Promise<any[]> {
    if (cachedSurveyData) return cachedSurveyData;

    const data = await readExcelFile(DATA_PATHS.survey);

    // 第一行是表头数据（实际内容），第二行开始是真正的数据
    // 跳过第一行
    cachedSurveyData = data.slice(1);

    return cachedSurveyData;
}

/**
 * 加载并解析作品清单数据
 */
export async function loadWorksData(): Promise<any[]> {
    if (cachedWorksData) return cachedWorksData;

    const data = await readExcelFile(DATA_PATHS.works);
    cachedWorksData = data.slice(1); // 跳过表头

    return cachedWorksData;
}

/**
 * 加载并解析点赞明细数据
 */
export async function loadLikesData(): Promise<any[]> {
    if (cachedLikesData) return cachedLikesData;

    const data = await readExcelFile(DATA_PATHS.likes);
    cachedLikesData = data.slice(1); // 跳过表头

    return cachedLikesData;
}

/**
 * 加载并解析评论明细数据
 */
export async function loadCommentsData(): Promise<any[]> {
    if (cachedCommentsData) return cachedCommentsData;

    const data = await readExcelFile(DATA_PATHS.comments);
    cachedCommentsData = data.slice(1); // 跳过表头

    return cachedCommentsData;
}

/**
 * 从调研问卷数据生成学生节点
 * 
 * @param classInfo 要筛选的班级信息
 * @returns 学生节点数组
 */
export async function parseStudentNodes(classInfo: ClassInfo): Promise<GraphNode[]> {
    const surveyData = await loadSurveyData();
    const studentNodes: GraphNode[] = [];

    // 筛选指定学校、年级、班级的学生
    const filteredData = surveyData.filter(row => {
        const school = String(row[SURVEY_COLUMN_INDEX.学校] || '');
        const grade = String(row[SURVEY_COLUMN_INDEX.年级] || '');
        const classId = String(row[SURVEY_COLUMN_INDEX.班级] || '');

        return school === classInfo.school &&
            grade === classInfo.grade &&
            classId === classInfo.classId;
    });

    // 生成学生节点
    filteredData.forEach((row, index) => {
        const name = String(row[SURVEY_COLUMN_INDEX.姓名] || `学生${index + 1}`);
        const genderStr = String(row[SURVEY_COLUMN_INDEX.性别] || '男');
        const gender: '男' | '女' = genderStr === '女' ? '女' : '男'; // 确保类型正确
        const school = String(row[SURVEY_COLUMN_INDEX.学校] || '');
        const grade = String(row[SURVEY_COLUMN_INDEX.年级] || '');
        const classId = String(row[SURVEY_COLUMN_INDEX.班级] || '');

        // 计算认知属性
        const knowledgeReserve = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.knowledgeReserve
        );
        const learningEngagement = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.learningEngagement
        );
        const cognitiveLoad = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.cognitiveLoad
        );
        const learningMotivation = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.learningMotivation
        );
        const computationalThinking = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.computationalThinking
        );
        const humanAiTrust = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.humanAiTrust
        );
        const learningMethod = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.learningMethod
        );
        const learningAttitude = calculateCognitiveDimension(
            row,
            COGNITIVE_DIMENSION_MAPPING.learningAttitude
        );

        // 也考虑基础属性的映射
        const learningPref = row[SURVEY_COLUMN_INDEX.学习偏好];
        const personality = row[SURVEY_COLUMN_INDEX.性格];

        // 如果learningMethod全是一般，则从学习偏好推断
        const finalLearningMethod = learningMethod === 3 && learningPref
            ? LEARNING_PREFERENCE_MAP[String(learningPref)] || learningMethod
            : learningMethod;

        // 如果learningAttitude全是一般，则从性格推断
        const finalLearningAttitude = learningAttitude === 3 && personality
            ? PERSONALITY_MAP[String(personality)] || learningAttitude
            : learningAttitude;

        studentNodes.push({
            id: `S${index}`,
            type: NodeType.STUDENT,
            name,
            group: 3,
            val: 8,
            studentProfile: {
                gender,
                school,
                grade,
                classId,
                knowledgeReserve,
                learningEngagement,
                cognitiveLoad,
                learningMotivation,
                computationalThinking,
                humanAiTrust,
                learningMethod: finalLearningMethod,
                learningAttitude: finalLearningAttitude,
            },
        });
    });

    return studentNodes;
}

/**
 * 解析学生之间的交互关系（基于点赞和评论数据）
 * 
 * @param studentNodes 已生成的学生节点
 * @returns 学生-学生交互边数组
 */
export async function parseStudentInteractions(studentNodes: GraphNode[]): Promise<GraphLink[]> {
    const links: GraphLink[] = [];

    // 创建学生姓名到节点ID的映射
    const nameToId = new Map<string, string>();
    studentNodes.forEach(node => {
        if (node.studentProfile) {
            nameToId.set(node.name, node.id);
        }
    });

    // 从点赞数据生成交互边
    const likesData = await loadLikesData();
    const worksData = await loadWorksData();

    // 创建作品ID到作者姓名的映射
    const workIdToAuthor = new Map<string, string>();
    worksData.forEach(row => {
        const workId = String(row[WORKS_COLUMN_INDEX.作品ID] || '');
        const author = String(row[WORKS_COLUMN_INDEX.创建学生昵称] || '');
        if (workId && author) {
            workIdToAuthor.set(workId, author);
        }
    });

    // 解析点赞关系
    likesData.forEach(row => {
        const workId = String(row[0] || ''); // 假设第一列是作品ID
        const likerName = String(row[2] || ''); // 假设第三列是点赞学生姓名

        const authorName = workIdToAuthor.get(workId);

        if (authorName && likerName) {
            const likerId = nameToId.get(likerName);
            const authorId = nameToId.get(authorName);

            if (likerId && authorId && likerId !== authorId) {
                // 检查是否已存在此边
                const exists = links.find(
                    l => (l.source === likerId && l.target === authorId) ||
                        (l.source === authorId && l.target === likerId)
                );

                if (!exists) {
                    links.push({
                        source: likerId,
                        target: authorId,
                        value: 1,
                        type: InteractionType.PLATFORM,
                    });
                }
            }
        }
    });

    // 从评论数据生成交互边
    const commentsData = await loadCommentsData();

    commentsData.forEach(row => {
        const workId = String(row[1] || ''); // 假设第二列是作品ID
        const commenterName = String(row[3] || ''); // 假设第四列是评论学生姓名

        const authorName = workIdToAuthor.get(workId);

        if (authorName && commenterName) {
            const commenterId = nameToId.get(commenterName);
            const authorId = nameToId.get(authorName);

            if (commenterId && authorId && commenterId !== authorId) {
                // 检查是否已存在此边
                const exists = links.find(
                    l => (l.source === commenterId && l.target === authorId) ||
                        (l.source === authorId && l.target === commenterId)
                );

                if (!exists) {
                    links.push({
                        source: commenterId,
                        target: authorId,
                        value: 1,
                        type: InteractionType.PLATFORM,
                    });
                }
            }
        }
    });

    return links;
}

/**
 * 清除缓存的数据
 */
export function clearDataCache(): void {
    cachedSurveyData = null;
    cachedWorksData = null;
    cachedLikesData = null;
    cachedCommentsData = null;
}

/**
 * 获取所有可用的学校、年级、班级选项
 */
export async function getAvailableClassOptions(): Promise<{
    schools: string[];
    grades: string[];
    classes: string[];
}> {
    const surveyData = await loadSurveyData();

    const schools = new Set<string>();
    const grades = new Set<string>();
    const classes = new Set<string>();

    surveyData.forEach(row => {
        const school = String(row[SURVEY_COLUMN_INDEX.学校] || '');
        const grade = String(row[SURVEY_COLUMN_INDEX.年级] || '');
        const classId = String(row[SURVEY_COLUMN_INDEX.班级] || '');

        if (school) schools.add(school);
        if (grade) grades.add(grade);
        if (classId) classes.add(classId);
    });

    return {
        schools: Array.from(schools).sort(),
        grades: Array.from(grades).sort(),
        classes: Array.from(classes).sort(),
    };
}
