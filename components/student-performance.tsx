import React from "react";
import { StudentPerformance as StudentPerformanceType } from "@/types/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardTitle } from "./ui/card";

interface StudentPerformanceProps {
  performance: StudentPerformanceType;
}

const COLORS = ["#FF8042", "#0088FE", "#00C49F", "#FFBB28", "#8884d8"];

export default function StudentPerformance({
  performance,
}: StudentPerformanceProps) {
  // Add default values for safety
  const safePerformance = {
    highFrequencyErrors: performance.highFrequencyErrors || [],
    studentsNeedingAttention: performance.studentsNeedingAttention || [],
  };

  // Prepare data for charts
  const highFrequencyErrorsData = safePerformance.highFrequencyErrors.map(
    (error, index) => ({
      name:
        (error.knowledgePoint?.length || 0) > 15
          ? `${error.knowledgePoint.substring(0, 15)}...`
          : error.knowledgePoint || '未知知识点',
      errorCount: error.errorCount || 0,
      affectedStudents: error.affectedStudents || 0,
    })
  );

  const studentsNeedingAttentionData = safePerformance.studentsNeedingAttention.map(
    (student, index) => ({
      name: student.studentId || `学生${index}`,
      errorCount: student.errorCount || 0,
      courses: student.courses?.length || 0,
    })
  );

  return (
    <div className="space-y-6">
      {/* High Frequency Errors */}
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <CardTitle className="text-lg font-medium mb-4">
            高频错误分析
          </CardTitle>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={highFrequencyErrorsData}
                margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    `${value}`,
                    name === "errorCount" ? "错误次数" : "影响学生数",
                  ]}
                />
                <Bar dataKey="errorCount" name="错误次数" fill={COLORS[0]} />
                <Bar
                  dataKey="affectedStudents"
                  name="影响学生数"
                  fill={COLORS[1]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Students Needing Attention */}
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <CardTitle className="text-lg font-medium mb-4">
            需要关注的学生
          </CardTitle>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-2">学生ID</th>
                  <th className="px-4 py-2">错误次数</th>
                  <th className="px-4 py-2">课程数</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {studentsNeedingAttentionData.map((student, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium">{student.name}</td>
                    <td className="px-4 py-3">{student.errorCount}</td>
                    <td className="px-4 py-3">{student.courses}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {studentsNeedingAttentionData.length === 0 && (
              <div className="text-center py-4 text-muted-foreground">
                没有需要特别关注的学生
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
