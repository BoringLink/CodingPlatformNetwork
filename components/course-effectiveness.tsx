import React from 'react';
import { CourseEffectiveness as CourseEffectivenessType } from '@/types/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

interface CourseEffectivenessProps {
  effectiveness: CourseEffectivenessType;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function CourseEffectiveness({ effectiveness }: CourseEffectivenessProps) {
  // Add default values for safety
  const safeEffectiveness = {
    courseMetrics: effectiveness.courseMetrics || [],
  };

  // Prepare data for charts
  const courseMetricsData = safeEffectiveness.courseMetrics.map((course, index) => ({
    name: (course.courseName?.length || 0) > 15 
      ? `${course.courseName.substring(0, 15)}...` 
      : course.courseName || `课程${index}`,
    participationRate: ((course.participationRate || 0) * 100).toFixed(1),
    errorRate: ((course.errorRate || 0) * 100).toFixed(1),
    averageProgress: ((course.averageProgress || 0) * 100).toFixed(1),
  }));

  // Radar chart data (for each course)
  const radarChartData = safeEffectiveness.courseMetrics.map(course => ({
    subject: course.courseName || `课程`,
    participation: (course.participationRate || 0) * 100,
    error: (course.errorRate || 0) * 100,
    progress: (course.averageProgress || 0) * 100,
  }));

  return (
    <div className="space-y-6">
      {/* 课程指标 - 柱状图 */}
      <div>
        <h3 className="text-lg font-medium mb-4">课程指标</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={courseMetricsData}
              margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={60}
              />
              <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
              <Tooltip formatter={(value) => [`${value}%`, '']} />
              <Bar dataKey="participationRate" name="参与率" fill={COLORS[0]} />
              <Bar dataKey="averageProgress" name="平均进度" fill={COLORS[1]} />
              <Bar dataKey="errorRate" name="错误率" fill={COLORS[2]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 课程对比 - 雷达图 */}
      {safeEffectiveness.courseMetrics.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-4">课程对比</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarChartData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                <Radar 
                  name="参与率" 
                  dataKey="participation" 
                  stroke={COLORS[0]} 
                  fill={COLORS[0]} 
                  fillOpacity={0.3} 
                />
                <Radar 
                  name="进度" 
                  dataKey="progress" 
                  stroke={COLORS[1]} 
                  fill={COLORS[1]} 
                  fillOpacity={0.3} 
                />
                <Radar 
                  name="错误率" 
                  dataKey="error" 
                  stroke={COLORS[2]} 
                  fill={COLORS[2]} 
                  fillOpacity={0.3} 
                />
                <Tooltip formatter={(value) => [`${value}%`, '']} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* 课程详情表格 */}
      <div>
        <h3 className="text-lg font-medium mb-4">课程详情</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-900">
            <thead className="text-xs text-gray-900 uppercase bg-gray-50">
              <tr>
                <th className="px-4 py-2">课程</th>
                <th className="px-4 py-2">参与率</th>
                <th className="px-4 py-2">错误率</th>
                <th className="px-4 py-2">平均进度</th>
              </tr>
            </thead>
            <tbody>
              {safeEffectiveness.courseMetrics.map((course, index) => (
                <tr 
                  key={index} 
                  className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} text-gray-900`}
                >
                  <td className="px-4 py-3 font-medium">{course.courseName || `课程${index}`}</td>
                  <td className="px-4 py-3">{((course.participationRate || 0) * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3">{((course.errorRate || 0) * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3">{((course.averageProgress || 0) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          {safeEffectiveness.courseMetrics.length === 0 && (
            <div className="text-center py-4 text-muted-foreground">
              暂无课程数据
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
