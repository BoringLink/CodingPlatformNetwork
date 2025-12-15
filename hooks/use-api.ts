import {
  useQuery,
  useMutation,
  UseMutationOptions,
  UseQueryOptions,
  useQueryClient,
} from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import {
  GraphFilter,
  NodeDetails,
  Node,
  Relationship,
  Subgraph,
  VisualizationData,
  Subview,
  ImportResult,
  Report,
} from "@/types/api";

/**
 * Custom hooks for API data fetching using TanStack Query
 */

// Nodes hooks
export function useNodes(
  params?: Record<string, unknown>,
  options?: UseQueryOptions<{ nodes: Node[] }>
) {
  return useQuery({
    queryKey: ["nodes", params],
    queryFn: () => apiClient.nodes.list(params),
    ...options,
  });
}

export function useNodeDetails(
  nodeId: string,
  options?: UseQueryOptions<NodeDetails>
) {
  return useQuery({
    queryKey: ["nodeDetails", nodeId],
    queryFn: () => apiClient.nodes.getDetails(nodeId),
    enabled: !!nodeId,
    ...options,
  });
}

// Relationships hooks
export function useRelationships(
  params?: Record<string, unknown>,
  options?: UseQueryOptions<{ relationships: Relationship[] }>
) {
  return useQuery({
    queryKey: ["relationships", params],
    queryFn: () => apiClient.relationships.list(params),
    ...options,
  });
}

// Subgraph hooks
export function useSubgraph(
  rootNodeId: string,
  depth: number,
  params?: Record<string, unknown>,
  options?: UseQueryOptions<Subgraph>
) {
  return useQuery({
    queryKey: ["subgraph", rootNodeId, depth, params],
    queryFn: () => apiClient.subgraph.get(rootNodeId, depth, params),
    enabled: !!rootNodeId && depth > 0,
    ...options,
  });
}

// Visualization hooks
export function useVisualization(
  rootNodeId: string,
  depth: number,
  params?: Record<string, unknown>,
  options?: UseQueryOptions<VisualizationData>
) {
  return useQuery({
    queryKey: ["visualization", rootNodeId, depth, params],
    queryFn: () => apiClient.visualization.get(rootNodeId, depth, params),
    enabled: !!rootNodeId && depth > 0,
    ...options,
  });
}

// Subviews hooks
export function useSubviews(
  options?: UseQueryOptions<{ subviews: Subview[] }>
) {
  return useQuery({
    queryKey: ["subviews"],
    queryFn: () => apiClient.subviews.list(),
    ...options,
  });
}

export function useSubview(
  subviewId: string,
  options?: UseQueryOptions<Subview>
) {
  return useQuery({
    queryKey: ["subview", subviewId],
    queryFn: () => apiClient.subviews.get(subviewId),
    enabled: !!subviewId,
    ...options,
  });
}

export function useCreateSubview(
  options?: UseMutationOptions<
    Subview,
    Error,
    { name: string; filter: GraphFilter }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => apiClient.subviews.create(data),
    onSuccess: () => {
      // Invalidate subviews list when a new subview is created
      queryClient.invalidateQueries({ queryKey: ["subviews"] });
    },
    ...options,
  });
}

// Import hooks
export function useImportData(
  options?: UseMutationOptions<
    ImportResult,
    Error,
    { records: Record<string, unknown>[]; batchSize: number }
  >
) {
  return useMutation({
    mutationFn: (data) => apiClient.import.importBatch(data),
    ...options,
  });
}

// Report hooks
export function useReport(
  params?: Record<string, unknown>,
  options?: UseQueryOptions<Report>
) {
  return useQuery({
    queryKey: ["report", params],
    queryFn: () => apiClient.reports.generate(params),
    ...options,
  });
}
