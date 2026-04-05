import {
  GraphData,
  Scenario,
  Resource,
  ClassInfo,
  StudentProfile,
  StudentCognitiveTemplate,
} from "../types";
import {
  fetchGraphData as fetchGraphDataFromApi,
  fetchSchools,
  fetchGradesBySchool,
  fetchClassesBySchoolAndGrade,
  fetchStudentCognitiveTemplate as fetchStudentCognitiveTemplateFromApi,
} from "./apiService";
import {
  transformGraphData,
  validateClassInfo,
  validateScenario,
  sanitizeGraphData,
} from "./dataValidator";
import {
  withCache,
  generateCacheKey,
  graphDataCache,
} from "./performanceUtils";

/**
 * 获取可用的学校列表
 */
export const getSchools = async (): Promise<string[]> => {
  try {
    return await fetchSchools();
  } catch (error) {
    console.error("获取学校列表失败:", error);
    return [];
  }
};

/**
 * 根据学校获取年级列表
 */
export const getGradesBySchool = async (school: string): Promise<string[]> => {
  try {
    return await fetchGradesBySchool(school);
  } catch (error) {
    console.error("获取年级列表失败:", error);
    return [];
  }
};

/**
 * 根据学校和年级获取班级列表
 */
export const getClassesBySchoolAndGrade = async (
  school: string,
  grade: string,
): Promise<string[]> => {
  try {
    return await fetchClassesBySchoolAndGrade(school, grade);
  } catch (error) {
    console.error("获取班级列表失败:", error);
    return [];
  }
};

/**
 * 从API获取图谱数据
 */
export const fetchGraphData = async (
  scenario: Scenario,
  classInfo: ClassInfo,
): Promise<GraphData> => {
  console.log("从API获取图谱数据...", { scenario, classInfo });

  try {
    // 验证输入参数
    validateScenario(scenario);
    validateClassInfo(classInfo);

    // 生成缓存键
    const cacheKey = generateCacheKey("graphData", {
      scenario,
      school: classInfo.school,
      grade: classInfo.grade,
      classId: classInfo.classId,
    });

    // 使用缓存
    const data = await withCache(cacheKey, async () => {
      // 调用API服务获取数据
      const rawData = await fetchGraphDataFromApi({
        scenario,
        school: classInfo.school,
        grade: classInfo.grade,
        classId: classInfo.classId,
      });

      // 转换和验证数据
      const transformedData = transformGraphData(rawData);

      // 清理和规范化数据
      const sanitizedData = sanitizeGraphData(transformedData);

      return sanitizedData;
    });

    // 验证数据内容
    if (data.nodes.length === 0) {
      console.warn("API返回空节点数据");
    }

    if (data.links.length === 0) {
      console.warn("API返回空链接数据");
    }

    console.log("API数据获取成功:", {
      nodeCount: data.nodes.length,
      linkCount: data.links.length,
      nodeTypes: Array.from(new Set(data.nodes.map((node) => node.type))),
      linkTypes: Array.from(new Set(data.links.map((link) => link.type))),
      cacheSize: graphDataCache.size(),
    });

    return data;
  } catch (error) {
    console.error("获取图谱数据失败:", error);

    // 增强错误信息
    if (error instanceof Error) {
      throw new Error(`获取图谱数据失败: ${error.message}`, { cause: error });
    }

    throw new Error("获取图谱数据失败: 未知错误");
  }
};

/**
 * 生成学习资源（暂时保留，后续可从API获取）
 */
export const generateResources = (knowledgeNodes: any[]): Resource[] => {
  const resources: Resource[] = [];

  if (!knowledgeNodes || knowledgeNodes.length === 0) {
    console.warn("无知识点数据，无法生成资源");
    return resources;
  }

  const templates = [
    { suffix: "操作演示视频", type: "视频", url: "https://b23.tv/example1" },
    { suffix: "基础教程文档", type: "文档", url: "course-doc.pdf" },
    { suffix: "进阶技巧解析", type: "文章", url: "advanced-tips.html" },
    { suffix: "练习题集", type: "练习题", url: "exercises.pdf" },
    { suffix: "互动小测验", type: "互动游戏", url: "quiz.app" },
    { suffix: "常见问题解答", type: "文章", url: "faq.html" },
  ];

  for (let i = 0; i < Math.min(6, knowledgeNodes.length); i++) {
    const kCount = Math.min(2, knowledgeNodes.length);
    const relatedKNodes = knowledgeNodes
      .sort(() => 0.5 - Math.random())
      .slice(0, kCount);

    const kIds = relatedKNodes.map((n) => n.id);
    const mainKNode = relatedKNodes[0];

    const template = templates[i % templates.length];

    resources.push({
      id: `R${i}`,
      title: `${mainKNode.name} - ${template.suffix}`,
      type: template.type,
      relatedKnowledgeIds: kIds,
      accuracy: Math.floor(Math.random() * 20) + 80, // 80-99
      description: `针对"${relatedKNodes.map((n) => n.name).join("、")}"的${
        template.type
      }资源，旨在帮助学生掌握核心概念与操作步骤。`,
      url: template.url,
    });
  }

  console.log("生成学习资源成功:", resources.length);
  return resources;
};

const dimensionCodeToKey: Record<string, keyof StudentProfile> = {
  knowledgeReserve: "knowledgeReserve",
  learningEngagement: "learningEngagement",
  cognitiveLoad: "cognitiveLoad",
  learningMotivation: "learningMotivation",
  computationalThinking: "computationalThinking",
  humanAiTrust: "humanAiTrust",
  humanMachineTrust: "humanAiTrust",
  learningMethod: "learningMethod",
  learningApproach: "learningMethod",
  learningAttitude: "learningAttitude",
  priorKnowledge: "knowledgeReserve",
  selfRegulatedLearning: "selfRegulatedLearning",
  aiLiteracy: "aiLiteracy",
};

export const fetchStudentCognitiveTemplate = async (
  studentNodeId: string,
): Promise<Partial<StudentProfile>> => {
  const result = await fetchStudentCognitiveTemplateFromApi(studentNodeId);

  const mappedScores: Partial<StudentProfile> = {
    school: result.student.school || "",
    grade: result.student.grade || "",
    classId: result.student.classId || "",
    learningStylePreference:
      result.student.learningStylePreference || undefined,
    personality: result.student.personality || undefined,
    groupBehavior: result.student.groupBehavior || undefined,
  };

  result.dimensions.forEach((dimension) => {
    const key = dimensionCodeToKey[dimension.dimensionCode];
    if (!key) {
      return;
    }

    (mappedScores as any)[key] = dimension.scoreValue;
  });

  const findScore = (codes: string[]): number | undefined => {
    const match = result.dimensions.find((item) =>
      codes.includes(item.dimensionCode),
    );
    return typeof match?.scoreValue === "number" ? match.scoreValue : undefined;
  };

  const learningMotivationScore = findScore(["learningMotivation"]);
  const learningAttitudeScore = findScore(["learningAttitude"]);
  const learningEngagementScore = findScore(["learningEngagement"]);
  const selfRegulatedLearningScore = findScore(["selfRegulatedLearning"]);
  const computationalThinkingScore = findScore(["computationalThinking"]);
  const learningApproachScore = findScore([
    "learningApproach",
    "learningMethod",
  ]);
  const cognitiveLoadScore = findScore(["cognitiveLoad"]);
  const humanMachineTrustScore = findScore([
    "humanMachineTrust",
    "humanAiTrust",
  ]);
  const aiLiteracyScore = findScore(["aiLiteracy"]);
  const knowledgeReserveScore = findScore([
    "priorKnowledge",
    "knowledgeReserve",
  ]);

  const template: StudentCognitiveTemplate = {
    profileMeta: {
      version: result.profile?.version,
      generatedAt: result.profile?.generatedAt,
      totalScore: result.profile?.totalScore,
    },
    dimensions: result.dimensions.map((dimension) => ({
      code: dimension.dimensionCode,
      name: dimension.dimensionNameZh,
      category: dimension.category,
      score: dimension.scoreValue,
      level: dimension.scoreLevel,
    })),
    learningStyle: {
      preference: result.student.learningStylePreference || undefined,
      personality: result.student.personality || undefined,
      groupBehavior: result.student.groupBehavior || undefined,
    },
    learningMotivation:
      typeof learningMotivationScore === "number"
        ? {
            interest: learningMotivationScore,
            usefulness: learningMotivationScore,
            expectation: learningMotivationScore,
          }
        : undefined,
    learningAttitude:
      typeof learningAttitudeScore === "number"
        ? {
            enjoyment: learningAttitudeScore,
            confidence: learningAttitudeScore,
            interest: learningAttitudeScore,
          }
        : undefined,
    learningEngagement:
      typeof learningEngagementScore === "number"
        ? {
            cognitiveEngagement: [learningEngagementScore],
          }
        : undefined,
    selfRegulatedLearning:
      typeof selfRegulatedLearningScore === "number"
        ? [selfRegulatedLearningScore]
        : undefined,
    computationalThinking:
      typeof computationalThinkingScore === "number"
        ? {
            evaluation: [computationalThinkingScore],
          }
        : undefined,
    learningApproach:
      typeof learningApproachScore === "number"
        ? {
            deepLearning: [learningApproachScore],
          }
        : undefined,
    cognitiveLoad:
      typeof cognitiveLoadScore === "number"
        ? {
            internalLoad: [cognitiveLoadScore],
          }
        : undefined,
    humanMachineTrust:
      typeof humanMachineTrustScore === "number"
        ? [humanMachineTrustScore]
        : undefined,
    aiLiteracy:
      typeof aiLiteracyScore === "number" ? [aiLiteracyScore] : undefined,
    knowledgeReserve:
      typeof knowledgeReserveScore === "number"
        ? {
            dataConcept: knowledgeReserveScore,
            algorithmConcept: knowledgeReserveScore,
            networkConcept: knowledgeReserveScore,
            informationProcessing: knowledgeReserveScore,
            informationSecurity: knowledgeReserveScore,
            aiConcept: knowledgeReserveScore,
          }
        : undefined,
  };

  mappedScores.template = template;
  return mappedScores;
};
