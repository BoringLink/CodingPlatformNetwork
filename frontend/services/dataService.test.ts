import { fetchGraphData, generateResources } from './dataService';
import { fetchGraphData as fetchGraphDataFromApi } from './apiService';
import { transformGraphData } from './dataValidator';
import { graphDataCache } from './performanceUtils';

// Mock dependencies
jest.mock('./apiService');
jest.mock('./dataValidator');

const mockFetchGraphDataFromApi = fetchGraphDataFromApi as jest.MockedFunction<typeof fetchGraphDataFromApi>;
const mockTransformGraphData = transformGraphData as jest.MockedFunction<typeof transformGraphData>;

describe('dataService', () => {
  beforeEach(() => {
    mockFetchGraphDataFromApi.mockClear();
    mockTransformGraphData.mockClear();
    graphDataCache.clear();
  });

  describe('fetchGraphData', () => {
    it('should fetch and transform graph data successfully', async () => {
      const mockRawData = {
        nodes: [
          {
            id: 'S1',
            type: 'STUDENT',
            name: '学生1',
            group: 3,
            val: 8,
          },
        ],
        links: [],
      };

      const mockTransformedData = {
        nodes: [
          {
            id: 'S1',
            type: 'STUDENT',
            name: '学生1',
            group: 3,
            val: 8,
          },
        ],
        links: [],
      };

      mockFetchGraphDataFromApi.mockResolvedValueOnce(mockRawData);
      mockTransformGraphData.mockReturnValueOnce(mockTransformedData);

      const result = await fetchGraphData('ONLINE_COURSE', {
        school: '三墩小学',
        grade: '五年级',
        classId: '2班',
      });

      expect(result).toEqual(mockTransformedData);
      expect(mockFetchGraphDataFromApi).toHaveBeenCalledTimes(1);
      expect(mockTransformGraphData).toHaveBeenCalledTimes(1);
    });

    it('should use cached data when available', async () => {
      const mockRawData = {
        nodes: [
          {
            id: 'S1',
            type: 'STUDENT',
            name: '学生1',
            group: 3,
            val: 8,
          },
        ],
        links: [],
      };

      const mockTransformedData = {
        nodes: [
          {
            id: 'S1',
            type: 'STUDENT',
            name: '学生1',
            group: 3,
            val: 8,
          },
        ],
        links: [],
      };

      // First call (should fetch from API)
      mockFetchGraphDataFromApi.mockResolvedValueOnce(mockRawData);
      mockTransformGraphData.mockReturnValueOnce(mockTransformedData);

      const firstResult = await fetchGraphData('ONLINE_COURSE', {
        school: '三墩小学',
        grade: '五年级',
        classId: '2班',
      });

      expect(firstResult).toEqual(mockTransformedData);
      expect(mockFetchGraphDataFromApi).toHaveBeenCalledTimes(1);

      // Reset mock call count
      mockFetchGraphDataFromApi.mockClear();

      // Second call (should use cache)
      const secondResult = await fetchGraphData('ONLINE_COURSE', {
        school: '三墩小学',
        grade: '五年级',
        classId: '2班',
      });

      expect(secondResult).toEqual(mockTransformedData);
      expect(mockFetchGraphDataFromApi).not.toHaveBeenCalled();
    });

    it('should throw error for invalid class info', async () => {
      await expect(
        fetchGraphData('ONLINE_COURSE', {
          school: '',
          grade: '五年级',
          classId: '2班',
        })
      ).rejects.toThrow('学校名称不能为空');
    });

    it('should throw error when API fails', async () => {
      const mockError = new Error('API error');
      mockFetchGraphDataFromApi.mockRejectedValueOnce(mockError);

      await expect(
        fetchGraphData('ONLINE_COURSE', {
          school: '三墩小学',
          grade: '五年级',
          classId: '2班',
        })
      ).rejects.toThrow('获取图谱数据失败: API error');
    });
  });

  describe('generateResources', () => {
    it('should generate resources from knowledge nodes', () => {
      const mockKnowledgeNodes = [
        {
          id: 'K1',
          type: 'KNOWLEDGE',
          name: '知识点1',
          group: 2,
          val: 15,
        },
        {
          id: 'K2',
          type: 'KNOWLEDGE',
          name: '知识点2',
          group: 2,
          val: 15,
        },
      ];

      const resources = generateResources(mockKnowledgeNodes);
      expect(resources).toBeInstanceOf(Array);
      expect(resources.length).toBeGreaterThan(0);
      expect(resources[0]).toHaveProperty('id');
      expect(resources[0]).toHaveProperty('title');
      expect(resources[0]).toHaveProperty('type');
      expect(resources[0]).toHaveProperty('relatedKnowledgeIds');
      expect(resources[0]).toHaveProperty('accuracy');
      expect(resources[0]).toHaveProperty('description');
    });

    it('should return empty array for no knowledge nodes', () => {
      const resources = generateResources([]);
      expect(resources).toEqual([]);
    });

    it('should handle null knowledge nodes', () => {
      const resources = generateResources(null as any);
      expect(resources).toEqual([]);
    });
  });
});
