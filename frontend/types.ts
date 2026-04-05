import { SimulationNodeDatum, SimulationLinkDatum } from "d3";

export enum NodeType {
  STUDENT = "STUDENT",
  TEACHER = "TEACHER",
  KNOWLEDGE = "KNOWLEDGE",
}

export enum InteractionType {
  PHYSICAL = "PHYSICAL", // 基于物理空间采集 (实线)
  PLATFORM = "PLATFORM", // 基于平台采集 (虚线)
}

export enum Scenario {
  SHOW_CASE = "展示场景",
  ONLINE_COURSE = "学科课程在线学习",
  TEACHER_QA = "课后线上教师授课答疑",
  HOME_LEARNING = "家庭在线学习",
  COLLABORATIVE_LEARNING = "在线协作学习",
  INFORMAL_LEARNING = "社团课等非正式学习",
}

export interface CognitiveAttributes {
  knowledgeReserve: number; // 知识储备
  learningEngagement: number; // 学习投入
  cognitiveLoad: number; // 认知负荷
  learningMotivation: number; // 学习动机
  computationalThinking: number; // 计算思维
  humanAiTrust: number; // 人机信任度
  learningMethod: number; // 学习方法倾向
  learningAttitude: number; // 学习态度
}

export interface LearningStyleProfile {
  preference?: "和他人一起学习" | "独自学习" | string;
  personality?: "外向" | "内向" | string;
  groupBehavior?: "挺身而出，畅所欲言" | "保持安静，倾听意见" | string;
}

export interface StudentTemplateDimension {
  code: string;
  name: string;
  category: string;
  score: number;
  level: string;
}

export interface StudentCognitiveTemplate {
  // 认知模板文档中的完整结构（用于详情面板或后续扩展）
  profileMeta?: {
    version?: string;
    generatedAt?: string;
    totalScore?: number;
  };
  dimensions?: StudentTemplateDimension[];
  learningStyle?: LearningStyleProfile;
  knowledgeReserve?: {
    dataConcept?: number;
    algorithmConcept?: number;
    networkConcept?: number;
    informationProcessing?: number;
    informationSecurity?: number;
    aiConcept?: number;
  };
  learningMotivation?: {
    interest?: number;
    usefulness?: number;
    expectation?: number;
  };
  learningAttitude?: {
    enjoyment?: number;
    confidence?: number;
    interest?: number;
  };
  learningEngagement?: {
    cognitiveEngagement?: number[];
  };
  selfRegulatedLearning?: number[];
  computationalThinking?: {
    evaluation?: number[];
  };
  learningApproach?: {
    deepLearning?: number[];
  };
  cognitiveLoad?: {
    internalLoad?: number[];
  };
  humanMachineTrust?: number[];
  aiLiteracy?: number[];
}

export interface StudentProfile extends CognitiveAttributes {
  school: string;
  grade: string;
  classId: string;

  // 认知模板文档中的非8维核心字段
  learningStylePreference?: LearningStyleProfile["preference"];
  personality?: LearningStyleProfile["personality"];
  groupBehavior?: LearningStyleProfile["groupBehavior"];
  selfRegulatedLearning?: number;
  aiLiteracy?: number;

  // 文档命名兼容别名
  humanMachineTrust?: number; // = humanAiTrust
  learningApproach?: number; // = learningMethod
  priorKnowledge?: number; // = knowledgeReserve

  template?: StudentCognitiveTemplate;
}

export interface KnowledgeProfile {
  content: string; // 知识点具体内容/操作步骤
  category?: string; // 分类，如 Word操作，数学概念
  type: "知识单元" | "知识点"; // 知识点类型
  parentId?: string; // 上级知识点ID
  parentName?: string; // 上级知识点名称
  relatedKnowledgeIds: string[]; // 关联知识点ID数组
  relatedKnowledgeNames: string[]; // 关联知识点名称数组
}

export interface TeacherProfile {
  school: string;
  teachingGrade: string;
  teachingClass: string;
  subject?: string;
}

export interface GraphNode extends SimulationNodeDatum {
  id: string;
  type: NodeType;
  name: string;
  group: number;
  val: number; // For visualization radius
  studentProfile?: StudentProfile; // Optional profile for students
  knowledgeProfile?: KnowledgeProfile; // Optional profile for knowledge points
  teacherProfile?: TeacherProfile; // Optional profile for teachers
}

export interface GraphLink extends SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number; // For stroke width
  type: InteractionType; // Interaction classification
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface Resource {
  id: string;
  title: string;
  type: string;
  relatedKnowledgeIds: string[]; // IDs of K-nodes this resource covers
  accuracy: number; // 0-100%
  description: string;
  url?: string; // Optional URL for display
}

export interface ClassInfo {
  school: string;
  grade: string;
  classId: string;
}
