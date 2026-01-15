import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { NodeType, RelationshipType } from "@/types/api";
import { DateRange } from "react-day-picker";

// Types for graph visualization
export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  color: string;
  size: number;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: RelationshipType;
  weight?: number;
}

export interface GraphFilter {
  nodeTypes: NodeType[];
  relationshipTypes: RelationshipType[];
  dateRange?: DateRange;
  school?: string;
  grade?: number;
  class?: string;
}

interface GraphState {
  // Graph data
  nodes: GraphNode[];
  edges: GraphEdge[];

  // Selected elements
  selectedNodeId: string | null;
  highlightedNodeIds: string[];
  hoveredNodeId: string | null;

  // Interaction state
  isInteracting: boolean;
  interactionMode: "select" | "highlight" | "pan" | "zoom";

  // Filters
  pendingFilter: GraphFilter;
  appliedFilter: GraphFilter;

  // Subview
  currentSubviewId: string | null;

  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setHighlightedNodes: (nodeIds: string[]) => void;
  setHoveredNode: (nodeId: string | null) => void;
  setPendingFilter: (filter: GraphFilter) => void;
  setAppliedFilter: (filter: GraphFilter) => void;
  resetFilters: () => void;
  setCurrentSubview: (subviewId: string | null) => void;
  setInteractionMode: (mode: "select" | "highlight" | "pan" | "zoom") => void;
  setIsInteracting: (isInteracting: boolean) => void;
  highlightNodeNeighbors: (nodeId: string) => void;
  clearHighlighting: () => void;
  clearGraph: () => void;
}

const defaultPendingFilter: GraphFilter = {
  nodeTypes: ["Student", "Teacher", "KnowledgePoint"],
  relationshipTypes: [
    "CHAT_WITH",
    "LIKES",
    "TEACHES",
    "LEARNS",
    "CONTAINS",
    "RELATES_TO",
  ],
  // dateRange: { from: new Date(), to: new Date() },
  school: undefined, // 保持为空，用户需要主动选择
  grade: undefined, // 保持为空，用户需要主动选择
  class: undefined, // 保持为空，用户需要主动选择
};

// 初始应用筛选器为空，强制用户主动选择筛选条件
const initialAppliedFilter: GraphFilter = {
  nodeTypes: [], // 空数组，阻止初始加载
  relationshipTypes: [],
  // dateRange: undefined,
  school: undefined,
  grade: undefined, // undefined，阻止初始加载
  class: undefined,
};

export const useGraphStore = create<GraphState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        nodes: [],
        edges: [],
        selectedNodeId: null,
        highlightedNodeIds: [],
        hoveredNodeId: null,
        isInteracting: false,
        interactionMode: "select",
        pendingFilter: { ...defaultPendingFilter },
        appliedFilter: { ...initialAppliedFilter },
        currentSubviewId: null,

        // Actions
        setNodes: (nodes) => set({ nodes }),
        setEdges: (edges) => set({ edges }),
        setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
        setHighlightedNodes: (nodeIds) => set({ highlightedNodeIds: nodeIds }),
        setHoveredNode: (nodeId) => set({ hoveredNodeId: nodeId }),
        setPendingFilter: (filter) => set({ pendingFilter: filter }),
        setAppliedFilter: (filter) => set({ appliedFilter: filter }),
        resetFilters: () =>
          set({
            pendingFilter: { ...defaultPendingFilter },
            appliedFilter: { ...initialAppliedFilter },
          }),
        setCurrentSubview: (subviewId) => set({ currentSubviewId: subviewId }),
        setInteractionMode: (mode) => set({ interactionMode: mode }),
        setIsInteracting: (isInteracting) => set({ isInteracting }),

        // Highlight node neighbors
        highlightNodeNeighbors: (nodeId) => {
          const { edges } = get();

          // Find all edges connected to the node
          const connectedEdges = edges.filter(
            (edge) => edge.source === nodeId || edge.target === nodeId
          );

          // Get all connected nodes
          const connectedNodeIds = new Set<string>([nodeId]);
          connectedEdges.forEach((edge) => {
            if (edge.source !== nodeId) connectedNodeIds.add(edge.source);
            if (edge.target !== nodeId) connectedNodeIds.add(edge.target);
          });

          set({
            highlightedNodeIds: Array.from(connectedNodeIds),
            selectedNodeId: nodeId,
          });
        },

        // Clear highlighting
        clearHighlighting: () =>
          set({ highlightedNodeIds: [], selectedNodeId: null }),

        // Clear graph
        clearGraph: () =>
          set({
            nodes: [],
            edges: [],
            selectedNodeId: null,
            highlightedNodeIds: [],
            hoveredNodeId: null,
          }),
      }),
      {
        name: "graph-storage",
        version: 2, // 版本号用于触发迁移
        partialize: (state) => ({
          pendingFilter: state.pendingFilter,
          appliedFilter: state.appliedFilter,
          currentSubviewId: state.currentSubviewId,
        }),
        // 深度合并恢复的状态与默认状态
        merge: (persistedState, currentState) => {
          const persisted = persistedState as Partial<GraphState>;
          return {
            ...currentState,
            ...persisted,
            // 深度合并 pendingFilter
            pendingFilter: {
              ...currentState.pendingFilter,
              ...(persisted.pendingFilter || {}),
            },
            // 深度合并 appliedFilter
            appliedFilter: {
              ...currentState.appliedFilter,
              ...(persisted.appliedFilter || {}),
            },
          };
        },
        // 迁移函数：从数组格式迁移到单值格式
        migrate: (persistedState: unknown, version: number) => {
          const state = persistedState as Record<string, unknown>;
          
          if (version < 2) {
            // 迁移 pendingFilter
            const pendingFilter = state.pendingFilter as Record<string, unknown> | undefined;
            if (pendingFilter) {
              // 从数组取第一个值，或设为 undefined
              if (Array.isArray(pendingFilter.schools)) {
                pendingFilter.school = pendingFilter.schools[0];
                delete pendingFilter.schools;
              }
              if (Array.isArray(pendingFilter.grades)) {
                pendingFilter.grade = pendingFilter.grades[0];
                delete pendingFilter.grades;
              }
              if (Array.isArray(pendingFilter.classes)) {
                pendingFilter.class = pendingFilter.classes[0];
                delete pendingFilter.classes;
              }
            }
            
            // 迁移 appliedFilter
            const appliedFilter = state.appliedFilter as Record<string, unknown> | undefined;
            if (appliedFilter) {
              if (Array.isArray(appliedFilter.schools)) {
                appliedFilter.school = appliedFilter.schools[0];
                delete appliedFilter.schools;
              }
              if (Array.isArray(appliedFilter.grades)) {
                appliedFilter.grade = appliedFilter.grades[0];
                delete appliedFilter.grades;
              }
              if (Array.isArray(appliedFilter.classes)) {
                appliedFilter.class = appliedFilter.classes[0];
                delete appliedFilter.classes;
              }
            }
          }
          
          return state;
        },
      }
    ),
    { name: "GraphStore" }
  )
);
