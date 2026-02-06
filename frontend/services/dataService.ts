import { GraphData, GraphNode, GraphLink, NodeType, Scenario, Resource, ClassInfo, InteractionType } from '../types';
import { realStudentData, studentInteractions, getAvailableOptions } from './realData';

// Teacher data constants (暂时保留教师数据模拟生成，因为没有真实教师数据)
const TEACHER_SLOGANS = [
  "因材施教，寓教于乐。",
  "点燃智慧的火花，照亮未来的道路。",
  "用心灵教书，用爱心育人。",
  "每个孩子都是一颗闪亮的星星。",
  "科技赋能教育，创新引领未来。",
  "做学生的良师益友。",
  "不仅传授知识，更要启迪智慧。"
];
const TEACHER_TITLES = ["高级教师", "一级教师", "二级教师", "特级教师", "实习教师"];
const SUBJECTS = ["信息技术", "数学", "科学", "综合实践"];

// Predefined Knowledge Data for Collaborative Scenario (Word/Poster making)
const WORD_KNOWLEDGE_DATA = [
  { name: '插入图片', category: 'Word操作', content: '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。' },
  { name: '设置艺术字', category: 'Word操作', content: '选中文本，点击"插入"选项卡，选择"艺术字"，挑选喜欢的样式并调整大小。' },
  { name: '页面布局', category: 'Word操作', content: '点击"布局"选项卡，设置页边距、纸张方向（横向/纵向）及分栏。' },
  { name: '文本框使用', category: 'Word操作', content: '点击"插入"->"文本框"，绘制横排或竖排文本框，便于自由移动文字位置。' },
  { name: '表格制作', category: 'Word操作', content: '点击"插入"->"表格"，拖动鼠标选择行数和列数，或点击"插入表格"输入数值。' },
  { name: '图片环绕', category: 'Word操作', content: '选中图片，点击出现的"布局选项"图标，选择"四周型"或"紧密型"环绕，使文字围绕图片排版。' },
  { name: '字体美化', category: 'Word操作', content: '选中文字，在"开始"选项卡中调整字体、字号、颜色及加粗倾斜效果。' },
  { name: '背景设置', category: 'Word操作', content: '点击"设计"选项卡，选择"页面颜色"为文档添加背景色或填充效果。' },
  { name: '形状绘制', category: 'Word操作', content: '点击"插入"->"形状"，选择矩形、圆形或线条进行绘制，并设置填充与轮廓。' },
  { name: '保存与导出', category: 'Word操作', content: '点击"文件"->"另存为"，选择保存路径和文件格式（如.docx或.pdf）。' },
];

// Predefined Knowledge Data for Information Technology (Python Programming)
const PYTHON_KNOWLEDGE_DATA = [
  { name: '变量与赋值', category: 'Python基础', content: '理解变量作为存储数据的容器，掌握命名规则，学会使用 = 进行赋值操作。' },
  { name: '数据类型', category: 'Python基础', content: '掌握整数(int)、浮点数(float)、字符串(str)和布尔值(bool)的基本概念与转换。' },
  { name: '输入与输出', category: '交互逻辑', content: '熟练使用 print() 输出结果，使用 input() 获取用户输入并进行类型转换。' },
  { name: '条件判断', category: '控制结构', content: '理解程序的分支逻辑，掌握 if-elif-else 结构及缩进规则。' },
  { name: '逻辑运算', category: '运算逻辑', content: '掌握 and, or, not 逻辑运算符的使用，能够构建复杂的条件表达式。' },
  { name: 'For循环', category: '循环结构', content: '学会使用 for 循环遍历 range() 序列或列表，实现重复执行代码块。' },
  { name: 'While循环', category: '循环结构', content: '理解 while 循环的执行条件，掌握 break 和 continue 语句控制循环流程。' },
  { name: '列表操作', category: '数据结构', content: '掌握列表(List)的创建、索引访问、切片以及 append()、remove() 等常用方法。' },
  { name: 'Turtle绘图', category: '图形编程', content: '使用 Python 的 turtle 库绘制几何图形，通过控制画笔移动理解顺序执行。' },
  { name: '调试与纠错', category: '编程思维', content: '能够识别常见的语法错误(SyntaxError)和缩进错误，学会阅读报错信息进行调试。' },
];

// Predefined Knowledge Data for General Subjects (Fallback)
const GENERAL_KNOWLEDGE_DATA = [
  { name: '鸡兔同笼基础', category: '数学概念', content: '理解假设法的基本原理，学会用列表法解决简单的鸡兔同笼问题。' },
  { name: '假设法', category: '解题策略', content: '假设全是鸡或全是兔，计算出腿数差，从而推导出另一种动物的数量。' },
  { name: '方程解法', category: '代数方法', content: '设立未知数x和y，根据头和脚的数量建立二元一次方程组求解。' },
  { name: '抬腿法', category: '趣味解法', content: '想象所有动物抬起两只脚，剩余的脚数除以2即为兔子的数量。' },
  { name: '列表枚举', category: '基础方法', content: '有序地列出可能的头数组合，计算对应的脚数，直到找到符合条件的答案。' },
  { name: '应用题分析', category: '逻辑思维', content: '从文字描述中提取关键信息（头总数、脚总数），转化为数学模型。' },
  { name: '验算', category: '学习习惯', content: '将计算出的鸡和兔的数量带入原题，核对头和脚的总数是否正确。' },
  { name: '图形结合', category: '数形结合', content: '画圆圈代表头，画竖线代表脚，直观地分配脚的数量来求解。' },
  { name: '进阶变式', category: '拓展应用', content: '解决"得失问题"或"租船问题"等本质与鸡兔同笼相同的变式题目。' },
  { name: '错题分析', category: '反思总结', content: '分析计算错误或逻辑漏洞，总结解题步骤中的易错点。' },
];

// Helper to get random int (仅用于教师和知识点生成)
const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

/**
 * 获取可用的班级选项（从真实数据中获取）
 */
export const getClassOptions = () => {
  return getAvailableOptions();
};

/**
 * 生成教师节点（暂时保留模拟数据）
 */
function generateTeacherNodes(classInfo: ClassInfo, scenario: Scenario): GraphNode[] {
  const nodes: GraphNode[] = [];
  const teacherCount = randomInt(1, 2);

  for (let i = 0; i < teacherCount; i++) {
    const gender = Math.random() > 0.5 ? '男' : '女';
    nodes.push({
      id: `T${i}`,
      type: NodeType.TEACHER,
      name: `教师 ${String.fromCharCode(65 + i)}`,
      group: 1,
      val: 25,
      teacherProfile: {
        gender,
        age: randomInt(25, 55),
        school: classInfo.school,
        employeeId: `T${2024001 + i}`,
        title: TEACHER_TITLES[randomInt(0, TEACHER_TITLES.length - 1)],
        teachingGrade: classInfo.grade,
        teachingClass: classInfo.classId,
        subject: scenario === Scenario.ONLINE_COURSE ? "信息技术" : SUBJECTS[randomInt(0, SUBJECTS.length - 1)],
        slogan: TEACHER_SLOGANS[randomInt(0, TEACHER_SLOGANS.length - 1)]
      }
    });
  }

  return nodes;
}

/**
 * 生成知识点节点
 */
function generateKnowledgeNodes(scenario: Scenario): GraphNode[] {
  const nodes: GraphNode[] = [];

  let knowledgeSource = GENERAL_KNOWLEDGE_DATA;
  if (scenario === Scenario.COLLABORATIVE) {
    knowledgeSource = WORD_KNOWLEDGE_DATA;
  } else if (scenario === Scenario.ONLINE_COURSE) {
    knowledgeSource = PYTHON_KNOWLEDGE_DATA;
  }

  const knowledgeCount = Math.min(knowledgeSource.length, randomInt(9, 11));
  for (let i = 0; i < knowledgeCount; i++) {
    const kData = knowledgeSource[i % knowledgeSource.length];
    nodes.push({
      id: `K${i}`,
      type: NodeType.KNOWLEDGE,
      name: kData.name,
      group: 2,
      val: 15,
      knowledgeProfile: {
        content: kData.content,
        category: kData.category
      }
    });
  }

  return nodes;
}

/**
 * 从真实数据生成学生节点
 */
function generateStudentNodesFromRealData(classInfo: ClassInfo): GraphNode[] {
  const nodes: GraphNode[] = [];

  // 筛选匹配的学生
  const matchedStudents = realStudentData.filter(student =>
    student.school === classInfo.school &&
    student.grade === classInfo.grade &&
    student.classId === classInfo.classId
  );

  // 如果没有匹配的学生，使用所有学生作为fallback
  const studentsToUse = matchedStudents.length > 0 ? matchedStudents : realStudentData;

  studentsToUse.forEach((student, index) => {
    nodes.push({
      id: `S${index}`,
      type: NodeType.STUDENT,
      name: student.name,
      group: 3,
      val: 8,
      studentProfile: student.profile
    });
  });

  return nodes;
}

/**
 * 生成教师-学生交互边
 */
function generateTeacherStudentLinks(
  teacherNodes: GraphNode[],
  studentNodes: GraphNode[]
): GraphLink[] {
  const links: GraphLink[] = [];

  teacherNodes.forEach(teacher => {
    const targetCount = randomInt(14, 16);
    const shuffledStudents = [...studentNodes].sort(() => 0.5 - Math.random());
    const targets = shuffledStudents.slice(0, targetCount);

    targets.forEach(student => {
      const isPhysical = Math.random() > 0.2;
      links.push({
        source: teacher.id,
        target: student.id,
        value: 2,
        type: isPhysical ? InteractionType.PHYSICAL : InteractionType.PLATFORM
      });
    });
  });

  return links;
}

/**
 * 从真实交互数据生成学生-学生边
 */
function generateStudentInteractionLinks(studentNodes: GraphNode[]): GraphLink[] {
  const links: GraphLink[] = [];

  // 创建姓名到节点ID的映射
  const nameToId = new Map<string, string>();
  studentNodes.forEach(node => {
    nameToId.set(node.name, node.id);
  });

  // 基于真实交互数据生成边
  studentInteractions.forEach(interaction => {
    const sourceId = nameToId.get(interaction.source);
    const targetId = nameToId.get(interaction.target);

    if (sourceId && targetId) {
      // 检查是否已存在
      const exists = links.find(
        l => (l.source === sourceId && l.target === targetId) ||
          (l.source === targetId && l.target === sourceId)
      );

      if (!exists) {
        links.push({
          source: sourceId,
          target: targetId,
          value: 1,
          type: InteractionType.PLATFORM
        });
      }
    }
  });

  // 如果真实交互数据不足，随机补充一些边
  const minPeerLinks = studentNodes.length * 3; // 每个学生平均3-4个同伴
  if (links.length < minPeerLinks) {
    studentNodes.forEach(student => {
      const existingPeers = links.filter(
        l => l.source === student.id || l.target === student.id
      ).length;

      if (existingPeers < 3) {
        const peerCount = randomInt(3 - existingPeers, 4 - existingPeers);
        const peers = studentNodes.filter(s => s.id !== student.id);
        const selectedPeers = peers.sort(() => 0.5 - Math.random()).slice(0, peerCount);

        selectedPeers.forEach(peer => {
          const exists = links.find(
            l => (l.source === student.id && l.target === peer.id) ||
              (l.source === peer.id && l.target === student.id)
          );

          if (!exists) {
            const isPhysical = Math.random() > 0.15;
            links.push({
              source: student.id,
              target: peer.id,
              value: 1,
              type: isPhysical ? InteractionType.PHYSICAL : InteractionType.PLATFORM
            });
          }
        });
      }
    });
  }

  return links;
}

/**
 * 生成学生-知识点交互边
 */
function generateStudentKnowledgeLinks(
  studentNodes: GraphNode[],
  knowledgeNodes: GraphNode[]
): GraphLink[] {
  const links: GraphLink[] = [];

  studentNodes.forEach(student => {
    const kCount = randomInt(3, 4);
    const selectedKPs = [...knowledgeNodes].sort(() => 0.5 - Math.random()).slice(0, kCount);

    selectedKPs.forEach(kp => {
      links.push({
        source: student.id,
        target: kp.id,
        value: 1.5,
        type: InteractionType.PLATFORM
      });
    });
  });

  return links;
}

/**
 * 生成图谱数据（使用真实学生数据）
 */
export const generateGraphData = (scenario: Scenario, classInfo: ClassInfo): GraphData => {
  const nodes: GraphNode[] = [];
  const links: GraphLink[] = [];

  console.log('开始生成图谱数据（使用真实学生数据）...', { scenario, classInfo });

  // 1. 生成教师节点（模拟数据）
  const teacherNodes = generateTeacherNodes(classInfo, scenario);
  nodes.push(...teacherNodes);

  // 2. 生成知识点节点
  const knowledgeNodes = generateKnowledgeNodes(scenario);
  nodes.push(...knowledgeNodes);

  // 3. 生成学生节点（真实数据）
  const studentNodes = generateStudentNodesFromRealData(classInfo);
  console.log(`成功加载 ${studentNodes.length} 个学生节点（真实数据）`);
  nodes.push(...studentNodes);

  // 4. 生成教师-学生交互边
  const teacherStudentLinks = generateTeacherStudentLinks(teacherNodes, studentNodes);
  links.push(...teacherStudentLinks);

  // 5. 生成学生-学生交互边（基于真实交互数据）
  const studentInteractionLinks = generateStudentInteractionLinks(studentNodes);
  console.log(`成功生成 ${studentInteractionLinks.length} 个学生交互边（含真实数据）`);
  links.push(...studentInteractionLinks);

  // 6. 生成学生-知识点交互边
  const studentKnowledgeLinks = generateStudentKnowledgeLinks(studentNodes, knowledgeNodes);
  links.push(...studentKnowledgeLinks);

  console.log(`图谱生成完成: ${nodes.length} 个节点, ${links.length} 条边`);

  return { nodes, links };
};

/**
 * 生成学习资源
 */
export const generateResources = (knowledgeNodes: GraphNode[]): Resource[] => {
  const resources: Resource[] = [];

  const templates = [
    { suffix: '操作演示视频', type: '视频', url: 'https://b23.tv/example1' },
    { suffix: '基础教程文档', type: '文档', url: 'course-doc.pdf' },
    { suffix: '进阶技巧解析', type: '文章', url: 'advanced-tips.html' },
    { suffix: '练习题集', type: '练习题', url: 'exercises.pdf' },
    { suffix: '互动小测验', type: '互动游戏', url: 'quiz.app' },
    { suffix: '常见问题解答', type: '文章', url: 'faq.html' }
  ];

  for (let i = 0; i < 6; i++) {
    const kCount = randomInt(1, 2);
    const relatedKNodes = knowledgeNodes
      .sort(() => 0.5 - Math.random())
      .slice(0, kCount);

    const kIds = relatedKNodes.map(n => n.id);
    const mainKNode = relatedKNodes[0];

    const template = templates[i % templates.length];

    resources.push({
      id: `R${i}`,
      title: `${mainKNode.name} - ${template.suffix}`,
      type: template.type,
      relatedKnowledgeIds: kIds,
      accuracy: randomInt(80, 99),
      description: `针对"${relatedKNodes.map(n => n.name).join('、')}"的${template.type}资源，旨在帮助学生掌握核心概念与操作步骤。`,
      url: template.url
    });
  }
  return resources;
};