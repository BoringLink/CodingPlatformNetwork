/**
 * 数据配置文件
 * 定义真实数据文件路径和相关配置
 */

// 真实数据文件路径
export const DATA_PATHS = {
    // 调研问卷数据（学生基本信息 + 认知属性量表）
    survey: '/Users/tk/Documents/浙江大学/260115 省中心取数/调研问卷明细 0115.xls',

    // 作品相关数据
    works: '/Users/tk/Documents/浙江大学/260115 省中心取数/260115作品清单（寒暑假活动）.xls',
    likes: '/Users/tk/Documents/浙江大学/260115 省中心取数/260115作品点赞明细查询.xls',
    comments: '/Users/tk/Documents/浙江大学/260115 省中心取数/260115作品评论明细.xls',

    // AI助手使用数据
    aiData: '/Users/tk/Documents/浙江大学/260115 省中心取数/260119学生AI助手使用数据.xlsx',
};

// 李克特量表值映射（调研问卷中的量表题答案）
export const LIKERT_SCALE_MAP: Record<string, number> = {
    '非常同意': 5,
    '同意': 4,
    '一般': 3,
    '不同意': 2,
    '非常不同意': 1,
};

// 学习偏好映射
export const LEARNING_PREFERENCE_MAP: Record<string, number> = {
    '和他人一起学习': 5,
    '独自学习': 2,
};

// 性格特征映射
export const PERSONALITY_MAP: Record<string, number> = {
    '外向': 5,
    '内向': 2,
};

// 领导力倾向映射
export const LEADERSHIP_MAP: Record<string, number> = {
    '挺身而出，畅所欲言': 5,
    '保持安静，倾听意见': 3,
};

/**
 * 调研问卷列索引映射
 * 基于实际Excel文件的列结构
 */
export const SURVEY_COLUMN_INDEX = {
    序号: 0,
    姓名: 1,
    行政区划代码: 2,
    市: 3,
    区县: 4,
    学校: 5,
    学段: 6,
    年级: 7,
    班级: 8,
    提交时间: 9,
    性别: 10,
    学习偏好: 11,
    性格: 12,
    领导力倾向: 13,
    // 认知量表题从列14开始（索引从0开始，所以是14-51共38题）
    量表题开始: 14,
    量表题结束: 51,
};

/**
 * 认知维度与问卷题目的映射关系
 * 每个认知维度对应调研问卷中的若干题目（列索引）
 * 
 * 注意：这是一个初步映射方案，实际映射需要根据问卷题目的具体含义调整
 * 由于缺少问卷的题目说明，这里采用平均分配的方式
 */
export const COGNITIVE_DIMENSION_MAPPING = {
    // 知识储备 (5题): 列14-18
    knowledgeReserve: [14, 15, 16, 17, 18],

    // 学习投入度 (5题): 列19-23
    learningEngagement: [19, 20, 21, 22, 23],

    // 认知负荷 (5题): 列24-28
    cognitiveLoad: [24, 25, 26, 27, 28],

    // 学习动机 (5题): 列29-33
    learningMotivation: [29, 30, 31, 32, 33],

    // 计算思维 (5题): 列34-38
    computationalThinking: [34, 35, 36, 37, 38],

    // 人机信任 (5题): 列39-43
    humanAiTrust: [39, 40, 41, 42, 43],

    // 学习方法 (4题): 列44-47
    learningMethod: [44, 45, 46, 47],

    // 学习态度 (5题): 列48-51 + 基础属性列11-13
    learningAttitude: [48, 49, 50, 51],
};

/**
 * 作品清单列索引
 */
export const WORKS_COLUMN_INDEX = {
    作品ID: 0,
    作品标题: 1,
    创建学生昵称: 2,
    学校: 3,
    年级: 4,
    班级: 5,
    作品链接: 6,
};

/**
 * 点赞明细列索引（待确认具体列名）
 */
export const LIKES_COLUMN_INDEX = {
    作品ID: 0,
    点赞学生账号: 1,
    学生姓名: 2,
    // 其他列待补充
};

/**
 * 评论明细列索引（待确认具体列名）
 */
export const COMMENTS_COLUMN_INDEX = {
    评论ID: 0,
    作品ID: 1,
    评论内容: 2,
    评论学生姓名: 3,
    // 其他列待补充
};
