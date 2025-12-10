"use client";
import React, { Suspense } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Report } from "@/types/api";
import { MobileNavigation } from "@/components/mobile-navigation";

// Dynamically import chart components to avoid SSR issues with Recharts
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

export default function ReportsPage() {
  const {
    data: report,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["report"],
    queryFn: () => apiClient.reports.generate(),
  });

  const handleExport = (format: "json" | "pdf") => {
    if (!report) return;

    if (format === "json") {
      const dataStr = JSON.stringify(report, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `knowledge-graph-report-${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else if (format === "pdf") {
      // PDF export implementation would go here
      // This would typically use a library like jsPDF or html2canvas
      alert("PDF export functionality coming soon!");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl font-medium">Loading report...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <div className="text-xl font-medium text-red-600">
          Failed to load report
        </div>
        <Button onClick={() => refetch()} variant="default">
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">知识图谱报告</h1>
          <p className="text-muted-foreground mt-1">
            生成于 {new Date(report!.generatedAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <MobileNavigation />
          <Button onClick={() => handleExport("json")} variant="secondary">
            <Download className="mr-2 h-4 w-4" />
            导出 JSON
          </Button>
          <Button onClick={() => handleExport("pdf")} variant="default">
            <Download className="mr-2 h-4 w-4" />
            导出 PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Graph Statistics */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Graph Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <Suspense
              fallback={
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              }
            >
              <ReportStatistics
                statistics={
                  report?.graphStatistics || {
                    totalNodes: 0,
                    nodesByType: {
                      Student: 0,
                      Teacher: 0,
                      Course: 0,
                      KnowledgePoint: 0,
                      ErrorType: 0,
                    },
                    totalRelationships: 0,
                    relationshipsByType: {
                      LEARNS: 0,
                      TEACHES: 0,
                      CONTAINS: 0,
                      HAS_ERROR: 0,
                      RELATES_TO: 0,
                      CHAT_WITH: 0,
                      LIKES: 0,
                    },
                  }
                }
              />
            </Suspense>
          </CardContent>
        </Card>

        {/* Student Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Student Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <Suspense
              fallback={
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              }
            >
              <StudentPerformance
                performance={
                  report?.studentPerformance || {
                    highFrequencyErrors: [],
                    studentsNeedingAttention: [],
                  }
                }
              />
            </Suspense>
          </CardContent>
        </Card>

        {/* Course Effectiveness */}
        <Card>
          <CardHeader>
            <CardTitle>Course Effectiveness</CardTitle>
          </CardHeader>
          <CardContent>
            <Suspense
              fallback={
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              }
            >
              <CourseEffectiveness
                effectiveness={
                  report?.courseEffectiveness || { courseMetrics: [] }
                }
              />
            </Suspense>
          </CardContent>
        </Card>

        {/* Interaction Patterns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Interaction Patterns</CardTitle>
          </CardHeader>
          <CardContent>
            <Suspense
              fallback={
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              }
            >
              <InteractionPatterns
                patterns={
                  report?.interactionPatterns || {
                    activeCommunities: [],
                    isolatedStudents: [],
                  }
                }
              />
            </Suspense>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
