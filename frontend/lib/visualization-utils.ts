import {
  Subgraph,
  VisualizationData,
  VisualizationNode,
  VisualizationEdge,
  NodeType,
  RelationshipType,
} from "@/types/api";

/**
 * Convert Subgraph data to VisualizationData format
 */
export function convertSubgraphToVisualizationData(
  subgraph: Subgraph
): VisualizationData {
  // Map node types to sizes
  const nodeSizeMap: Record<NodeType, number> = {
    Student: 30,
    Teacher: 35,
    Course: 40,
    KnowledgePoint: 25,
    ErrorType: 25,
  };

  // Map node types to colors
  const nodeColorMap: Record<NodeType, string> = {
    Student: "#60a5fa", // blue
    Teacher: "#34d399", // green
    Course: "#fbbf24", // yellow
    KnowledgePoint: "#a78bfa", // purple
    ErrorType: "#f87171", // red
  };

  // Create visualization nodes
  const nodes: VisualizationNode[] = subgraph.nodes.map((node) => {
    // Generate a label based on node properties
    let label =
      node.properties.name ||
      node.properties.studentId ||
      node.properties.courseId ||
      node.properties.knowledgePointId ||
      node.properties.errorTypeId ||
      node.id;
    label = String(label).substring(0, 20); // Truncate long labels

    return {
      id: node.id,
      label: label as string,
      type: node.type,
      color: nodeColorMap[node.type] || "#9ca3af",
      size: nodeSizeMap[node.type] || 30,
    };
  });

  // Create visualization edges
  const edges: VisualizationEdge[] = subgraph.relationships.map(
    (relationship) => ({
      id: relationship.id,
      source: relationship.fromNodeId,
      target: relationship.toNodeId,
      type: relationship.type,
      weight: relationship.weight,
    })
  );

  return {
    nodes,
    edges,
  };
}

/**
 * Generate a unique ID for elements
 */
export function generateId(prefix: string = "id"): string {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Calculate node degree (number of connections)
 */
export function calculateNodeDegrees(
  nodes: VisualizationNode[],
  edges: VisualizationEdge[]
): Record<string, number> {
  const degrees: Record<string, number> = {};

  // Initialize all nodes with degree 0
  nodes.forEach((node) => {
    degrees[node.id] = 0;
  });

  // Count edges
  edges.forEach((edge) => {
    degrees[edge.source] = (degrees[edge.source] || 0) + 1;
    degrees[edge.target] = (degrees[edge.target] || 0) + 1;
  });

  return degrees;
}

/**
 * Filter visualization data based on criteria
 */
export function filterVisualizationData(
  data: VisualizationData,
  filters: {
    nodeTypes?: NodeType[];
    relationshipTypes?: RelationshipType[];
  }
): VisualizationData {
  const { nodeTypes, relationshipTypes } = filters;

  // Filter nodes if nodeTypes is provided
  const filteredNodes = nodeTypes
    ? data.nodes.filter((node) => nodeTypes.includes(node.type))
    : data.nodes;

  // Get filtered node IDs
  const filteredNodeIds = new Set(filteredNodes.map((node) => node.id));

  // Filter edges: only include edges where both source and target are in filtered nodes
  // and edge type is in relationshipTypes (if provided)
  const filteredEdges = data.edges.filter((edge) => {
    const sourceIncluded = filteredNodeIds.has(edge.source);
    const targetIncluded = filteredNodeIds.has(edge.target);
    const typeIncluded =
      !relationshipTypes || relationshipTypes.includes(edge.type);

    return sourceIncluded && targetIncluded && typeIncluded;
  });

  return {
    nodes: filteredNodes,
    edges: filteredEdges,
  };
}

/**
 * Calculate graph statistics
 */
export function calculateGraphStatistics(data: VisualizationData) {
  const nodeTypeCount: Record<string, number> = {};
  const relationshipTypeCount: Record<string, number> = {};

  // Count node types
  data.nodes.forEach((node) => {
    nodeTypeCount[node.type] = (nodeTypeCount[node.type] || 0) + 1;
  });

  // Count relationship types
  data.edges.forEach((edge) => {
    relationshipTypeCount[edge.type] = (relationshipTypeCount[edge.type] || 0) + 1;
  });

  const nodeDegrees = calculateNodeDegrees(data.nodes, data.edges);
  const averageDegree =
    Object.values(nodeDegrees).reduce((sum, degree) => sum + degree, 0) /
    data.nodes.length;

  return {
    totalNodes: data.nodes.length,
    totalEdges: data.edges.length,
    nodeTypeCount,
    relationshipTypeCount,
    averageDegree,
    maxDegree: Math.max(...Object.values(nodeDegrees)),
    minDegree: Math.min(...Object.values(nodeDegrees)),
  };
}
