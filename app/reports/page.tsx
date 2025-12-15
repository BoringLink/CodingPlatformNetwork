"use client";

import React, { Suspense, useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Download,
  RefreshCw,
  Loader2,
  LayoutDashboard,
  GraduationCap,
  BookOpen,
  Network,
  Share2,
  FileText,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { MobileNavigation } from "@/components/mobile-navigation";
import { cn } from "@/lib/utils";

// 动态导入图表组件
const ReportStatistics = React.lazy(
  () => import("@/components/report-statistics")
);
const StudentPerformance = React.lazy(
  () => import("@/components/student-performance")
);
const CourseEffectiveness = React.lazy(
  () => import("@/components/course-effectiveness")
);
const InteractionPatterns = React.lazy(
  () => import("@/components/interaction-patterns")
);

// 定义 Tab 类型
type TabType = "overview" | "students" | "courses" | "network";

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");

  const {
    data: report,
    isLoading,
    isError,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ["report"],
    queryFn: () => apiClient.reports.generate(),
    staleTime: 1000 * 60 * 5, // 5分钟缓存
  });

  // 处理导出逻辑
  const handleExport = (format: "json" | "pdf") => {
    if (!report) return;
    if (format === "json") {
      const dataStr = JSON.stringify(report, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `kg-report-${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else {
      alert("PDF 导出功能即将上线");
    }
  };

  // 提取顶部 KPI 数据
  const kpiData = useMemo(() => {
    if (!report) return null;
    return [
      {
        label: "总知识节点",
        value: report.graphStatistics.totalNodes,
        icon: Network,
        color: "text-blue-500",
        bg: "bg-blue-50",
      },
      {
        label: "关联关系",
        value: report.graphStatistics.totalRelationships,
        icon: Share2,
        color: "text-purple-500",
        bg: "bg-purple-50",
      },
      {
        label: "高频错误点",
        value: report.studentPerformance.highFrequencyErrors.length,
        icon: FileText,
        color: "text-red-500",
        bg: "bg-red-50",
      },
      {
        label: "活跃课程",
        value: report.courseEffectiveness.courseMetrics.length,
        icon: BookOpen,
        color: "text-green-500",
        bg: "bg-green-50",
      },
    ];
  }, [report]);

  // 加载状态组件 - 骨架屏
  if (isLoading) {
    return <DashboardSkeleton />;
  }

  // 错误状态组件
  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-[80vh] gap-4">
        <div className="p-4 rounded-full bg-red-50">
          <Loader2 className="h-8 w-8 text-red-500 animate-spin" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900">报告加载失败</h3>
        <p className="text-muted-foreground">
          无法获取最新的知识图谱分析数据。
        </p>
        <Button onClick={() => refetch()} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          重试
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-gray-900/50 pb-10">
      {/* 顶部导航与操作栏 */}
      <header className="sticky top-0 z-30 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <MobileNavigation />
            <div>
              <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
                <LayoutDashboard className="h-5 w-5 text-primary" />
                知识图谱分析报告
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground hidden md:inline-block mr-2">
              生成时间: {new Date(report!.generatedAt).toLocaleDateString()}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => refetch()}
              disabled={isRefetching}
              title="刷新数据"
            >
              <RefreshCw
                className={cn("h-4 w-4", isRefetching && "animate-spin")}
              />
            </Button>
            <div className="h-4 w-[1px] bg-border mx-1" />
            <Button
              onClick={() => handleExport("json")}
              variant="outline"
              size="sm"
            >
              <Download className="mr-2 h-4 w-4" />
              JSON
            </Button>
            <Button onClick={() => handleExport("pdf")} size="sm">
              <Download className="mr-2 h-4 w-4" />
              PDF
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 md:p-6 space-y-6">
        {/* KPI 概览区域 */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiData?.map((item, idx) => (
            <Card
              key={idx}
              className="border-none shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <CardContent className="p-6 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {item.label}
                  </p>
                  <h3 className="text-2xl font-bold mt-1 tracking-tight">
                    {item.value.toLocaleString()}
                  </h3>
                </div>
                <div className={cn("p-3 rounded-xl", item.bg)}>
                  <item.icon className={cn("h-5 w-5", item.color)} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 导航 Tabs */}
        <div className="flex flex-col space-y-6">
          <div className="flex items-center gap-1 p-1 bg-muted/50 rounded-lg w-full md:w-fit overflow-x-auto">
            <TabButton
              active={activeTab === "overview"}
              onClick={() => setActiveTab("overview")}
              icon={LayoutDashboard}
              label="全景概览"
            />
            <TabButton
              active={activeTab === "students"}
              onClick={() => setActiveTab("students")}
              icon={GraduationCap}
              label="学生表现"
            />
            <TabButton
              active={activeTab === "courses"}
              onClick={() => setActiveTab("courses")}
              icon={BookOpen}
              label="课程效能"
            />
            <TabButton
              active={activeTab === "network"}
              onClick={() => setActiveTab("network")}
              icon={Network}
              label="交互网络"
            />
          </div>

          {/* 内容区域 - 懒加载 */}
          <Suspense fallback={<SectionSkeleton />}>
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
              {activeTab === "overview" && (
                <div className="grid grid-cols-1 gap-6">
                  <Card className="border-none shadow-md">
                    <CardHeader>
                      <CardTitle>图谱数据统计</CardTitle>
                      <CardDescription>
                        节点分布与关系类型构成的全景视图
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ReportStatistics statistics={report!.graphStatistics} />
                    </CardContent>
                  </Card>

                  {/* 概览页也展示部分关键错误分析，作为摘要 */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">
                          需关注的高频错误
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <StudentPerformance
                          performance={{
                            ...report!.studentPerformance,
                            studentsNeedingAttention: [], // 仅显示错误，简化视图
                          }}
                        />
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}

              {activeTab === "students" && (
                <Card className="border-none shadow-md">
                  <CardHeader>
                    <CardTitle>学生学习表现分析</CardTitle>
                    <CardDescription>
                      基于错误模式和学习路径的深度分析
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <StudentPerformance
                      performance={report!.studentPerformance}
                    />
                  </CardContent>
                </Card>
              )}

              {activeTab === "courses" && (
                <Card className="border-none shadow-md">
                  <CardHeader>
                    <CardTitle>课程教学效能评估</CardTitle>
                    <CardDescription>
                      参与度、完成率与知识点覆盖情况
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <CourseEffectiveness
                      effectiveness={report!.courseEffectiveness}
                    />
                  </CardContent>
                </Card>
              )}

              {activeTab === "network" && (
                <Card className="border-none shadow-md">
                  <CardHeader>
                    <CardTitle>社区交互模式</CardTitle>
                    <CardDescription>
                      学习社区中的孤立节点与活跃群体识别
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <InteractionPatterns
                      patterns={report!.interactionPatterns}
                    />
                  </CardContent>
                </Card>
              )}
            </div>
          </Suspense>
        </div>
      </main>
    </div>
  );
}

// 子组件：Tab 按钮
function TabButton({
  active,
  onClick,
  icon: Icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ElementType;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 whitespace-nowrap",
        active
          ? "bg-white text-gray-900 shadow-sm dark:bg-gray-800 dark:text-white"
          : "text-muted-foreground hover:bg-white/50 hover:text-foreground dark:hover:bg-gray-800/50"
      )}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}

// 子组件：骨架屏
function DashboardSkeleton() {
  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="flex gap-2">
          <div className="h-9 w-24 bg-gray-200 rounded animate-pulse" />
          <div className="h-9 w-24 bg-gray-200 rounded animate-pulse" />
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse" />
        ))}
      </div>
      <div className="h-96 bg-gray-200 rounded-xl animate-pulse" />
    </div>
  );
}

function SectionSkeleton() {
  return (
    <div className="w-full space-y-6">
      <div className="h-[400px] w-full bg-muted/30 rounded-lg animate-pulse border-2 border-dashed border-muted" />
    </div>
  );
}
