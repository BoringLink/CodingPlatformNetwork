export interface StudentProfile {
  school: string | null;
  grade: string | null;
  classId: string | null;
  learningStylePreference?: string | null;
  personality?: string | null;
  groupBehavior?: string | null;
}

export interface TeacherProfile {
  school: string | null;
  teachingGrade?: string | null;
  teachingClass?: string | null;
  subject?: string | null;
}

export interface KnowledgeProfile {
  content?: string | null;
  type?: string | null;
  category?: string | null;
  parentId?: string | null;
  parentName?: string | null;
}

export interface Node {
  id: string;
  type: "STUDENT" | "TEACHER" | "KNOWLEDGE";
  name: string;
  group: number;
  val: number;
  studentProfile?: StudentProfile;
  teacherProfile?: TeacherProfile;
  knowledgeProfile?: KnowledgeProfile;
}

export interface Link {
  source: string;
  target: string;
  value: number;
  type: "PHYSICAL" | "PLATFORM";
  actionType?: string | null;
}

export interface GraphMeta {
  nodeCount: number;
  linkCount: number;
  scenarioCode: string;
}

export interface GraphData {
  nodes: Node[];
  links: Link[];
  meta: GraphMeta;
}
