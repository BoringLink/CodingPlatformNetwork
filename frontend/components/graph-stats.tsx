import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VisualizationNode, VisualizationEdge, NodeType } from "@/types/api";

interface GraphStatsProps {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
}

// 节点类型中文映射
const nodeTypeLabels: Record<NodeType | string, string> = {
  Student: "学生",
  Teacher: "教师",
  KnowledgePoint: "知识点",
};

export const GraphStats = ({ nodes, edges }: GraphStatsProps) => {
  // 计算节点类型统计
  const nodeTypeStats = nodes.reduce((acc, node) => {
    const type = node.type;
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // 计算总节点和总边数量
  const totalNodes = nodes.length;
  const totalEdges = edges.length;

  return (
    <div className="flex items-center gap-2">
      {/* 总节点和总边数量 */}
      <Badge variant="outline" className="text-sm">
        总节点: {totalNodes}
      </Badge>
      <Badge variant="outline" className="text-sm">
        总边数: {totalEdges}
      </Badge>
      
      {/* 节点类型统计 */}
      {Object.entries(nodeTypeStats).map(([type, count]) => (
        <Badge key={type} variant="secondary" className="text-sm">
          {nodeTypeLabels[type] || type}: {count}
        </Badge>
      ))}
    </div>
  );
};

// 统计卡片组件，用于侧边栏或其他位置
export const GraphStatsCard = ({ nodes, edges }: GraphStatsProps) => {
  // 计算节点类型统计
  const nodeTypeStats = nodes.reduce((acc, node) => {
    const type = node.type;
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // 计算总节点和总边数量
  const totalNodes = nodes.length;
  const totalEdges = edges.length;

  return (
    <Card className="mt-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">图谱统计</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* 总览 */}
          <div className="flex flex-col gap-1">
            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400">总览</h4>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-xs">
                总节点: {totalNodes}
              </Badge>
              <Badge variant="outline" className="text-xs">
                总边数: {totalEdges}
              </Badge>
            </div>
          </div>

          {/* 节点类型分布 */}
          <div>
            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">节点类型分布</h4>
            <div className="space-y-1">
              {Object.entries(nodeTypeStats).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-xs">{nodeTypeLabels[type] || type}</span>
                  <Badge variant="secondary" className="text-xs">
                    {count}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
