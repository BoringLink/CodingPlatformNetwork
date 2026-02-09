import { fetchGraphData, fetchWithRetry } from "./apiService";

// Mock fetch API and Response
global.fetch = jest.fn();
global.Response = class MockResponse implements Response {
  constructor(body: any, init?: ResponseInit) {
    this.body = body;
    this.status = init?.status || 200;
    this.statusText = init?.statusText || "OK";
    this.headers = new Map(Object.entries(init?.headers || {}));
  }

  body: any;
  status: number;
  statusText: string;
  headers: Map<string, string>;
  redirected: boolean = false;
  type: ResponseType = "basic";
  url: string = "";

  get ok(): boolean {
    return this.status >= 200 && this.status < 300;
  }

  async json() {
    if (!this.body) {
      throw new Error("Unexpected end of JSON input");
    }
    return JSON.parse(this.body);
  }

  async text() {
    return this.body;
  }

  async formData() {
    return new FormData();
  }

  async blob() {
    return new Blob([this.body]);
  }

  async arrayBuffer() {
    return new TextEncoder().encode(this.body);
  }

  get bodyUsed() {
    return false;
  }

  get() {
    return "";
  }

  has() {
    return false;
  }

  keys() {
    return [];
  }

  values() {
    return [];
  }

  entries() {
    return [];
  }

  forEach() {
    // Empty implementation
  }
} as any;

const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe("apiService", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe("fetchWithRetry", () => {
    it("should succeed on first attempt", async () => {
      const mockResponse = new Response(JSON.stringify({ data: "test" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });

      mockFetch.mockResolvedValueOnce(mockResponse);

      const response = await fetchWithRetry("http://example.com");
      expect(response).toBe(mockResponse);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://example.com",
        expect.objectContaining({}),
      );
    });

    it("should retry on failure", async () => {
      const mockError = new Error("Network error");
      const mockResponse = new Response(JSON.stringify({ data: "test" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });

      mockFetch.mockRejectedValueOnce(mockError);
      mockFetch.mockResolvedValueOnce(mockResponse);

      const response = await fetchWithRetry("http://example.com", {}, 2);
      expect(response).toBe(mockResponse);
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://example.com",
        expect.objectContaining({}),
      );
    });

    it("should throw error after max retries", async () => {
      const mockError = new Error("Network error");

      mockFetch.mockRejectedValue(mockError);

      await expect(fetchWithRetry("http://example.com", {}, 2)).rejects.toThrow(
        "Network error",
      );
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenCalledWith(
        "http://example.com",
        expect.objectContaining({}),
      );
    });
  });

  describe("fetchGraphData", () => {
    it("should fetch graph data successfully", async () => {
      const mockData = {
        nodes: [
          {
            id: "S1",
            type: "STUDENT",
            name: "学生1",
            group: 3,
            val: 8,
          },
        ],
        links: [],
      };

      const mockResponse = new Response(JSON.stringify(mockData), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });

      mockFetch.mockResolvedValueOnce(mockResponse);

      const data = await fetchGraphData({
        school: "三墩小学",
        grade: "五年级",
        classId: "2班",
      });

      expect(data).toEqual(mockData);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      // 检查URL是否包含正确的参数（不检查具体编码）
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("http://localhost:3000/api/v1/graph-data"),
        expect.objectContaining({
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }),
      );
    });

    it("should handle API error", async () => {
      const mockResponse = new Response(
        JSON.stringify({ message: "API error" }),
        {
          status: 500,
          statusText: "Internal Server Error",
          headers: { "Content-Type": "application/json" },
        },
      );

      mockFetch.mockResolvedValueOnce(mockResponse);

      await expect(
        fetchGraphData({
          school: "三墩小学",
          grade: "五年级",
          classId: "2班",
        }),
      ).rejects.toThrow("API error");
    });

    it("should handle network error", async () => {
      const mockError = new Error("Network error");

      mockFetch.mockRejectedValueOnce(mockError);

      await expect(
        fetchGraphData({
          school: "三墩小学",
          grade: "五年级",
          classId: "2班",
        }),
      ).rejects.toThrow("Network error");
    });

    it("should handle empty response", async () => {
      const mockResponse = new Response("", {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });

      mockFetch.mockResolvedValueOnce(mockResponse);

      await expect(
        fetchGraphData({
          school: "三墩小学",
          grade: "五年级",
          classId: "2班",
        }),
      ).rejects.toThrow("Unexpected end of JSON input");
    });
  });
});
