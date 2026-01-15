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
import { useFilterOptions } from "@/hooks/use-api";
import {
  Filter,
  RefreshCw,
  Save,
  Layers,
  Network,
  Check,
  Building2,
  GraduationCap,
  Users,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { cn } from "@/lib/utils";
import { DateRange } from "react-day-picker";

interface FilterPanelProps {
  selectedNodeTypes: NodeType[];
  onNodeTypeChange: (nodeTypes: NodeType[]) => void;
  selectedRelationshipTypes: RelationshipType[];
  onRelationshipTypeChange: (relationshipTypes: RelationshipType[]) => void;
  dateRange?: DateRange;
  onDateRangeChange: (date: DateRange | undefined) => void;
  selectedSchool?: string;
  onSchoolChange: (school: string | undefined) => void;
  selectedGrade?: number;
  onGradeChange: (grade: number | undefined) => void;
  selectedClass?: string;
  onClassChange: (className: string | undefined) => void;
  onApplyFilters: () => void;
  onResetFilters: () => void;
  onCreateSubview: () => void;
  isLoading?: boolean;
}

// 颜色配置：与 GraphVisualization 保持视觉一致
// 使用 Tailwind 类近似 hex 颜色:
// Student(#60a5fa) -> blue-400
// Teacher(#34d399) -> emerald-400
// KnowledgePoint(#a78bfa) -> violet-400
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
  KnowledgePoint: {
    label: "知识点",
    colorClass: "bg-violet-400 border-violet-400 hover:bg-violet-500",
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
  dateRange,
  onDateRangeChange,
  selectedSchool,
  onSchoolChange,
  selectedGrade,
  onGradeChange,
  selectedClass,
  onClassChange,
  onApplyFilters,
  onResetFilters,
  onCreateSubview,
  isLoading = false,
}: FilterPanelProps) {
  // Fetch filter options with hierarchical filtering
  const { data: filterOptions, isLoading: isFilterOptionsLoading } =
    useFilterOptions(selectedSchool, selectedGrade);

  // Toggle helpers for node and relationship types (still multi-select)
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

  // 处理学校选择
  const handleSchoolChange = (school: string | undefined) => {
    onSchoolChange(school);
    // 级联重置由父组件处理
  };

  // 处理年级选择
  const handleGradeChange = (grade: string | undefined) => {
    const gradeNumber = grade ? parseInt(grade, 10) : undefined;
    onGradeChange(gradeNumber);
    // 级联重置由父组件处理
  };

  // 处理班级选择
  const handleClassChange = (className: string | undefined) => {
    onClassChange(className);
  };

  // 检查年级是否可用 - 必须先选择学校
  const isGradesDisabled = !selectedSchool;

  // 检查班级是否可用 - 必须先选择年级
  const isClassesDisabled = !selectedGrade;

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
          <div className="flex items-center flex-col">
            <span>定制图谱的显示元素与连接</span>
            <div className="flex content-start gap-2">
              <span>
                已选
                {selectedNodeTypes.length +
                  selectedRelationshipTypes.length +
                  (selectedSchool ? 1 : 0) +
                  (selectedGrade ? 1 : 0) +
                  (selectedClass ? 1 : 0)}
                项
              </span>
            </div>
            {selectedSchool && selectedGrade && selectedClass && (
              <span className="text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded text-xs">
                可加载
              </span>
            )}
          </div>
        </CardDescription>
      </CardHeader>

      <CardContent className="p-5 space-y-5">
        {/* Student Filters - Primary filters for data scoping */}
        <div className="space-y-4">
          {/* School Section */}
          <div className="space-y-3 pl-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Building2 className="h-4 w-4 text-blue-500" />
                <h3 className="text-foreground">学校</h3>
              </div>
            </div>

            <div className="space-y-2">
              <Select
                value={selectedSchool ?? ""}
                onValueChange={(value) =>
                  handleSchoolChange(value || undefined)
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="请选择学校" />
                </SelectTrigger>
                <SelectContent>
                  {isFilterOptionsLoading ? (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 inline-block mr-2" />
                      加载学校数据中...
                    </div>
                  ) : filterOptions?.schools &&
                    filterOptions.schools.length > 0 ? (
                    filterOptions.schools.map((school) => (
                      <SelectItem key={school} value={school}>
                        {school}
                      </SelectItem>
                    ))
                  ) : (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      暂无可选学校
                    </div>
                  )}
                </SelectContent>
              </Select>

              {(!filterOptions?.schools ||
                filterOptions.schools.length === 0) &&
                !isFilterOptionsLoading && (
                  <div className="text-xs text-muted-foreground bg-blue-50 border border-blue-200 rounded-md p-3">
                    <p className="font-medium text-blue-800">📚 暂无可选学校</p>
                    <div className="text-blue-600 mt-1 space-y-1">
                      <p>• 导入包含学校信息的学生数据后可使用此筛选</p>
                    </div>
                  </div>
                )}
            </div>
          </div>

          <div className="h-[1px] bg-border/30 w-full ml-6" />

          {/* Grade Section */}
          <div className="space-y-3 pl-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium">
                <GraduationCap className="h-4 w-4 text-green-500" />
                <h3 className="text-foreground">年级</h3>
              </div>
            </div>

            <div className="space-y-2">
              <Select
                value={selectedGrade?.toString() ?? ""}
                onValueChange={(value) => handleGradeChange(value || undefined)}
                disabled={isGradesDisabled}
              >
                <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={
                      isGradesDisabled ? "请先选择学校" : "请选择年级"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {isFilterOptionsLoading ? (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-500 inline-block mr-2" />
                      加载年级数据中...
                    </div>
                  ) : !isGradesDisabled &&
                    filterOptions?.grades &&
                    filterOptions.grades.length > 0 ? (
                    filterOptions.grades.map((grade) => (
                      <SelectItem key={grade} value={grade.toString()}>
                        {grade}年级
                      </SelectItem>
                    ))
                  ) : !isGradesDisabled ? (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      暂无可选年级
                    </div>
                  ) : null}
                </SelectContent>
              </Select>

              {isGradesDisabled && (
                <div className="text-xs text-gray-600 bg-gray-50 border border-gray-200 rounded-md p-3">
                  <p className="font-medium text-gray-800">📚 请先选择学校</p>
                  <p className="text-gray-500 mt-1">
                    选择学校后，系统将显示该学校可用的年级列表
                  </p>
                </div>
              )}

              {!isGradesDisabled &&
                !isFilterOptionsLoading &&
                (!filterOptions?.grades ||
                  filterOptions.grades.length === 0) && (
                  <div className="text-xs text-muted-foreground bg-green-50 border border-green-200 rounded-md p-3">
                    <p className="font-medium text-green-800">
                      📚 暂无可选年级
                    </p>
                    <div className="text-green-600 mt-1 space-y-1">
                      <p>• 所选学校暂无可用年级数据</p>
                      <p>• 请选择其他学校或导入相关数据</p>
                    </div>
                  </div>
                )}
            </div>
          </div>

          <div className="h-[1px] bg-border/30 w-full ml-6" />

          {/* Class Section */}
          <div className="space-y-3 pl-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Users className="h-4 w-4 text-purple-500" />
                <h3 className="text-foreground">班级</h3>
              </div>
            </div>

            <div className="space-y-2">
              <Select
                value={selectedClass ?? ""}
                onValueChange={(value) => handleClassChange(value || undefined)}
                disabled={isClassesDisabled}
              >
                <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={
                      isClassesDisabled ? "请先选择年级" : "请选择班级"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {isFilterOptionsLoading ? (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-500 inline-block mr-2" />
                      加载班级数据中...
                    </div>
                  ) : !isClassesDisabled &&
                    filterOptions?.classes &&
                    filterOptions.classes.length > 0 ? (
                    filterOptions.classes.map((className) => (
                      <SelectItem key={className} value={className}>
                        {className}
                      </SelectItem>
                    ))
                  ) : !isClassesDisabled ? (
                    <div className="p-2 text-center text-sm text-muted-foreground">
                      暂无可选班级
                    </div>
                  ) : null}
                </SelectContent>
              </Select>

              {isClassesDisabled && (
                <div className="text-xs text-gray-600 bg-gray-50 border border-gray-200 rounded-md p-3">
                  <p className="font-medium text-gray-800">👥 请先选择年级</p>
                  <p className="text-gray-500 mt-1">
                    选择年级后，系统将显示该年级可用的班级列表
                  </p>
                </div>
              )}

              {!isClassesDisabled &&
                !isFilterOptionsLoading &&
                (!filterOptions?.classes ||
                  filterOptions.classes.length === 0) && (
                  <div className="text-xs text-muted-foreground bg-purple-50 border border-purple-200 rounded-md p-3">
                    <p className="font-medium text-purple-800">
                      👥 暂无可选班级
                    </p>
                    <div className="text-purple-600 mt-1 space-y-1">
                      <p>• 所选年级暂无可用班级数据</p>
                      <p>• 请选择其他年级或导入相关数据</p>
                    </div>
                  </div>
                )}
            </div>
          </div>
        </div>

        <div className="h-[1px] bg-border/50 w-full" />

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

        {/* Date Range Section */}
        <div className="flex items-center w-full">
          {/* <DatePicker
            title="时间筛选"
            dateRange={dateRange}
            onDateRangeChange={onDateRangeChange}
          /> */}
        </div>
      </CardContent>

      <CardFooter className="p-4 flex flex-col gap-2 border-t bg-muted/10">
        <Button
          className={`w-full shadow-md hover:shadow-lg transition-all ${
            selectedSchool && selectedGrade !== undefined && selectedClass
              ? "bg-blue-600 hover:bg-blue-700 text-white"
              : "bg-gray-400 hover:bg-gray-500 text-white"
          }`}
          onClick={onApplyFilters}
          disabled={
            isLoading ||
            !selectedSchool ||
            selectedGrade === undefined ||
            !selectedClass
          }
        >
          {isLoading ? (
            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Filter className="mr-2 h-4 w-4" />
          )}
          {selectedSchool && selectedGrade !== undefined && selectedClass
            ? "应用筛选并加载数据"
            : "请完成学校、年级和班级选择"}
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
