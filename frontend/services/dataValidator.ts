import { GraphData, GraphNode, GraphLink, NodeType, InteractionType } from '../types';

/**
 * 验证GraphData数据结构
 */
export const validateGraphData = (data: any): asserts data is GraphData => {
  if (!data) {
    throw new Error('数据为空');
  }

  if (!data.nodes || !Array.isArray(data.nodes)) {
    throw new Error('nodes必须是数组');
  }

  if (!data.links || !Array.isArray(data.links)) {
    throw new Error('links必须是数组');
  }

  // 验证每个节点
  data.nodes.forEach((node, index) => {
    validateGraphNode(node, index);
  });

  // 如果nodes为空，links也应该为空
  if (data.nodes.length === 0) {
    if (data.links.length > 0) {
      console.warn('nodes为空时，links也应该为空，已自动过滤无效链接');
      data.links = [];
    }
    return;
  }

  // 创建节点ID集合用于快速查找
  const nodeIds = new Set(data.nodes.map((node: any) => node.id));

  // 验证每个链接
  data.links.forEach((link, index) => {
    validateGraphLink(link, index);
    
    // 额外验证：确保链接的source和target都在节点集合中
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    if (!nodeIds.has(sourceId)) {
      throw new Error(`链接 ${index} 缺少有效的source`);
    }
    
    if (!nodeIds.has(targetId)) {
      throw new Error(`链接 ${index} 缺少有效的target`);
    }
  });
};

/**
 * 验证GraphNode数据结构
 */
export const validateGraphNode = (node: any, index: number): asserts node is GraphNode => {
  if (!node) {
    throw new Error(`节点 ${index} 为空`);
  }

  if (!node.id || typeof node.id !== 'string') {
    throw new Error(`节点 ${index} 缺少有效的id`);
  }

  if (!node.type || !Object.values(NodeType).includes(node.type)) {
    throw new Error(`节点 ${index} 缺少有效的type`);
  }

  if (!node.name || typeof node.name !== 'string') {
    throw new Error(`节点 ${index} 缺少有效的name`);
  }

  if (node.val === undefined || typeof node.val !== 'number' || node.val <= 0) {
    throw new Error(`节点 ${index} 缺少有效的val`);
  }

  if (node.group === undefined || typeof node.group !== 'number') {
    throw new Error(`节点 ${index} 缺少有效的group`);
  }
};

/**
 * 验证GraphLink数据结构
 */
export const validateGraphLink = (link: any, index: number): asserts link is GraphLink => {
  if (!link) {
    throw new Error(`链接 ${index} 为空`);
  }

  if (!link.source) {
    throw new Error(`链接 ${index} 缺少有效的source`);
  }

  if (!link.target) {
    throw new Error(`链接 ${index} 缺少有效的target`);
  }

  if (link.value === undefined || typeof link.value !== 'number' || link.value < 0) {
    throw new Error(`链接 ${index} 缺少有效的value`);
  }

  if (!link.type || !Object.values(InteractionType).includes(link.type)) {
    throw new Error(`链接 ${index} 缺少有效的type`);
  }
};

/**
 * 转换API返回的数据为前端格式
 */
export const transformGraphData = (data: any): GraphData => {
  try {
    validateGraphData(data);

    // 确保数据结构正确
    return {
      nodes: data.nodes.map((node: any) => ({
        id: node.id,
        type: node.type,
        name: node.name,
        group: node.group || 0,
        val: node.val || 10,
        studentProfile: node.studentProfile,
        teacherProfile: node.teacherProfile,
        knowledgeProfile: node.knowledgeProfile
      })),
      links: data.links.map((link: any) => ({
        source: link.source,
        target: link.target,
        value: link.value,
        type: link.type
      }))
    };
  } catch (error) {
    console.error('转换数据失败:', error);
    throw error;
  }
};

/**
 * 验证ClassInfo数据结构
 */
export const validateClassInfo = (classInfo: any): asserts classInfo is { school: string; grade: string; classId: string } => {
  if (!classInfo) {
    throw new Error('班级信息为空');
  }

  if (!classInfo.school || typeof classInfo.school !== 'string' || classInfo.school.trim() === '') {
    throw new Error('学校名称不能为空');
  }

  if (!classInfo.grade || typeof classInfo.grade !== 'string' || classInfo.grade.trim() === '') {
    throw new Error('年级不能为空');
  }

  if (!classInfo.classId || typeof classInfo.classId !== 'string' || classInfo.classId.trim() === '') {
    throw new Error('班级不能为空');
  }
};

/**
 * 验证Scenario数据
 */
export const validateScenario = (scenario: any): asserts scenario is string => {
  if (!scenario || typeof scenario !== 'string') {
    throw new Error('场景类型必须是字符串');
  }
};

/**
 * 清理和规范化数据
 */
export const sanitizeGraphData = (data: GraphData): GraphData => {
  return {
    nodes: data.nodes.map(node => ({
      ...node,
      id: node.id.trim(),
      name: node.name.trim(),
      type: node.type
    })),
    links: data.links.map(link => ({
      ...link,
      source: typeof link.source === 'object' ? link.source : link.source.trim(),
      target: typeof link.target === 'object' ? link.target : link.target.trim(),
      type: link.type
    }))
  };
};
