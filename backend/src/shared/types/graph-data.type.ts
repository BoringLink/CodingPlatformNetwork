export interface StudentProfile {
  school: string;
  grade: string;
  classId: string;
  knowledgeReserve: number;
  learningEngagement: number;
  cognitiveLoad: number;
  learningMotivation: number;
  computationalThinking: number;
  humanAiTrust: number;
  learningMethod: number;
  learningAttitude: number;
}

export interface TeacherProfile {
  school: string;
  teachingGrade: string;
  teachingClass: string;
}

export interface KnowledgeProfile {
  content: string;
  type: string;
  parentId: string | null;
  parentName: string | null;
  relatedKnowledgeIds: string;
  relatedKnowledgeNames: string;
}

export interface Node {
  id: string;
  type: 'STUDENT' | 'TEACHER' | 'KNOWLEDGE';
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
  type: string;
}

export interface GraphData {
  nodes: Node[];
  links: Link[];
}