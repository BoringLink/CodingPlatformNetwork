import { GraphData } from '../types';

// API基础URL
const API_BASE_URL = 'http://localhost:3001/api/v1';

// 带重试机制的fetch函数
export const fetchWithRetry = async (
  url: string,
  options: RequestInit = {},
  retries = 3,
  delay = 1000
): Promise<Response> => {
  for (let i = 0; i < retries; i++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      if (i === retries - 1) throw error;
      console.warn(`请求失败，${delay * (i + 1)}ms后重试...`, error);
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
    }
  }
  throw new Error('请求失败');
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
    if (params.school) queryParams.append('school', params.school);
    if (params.grade) queryParams.append('grade', params.grade);
    if (params.classId) queryParams.append('class_id', params.classId);
    if (params.scenario) queryParams.append('scenario', params.scenario);

    // 构建完整URL
    const url = `${API_BASE_URL}/graph-data${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    console.log('请求图谱数据:', url);

    // 发送请求
    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 检查响应状态
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API请求失败: ${response.status} ${response.statusText}`);
    }

    // 解析响应数据
    const data = await response.json();
    console.log('获取图谱数据成功:', {
      nodeCount: data.nodes?.length || 0,
      linkCount: data.links?.length || 0,
    });

    // 验证数据结构
    if (!data.nodes || !Array.isArray(data.nodes)) {
      throw new Error('API返回数据结构错误: nodes数组缺失');
    }

    if (!data.links || !Array.isArray(data.links)) {
      throw new Error('API返回数据结构错误: links数组缺失');
    }

    // 验证节点数据结构
    const validNodeTypes = ['STUDENT', 'TEACHER', 'KNOWLEDGE'];
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
      if (node.type === 'STUDENT' && node.studentProfile) {
        const profile = node.studentProfile;
        if (!profile.school || !profile.grade || !profile.classId) {
          throw new Error(`API返回数据结构错误: 学生节点 ${node.id} 缺少必要的学生信息`);
        }
      }
      
      if (node.type === 'TEACHER' && node.teacherProfile) {
        const profile = node.teacherProfile;
        if (!profile.school || !profile.teachingGrade || !profile.teachingClass) {
          throw new Error(`API返回数据结构错误: 教师节点 ${node.id} 缺少必要的教师信息`);
        }
      }
      
      if (node.type === 'KNOWLEDGE' && node.knowledgeProfile) {
        const profile = node.knowledgeProfile;
        if (!profile.content || !profile.type) {
          throw new Error(`API返回数据结构错误: 知识点节点 ${node.id} 缺少必要的知识点信息`);
        }
        if (!Array.isArray(profile.relatedKnowledgeIds)) {
          throw new Error(`API返回数据结构错误: 知识点节点 ${node.id} 的 relatedKnowledgeIds 不是数组`);
        }
        if (!Array.isArray(profile.relatedKnowledgeNames)) {
          throw new Error(`API返回数据结构错误: 知识点节点 ${node.id} 的 relatedKnowledgeNames 不是数组`);
        }
      }
    });

    // 验证链接数据结构
    data.links.forEach((link, index) => {
      if (!link.source || !link.target) {
        throw new Error(`API返回数据结构错误: 链接 ${index} 缺少源节点或目标节点`);
      }
      if (typeof link.value !== 'number') {
        throw new Error(`API返回数据结构错误: 链接 ${index} 的 value 不是数字`);
      }
      if (!link.type) {
        throw new Error(`API返回数据结构错误: 链接 ${index} 缺少 type 字段`);
      }
    });

    return data;
  } catch (error) {
    console.error('获取图谱数据失败:', error);
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
    if (params.school) queryParams.append('school', params.school);
    if (params.grade) queryParams.append('grade', params.grade);
    if (params.classId) queryParams.append('class_id', params.classId);

    const url = `${API_BASE_URL}/students${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    console.log('请求学生数据:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取学生数据成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取学生数据失败:', error);
    throw error;
  }
};

// 获取教师列表
export const fetchTeachers = async (params: {
  school?: string;
}): Promise<any[]> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.school) queryParams.append('school', params.school);

    const url = `${API_BASE_URL}/teachers${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    console.log('请求教师数据:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取教师数据成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取教师数据失败:', error);
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
    if (params.grade) queryParams.append('grade', params.grade);
    if (params.type) queryParams.append('type', params.type);
    if (params.parentId) queryParams.append('parent_id', params.parentId);

    const url = `${API_BASE_URL}/knowledge-points${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    console.log('请求知识点数据:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取知识点数据成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取知识点数据失败:', error);
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
    if (params.sourceId) queryParams.append('source_id', params.sourceId);
    if (params.targetId) queryParams.append('target_id', params.targetId);
    if (params.sourceType) queryParams.append('source_type', params.sourceType);
    if (params.targetType) queryParams.append('target_type', params.targetType);
    if (params.type) queryParams.append('type', params.type);

    const url = `${API_BASE_URL}/interactions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    console.log('请求交互数据:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取交互数据成功:', data.data?.length || 0);
    return data.data || [];
  } catch (error) {
    console.error('获取交互数据失败:', error);
    throw error;
  }
};

// 获取学校列表
export const fetchSchools = async (): Promise<string[]> => {
  try {
    const url = `${API_BASE_URL}/students/options/schools`;
    console.log('请求学校列表:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取学校列表成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取学校列表失败:', error);
    throw error;
  }
};

// 根据学校获取年级列表
export const fetchGradesBySchool = async (school: string): Promise<string[]> => {
  try {
    const url = `${API_BASE_URL}/students/options/grades?school=${encodeURIComponent(school)}`;
    console.log('请求年级列表:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取年级列表成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取年级列表失败:', error);
    throw error;
  }
};

// 根据学校和年级获取班级列表
export const fetchClassesBySchoolAndGrade = async (school: string, grade: string): Promise<string[]> => {
  try {
    const url = `${API_BASE_URL}/students/options/classes?school=${encodeURIComponent(school)}&grade=${encodeURIComponent(grade)}`;
    console.log('请求班级列表:', url);

    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`);
    }

    const data = await response.json();
    console.log('获取班级列表成功:', data.length);
    return data;
  } catch (error) {
    console.error('获取班级列表失败:', error);
    throw error;
  }
};
