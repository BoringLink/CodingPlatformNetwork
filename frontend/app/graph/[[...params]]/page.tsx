"use client";

import { useState, useRef } from "react";
import { debounce } from "@/lib/utils";
import {
  GraphVisualization,
  GraphVisualizationRef,
} from "@/components/graph-visualization";
import { NodeDetailsDialog } from "@/components/node-details-dialog";
import { ZoomControls } from "@/components/zoom-controls";
import { FilterPanel } from "@/components/filter-panel";
import { SubviewManager } from "@/components/subview-manager";
import { MobileNavigation } from "@/components/mobile-navigation";
import { GraphLegend } from "@/components/graph-legend";
import { GraphStats } from "@/components/graph-stats";

import { useVisualization, useNodeDetails, useNodes } from "@/hooks/use-api";
import { NodeType, RelationshipType } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import { useGraphStore } from "@/store/graph-store";

export default function GraphPage() {
  const [layout, setLayout] = useState("cose");
  const [depth, setDepth] = useState(2);
  const [showNodeDetails, setShowNodeDetails] = useState(false);
  const [showSubviewManager, setShowSubviewManager] = useState(false);
  const [currentSubviewId, setCurrentSubviewId] = useState<string | null>(null);

  const cytoscapeRef = useRef<GraphVisualizationRef>(null);

  // Use graph store for state management
  const {
    selectedNodeId,
    highlightedNodeIds,
    pendingFilter,
    appliedFilter,
    setPendingFilter,
    setAppliedFilter,
    resetFilters,
    setSelectedNode,
    highlightNodeNeighbors,
    clearHighlighting,
  } = useGraphStore();

  // Apply filters to update visualization data
  const handleApplyFilters = () => {
    setAppliedFilter({ ...pendingFilter });
  };

  // Reset filters to default values
  const handleResetFilters = () => {
    resetFilters();
    refetch();
  };

  // Handle subview selection
  const handleSubviewSelect = (subviewId: string) => {
    setCurrentSubviewId(subviewId);
    setShowSubviewManager(false);
    // TODO: Implement loading subview filter and data
  };

  // Fetch nodes first to get a valid root node ID
  const { data: nodesData } = useNodes();

  // Use the first node as root if available, otherwise default to "1"
  const rootNodeId = nodesData?.nodes?.[0]?.id || "1";

  // Use the API hook to fetch visualization data
  const {
    data: visualizationData,
    isLoading,
    refetch,
  } = useVisualization(rootNodeId, depth, {
    nodeTypes: appliedFilter.nodeTypes,
    relationshipTypes: appliedFilter.relationshipTypes,
    school: appliedFilter.school,
    grade: appliedFilter.grade,
    class: appliedFilter.class,
    startDate: appliedFilter.dateRange?.from,
    endDate: appliedFilter.dateRange?.to,
  });

  // Fetch node details when selectedNodeId changes
  const { data: nodeDetails } = useNodeDetails(selectedNodeId || "");

  // Handle node click
  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId);
    highlightNodeNeighbors(nodeId);
    setShowNodeDetails(true);
  };

  // Handle node hover (empty for now, but required by component)
  const handleNodeHover = (_nodeId: string | null) => {
    // Additional hover logic can be added here in the future
  };

  // Zoom controls
  const handleZoomIn = () => {
    if (cytoscapeRef.current?.cy) {
      const currentZoom = cytoscapeRef.current.cy.zoom();
      cytoscapeRef.current.cy.zoom(currentZoom * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (cytoscapeRef.current?.cy) {
      const currentZoom = cytoscapeRef.current.cy.zoom();
      cytoscapeRef.current.cy.zoom(currentZoom * 0.8);
    }
  };

  const handleResetView = () => {
    if (cytoscapeRef.current?.cy) {
      cytoscapeRef.current.cy.fit(undefined, 50);
    }
  };

  // Get selected node from visualization data
  const selectedNode = visualizationData?.nodes.find(
    (node) => node.id === selectedNodeId
  );

  return (
    <div className="flex flex-col h-screen w-screen">
      {/* Header */}
      <header className="p-4 border-b bg-white dark:bg-gray-900">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold md:text-3xl">交互网络可视化</h1>
          <div className="flex gap-2 items-center flex-wrap">
            {/* 图谱统计信息 */}
            {visualizationData && (
              <GraphStats
                nodes={visualizationData.nodes}
                edges={visualizationData.edges}
              />
            )}
            <MobileNavigation />
            {selectedNodeId && (
              <Button variant="secondary" size="sm" onClick={clearHighlighting}>
                清除高亮
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar - Filter Panel */}
        <aside className="w-80 border-r bg-white dark:bg-gray-900 p-4 overflow-y-auto lg:block hidden">
          {/* Filter Panel */}
          <FilterPanel
            selectedNodeTypes={pendingFilter.nodeTypes}
            onNodeTypeChange={(types) =>
              setPendingFilter({ ...pendingFilter, nodeTypes: types })
            }
            selectedRelationshipTypes={pendingFilter.relationshipTypes}
            onRelationshipTypeChange={(types) =>
              setPendingFilter({ ...pendingFilter, relationshipTypes: types })
            }
            dateRange={pendingFilter.dateRange}
            onDateRangeChange={(date) =>
              setPendingFilter({ ...pendingFilter, dateRange: date })
            }
            onApplyFilters={handleApplyFilters}
            onResetFilters={handleResetFilters}
            onCreateSubview={() => setShowSubviewManager(true)}
            isLoading={isLoading}
          />

          {/* Graph Legend */}
          <GraphLegend />

          {/* Node Details Summary */}
          {selectedNodeId && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>节点摘要</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm space-y-2">
                  <p className="font-medium">ID: {selectedNodeId}</p>
                  {selectedNode && (
                    <>
                      <p>类型: {selectedNode.type}</p>
                      <p>标签: {selectedNode.label}</p>
                    </>
                  )}
                  <Button
                    variant="secondary"
                    size="sm"
                    className="w-full mt-2"
                    onClick={() => setShowNodeDetails(true)}
                  >
                    查看详细信息
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </aside>

        {/* Center - Graph Visualization */}
        <main className="flex-1 bg-gray-50 dark:bg-gray-800 relative">
          {isLoading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">
                  加载图谱数据...
                </p>
              </div>
            </div>
          ) : visualizationData &&
            visualizationData.nodes.length > 0 &&
            appliedFilter.nodeTypes.length > 0 ? (
            <>
              <GraphVisualization
                ref={cytoscapeRef}
                nodes={visualizationData.nodes}
                edges={visualizationData.edges}
                layout={layout}
                onNodeClick={handleNodeClick}
                onNodeHover={handleNodeHover}
                selectedNodeId={selectedNodeId || undefined}
                highlightedNodeIds={highlightedNodeIds}
                className="w-full h-full"
              />

              {/* Zoom Controls */}
              <ZoomControls
                onZoomIn={handleZoomIn}
                onZoomOut={handleZoomOut}
                onResetView={handleResetView}
                className="absolute bottom-4 right-4"
              />
            </>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  暂无图谱数据
                </p>
                <Button onClick={() => refetch()}>加载数据</Button>
              </div>
            </div>
          )}
        </main>

        {/* Right Sidebar - Subview Manager */}
        {showSubviewManager && (
          <aside className="w-80 border-l bg-white dark:bg-gray-900 p-4 overflow-y-auto lg:block hidden">
            <SubviewManager
              currentSubviewId={currentSubviewId}
              onSubviewSelect={handleSubviewSelect}
              onSubviewClose={() => setShowSubviewManager(false)}
              currentFilter={{
                nodeTypes: appliedFilter.nodeTypes,
                relationshipTypes: appliedFilter.relationshipTypes,
              }}
              isLoading={isLoading}
            />
          </aside>
        )}

        {/* Node Details Dialog */}
        <NodeDetailsDialog
          node={selectedNode || null}
          nodeDetails={nodeDetails || null}
          isOpen={showNodeDetails}
          onClose={() => setShowNodeDetails(false)}
        />
      </div>
    </div>
  );
}
