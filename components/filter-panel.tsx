"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "./ui/card";
import { Button } from "./ui/button";
import { NodeType, RelationshipType } from "@/types/api";
import {
  Filter,
  RefreshCw,
  Save,
  Layers,
  Network,
  CalendarClock,
  Check,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface FilterPanelProps {
  selectedNodeTypes: NodeType[];
  onNodeTypeChange: (nodeTypes: NodeType[]) => void;
  selectedRelationshipTypes: RelationshipType[];
  onRelationshipTypeChange: (relationshipTypes: RelationshipType[]) => void;
  dateRange?: { start: Date; end: Date };
  onDateRangeChange?: (range: { start: Date; end: Date } | undefined) => void;
  onApplyFilters: () => void;
  onResetFilters: () => void;
  onCreateSubview: () => void;
  isLoading?: boolean;
}

// 颜色配置：与 GraphVisualization 保持视觉一致
// 使用 Tailwind 类近似 hex 颜色:
// Student(#60a5fa) -> blue-400
// Teacher(#34d399) -> emerald-400
// Course(#fbbf24) -> amber-400
// KnowledgePoint(#a78bfa) -> violet-400
// ErrorType(#f87171) -> red-400
const NODE_CONFIG: Record<
  NodeType,
  { label: string; colorClass: string; icon?: React.ReactNode }
> = {
  Student: {
    label: "学生",
    colorClass: "bg-blue-400 border-blue-400 hover:bg-blue-500",
  },
  Teacher: {
    label: "教师",
    colorClass: "bg-emerald-400 border-emerald-400 hover:bg-emerald-500",
  },
  Course: {
    label: "课程",
    colorClass: "bg-amber-400 border-amber-400 hover:bg-amber-500",
  },
  KnowledgePoint: {
    label: "知识点",
    colorClass: "bg-violet-400 border-violet-400 hover:bg-violet-500",
  },
  ErrorType: {
    label: "错误类型",
    colorClass: "bg-red-400 border-red-400 hover:bg-red-500",
  },
};

// 关系颜色配置
const RELATION_CONFIG: Record<
  RelationshipType,
  { label: string; colorClass: string }
> = {
  CHAT_WITH: {
    label: "聊天互动",
    colorClass: "text-blue-500 border-blue-200 bg-blue-50",
  },
  LIKES: {
    label: "点赞互动",
    colorClass: "text-pink-500 border-pink-200 bg-pink-50",
  },
  TEACHES: {
    label: "教学互动",
    colorClass: "text-emerald-500 border-emerald-200 bg-emerald-50",
  },
  LEARNS: {
    label: "学习关系",
    colorClass: "text-amber-500 border-amber-200 bg-amber-50",
  },
  CONTAINS: {
    label: "包含关系",
    colorClass: "text-violet-500 border-violet-200 bg-violet-50",
  },
  HAS_ERROR: {
    label: "错误关系",
    colorClass: "text-red-500 border-red-200 bg-red-50",
  },
  RELATES_TO: {
    label: "关联关系",
    colorClass: "text-gray-500 border-gray-200 bg-gray-50",
  },
};

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
  // Toggle helpers
  const toggleNodeType = (type: NodeType) => {
    const newTypes = selectedNodeTypes.includes(type)
      ? selectedNodeTypes.filter((t) => t !== type)
      : [...selectedNodeTypes, type];
    onNodeTypeChange(newTypes);
  };

  const toggleRelType = (type: RelationshipType) => {
    const newTypes = selectedRelationshipTypes.includes(type)
      ? selectedRelationshipTypes.filter((t) => t !== type)
      : [...selectedRelationshipTypes, type];
    onRelationshipTypeChange(newTypes);
  };

  const selectAllNodes = () =>
    onNodeTypeChange(Object.keys(NODE_CONFIG) as NodeType[]);
  const clearAllNodes = () => onNodeTypeChange([]);

  const selectAllRels = () =>
    onRelationshipTypeChange(
      Object.keys(RELATION_CONFIG) as RelationshipType[]
    );
  const clearAllRels = () => onRelationshipTypeChange([]);

  return (
    <Card className="w-full border shadow-sm hover:shadow-md transition-all duration-300 bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
      {/* Header Area */}
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg font-semibold tracking-tight">
              视图筛选
            </CardTitle>
          </div>
          {/* Quick Actions (Reset) placed conveniently */}
          {isLoading && (
            <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />
          )}
        </div>
        <CardDescription className="flex justify-between items-center text-xs mt-1 text-muted-foreground">
          <span>定制图谱的显示元素与连接</span>
          <span>
            已选 {selectedNodeTypes.length + selectedRelationshipTypes.length}{" "}
            项
          </span>
        </CardDescription>
      </CardHeader>

      <CardContent className="p-5 space-y-6">
        {/* Node Types Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Layers className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-foreground">节点实体</h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={selectAllNodes}
                className="text-[10px] px-2 py-0.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
              >
                全选
              </button>
              <button
                onClick={clearAllNodes}
                className="text-[10px] px-2 py-0.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
              >
                清空
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {(
              Object.entries(NODE_CONFIG) as [
                NodeType,
                (typeof NODE_CONFIG)[NodeType]
              ][]
            ).map(([type, config]) => {
              const isSelected = selectedNodeTypes.includes(type);
              return (
                <button
                  key={type}
                  onClick={() => toggleNodeType(type)}
                  className={cn(
                    "group relative flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 border",
                    isSelected
                      ? cn(
                          "text-white shadow-sm ring-1 ring-offset-1 ring-transparent",
                          config.colorClass
                        )
                      : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-dashed border-gray-300 hover:border-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                  )}
                >
                  {isSelected && <Check className="h-3 w-3" />}
                  {config.label}
                  {/* Color dot indicator for unselected state */}
                  {!isSelected && (
                    <span
                      className={cn(
                        "absolute right-2 top-1.5 h-1.5 w-1.5 rounded-full opacity-50",
                        config.colorClass.split(" ")[0]
                      )}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        <div className="h-[1px] bg-border/50 w-full" />

        {/* Relationship Types Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Network className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-foreground">关系连接</h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={selectAllRels}
                className="text-[10px] px-2 py-0.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
              >
                全选
              </button>
              <button
                onClick={clearAllRels}
                className="text-[10px] px-2 py-0.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
              >
                清空
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {(
              Object.entries(RELATION_CONFIG) as [
                RelationshipType,
                (typeof RELATION_CONFIG)[RelationshipType]
              ][]
            ).map(([type, config]) => {
              const isSelected = selectedRelationshipTypes.includes(type);
              return (
                <button
                  key={type}
                  onClick={() => toggleRelType(type)}
                  className={cn(
                    "flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs transition-all duration-200 border",
                    isSelected
                      ? cn("font-medium shadow-sm", config.colorClass)
                      : "bg-gray-50 text-gray-400 border-transparent hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700"
                  )}
                >
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full transition-colors",
                      isSelected ? "bg-current" : "bg-gray-300"
                    )}
                  />
                  {config.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Date Range Section (Placeholder styled) */}
        <div className="rounded-lg border border-dashed p-3 bg-muted/30 flex items-center gap-3">
          <div className="p-2 bg-background rounded-full border shadow-sm">
            <CalendarClock className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-medium text-muted-foreground">
              时间维度筛选
            </p>
            <p className="text-[10px] text-muted-foreground/70">
              该功能正在开发中
            </p>
          </div>
        </div>
      </CardContent>

      <CardFooter className="p-4 flex flex-col gap-2 border-t bg-muted/10">
        <Button
          className="w-full shadow-md hover:shadow-lg transition-all bg-blue-600 hover:bg-blue-700 text-white"
          onClick={onApplyFilters}
          disabled={isLoading}
        >
          {isLoading ? (
            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Filter className="mr-2 h-4 w-4" />
          )}
          应用筛选
        </Button>

        <div className="flex gap-2">
          <Button
            variant="outline"
            className="flex-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={onResetFilters}
            disabled={isLoading}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            重置
          </Button>
          <Button
            className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600"
            onClick={onCreateSubview}
            disabled={isLoading}
          >
            <Save className="mr-2 h-4 w-4" />
            存为子视图
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
