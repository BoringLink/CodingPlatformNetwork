import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

// Types for graph visualization
export interface GraphNode {
  id: string;
  label: string;
  type: "Student" | "Teacher" | "Course" | "KnowledgePoint" | "ErrorType";
  color: string;
  size: number;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface GraphFilter {
  nodeTypes?: string[];
  relationshipTypes?: string[];
  dateRange?: { start: Date; end: Date };
}

interface GraphState {
  // Graph data
  nodes: GraphNode[];
  edges: GraphEdge[];
  
  // Selected elements
  selectedNodeId: string | null;
  highlightedNodeIds: string[];
  
  // Filters
  filter: GraphFilter;
  
  // Subview
  currentSubviewId: string | null;
  
  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setHighlightedNodes: (nodeIds: string[]) => void;
  setFilter: (filter: GraphFilter) => void;
  setCurrentSubview: (subviewId: string | null) => void;
  clearGraph: () => void;
}

export const useGraphStore = create<GraphState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        nodes: [],
        edges: [],
        selectedNodeId: null,
        highlightedNodeIds: [],
        filter: {},
        currentSubviewId: null,

        // Actions
        setNodes: (nodes) => set({ nodes }),
        setEdges: (edges) => set({ edges }),
        setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
        setHighlightedNodes: (nodeIds) => set({ highlightedNodeIds: nodeIds }),
        setFilter: (filter) => set({ filter }),
        setCurrentSubview: (subviewId) => set({ currentSubviewId: subviewId }),
        clearGraph: () =>
          set({
            nodes: [],
            edges: [],
            selectedNodeId: null,
            highlightedNodeIds: [],
          }),
      }),
      {
        name: "graph-storage",
        partialize: (state) => ({
          filter: state.filter,
          currentSubviewId: state.currentSubviewId,
        }),
      }
    ),
    { name: "GraphStore" }
  )
);
