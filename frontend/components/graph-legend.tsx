import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// 导入类型定义
import { NodeType, RelationshipType } from "@/types/api";

// 颜色映射（与 graph-visualization.tsx 保持一致）
const nodeColorMap: Record<NodeType | string, string> = {
  Student: "#60a5fa",
  Teacher: "#34d399",
  Course: "#fbbf24",
  KnowledgePoint: "#a78bfa",
  ErrorType: "#f87171",
};

const edgeColorMap: Record<RelationshipType | string, string> = {
  CHAT_WITH: "#60a5fa",
  LIKES: "#f472b6",
  TEACHES: "#34d399",
  LEARNS: "#fbbf24",
  CONTAINS: "#a78bfa",
  HAS_ERROR: "#f87171",
  RELATES_TO: "#9ca3af",
};

const edgeStyleMap: Record<RelationshipType | string, string> = {
  CHAT_WITH: "solid",
  LIKES: "dashed",
  TEACHES: "solid",
  LEARNS: "solid",
  CONTAINS: "dot",
  HAS_ERROR: "solid",
  RELATES_TO: "dashed",
};

// 关系类型中文映射
const relationshipTypeLabels: Record<RelationshipType | string, string> = {
  CHAT_WITH: "聊天",
  LIKES: "喜欢",
  TEACHES: "教授",
  LEARNS: "学习",
  CONTAINS: "包含",
  HAS_ERROR: "存在错误",
  RELATES_TO: "相关",
};

// 节点类型中文映射
const nodeTypeLabels: Record<NodeType | string, string> = {
  Student: "学生",
  Teacher: "教师",
  Course: "课程",
  KnowledgePoint: "知识点",
  ErrorType: "错误类型",
};

export const GraphLegend = () => {
  return (
    <Card className="mt-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">图谱图例</CardTitle>
      </CardHeader>
      <CardContent>
        {/* 节点图例 */}
        <div className="mb-4">
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">节点类型</h4>
          <div className="space-y-2">
            {Object.entries(nodeColorMap).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full border border-white"
                  style={{ backgroundColor: color }}
                />
                <span className="text-sm">
                  {nodeTypeLabels[type] || type}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 边图例 */}
        <div>
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">关系类型</h4>
          <div className="space-y-2">
            {Object.entries(edgeColorMap).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div className="flex items-center gap-2">
                  {/* 线条样式 */}
                  <div
                    className="w-10 h-0.5"
                    style={{
                      backgroundColor: color,
                      borderStyle: edgeStyleMap[type] as any,
                      borderWidth: edgeStyleMap[type] === "dot" ? "2px" : "1px",
                      borderColor: edgeStyleMap[type] === "dot" ? "transparent" : color,
                    }}
                  />
                  {/* 箭头 */}
                  <div
                    className="w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent"
                    style={{ borderBottomColor: color }}
                  />
                </div>
                <span className="text-sm">
                  {relationshipTypeLabels[type] || type}
                </span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
