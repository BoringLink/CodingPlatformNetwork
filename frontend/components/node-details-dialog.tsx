"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  NodeDetails as NodeDetailsType,
  VisualizationNode,
  NodeType,
  RelationshipType,
} from "@/types/api";

interface NodeDetailsDialogProps {
  node: VisualizationNode | null;
  nodeDetails: NodeDetailsType | null;
  isOpen: boolean;
  onClose: () => void;
}

export function NodeDetailsDialog({
  node,
  nodeDetails,
  isOpen,
  onClose,
}: NodeDetailsDialogProps) {
  if (!node) return null;

  // Map node types to display names
  const nodeTypeName: Record<NodeType, string> = {
    Student: "学生",
    Teacher: "教师",
    KnowledgePoint: "知识点",
  };

  // Map relationship types to display names
  const relationshipTypeName: Record<string, string> = {
    CHAT_WITH: "聊天",
    LIKES: "喜欢",
    TEACHES: "教授",
    LEARNS: "学习",
    CONTAINS: "包含",
    HAS_ERROR: "有错误",
    RELATES_TO: "相关",
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-900">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <div
              className="w-6 h-6 rounded-full"
              style={{ backgroundColor: node.color }}
            />
            {nodeTypeName[node.type]} - {node.label}
          </DialogTitle>
          <DialogDescription>节点 ID: {node.id}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Node Properties */}
          <section>
            <h3 className="text-lg font-medium mb-3">基本信息</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <span className="text-sm text-gray-500">类型</span>
                <p className="font-medium">{nodeTypeName[node.type]}</p>
              </div>
              <div className="space-y-1">
                <span className="text-sm text-gray-500">标签</span>
                <p className="font-medium">{node.label}</p>
              </div>
              <div className="space-y-1">
                <span className="text-sm text-gray-500">大小</span>
                <p className="font-medium">{node.size}</p>
              </div>
              <div className="space-y-1">
                <span className="text-sm text-gray-500">颜色</span>
                <div className="flex items-center gap-2">
                  <div
                    className="w-4 h-4 rounded border"
                    style={{ backgroundColor: node.color }}
                  />
                  <span className="font-medium">{node.color}</span>
                </div>
              </div>
            </div>
          </section>

          {/* Node Details */}
          {nodeDetails && nodeDetails.node && (
            <section>
              <h3 className="text-lg font-medium mb-3">节点属性</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                {Object.entries(nodeDetails.node.properties).length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {Object.entries(nodeDetails.node.properties).map(
                      ([key, value]) => (
                        <div key={key} className="space-y-1">
                          <span className="text-sm text-gray-500 capitalize">
                            {key.replace(/([A-Z])/g, " $1").trim()}
                          </span>
                          <p className="font-medium break-all">
                            {typeof value === "object"
                              ? JSON.stringify(value)
                              : String(value)}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">暂无属性数据</p>
                )}
              </div>
            </section>
          )}

          {/* Relationship Statistics */}
          {nodeDetails && (
            <section>
              <h3 className="text-lg font-medium mb-3">关联关系</h3>
              <div className="space-y-4">
                {/* Relationship Counts */}
                <div className="bg-gray-50 p-4 rounded-md">
                  <h4 className="text-sm font-medium mb-2">关系类型统计</h4>
                  <div className="grid grid-cols-1 gap-3">
                    {Object.entries(nodeDetails.relationshipTypeCounts).map(
                      ([type, count]) => (
                        <div
                          key={type}
                          className="flex justify-between items-center"
                        >
                          <span className="text-sm text-gray-500 capitalize">
                            {relationshipTypeName[type].replace(/_/g, " ")}
                          </span>
                          <span className="font-medium">{count}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Connected Nodes */}
                {/* <div className="bg-gray-50 p-4 rounded-md">
                  <h4 className="text-sm font-medium mb-2">关联节点类型</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {nodeDetails.connectedNodes.map((connected, index) => (
                      <div
                        key={index}
                        className="flex justify-between items-center"
                      >
                        <span className="text-sm text-gray-500">
                          {nodeTypeName[connected.type as NodeType]}
                        </span>
                        <span className="font-medium">{connected.count}</span>
                      </div>
                    ))}
                  </div>
                </div> */}
              </div>
            </section>
          )}
        </div>

        <DialogFooter className="mt-6">
          <Button variant="secondary" onClick={onClose}>
            关闭
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
