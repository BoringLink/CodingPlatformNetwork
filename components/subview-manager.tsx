"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "./ui/dialog";
import { Subview } from "@/types/api";
import { Save, Edit, Trash2, Plus, X } from "lucide-react";
import { useCreateSubview, useDeleteSubview, useSubviews } from "@/hooks/use-graph-data";

interface SubviewManagerProps {
  // Current state
  currentSubviewId: string | null;
  onSubviewSelect: (subviewId: string) => void;
  onSubviewClose: () => void;
  
  // Filter state for creating new subview
  currentFilter: any; // Replace with proper GraphFilter type
  
  // Actions
  isLoading?: boolean;
}

interface SubviewListItemProps {
  subview: Subview;
  isSelected: boolean;
  onSelect: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

// Subview list item component
function SubviewListItem({
  subview,
  isSelected,
  onSelect,
  onEdit,
  onDelete,
}: SubviewListItemProps) {
  return (
    <div
      className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50 ${isSelected ? "bg-blue-50 border-blue-200" : "border-gray-200"}`}
      onClick={onSelect}
    >
      <div className="flex-1">
        <h4 className="font-medium text-sm">{subview.name}</h4>
        <p className="text-xs text-gray-500 mt-0.5">
          创建于 {new Date(subview.createdAt).toLocaleString()}
        </p>
      </div>
      <div className="flex gap-1 ml-2">
        {onEdit && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
            aria-label="编辑"
          >
            <Edit className="h-3.5 w-3.5" />
          </Button>
        )}
        {onDelete && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-red-500 hover:text-red-600 hover:bg-red-50"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            aria-label="删除"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>
    </div>
  );
}

export function SubviewManager({
  currentSubviewId,
  onSubviewSelect,
  onSubviewClose,
  currentFilter,
  isLoading = false,
}: SubviewManagerProps) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [subviewName, setSubviewName] = useState("");
  const [isSubviewLoading, setIsSubviewLoading] = useState(false);
  
  // Get subviews from API
  const { data: subviews = [], refetch: refetchSubviews } = useSubviews();
  
  // Create subview mutation
  const createSubviewMutation = useCreateSubview();
  
  // Delete subview mutation (to be implemented)
  // const deleteSubviewMutation = useDeleteSubview();
  
  // Handle subview creation
  const handleCreateSubview = async () => {
    if (!subviewName.trim()) return;
    
    setIsSubviewLoading(true);
    try {
      await createSubviewMutation.mutateAsync({
        name: subviewName.trim(),
        filter: currentFilter,
      });
      
      // Reset form and close dialog
      setSubviewName("");
      setShowCreateDialog(false);
      await refetchSubviews();
    } catch (error) {
      console.error("Failed to create subview:", error);
    } finally {
      setIsSubviewLoading(false);
    }
  };
  
  // Handle subview deletion
  const handleDeleteSubview = async (subviewId: string) => {
    if (confirm("确定要删除此子视图吗？")) {
      setIsSubviewLoading(true);
      try {
        // await deleteSubviewMutation.mutateAsync(subviewId);
        // await refetchSubviews();
        console.log("Delete subview:", subviewId);
        // TODO: Implement actual deletion
      } catch (error) {
        console.error("Failed to delete subview:", error);
      } finally {
        setIsSubviewLoading(false);
      }
    }
  };
  
  // Handle subview edit
  const handleEditSubview = (subview: Subview) => {
    console.log("Edit subview:", subview);
    // TODO: Implement edit functionality
  };
  
  return (
    <Card className="w-full">
      <CardHeader className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Save className="h-4 w-4" />
            <CardTitle className="text-lg font-medium">子视图管理</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onSubviewClose}
            aria-label="关闭"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription className="text-sm text-gray-500 mt-1">
          管理和创建自定义子视图
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        {/* Create Subview Button */}
        <Button
          className="w-full"
          onClick={() => setShowCreateDialog(true)}
          disabled={isSubviewLoading || isLoading}
        >
          <Plus className="mr-2 h-4 w-4" />
          创建新子视图
        </Button>
        
        {/* Subviews List */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">已保存的子视图</h3>
          {subviews.length === 0 ? (
            <div className="text-center py-6 text-sm text-gray-500">
              暂无子视图，点击上方按钮创建
            </div>
          ) : (
            <div className="space-y-1 max-h-60 overflow-y-auto pr-2">
              {subviews.map((subview) => (
                <SubviewListItem
                  key={subview.id}
                  subview={subview}
                  isSelected={subview.id === currentSubviewId}
                  onSelect={() => onSubviewSelect(subview.id)}
                  onEdit={() => handleEditSubview(subview)}
                  onDelete={() => handleDeleteSubview(subview.id)}
                />
              ))}
            </div>
          )}
        </div>
      </CardContent>
      
      {/* Create Subview Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>创建新子视图</DialogTitle>
            <DialogDescription>
              输入子视图名称，保存当前筛选条件
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="subview-name" className="text-sm font-medium">
                  子视图名称
                </label>
                <Input
                  id="subview-name"
                  placeholder="输入子视图名称"
                  value={subviewName}
                  onChange={(e) => setSubviewName(e.target.value)}
                  disabled={isSubviewLoading}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="secondary"
              onClick={() => setShowCreateDialog(false)}
              disabled={isSubviewLoading}
            >
              取消
            </Button>
            <Button
              onClick={handleCreateSubview}
              disabled={!subviewName.trim() || isSubviewLoading}
            >
              创建
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
