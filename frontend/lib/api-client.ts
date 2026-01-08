/**
 * API Client for communicating with the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: Record<string, unknown>
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || `HTTP Error ${response.status}`,
      response.status,
      errorData
    );
  }

  const result = await response.json();
  // 处理后端返回的 { success: boolean, data: T } 结构
  if (result && result.success && result.data !== undefined) {
    return result.data as T;
  }
  // 如果不是预期的结构，直接返回结果
  return result as T;
}

export const apiClient = {
  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
    const url = new URL(`${API_BASE_URL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            // 处理数组类型：只在数组非空时发送
            if (value.length > 0)
              value.forEach((item) =>
                url.searchParams.append(key, String(item))
              );
          } else {
            url.searchParams.append(key, String(value));
          }
        }
      });
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return handleResponse<T>(response);
  },

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return handleResponse<T>(response);
  },

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return handleResponse<T>(response);
  },

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return handleResponse<T>(response);
  },

  /**
   * API endpoints
   */
  nodes: {
    /**
     * Get nodes with optional filters
     */
    async list(params?: Record<string, unknown>) {
      return apiClient.get<{ nodes: import("../types/api").Node[] }>(
        "/api/nodes",
        params
      );
    },

    /**
     * Get node details by ID
     */
    async getDetails(nodeId: string) {
      return apiClient.get<import("../types/api").NodeDetails>(
        `/api/nodes/${nodeId}/details`
      );
    },
  },

  relationships: {
    /**
     * Get relationships with optional filters
     */
    async list(params?: Record<string, unknown>) {
      return apiClient.get<{
        relationships: import("../types/api").Relationship[];
      }>("/api/relationships", params);
    },
  },

  subgraph: {
    /**
     * Get subgraph by root node ID and depth
     */
    async get(
      rootNodeId: string,
      depth: number,
      params?: Record<string, unknown>
    ) {
      return apiClient.get<import("../types/api").Subgraph>("/api/subgraph", {
        rootNodeId,
        depth,
        ...params,
      });
    },
  },

  visualization: {
    /**
     * Get visualization data for a subgraph
     */
    async get(
      rootNodeId: string,
      depth: number,
      params?: Record<string, unknown>
    ) {
      return apiClient.get<import("../types/api").VisualizationData>(
        "/api/visualization",
        {
          rootNodeId,
          depth,
          ...params,
        }
      );
    },
  },

  subviews: {
    /**
     * Get all subviews
     */
    async list() {
      return apiClient.get<{ subviews: import("../types/api").Subview[] }>(
        "/api/subviews"
      );
    },

    /**
     * Create a new subview
     */
    async create(data: {
      name: string;
      filter: import("../types/api").GraphFilter;
    }) {
      return apiClient.post<import("../types/api").Subview>(
        "/api/subviews",
        data
      );
    },

    /**
     * Get a subview by ID
     */
    async get(subviewId: string) {
      return apiClient.get<import("../types/api").Subview>(
        `/api/subviews/${subviewId}`
      );
    },
  },

  import: {
    /**
     * Import data batch
     */
    async importBatch(data: {
      records: Record<string, unknown>[];
      batchSize: number;
    }) {
      return apiClient.post<import("../types/api").ImportResult>(
        "/api/import",
        data
      );
    },
  },

  reports: {
    /**
     * Generate a report
     */
    async generate(params?: Record<string, unknown>) {
      const rawReport = await apiClient.get<any>("/api/reports", params);

      // Transform snake_case to camelCase and adjust structure to match frontend types
      return {
        graphStatistics: {
          totalNodes: rawReport.graph_statistics.total_nodes,
          nodesByType: rawReport.graph_statistics.node_type_distribution,
          totalRelationships: rawReport.graph_statistics.total_relationships,
          relationshipsByType:
            rawReport.graph_statistics.relationship_type_distribution,
        },
        studentPerformance: {
          highFrequencyErrors: (
            rawReport.student_performance.high_frequency_errors || []
          ).map((error: any) => ({
            knowledgePoint: error.knowledge_point_name,
            errorCount: error.total_occurrences,
            affectedStudents: error.student_count,
          })),
          studentsNeedingAttention: (
            rawReport.student_performance.students_needing_attention || []
          ).map((student: any) => ({
            studentId: student.student_name,
            errorCount: student.total_errors,
            courses: [], // Not provided in backend response
          })),
        },
        courseEffectiveness: {
          courseMetrics: (
            rawReport.course_effectiveness.course_metrics || []
          ).map((metric: any) => ({
            courseId: metric.course_id,
            courseName: metric.course_name,
            participationRate: metric.participation || 0, // This is actually student count, not rate
            errorRate: metric.error_rate || 0,
            averageProgress: 0, // Not provided in backend response
          })),
        },
        interactionPatterns: {
          activeCommunities: (
            rawReport.interaction_patterns.social_networks || []
          ).map((network: any) => ({
            students: network.connected_students || [],
            interactionCount: network.connection_count || 0,
          })),
          isolatedStudents: (
            rawReport.interaction_patterns.isolated_students || []
          ).map((student: any) => student.student_id),
        },
        generatedAt: rawReport.generated_at,
      } as import("../types/api").Report;
    },
  },
};
