import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type {
  Node,
  Relationship,
  Subgraph,
  VisualizationData,
  NodeDetails,
  Subview,
  GraphFilter,
} from "@/types/api";

/**
 * Query keys for caching
 */
export const graphKeys = {
  all: ["graph"] as const,
  nodes: () => [...graphKeys.all, "nodes"] as const,
  nodesList: (filter?: GraphFilter) => [...graphKeys.nodes(), { filter }] as const,
  nodeDetails: (id: string) => [...graphKeys.nodes(), id] as const,
  relationships: () => [...graphKeys.all, "relationships"] as const,
  relationshipsList: (filter?: GraphFilter) =>
    [...graphKeys.relationships(), { filter }] as const,
  subgraph: (nodeId: string, depth: number) =>
    [...graphKeys.all, "subgraph", nodeId, depth] as const,
  visualization: (filter?: GraphFilter) =>
    [...graphKeys.all, "visualization", { filter }] as const,
  subviews: () => [...graphKeys.all, "subviews"] as const,
  subview: (id: string) => [...graphKeys.subviews(), id] as const,
};

/**
 * Fetch nodes with optional filtering
 */
export function useNodes(filter?: GraphFilter) {
  return useQuery({
    queryKey: graphKeys.nodesList(filter),
    queryFn: () => apiClient.get<Node[]>("/api/nodes", filter as unknown as Record<string, unknown>),
  });
}

/**
 * Fetch node details
 */
export function useNodeDetails(nodeId: string) {
  return useQuery({
    queryKey: graphKeys.nodeDetails(nodeId),
    queryFn: () => apiClient.get<NodeDetails>(`/api/nodes/${nodeId}/details`),
    enabled: !!nodeId,
  });
}

/**
 * Fetch relationships with optional filtering
 */
export function useRelationships(filter?: GraphFilter) {
  return useQuery({
    queryKey: graphKeys.relationshipsList(filter),
    queryFn: () => apiClient.get<Relationship[]>("/api/relationships", filter as unknown as Record<string, unknown>),
  });
}

/**
 * Fetch subgraph from a root node
 */
export function useSubgraph(nodeId: string, depth: number = 2) {
  return useQuery({
    queryKey: graphKeys.subgraph(nodeId, depth),
    queryFn: () =>
      apiClient.get<Subgraph>("/api/subgraph", { nodeId, depth }),
    enabled: !!nodeId,
  });
}

/**
 * Fetch visualization data
 */
export function useVisualization(filter?: GraphFilter) {
  return useQuery({
    queryKey: graphKeys.visualization(filter),
    queryFn: () => apiClient.get<VisualizationData>("/api/visualization", filter as unknown as Record<string, unknown>),
  });
}

/**
 * Fetch all subviews
 */
export function useSubviews() {
  return useQuery({
    queryKey: graphKeys.subviews(),
    queryFn: () => apiClient.get<Subview[]>("/api/subviews"),
  });
}

/**
 * Fetch a specific subview
 */
export function useSubview(subviewId: string) {
  return useQuery({
    queryKey: graphKeys.subview(subviewId),
    queryFn: () => apiClient.get<Subview>(`/api/subviews/${subviewId}`),
    enabled: !!subviewId,
  });
}

/**
 * Create a new subview
 */
export function useCreateSubview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; filter: GraphFilter }) =>
      apiClient.post<Subview>("/api/subviews", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: graphKeys.subviews() });
    },
  });
}

/**
 * Update subview filter
 */
export function useUpdateSubview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      subviewId,
      filter,
    }: {
      subviewId: string;
      filter: GraphFilter;
    }) => apiClient.put<Subview>(`/api/subviews/${subviewId}`, { filter }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: graphKeys.subview(variables.subviewId),
      });
      queryClient.invalidateQueries({ queryKey: graphKeys.subviews() });
    },
  });
}

/**
 * Delete a subview
 */
export function useDeleteSubview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subviewId: string) => apiClient.delete(`/api/subviews/${subviewId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: graphKeys.subviews() });
    },
  });
}
