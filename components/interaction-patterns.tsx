import React from "react";
import { InteractionPatterns as InteractionPatternsType } from "@/types/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from "recharts";

interface InteractionPatternsProps {
  patterns: InteractionPatternsType;
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8"];

export default function InteractionPatterns({
  patterns,
}: InteractionPatternsProps) {
  // Add default values for safety
  const safePatterns = {
    activeCommunities: patterns.activeCommunities || [],
    isolatedStudents: patterns.isolatedStudents || [],
  };

  // Prepare data for charts
  const activeCommunitiesData = safePatterns.activeCommunities.map(
    (community, index) => ({
      name: `Community ${index + 1}`,
      students: (community.students?.length || 0),
      interactions: community.interactionCount || 0,
    })
  );

  // Data for pie chart showing community distribution
  const communityDistributionData = safePatterns.activeCommunities.map(
    (community, index) => ({
      name: `Community ${index + 1}`,
      value: (community.students?.length || 0),
    })
  );

  // Add isolated students to distribution
  if (safePatterns.isolatedStudents.length > 0) {
    communityDistributionData.push({
      name: "Isolated Students",
      value: safePatterns.isolatedStudents.length,
    });
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Active Communities */}
      <div className="space-y-6">
        <h3 className="text-lg font-medium mb-4">Active Communities</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={activeCommunitiesData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value, name) => [
                  `${value}`,
                  name === "students" ? "Students" : "Interactions",
                ]}
              />
              <Bar dataKey="students" name="Students" fill={COLORS[0]} />
              <Bar
                dataKey="interactions"
                name="Interactions"
                fill={COLORS[1]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Community Details */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th className="px-4 py-2">Community</th>
                <th className="px-4 py-2">Students</th>
                <th className="px-4 py-2">Interactions</th>
              </tr>
            </thead>
            <tbody>
              {activeCommunitiesData.map((community, index) => (
                <tr
                  key={index}
                  className={`border-b ${
                    index % 2 === 0 ? "bg-white" : "bg-gray-50"
                  }`}
                >
                  <td className="px-4 py-3 font-medium">{community.name}</td>
                  <td className="px-4 py-3">{community.students}</td>
                  <td className="px-4 py-3">{community.interactions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Community Distribution */}
      <div className="space-y-6">
        <h3 className="text-lg font-medium mb-4">Community Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={communityDistributionData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) =>
                  `${name} ${((percent || 0) * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {communityDistributionData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} students`, "Count"]} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Isolated Students */}
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <h4 className="text-md font-medium mb-2">Isolated Students</h4>
          <div className="text-2xl font-bold">
            {safePatterns.isolatedStudents.length}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Students with no recorded interactions
          </p>
          {safePatterns.isolatedStudents.length > 0 && (
            <div className="mt-3">
              <h5 className="text-sm font-medium mb-2">Student IDs:</h5>
              <div className="flex flex-wrap gap-2">
                {safePatterns.isolatedStudents
                  .slice(0, 10)
                  .map((studentId, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-100 rounded-full text-xs"
                    >
                      {studentId}
                    </span>
                  ))}
                {safePatterns.isolatedStudents.length > 10 && (
                  <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                    +{safePatterns.isolatedStudents.length - 10} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
