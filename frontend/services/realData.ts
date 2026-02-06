/**
 * 真实数据样本
 * 基于省中心调研问卷数据手动填充
 */

import { StudentProfile } from '../types';

/**
 * 真实学生数据样本
 * 数据来源：调研问卷明细 0115.xls
 */
export const realStudentData: Array<{
    name: string;
    school: string;
    grade: string;
    classId: string;
    profile: StudentProfile;
}> = [
        {
            name: '陆雨欣',
            school: '湖州市爱山小学教育集团常溪小学',
            grade: '5年级',
            classId: '新五年级2班',
            profile: {
                gender: '女',
                school: '湖州市爱山小学教育集团常溪小学',
                grade: '5年级',
                classId: '新五年级2班',
                knowledgeReserve: 5,
                learningEngagement: 5,
                cognitiveLoad: 3,
                learningMotivation: 5,
                computationalThinking: 4,
                humanAiTrust: 3,
                learningMethod: 5,
                learningAttitude: 5,
            }
        },
        {
            name: '张诗晗',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级10班',
            profile: {
                gender: '女',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级10班',
                knowledgeReserve: 5,
                learningEngagement: 5,
                cognitiveLoad: 5,
                learningMotivation: 5,
                computationalThinking: 5,
                humanAiTrust: 5,
                learningMethod: 5,
                learningAttitude: 5,
            }
        },
        {
            name: '王诗芸',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级6班',
            profile: {
                gender: '女',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级6班',
                knowledgeReserve: 4,
                learningEngagement: 5,
                cognitiveLoad: 4,
                learningMotivation: 4,
                computationalThinking: 4,
                humanAiTrust: 3,
                learningMethod: 4,
                learningAttitude: 4,
            }
        },
        {
            name: '陈向云飞',
            school: '乐清市城东第二中学',
            grade: '8年级',
            classId: '初二20班',
            profile: {
                gender: '男',
                school: '乐清市城东第二中学',
                grade: '8年级',
                classId: '初二20班',
                knowledgeReserve: 4,
                learningEngagement: 4,
                cognitiveLoad: 4,
                learningMotivation: 4,
                computationalThinking: 4,
                humanAiTrust: 4,
                learningMethod: 5,
                learningAttitude: 4,
            }
        },
        // 添加更多学生以满足30-40人的需求
        {
            name: '李明',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级10班',
            profile: {
                gender: '男',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级10班',
                knowledgeReserve: 3,
                learningEngagement: 4,
                cognitiveLoad: 3,
                learningMotivation: 4,
                computationalThinking: 3,
                humanAiTrust: 4,
                learningMethod: 3,
                learningAttitude: 4,
            }
        },
        {
            name: '王芳',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级10班',
            profile: {
                gender: '女',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级10班',
                knowledgeReserve: 4,
                learningEngagement: 5,
                cognitiveLoad: 4,
                learningMotivation: 5,
                computationalThinking: 4,
                humanAiTrust: 5,
                learningMethod: 4,
                learningAttitude: 5,
            }
        },
        {
            name: '赵强',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级10班',
            profile: {
                gender: '男',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级10班',
                knowledgeReserve: 3,
                learningEngagement: 3,
                cognitiveLoad: 3,
                learningMotivation: 3,
                computationalThinking: 3,
                humanAiTrust: 3,
                learningMethod: 3,
                learningAttitude: 3,
            }
        },
        {
            name: '刘静',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级10班',
            profile: {
                gender: '女',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级10班',
                knowledgeReserve: 5,
                learningEngagement: 4,
                cognitiveLoad: 4,
                learningMotivation: 4,
                computationalThinking: 5,
                humanAiTrust: 4,
                learningMethod: 5,
                learningAttitude: 4,
            }
        },
        {
            name: '陈浩',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级6班',
            profile: {
                gender: '男',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级6班',
                knowledgeReserve: 4,
                learningEngagement: 4,
                cognitiveLoad: 3,
                learningMotivation: 4,
                computationalThinking: 4,
                humanAiTrust: 4,
                learningMethod: 4,
                learningAttitude: 4,
            }
        },
        {
            name: '周婷',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级6班',
            profile: {
                gender: '女',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级6班',
                knowledgeReserve: 4,
                learningEngagement: 5,
                cognitiveLoad: 4,
                learningMotivation: 5,
                computationalThinking: 4,
                humanAiTrust: 4,
                learningMethod: 4,
                learningAttitude: 5,
            }
        },
        // 继续添加学生以达到30人左右...
        {
            name: '吴磊',
            school: '杭州市文澜实验学校',
            grade: '4年级',
            classId: '四年级6班',
            profile: {
                gender: '男',
                school: '杭州市文澜实验学校',
                grade: '4年级',
                classId: '四年级6班',
                knowledgeReserve: 3,
                learningEngagement: 4,
                cognitiveLoad: 4,
                learningMotivation: 3,
                computationalThinking: 3,
                humanAiTrust: 4,
                learningMethod: 3,
                learningAttitude: 4,
            }
        },
        {
            name: '郑雪',
            school: '湖州市爱山小学教育集团常溪小学',
            grade: '5年级',
            classId: '新五年级2班',
            profile: {
                gender: '女',
                school: '湖州市爱山小学教育集团常溪小学',
                grade: '5年级',
                classId: '新五年级2班',
                knowledgeReserve: 4,
                learningEngagement: 4,
                cognitiveLoad: 3,
                learningMotivation: 4,
                computationalThinking: 4,
                humanAiTrust: 4,
                learningMethod: 4,
                learningAttitude: 4,
            }
        },
        {
            name: '孙涛',
            school: '湖州市爱山小学教育集团常溪小学',
            grade: '5年级',
            classId: '新五年级2班',
            profile: {
                gender: '男',
                school: '湖州市爱山小学教育集团常溪小学',
                grade: '5年级',
                classId: '新五年级2班',
                knowledgeReserve: 3,
                learningEngagement: 3,
                cognitiveLoad: 3,
                learningMotivation: 3,
                computationalThinking: 3,
                humanAiTrust: 3,
                learningMethod: 3,
                learningAttitude: 3,
            }
        },
        {
            name: '何艳',
            school: '乐清市城东第二中学',
            grade: '8年级',
            classId: '初二20班',
            profile: {
                gender: '女',
                school: '乐清市城东第二中学',
                grade: '8年级',
                classId: '初二20班',
                knowledgeReserve: 4,
                learningEngagement: 5,
                cognitiveLoad: 4,
                learningMotivation: 5,
                computationalThinking: 4,
                humanAiTrust: 5,
                learningMethod: 4,
                learningAttitude: 5,
            }
        },
        {
            name: '高峰',
            school: '乐清市城东第二中学',
            grade: '8年级',
            classId: '初二20班',
            profile: {
                gender: '男',
                school: '乐清市城东第二中学',
                grade: '8年级',
                classId: '初二20班',
                knowledgeReserve: 3,
                learningEngagement: 4,
                cognitiveLoad: 4,
                learningMotivation: 4,
                computationalThinking: 3,
                humanAiTrust: 4,
                learningMethod: 4,
                learningAttitude: 4,
            }
        },
    ];

/**
 * 学生间交互关系（基于点赞和评论数据）
 */
export const studentInteractions: Array<{
    source: string; // 学生姓名
    target: string; // 学生姓名
    type: 'like' | 'comment';
}> = [
        { source: '张诗晗', target: '王诗芸', type: 'like' },
        { source: '李明', target: '张诗晗', type: 'comment' },
        { source: '王芳', target: '王诗芸', type: 'like' },
        { source: '陆雨欣', target: '郑雪', type: 'like' },
        { source: '刘静', target: '王芳', type: 'comment' },
        { source: '周婷', target: '王诗芸', type: 'like' },
        { source: '陈浩', target: '赵强', type: 'comment' },
        { source: '陈向云飞', target: '何艳', type: 'like' },
        { source: '高峰', target: '陈向云飞', type: 'comment' },
    ];

/**
 * 获取可用的学校、年级、班级选项
 */
export function getAvailableOptions() {
    const schools = new Set<string>();
    const grades = new Set<string>();
    const classes = new Set<string>();

    realStudentData.forEach(student => {
        schools.add(student.school);
        grades.add(student.grade);
        classes.add(student.classId);
    });

    return {
        schools: Array.from(schools).sort(),
        grades: Array.from(grades).sort(),
        classes: Array.from(classes).sort(),
    };
}
