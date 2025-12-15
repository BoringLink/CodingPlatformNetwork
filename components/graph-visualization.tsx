"use client";

import React, {
  useEffect,
  useRef,
  forwardRef,
  useImperativeHandle,
  useCallback,
  useMemo,
} from "react";

import CytoscapeComponent from "react-cytoscapejs";
import {
  Core,
  EdgeSingular,
  StylesheetJsonBlock,
  LayoutOptions,
  ElementDefinition,
} from "cytoscape";
import {
  VisualizationNode,
  VisualizationEdge,
  NodeType,
  RelationshipType,
} from "@/types/api";

export interface GraphVisualizationRef {
  cy: Core | null;
}

interface GraphVisualizationProps {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  layout?: string;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  selectedNodeId?: string;
  selectedNodeIds?: string[];
  onSelectedNodesChange?: (nodeIds: string[]) => void;
  highlightedNodeIds?: string[];
  className?: string;
}

export const GraphVisualization = forwardRef<
  GraphVisualizationRef,
  GraphVisualizationProps
>(
  (
    {
      nodes = [],
      edges = [],
      layout = "cose",
      onNodeClick,
      onNodeHover,
      selectedNodeId,
      selectedNodeIds = [],
      onSelectedNodesChange,
      highlightedNodeIds = [],
      className = "w-full h-full",
    },
    ref
  ) => {
    const cytoscapeRef = useRef<{ cy: Core }>(null);
    // 使用 ref 保持回调最新，避免闭包问题
    const callbacksRef = useRef({ onNodeClick, onNodeHover, onSelectedNodesChange });

    useEffect(() => {
      callbacksRef.current = { onNodeClick, onNodeHover, onSelectedNodesChange };
    }, [onNodeClick, onNodeHover, onSelectedNodesChange]);

    useImperativeHandle(
      ref,
      () => ({
        get cy() {
          return cytoscapeRef.current?.cy || null;
        },
      }),
      []
    );

    // 1. 数据转换与清洗 (Memoized)
    const elements = useMemo(() => {
      const sanitizedNodes: ElementDefinition[] = nodes.map((node) => {
        // 彻底分离 position 和其余数据
        const { position, ...restData } = node;
        
        // 只有当 x 和 y 都是有效数字时才使用位置
        const hasValidPosition = 
          position && 
          typeof position.x === 'number' && 
          typeof position.y === 'number';

        return {
          // data 中不再包含 position 字段，防止污染
          data: restData,
          // 如果位置无效，显式设为 undefined，迫使布局算法接管
          position: hasValidPosition ? position : undefined,
          // 确保每个节点有唯一的 group
          group: 'nodes',
        };
      });

      const sanitizedEdges: ElementDefinition[] = edges.map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          weight: edge.weight,
        },
        group: 'edges',
      }));

      return [...sanitizedNodes, ...sanitizedEdges];
    }, [nodes, edges]);

    // 2. 样式定义 (Memoized)
    const cyStyles = useMemo<StylesheetJsonBlock[]>(() => {
        // 颜色映射
        const nodeColorMap: Record<string, string> = {
            Student: "#60a5fa", Teacher: "#34d399", Course: "#fbbf24", 
            KnowledgePoint: "#a78bfa", ErrorType: "#f87171",
        };
        const edgeColorMap: Record<string, string> = {
            CHAT_WITH: "#60a5fa", LIKES: "#f472b6", TEACHES: "#34d399",
            LEARNS: "#fbbf24", CONTAINS: "#a78bfa", HAS_ERROR: "#f87171", RELATES_TO: "#9ca3af",
        };
        const edgeStyleMap: Record<string, string> = {
            CHAT_WITH: "solid", LIKES: "dashed", TEACHES: "solid",
            LEARNS: "solid", CONTAINS: "dot", HAS_ERROR: "solid", RELATES_TO: "dashed",
        };

        const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

        return [
            {
                selector: "node",
                style: {
                    "background-color": (ele: any) => nodeColorMap[ele.data("type")] || "#9ca3af",
                    label: "data(label)",
                    "text-valign": "center", 
                    "text-halign": "center",
                    color: "#fff",
                    "font-size": isMobile ? "10px" : "12px",
                    width: (ele: any) => (ele.data("size") || (isMobile ? 40 : 30)),
                    height: (ele: any) => (ele.data("size") || (isMobile ? 40 : 30)),
                    "border-width": 2, 
                    "border-color": "#fff",
                },
            },
            {
                selector: "node:selected",
                style: { "border-width": 4, "border-color": "#2563eb", "background-color": "#3b82f6" },
            },
            {
                selector: "edge",
                style: {
                    width: (ele: any) => Math.min(Math.max((ele.data("weight") || 1) * 2, 1), 8),
                    "line-color": (ele: any) => edgeColorMap[ele.data("type")] || "#9ca3af",
                    "target-arrow-color": (ele: any) => edgeColorMap[ele.data("type")] || "#9ca3af",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier",
                    "line-style": (ele: any) => edgeStyleMap[ele.data("type")] || "solid",
                },
            },
            // 状态样式
            { selector: "node.highlighted", style: { "border-width": 4, "border-color": "#10b981", "opacity": 1 } },
            { selector: "edge.highlighted", style: { "line-color": "#10b981", "target-arrow-color": "#10b981", "opacity": 1, "width": 4 } },
            { selector: "node.faded", style: { "opacity": 0.2 } },
            { selector: "edge.faded", style: { "opacity": 0.1 } },
            { selector: "node.hovered", style: { "border-width": 4, "border-color": "#6366f1" } }, // 悬停样式
        ];
    }, []);

    // 3. 布局配置 (Memoized)
    const layoutConfig = useMemo<LayoutOptions>(() => {
        const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
        return {
            name: layout,
            fit: true,
            padding: 50,
            animate: true,
            animationDuration: 500,
            // Cose 特定配置
            ...(layout === 'cose' ? {
                componentSpacing: 40,
                nodeOverlap: 4,
                refresh: 20,
                idealEdgeLength: isMobile ? 80 : 100,
                nodeRepulsion: (node: any) => 10000,
                edgeElasticity: (edge: any) => 100,
                nestingFactor: 1.2,
                gravity: 1,
                numIter: 1000,
                initialTemp: 1000,
                coolingFactor: 0.99,
                minTemp: 1.0,
                randomize: true, // 强制随机初始位置，这对空坐标很重要
            } : {}),
            // Dagre 特定配置
            ...(layout === 'dagre' ? { nodeSep: 50, rankSep: 100 } : {}),
            // Circle 特定配置
            ...(layout === 'circle' ? { radius: 200 } : {}),
        } as LayoutOptions;
    }, [layout]);

    // 4. 初始化 Cy 实例
    const onCy = useCallback((cy: Core) => {
        // @ts-ignore
        cytoscapeRef.current = { cy };

        // 事件处理
        const handleMouseOver = (e: any) => {
            if (cy.container()) cy.container()!.style.cursor = 'pointer';
            e.target.addClass('hovered');
            callbacksRef.current.onNodeHover?.(e.target.id());
        };
        const handleMouseOut = (e: any) => {
            if (cy.container()) cy.container()!.style.cursor = 'default';
            e.target.removeClass('hovered');
            callbacksRef.current.onNodeHover?.(null);
        };
        const handleTap = (e: any) => {
            const nodeId = e.target.id();
            const { onNodeClick, onSelectedNodesChange } = callbacksRef.current;
            if (onNodeClick) onNodeClick(nodeId);
            if (!onSelectedNodesChange) {
                cy.nodes().unselect();
                e.target.select();
            }
        };

        // 绑定事件 (先解绑防止重复)
        cy.off('mouseover', 'node', handleMouseOver);
        cy.off('mouseout', 'node', handleMouseOut);
        cy.off('tap', 'node', handleTap);

        cy.on('mouseover', 'node', handleMouseOver);
        cy.on('mouseout', 'node', handleMouseOut);
        cy.on('tap', 'node', handleTap);
    }, []);

    // 5. 显式运行布局的副作用
    // 当节点变化或布局类型变化时，手动触发布局
    useEffect(() => {
        const cy = cytoscapeRef.current?.cy;
        if (!cy || elements.length === 0) return;

        // 稍微延迟以确保 DOM 准备就绪
        const timer = setTimeout(() => {
             // 显式运行布局
             const layoutInstance = cy.layout(layoutConfig);
             layoutInstance.run();
             // 强制适配视图
             cy.fit(undefined, 50);
        }, 100);

        return () => clearTimeout(timer);
    }, [elements, layoutConfig]);

    // 6. 交互状态同步 (Selection & Highlight)
    useEffect(() => {
        const cy = cytoscapeRef.current?.cy;
        if (!cy) return;
        
        cy.batch(() => {
            cy.nodes().unselect();
            if (selectedNodeId) cy.getElementById(selectedNodeId).select();
            selectedNodeIds.forEach(id => cy.getElementById(id).select());
            
            cy.elements().removeClass("highlighted faded");
            if (highlightedNodeIds.length > 0) {
                highlightedNodeIds.forEach(id => cy.getElementById(id).addClass("highlighted"));
                highlightedNodeIds.forEach(id => {
                     cy.getElementById(id).connectedEdges().forEach(edge => {
                         if (highlightedNodeIds.includes(edge.target().id()) || highlightedNodeIds.includes(edge.source().id())) {
                             edge.addClass("highlighted");
                         }
                     });
                });
                cy.elements().not(".highlighted").not(":selected").addClass("faded");
            }
        });
    }, [selectedNodeId, selectedNodeIds, highlightedNodeIds]);

    return (
        <div className={`relative ${className}`} style={{ width: '100%', height: '100%' }}>
            {/* 这里的 div 充当绝对定位的容器，确保 Cytoscape 有明确大小 */}
            <div className="absolute inset-0">
                <CytoscapeComponent
                    cy={onCy}
                    elements={elements}
                    stylesheet={cyStyles}
                    layout={layoutConfig} // 这里传给组件，初始化时也会跑一次
                    className="w-full h-full"
                    style={{ width: '100%', height: '100%' }}
                />
            </div>
        </div>
    );
  }
);

GraphVisualization.displayName = "GraphVisualization";