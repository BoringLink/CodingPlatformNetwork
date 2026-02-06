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
  ONLINE_COURSE = "学科课程在线学习",
  AFTER_SCHOOL_QA = "课后线上教师授课答疑",
  HOME_LEARNING = "家庭在线学习",
  COLLABORATIVE = "在线协作学习",
  INFORMAL_CLUBS = "社团课等非正式学习",
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

export interface StudentProfile extends CognitiveAttributes {
  gender: "男" | "女";
  school: string;
  grade: string;
  classId: string;
}

export interface KnowledgeProfile {
  content: string; // 知识点具体内容/操作步骤
  category: string; // 分类，如 Word操作，数学概念
  type: "知识单元" | "知识点"; // 知识点类型
  parentId?: string; // 上级知识点ID
  parentName?: string; // 上级知识点名称
  relatedKnowledgeIds?: string[]; // 关联知识点ID数组
  relatedKnowledgeNames?: string[]; // 关联知识点名称数组
}

export interface TeacherProfile {
  school: string;
  teachingGrade: string;
  teachingClass: string;
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
