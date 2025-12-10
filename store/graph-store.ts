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
  hoveredNodeId: string | null;
  
  // Interaction state
  isInteracting: boolean;
  interactionMode: 'select' | 'highlight' | 'pan' | 'zoom';
  
  // Filters
  filter: GraphFilter;
  
  // Subview
  currentSubviewId: string | null;
  
  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setHighlightedNodes: (nodeIds: string[]) => void;
  setHoveredNode: (nodeId: string | null) => void;
  setFilter: (filter: GraphFilter) => void;
  setCurrentSubview: (subviewId: string | null) => void;
  setInteractionMode: (mode: 'select' | 'highlight' | 'pan' | 'zoom') => void;
  setIsInteracting: (isInteracting: boolean) => void;
  highlightNodeNeighbors: (nodeId: string) => void;
  clearHighlighting: () => void;
  clearGraph: () => void;
}

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
        interactionMode: 'select',
        filter: {},
        currentSubviewId: null,

        // Actions
        setNodes: (nodes) => set({ nodes }),
        setEdges: (edges) => set({ edges }),
        setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
        setHighlightedNodes: (nodeIds) => set({ highlightedNodeIds: nodeIds }),
        setHoveredNode: (nodeId) => set({ hoveredNodeId: nodeId }),
        setFilter: (filter) => set({ filter }),
        setCurrentSubview: (subviewId) => set({ currentSubviewId: subviewId }),
        setInteractionMode: (mode) => set({ interactionMode: mode }),
        setIsInteracting: (isInteracting) => set({ isInteracting }),
        
        // Highlight node neighbors
        highlightNodeNeighbors: (nodeId) => {
          const { edges } = get();
          
          // Find all edges connected to the node
          const connectedEdges = edges.filter(
            edge => edge.source === nodeId || edge.target === nodeId
          );
          
          // Get all connected nodes
          const connectedNodeIds = new Set<string>([nodeId]);
          connectedEdges.forEach(edge => {
            if (edge.source !== nodeId) connectedNodeIds.add(edge.source);
            if (edge.target !== nodeId) connectedNodeIds.add(edge.target);
          });
          
          set({ 
            highlightedNodeIds: Array.from(connectedNodeIds),
            selectedNodeId: nodeId
          });
        },
        
        // Clear highlighting
        clearHighlighting: () => set({ highlightedNodeIds: [], selectedNodeId: null }),
        
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
        partialize: (state) => ({
          filter: state.filter,
          currentSubviewId: state.currentSubviewId,
        }),
      }
    ),
    { name: "GraphStore" }
  )
);
