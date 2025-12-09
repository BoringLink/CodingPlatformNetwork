"use client";

import { useState } from "react";
import { GraphVisualization } from "@/components/graph-visualization";

import { useVisualization } from "@/hooks/use-api";
import { NodeType, RelationshipType } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Filter, RefreshCw } from "lucide-react";

const GRAPH_LAYOUTS = [
  { value: "cose", label: "自动布局 (Cose)" },
  { value: "circle", label: "环形布局 (Circle)" },
  { value: "grid", label: "网格布局 (Grid)" },
  { value: "dagre", label: "层次布局 (Dagre)" },
  { value: "random", label: "随机布局 (Random)" },
];

const NODE_TYPES = [
  { value: "Student", label: "学生" },
  { value: "Teacher", label: "教师" },
  { value: "Course", label: "课程" },
  { value: "KnowledgePoint", label: "知识点" },
  { value: "ErrorType", label: "错误类型" },
];

const RELATIONSHIP_TYPES = [
  { value: "CHAT_WITH", label: "聊天互动" },
  { value: "LIKES", label: "点赞互动" },
  { value: "TEACHES", label: "教学互动" },
  { value: "LEARNS", label: "学习关系" },
  { value: "CONTAINS", label: "包含关系" },
  { value: "HAS_ERROR", label: "错误关系" },
  { value: "RELATES_TO", label: "关联关系" },
];

export default function GraphPage() {
  const [layout, setLayout] = useState("cose");
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();

  const [selectedNodeTypes, setSelectedNodeTypes] = useState<NodeType[]>([
    "Student",
    "Teacher",
    "Course",
    "KnowledgePoint",
    "ErrorType",
  ]);
  const [selectedRelationshipTypes, setSelectedRelationshipTypes] = useState<
    RelationshipType[]
  >([
    "CHAT_WITH",
    "LIKES",
    "TEACHES",
    "LEARNS",
    "CONTAINS",
    "HAS_ERROR",
    "RELATES_TO",
  ]);
  const [depth, setDepth] = useState(2);

  // Use the API hook to fetch visualization data
  // For now, we'll use a default root node ID and depth
  const {
    data: visualizationData,
    isLoading,
    refetch,
  } = useVisualization(
    "1", // Default root node ID
    depth,
    {
      nodeTypes: selectedNodeTypes,
      relationshipTypes: selectedRelationshipTypes,
    }
  );

  // Handle layout change
  const handleLayoutChange = (value: string) => {
    setLayout(value);
  };

  // Handle node type selection change
  const handleNodeTypeChange = (nodeType: NodeType) => {
    setSelectedNodeTypes((prev) => {
      if (prev.includes(nodeType)) {
        return prev.filter((type) => type !== nodeType);
      } else {
        return [...prev, nodeType];
      }
    });
  };

  // Handle relationship type selection change
  const handleRelationshipTypeChange = (relationshipType: RelationshipType) => {
    setSelectedRelationshipTypes((prev) => {
      if (prev.includes(relationshipType)) {
        return prev.filter((type) => type !== relationshipType);
      } else {
        return [...prev, relationshipType];
      }
    });
  };

  // Handle depth change
  const handleDepthChange = (newDepth: number) => {
    setDepth(newDepth);
  };

  // Handle node click
  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);
  };

  return (
    <div className="flex flex-col h-screen w-screen">
      {/* Header */}
      <header className="p-4 border-b bg-white dark:bg-gray-900">
        <h1 className="text-2xl font-bold">教育知识图谱可视化</h1>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 border-r bg-white dark:bg-gray-900 p-4 overflow-y-auto">
          {/* Controls Card */}
          <Card className="mb-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                可视化控制
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Layout Selector */}
              <div className="space-y-2">
                <label className="text-sm font-medium">布局类型</label>
                <Select value={layout} onValueChange={handleLayoutChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择布局" />
                  </SelectTrigger>
                  <SelectContent>
                    {GRAPH_LAYOUTS.map((layoutOption) => (
                      <SelectItem
                        key={layoutOption.value}
                        value={layoutOption.value}
                      >
                        {layoutOption.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Depth Control */}
              <div className="space-y-2">
                <label className="text-sm font-medium">探索深度: {depth}</label>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDepthChange(Math.max(1, depth - 1))}
                    disabled={depth <= 1}
                  >
                    -1
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDepthChange(depth + 1)}
                    disabled={depth >= 5}
                  >
                    +1
                  </Button>
                </div>
              </div>

              {/* Node Types */}
              <div className="space-y-2">
                <label className="text-sm font-medium">节点类型</label>
                <div className="space-y-1">
                  {NODE_TYPES.map((nodeType) => (
                    <div
                      key={nodeType.value}
                      className="flex items-center gap-2"
                    >
                      <Checkbox
                        id={`node-type-${nodeType.value}`}
                        checked={selectedNodeTypes.includes(
                          nodeType.value as NodeType
                        )}
                        onCheckedChange={() =>
                          handleNodeTypeChange(nodeType.value as NodeType)
                        }
                      />
                      <label
                        htmlFor={`node-type-${nodeType.value}`}
                        className="text-sm cursor-pointer"
                      >
                        {nodeType.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Relationship Types */}
              <div className="space-y-2">
                <label className="text-sm font-medium">关系类型</label>
                <div className="space-y-1 max-h-40 overflow-y-auto pr-2">
                  {RELATIONSHIP_TYPES.map((relationshipType) => (
                    <div
                      key={relationshipType.value}
                      className="flex items-center gap-2"
                    >
                      <Checkbox
                        id={`rel-type-${relationshipType.value}`}
                        checked={selectedRelationshipTypes.includes(
                          relationshipType.value as RelationshipType
                        )}
                        onCheckedChange={() =>
                          handleRelationshipTypeChange(
                            relationshipType.value as RelationshipType
                          )
                        }
                      />
                      <label
                        htmlFor={`rel-type-${relationshipType.value}`}
                        className="text-sm cursor-pointer"
                      >
                        {relationshipType.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Refresh Button */}
              <Button
                className="w-full"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                {isLoading ? "加载中..." : "刷新数据"}
              </Button>
            </CardContent>
          </Card>

          {/* Node Details Card */}
          {selectedNodeId && (
            <Card>
              <CardHeader>
                <CardTitle>节点详情</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm space-y-2">
                  <p>节点ID: {selectedNodeId}</p>
                  {/* More details will be added here when we implement the node details fetching */}
                </div>
              </CardContent>
            </Card>
          )}
        </aside>

        {/* Graph Visualization */}
        <main className="flex-1 bg-gray-50 dark:bg-gray-800">
          {isLoading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">
                  加载图谱数据...
                </p>
              </div>
            </div>
          ) : visualizationData ? (
            <GraphVisualization
              nodes={visualizationData.nodes}
              edges={visualizationData.edges}
              layout={layout}
              onNodeClick={handleNodeClick}
              selectedNodeId={selectedNodeId}
              className="w-full h-full"
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  暂无图谱数据
                </p>
                <Button onClick={() => refetch()}>加载数据</Button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
