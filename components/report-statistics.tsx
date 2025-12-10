import React from "react";
import { GraphStatistics } from "@/types/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Card, CardContent, CardTitle } from "./ui/card";

interface ReportStatisticsProps {
  statistics: GraphStatistics;
}

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#82ca9d",
];

export default function ReportStatistics({
  statistics,
}: ReportStatisticsProps) {
  // Add default values for safety
  const safeStatistics = {
    totalNodes: statistics.totalNodes || 0,
    nodesByType: statistics.nodesByType || {},
    totalRelationships: statistics.totalRelationships || 0,
    relationshipsByType: statistics.relationshipsByType || {},
  };

  // Prepare data for charts with safe default values
  const nodesByTypeData = Object.entries(safeStatistics.nodesByType).map(
    ([type, count]) => ({
      name: type,
      value: count || 0,
    })
  );

  const relationshipsByTypeData = Object.entries(
    safeStatistics.relationshipsByType
  ).map(([type, count]) => ({
    name: type,
    value: count || 0,
  }));

  const summaryData = [
    { name: "Total Nodes", value: safeStatistics.totalNodes || 0 },
    { name: "Total Relationships", value: safeStatistics.totalRelationships || 0 },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {summaryData.map((item, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">{item.name}</div>
              <div className="text-3xl font-bold mt-1">{item.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Nodes by Type - Pie Chart */}
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <CardTitle className="text-lg font-medium mb-4">
            Nodes by Type
          </CardTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={nodesByTypeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${((percent || 0) * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {nodesByTypeData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} nodes`, "Count"]} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Relationships by Type - Bar Chart */}
      <Card className="hover:shadow-md transition-shadow lg:col-span-2">
        <CardContent className="p-4">
          <CardTitle className="text-lg font-medium mb-4">
            Relationships by Type
          </CardTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={relationshipsByTypeData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value) => [`${value} relationships`, "Count"]}
              />
              <Bar dataKey="value" fill="#8884d8">
                {relationshipsByTypeData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
