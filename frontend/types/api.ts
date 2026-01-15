/**
 * API Types - matching backend data models
 */

// Node Types
import { ElementDefinition } from "cytoscape";

export type NodeType = "Student" | "Teacher" | "KnowledgePoint";

// Relationship Types
export type RelationshipType =
  | "CHAT_WITH"
  | "LIKES"
  | "TEACHES"
  | "LEARNS"
  | "CONTAINS"
  | "RELATES_TO";

// Node interface
export interface Node {
  id: string;
  type: NodeType;
  properties: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

// Relationship interface
export interface Relationship {
  id: string;
  type: RelationshipType;
  fromNodeId: string;
  toNodeId: string;
  properties?: Record<string, unknown>;
  weight?: number;
}

// Subgraph interface
export interface Subgraph {
  nodes: Node[];
  relationships: Relationship[];
  metadata: {
    nodeCount: number;
    relationshipCount: number;
  };
}

// Visualization data
export interface VisualizationNode {
  id: string;
  label: string;
  type: NodeType;
  color: string;
  size: number;
  position?: { x: number; y: number };
}

export interface VisualizationEdge {
  id: string;
  source: string;
  target: string;
  type: RelationshipType;
  weight?: number;
}

export interface VisualizationData {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  layout?: {
    name: string;
    options: Record<string, unknown>;
  };
  llm_analysis?: unknown;
}

// Node details
export interface NodeDetails {
  node: Node;
  relationshipTypeCounts: Record<RelationshipType, number>;
  // connectedNodesCounts: {
  //   type: NodeType;
  //   count: number;
  // }[];
}

// Subview
export interface Subview {
  id: string;
  name: string;
  filter: GraphFilter;
  subgraph: Subgraph;
  createdAt: string;
}

// Graph filter
export interface GraphFilter {
  nodeTypes?: NodeType[];
  relationshipTypes?: RelationshipType[];
  dateRange?: { start: string; end: string };
  school?: string;
  grade?: number;
  class?: string;
  properties?: Record<string, unknown>;
  limit?: number;
  offset?: number;
}

// Import result
export interface ImportResult {
  successCount: number;
  failureCount: number;
  errors: ValidationError[];
}

export interface ValidationError {
  recordIndex: number;
  field: string;
  message: string;
}

// Report types
export interface Report {
  graphStatistics: GraphStatistics;
  studentPerformance: StudentPerformance;
  courseEffectiveness: CourseEffectiveness;
  interactionPatterns: InteractionPatterns;
  generatedAt: string;
}

export interface GraphStatistics {
  totalNodes: number;
  nodesByType: Record<NodeType, number>;
  totalRelationships: number;
  relationshipsByType: Record<RelationshipType, number>;
}

export interface StudentPerformance {
  highFrequencyErrors: {
    knowledgePoint: string;
    errorCount: number;
    affectedStudents: number;
  }[];
  studentsNeedingAttention: {
    studentId: string;
    errorCount: number;
    courses: string[];
  }[];
}

export interface CourseEffectiveness {
  courseMetrics: {
    courseId: string;
    courseName: string;
    participationRate: number;
    errorRate: number;
    averageProgress: number;
  }[];
}

export interface InteractionPatterns {
  activeCommunities: {
    students: string[];
    interactionCount: number;
  }[];
  isolatedStudents: string[];
}
