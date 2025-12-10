"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "./ui/card";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { NodeType, RelationshipType } from "@/types/api";
import { Filter, RefreshCw, Save } from "lucide-react";

interface FilterPanelProps {
  // Node type filtering
  selectedNodeTypes: NodeType[];
  onNodeTypeChange: (nodeTypes: NodeType[]) => void;

  // Relationship type filtering
  selectedRelationshipTypes: RelationshipType[];
  onRelationshipTypeChange: (relationshipTypes: RelationshipType[]) => void;

  // Date range filtering (optional for now)
  dateRange?: { start: Date; end: Date };
  onDateRangeChange?: (range: { start: Date; end: Date } | undefined) => void;

  // Actions
  onApplyFilters: () => void;
  onResetFilters: () => void;
  onCreateSubview: () => void;

  // State
  isLoading?: boolean;
}

const NODE_TYPES = [
  { value: "Student" as const, label: "学生" },
  { value: "Teacher" as const, label: "教师" },
  { value: "Course" as const, label: "课程" },
  { value: "KnowledgePoint" as const, label: "知识点" },
  { value: "ErrorType" as const, label: "错误类型" },
];

const RELATIONSHIP_TYPES = [
  { value: "CHAT_WITH" as const, label: "聊天互动" },
  { value: "LIKES" as const, label: "点赞互动" },
  { value: "TEACHES" as const, label: "教学互动" },
  { value: "LEARNS" as const, label: "学习关系" },
  { value: "CONTAINS" as const, label: "包含关系" },
  { value: "HAS_ERROR" as const, label: "错误关系" },
  { value: "RELATES_TO" as const, label: "关联关系" },
];

export function FilterPanel({
  selectedNodeTypes,
  onNodeTypeChange,
  selectedRelationshipTypes,
  onRelationshipTypeChange,
  onApplyFilters,
  onResetFilters,
  onCreateSubview,
  isLoading = false,
}: FilterPanelProps) {
  // Handle node type checkbox change
  const handleNodeTypeToggle = (nodeType: NodeType) => {
    const newSelectedTypes = selectedNodeTypes.includes(nodeType)
      ? selectedNodeTypes.filter((type) => type !== nodeType)
      : [...selectedNodeTypes, nodeType];
    onNodeTypeChange(newSelectedTypes);
  };

  // Handle relationship type checkbox change
  const handleRelationshipTypeToggle = (relationshipType: RelationshipType) => {
    const newSelectedTypes = selectedRelationshipTypes.includes(
      relationshipType
    )
      ? selectedRelationshipTypes.filter((type) => type !== relationshipType)
      : [...selectedRelationshipTypes, relationshipType];
    onRelationshipTypeChange(newSelectedTypes);
  };

  return (
    <Card className="w-full">
      <CardHeader className="p-4 px-4 py-3 sm:p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            <CardTitle className="text-base sm:text-lg font-medium">筛选条件</CardTitle>
          </div>
        </div>
        <CardDescription className="text-xs sm:text-sm text-gray-500 mt-1">
          自定义知识图谱的显示内容
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 px-4 py-3 sm:p-4 space-y-4">
        {/* Node Type Filter */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">节点类型</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {NODE_TYPES.map((nodeType) => (
              <div key={nodeType.value} className="flex items-center gap-2">
                <Checkbox
                  id={`node-type-${nodeType.value}`}
                  checked={selectedNodeTypes.includes(nodeType.value)}
                  onCheckedChange={() => handleNodeTypeToggle(nodeType.value)}
                  className="h-4 w-4"
                />
                <label
                  htmlFor={`node-type-${nodeType.value}`}
                  className="text-sm font-medium truncate"
                >
                  {nodeType.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Relationship Type Filter */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">关系类型</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {RELATIONSHIP_TYPES.map((relationshipType) => (
              <div
                key={relationshipType.value}
                className="flex items-center gap-2"
              >
                <Checkbox
                  id={`rel-type-${relationshipType.value}`}
                  checked={selectedRelationshipTypes.includes(
                    relationshipType.value
                  )}
                  onCheckedChange={() =>
                    handleRelationshipTypeToggle(relationshipType.value)
                  }
                  className="h-4 w-4"
                />
                <label
                  htmlFor={`rel-type-${relationshipType.value}`}
                  className="text-sm font-medium truncate"
                >
                  {relationshipType.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Date Range Filter (placeholder for now) */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">时间范围</h3>
          <div className="space-y-2">
            <p className="text-sm text-gray-500">时间范围筛选功能即将推出</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 pt-2 border-t pt-4">
          <Button
            className="flex-1"
            onClick={onApplyFilters}
            disabled={isLoading}
            size="sm"
          >
            <Filter className="mr-2 h-3 w-3 sm:mr-2 sm:h-4 sm:w-4" />
            应用筛选
          </Button>
          <Button
            variant="secondary"
            className="flex-1"
            onClick={onResetFilters}
            disabled={isLoading}
            size="sm"
          >
            <RefreshCw className="mr-2 h-3 w-3 sm:mr-2 sm:h-4 sm:w-4" />
            重置
          </Button>
          <Button
            variant="secondary"
            className="flex-1"
            onClick={onCreateSubview}
            disabled={isLoading}
            size="sm"
          >
            <Save className="mr-2 h-3 w-3 sm:mr-2 sm:h-4 sm:w-4" />
            保存为子视图
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
