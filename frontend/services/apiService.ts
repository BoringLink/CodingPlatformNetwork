import { GraphData } from "../types";

export interface StudentCognitiveTemplateApiResponse {
  student: {
    id: string;
    name: string;
    school: string | null;
    grade: string | null;
    classId: string | null;
    learningStylePreference?: string | null;
    personality?: string | null;
    groupBehavior?: string | null;
  };
  profile: {
    version: string;
    generatedAt: string;
    totalScore: number;
  } | null;
  dimensions: Array<{
    dimensionCode: string;
    dimensionNameZh: string;
    category: string;
    scoreValue: number;
    scoreLevel: string;
  }>;
}

// API基础URL
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "http://interaction-network.mgsai.cn/api/v1"
    : "http://localhost:3333/api/v1";

const scenarioCodeMap: Record<string, string> = {
  展示场景: "SHOW_CASE",
  学科课程在线学习: "ONLINE_COURSE",
  课后线上教师授课答疑: "TEACHER_QA",
  家庭在线学习: "HOME_LEARNING",
  在线协作学习: "COLLABORATIVE_LEARNING",
  社团课等非正式学习: "INFORMAL_LEARNING",
};

const schoolNameToId = new Map<string, string>();
const gradeKeyToId = new Map<string, string>();
const classKeyToId = new Map<string, string>();
const gradeDisplayToRaw = new Map<string, string>();
const classDisplayToRaw = new Map<string, string>();

type OrgOptionLike =
  | string
  | {
      id?: string;
      name?: string;
      schoolName?: string;
      gradeName?: string;
      className?: string;
    };

const normalizeOrgOption = (
  item: OrgOptionLike,
): { id: string; label: string; rawLabel: string } | null => {
  if (typeof item === "string") {
    const value = item.trim();
    return value ? { id: value, label: value, rawLabel: value } : null;
  }

  if (!item || typeof item !== "object") {
    return null;
  }

  const labelRaw =
    item.name ?? item.schoolName ?? item.gradeName ?? item.className;
  let rawLabel = typeof labelRaw === "string" ? labelRaw.trim() : String(labelRaw);
  
  let label = rawLabel;
  if (item.gradeName !== undefined) {
    label = `${rawLabel}年级`;
  } else if (item.className !== undefined) {
    label = `${rawLabel}班`;
  }
  
  const id =
    typeof item.id === "string" && item.id.trim() !== ""
      ? item.id.trim()
      : rawLabel;

  if (!rawLabel) {
    return null;
  }

  return { id, label, rawLabel };
};

// 带重试机制的fetch函数
export const fetchWithRetry = async (
  url: string,
  options: RequestInit = {},
  retries = 3,
  delay = 1000,
): Promise<Response> => {
  for (let i = 0; i < retries; i++) {
    let timeoutId: NodeJS.Timeout | undefined;
    try {
      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort("请求超时"), 30000); // 30秒超时

      console.log(`发送请求 (尝试 ${i + 1}/${retries}):`, url);
      const startTime = Date.now();

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const endTime = Date.now();
      console.log(`请求成功 (${endTime - startTime}ms):`, url, response.status);
      return response;
    } catch (error) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      // 详细的错误处理
      if (error instanceof Error) {
        if (error.name === "AbortError") {
          console.warn(
            `请求超时 (尝试 ${i + 1}/${retries}):`,
            url,
            error.message,
          );
        } else {
          console.warn(
            `请求失败 (尝试 ${i + 1}/${retries}):`,
            url,
            error.message,
          );
        }
      } else {
        console.warn(`请求失败 (尝试 ${i + 1}/${retries}):`, url, error);
      }

      if (i === retries - 1) {
        console.error(`所有重试均失败:`, url);
        throw error;
      }

      const retryDelay = delay * (i + 1);
      console.warn(`将在 ${retryDelay}ms 后重试...`);
      await new Promise((resolve) => setTimeout(resolve, retryDelay));
    }
  }
  throw new Error("请求失败");
};

// 获取图谱数据
export const fetchGraphData = async (params: {
  scenario?: string;
  school?: string;
  grade?: string;
  classId?: string;
}): Promise<GraphData> => {
  try {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    const scenarioCode = params.scenario
      ? scenarioCodeMap[params.scenario] || params.scenario
      : undefined;
    if (scenarioCode) queryParams.append("scenario_code", scenarioCode);

    // 优先使用ID参数兼容v2后端；找不到映射时回退到旧参数名。
    const schoolId = params.school
      ? schoolNameToId.get(params.school)
      : undefined;
    
    // 转换显示格式回原始值
    const rawGrade = params.grade 
      ? (gradeDisplayToRaw.get(params.grade) || params.grade)
      : undefined;
    const rawClassId = params.classId 
      ? (classDisplayToRaw.get(params.classId) || params.classId)
      : undefined;
    
    const gradeId =
      params.school && rawGrade
        ? gradeKeyToId.get(`${params.school}::${rawGrade}`)
        : undefined;
    const classId =
      params.school && rawGrade && rawClassId
        ? classKeyToId.get(
            `${params.school}::${rawGrade}::${rawClassId}`,
          )
        : undefined;

    if (schoolId) {
      queryParams.append("school_id", schoolId);
    }

    if (gradeId) {
      queryParams.append("grade_id", gradeId);
    }

    if (classId) {
      queryParams.append("class_id", classId);
    }

    // 构建完整URL
    const url = `${API_BASE_URL}/graph-data${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;
    console.log("请求图谱数据:", url);

    // 发送请求
    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // 检查响应状态
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message ||
          `API请求失败: ${response.status} ${response.statusText}`,
      );
    }

    // 解析响应数据
    const payload = await response.json();
    const data = payload?.data ?? payload;
    console.log("获取图谱数据成功:", {
      nodeCount: data.nodes?.length || 0,
      linkCount: data.links?.length || 0,
    });

    // 验证数据结构
    if (!data.nodes || !Array.isArray(data.nodes)) {
      throw new Error("API返回数据结构错误: nodes数组缺失");
    }

    if (!data.links || !Array.isArray(data.links)) {
      throw new Error("API返回数据结构错误: links数组缺失");
    }

    // 验证节点数据结构（容错降级，避免因单条脏数据导致整页不可用）
    const validNodeTypes = ["STUDENT", "TEACHER", "KNOWLEDGE"];
    data.nodes.forEach((node, index) => {
      if (!node.id) {
        throw new Error(`API返回数据结构错误: 节点 ${index} 缺少id字段`);
      }
      if (!node.type || !validNodeTypes.includes(node.type)) {
        throw new Error(`API返回数据结构错误: 节点 ${node.id} 类型无效或缺失`);
      }
      if (!node.name) {
        throw new Error(`API返回数据结构错误: 节点 ${node.id} 缺少name字段`);
      }

      // 验证节点特定属性
      if (node.type === "STUDENT" && node.studentProfile) {
        const profile = node.studentProfile;
        // v2 后端允许组织字段为空，前端只在有值时展示
        profile.school = profile.school ?? "";
        profile.grade = profile.grade ?? "";
        profile.classId = profile.classId ?? "";
      }

      if (node.type === "TEACHER" && node.teacherProfile) {
        const profile = node.teacherProfile;
        profile.school = profile.school ?? "";
        profile.teachingGrade = profile.teachingGrade ?? "";
        profile.teachingClass = profile.teachingClass ?? "";
      }

      if (node.type === "KNOWLEDGE" && node.knowledgeProfile) {
        const profile = node.knowledgeProfile;
        profile.content = profile.content || node.name || "未命名知识点";
        profile.type = profile.type || "知识点";
        profile.relatedKnowledgeIds = Array.isArray(profile.relatedKnowledgeIds)
          ? profile.relatedKnowledgeIds
          : [];
        profile.relatedKnowledgeNames = Array.isArray(
          profile.relatedKnowledgeNames,
        )
          ? profile.relatedKnowledgeNames
          : [];
      }
    });

    // 过滤不完整链接，避免 forceLink 因非法数据抛错。
    data.links = data.links
      .filter((link) => Boolean(link?.source) && Boolean(link?.target))
      .map((link) => ({
        ...link,
        value: typeof link.value === "number" ? link.value : 1,
        type: link.type || "PLATFORM",
      }));

    return data;
  } catch (error) {
    console.error("获取图谱数据失败:", error);
    throw error;
  }
};

// 获取学生列表
export const fetchStudents = async (params: {
  school?: string;
  grade?: string;
  classId?: string;
}): Promise<any[]> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.school) queryParams.append("school", params.school);
    if (params.grade) queryParams.append("grade", params.grade);
    if (params.classId) queryParams.append("class_id", params.classId);

    const url = `${API_BASE_URL}/students${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;
    console.log("请求学生数据:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log("获取学生数据成功:", data.length);
    return data;
  } catch (error) {
    console.error("获取学生数据失败:", error);
    throw error;
  }
};

// 获取教师列表
export const fetchTeachers = async (params: {
  school?: string;
}): Promise<any[]> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.school) queryParams.append("school", params.school);

    const url = `${API_BASE_URL}/teachers${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;
    console.log("请求教师数据:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log("获取教师数据成功:", data.length);
    return data;
  } catch (error) {
    console.error("获取教师数据失败:", error);
    throw error;
  }
};

// 获取知识点列表
export const fetchKnowledgePoints = async (params: {
  grade?: string;
  type?: string;
  parentId?: string;
}): Promise<any[]> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.grade) queryParams.append("grade", params.grade);
    if (params.type) queryParams.append("type", params.type);
    if (params.parentId) queryParams.append("parent_id", params.parentId);

    const url = `${API_BASE_URL}/knowledge-points${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;
    console.log("请求知识点数据:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log("获取知识点数据成功:", data.length);
    return data;
  } catch (error) {
    console.error("获取知识点数据失败:", error);
    throw error;
  }
};

// 获取交互列表
export const fetchInteractions = async (params: {
  sourceId?: string;
  targetId?: string;
  sourceType?: string;
  targetType?: string;
  type?: string;
}): Promise<any[]> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.sourceId) queryParams.append("source_id", params.sourceId);
    if (params.targetId) queryParams.append("target_id", params.targetId);
    if (params.sourceType) queryParams.append("source_type", params.sourceType);
    if (params.targetType) queryParams.append("target_type", params.targetType);
    if (params.type) queryParams.append("type", params.type);

    const url = `${API_BASE_URL}/interactions${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;
    console.log("请求交互数据:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log("获取交互数据成功:", data.data?.length || 0);
    return data.data || [];
  } catch (error) {
    console.error("获取交互数据失败:", error);
    throw error;
  }
};

// 获取学校列表
export const fetchSchools = async (): Promise<string[]> => {
  try {
    const url = `${API_BASE_URL}/org/schools`;
    console.log("请求学校列表:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const payload = await response.json();
    const list = Array.isArray(payload?.data) ? payload.data : [];

    schoolNameToId.clear();
    const names: string[] = [];
    list.forEach((item: OrgOptionLike) => {
      const normalized = normalizeOrgOption(item);
      if (!normalized) return;
      schoolNameToId.set(normalized.label, normalized.id);
      names.push(normalized.label);
    });

    console.log("获取学校列表成功:", names.length);
    return names;
  } catch (error) {
    console.error("获取学校列表失败:", error);
    throw error;
  }
};

// 根据学校获取年级列表
export const fetchGradesBySchool = async (
  school: string,
): Promise<string[]> => {
  try {
    const schoolId = schoolNameToId.get(school);
    if (!schoolId) {
      return [];
    }

    const url = `${API_BASE_URL}/org/grades?school_id=${encodeURIComponent(
      schoolId,
    )}`;
    console.log("请求年级列表:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const payload = await response.json();
    const list = Array.isArray(payload?.data) ? payload.data : [];

    const gradeNames: string[] = [];
    list.forEach((item: OrgOptionLike) => {
      const normalized = normalizeOrgOption(item);
      if (!normalized) return;
      gradeKeyToId.set(`${school}::${normalized.rawLabel}`, normalized.id);
      gradeDisplayToRaw.set(normalized.label, normalized.rawLabel);
      gradeNames.push(normalized.label);
    });

    console.log("获取年级列表成功:", gradeNames.length);
    console.log("gradeKeyToId 映射:", Array.from(gradeKeyToId.entries()));
    console.log("gradeDisplayToRaw 映射:", Array.from(gradeDisplayToRaw.entries()));
    return gradeNames;
  } catch (error) {
    console.error("获取年级列表失败:", error);
    throw error;
  }
};

// 根据学校和年级获取班级列表
export const fetchClassesBySchoolAndGrade = async (
  school: string,
  grade: string,
): Promise<string[]> => {
  try {
    const schoolId = schoolNameToId.get(school);
    const rawGrade = gradeDisplayToRaw.get(grade) || grade;
    const gradeId = gradeKeyToId.get(`${school}::${rawGrade}`);
    
    console.log("fetchClassesBySchoolAndGrade 调试信息:");
    console.log("- school:", school);
    console.log("- grade:", grade);
    console.log("- schoolId:", schoolId);
    console.log("- rawGrade:", rawGrade);
    console.log("- gradeId:", gradeId);
    console.log("- gradeKeyToId 可用键:", Array.from(gradeKeyToId.keys()));
    console.log("- gradeDisplayToRaw 可用键:", Array.from(gradeDisplayToRaw.keys()));
    
    if (!schoolId || !gradeId) {
      console.log("缺少 schoolId 或 gradeId，返回空数组");
      return [];
    }

    const url = `${API_BASE_URL}/org/classes?grade_id=${encodeURIComponent(
      gradeId,
    )}`;
    console.log("请求班级列表:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const payload = await response.json();
    const list = Array.isArray(payload?.data) ? payload.data : [];

    const classNames: string[] = [];
    list.forEach((item: OrgOptionLike) => {
      const normalized = normalizeOrgOption(item);
      if (!normalized) return;
      classKeyToId.set(
        `${school}::${rawGrade}::${normalized.rawLabel}`,
        normalized.id,
      );
      classDisplayToRaw.set(normalized.label, normalized.rawLabel);
      classNames.push(normalized.label);
    });

    console.log("获取班级列表成功:", classNames.length);
    return classNames;
  } catch (error) {
    console.error("获取班级列表失败:", error);
    throw error;
  }
};

export const fetchStudentCognitiveTemplate = async (
  studentNodeId: string,
): Promise<StudentCognitiveTemplateApiResponse> => {
  try {
    const url = `${API_BASE_URL}/students/${encodeURIComponent(
      studentNodeId,
    )}/cognitive-template`;
    console.log("请求学生认知模板:", url);

    const response = await fetchWithRetry(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const payload = await response.json();
    const data = payload?.data ?? payload;
    if (!data || !data.student) {
      throw new Error("认知模板返回结构无效");
    }

    const normalized: StudentCognitiveTemplateApiResponse = {
      student: data.student,
      profile: data.profile
        ? {
            version: data.profile.profileVersion,
            generatedAt: data.profile.generatedAt,
            totalScore: data.profile.totalScore,
          }
        : null,
      dimensions: Array.isArray(data.dimensions) ? data.dimensions : [],
    };

    return normalized;
  } catch (error) {
    console.error("获取学生认知模板失败:", error);
    throw error;
  }
};
