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

  return response.json();
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
          url.searchParams.append(key, String(value));
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
      return apiClient.get<{ nodes: import('../types/api').Node[] }>('/api/nodes', params);
    },

    /**
     * Get node details by ID
     */
    async getDetails(nodeId: string) {
      return apiClient.get<import('../types/api').NodeDetails>(`/api/nodes/${nodeId}/details`);
    },
  },

  relationships: {
    /**
     * Get relationships with optional filters
     */
    async list(params?: Record<string, unknown>) {
      return apiClient.get<{ relationships: import('../types/api').Relationship[] }>('/api/relationships', params);
    },
  },

  subgraph: {
    /**
     * Get subgraph by root node ID and depth
     */
    async get(rootNodeId: string, depth: number, params?: Record<string, unknown>) {
      return apiClient.get<import('../types/api').Subgraph>('/api/subgraph', {
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
    async get(rootNodeId: string, depth: number, params?: Record<string, unknown>) {
      return apiClient.get<import('../types/api').VisualizationData>('/api/visualization', {
        rootNodeId,
        depth,
        ...params,
      });
    },
  },

  subviews: {
    /**
     * Get all subviews
     */
    async list() {
      return apiClient.get<{ subviews: import('../types/api').Subview[] }>('/api/subviews');
    },

    /**
     * Create a new subview
     */
    async create(data: { name: string; filter: import('../types/api').GraphFilter }) {
      return apiClient.post<import('../types/api').Subview>('/api/subviews', data);
    },

    /**
     * Get a subview by ID
     */
    async get(subviewId: string) {
      return apiClient.get<import('../types/api').Subview>(`/api/subviews/${subviewId}`);
    },
  },

  import: {
    /**
     * Import data batch
     */
    async importBatch(data: { records: Record<string, unknown>[]; batchSize: number }) {
      return apiClient.post<import('../types/api').ImportResult>('/api/import', data);
    },
  },

  reports: {
    /**
     * Generate a report
     */
    async generate(params?: Record<string, unknown>) {
      return apiClient.get<import('../types/api').Report>('/api/reports', params);
    },
  },
};
