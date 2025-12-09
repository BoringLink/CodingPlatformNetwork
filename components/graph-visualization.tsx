"use client";

import React, { useEffect, useRef } from "react";
// @ts-expect-error - No types available for react-cytoscapejs
import CytoscapeComponent from "react-cytoscapejs";
import {
  VisualizationNode,
  VisualizationEdge,
  NodeType,
  RelationshipType,
} from "@/types/api";

interface GraphVisualizationProps {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  layout?: string;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  selectedNodeId?: string;
  className?: string;
}

export function GraphVisualization({
  nodes,
  edges,
  layout = "cose",
  onNodeClick,
  onNodeHover,
  selectedNodeId,
  className = "w-full h-full",
}: GraphVisualizationProps) {
  const cytoscapeRef = useRef<any>(null);

  // Map node types to colors
  const nodeColorMap: Record<NodeType, string> = {
    Student: "#60a5fa", // blue
    Teacher: "#34d399", // green
    Course: "#fbbf24", // yellow
    KnowledgePoint: "#a78bfa", // purple
    ErrorType: "#f87171", // red
  };

  // Map relationship types to colors
  const edgeColorMap: Record<RelationshipType, string> = {
    CHAT_WITH: "#60a5fa", // blue
    LIKES: "#f472b6", // pink
    TEACHES: "#34d399", // green
    LEARNS: "#fbbf24", // yellow
    CONTAINS: "#a78bfa", // purple
    HAS_ERROR: "#f87171", // red
    RELATES_TO: "#9ca3af", // gray
  };

  // Map relationship types to line styles
  const edgeStyleMap: Record<RelationshipType, string> = {
    CHAT_WITH: "solid",
    LIKES: "dashed",
    TEACHES: "solid",
    LEARNS: "solid",
    CONTAINS: "dot",
    HAS_ERROR: "solid",
    RELATES_TO: "dashed",
  };

  // Convert visualization data to Cytoscape format
  const cyNodes = nodes.map((node) => ({
    data: {
      ...node,
    },
    position: node.position,
  }));

  const cyEdges = edges.map((edge) => ({
    data: {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
      weight: edge.weight,
    },
  }));

  // Cytoscape styles
  const cyStyles = [
    // Node styles
    {
      selector: "node",
      style: {
        "background-color": (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const type = ele.data("type") as NodeType;
          return nodeColorMap[type] || "#9ca3af";
        },
        label: "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        color: "#fff",
        "font-size": "12px",
        width: (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const size = ele.data("size");
          return typeof size === "number" ? size : 30;
        },
        height: (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const size = ele.data("size");
          return typeof size === "number" ? size : 30;
        },
        "border-width": 2,
        "border-color": "#fff",
        "text-outline-width": 2,
        "text-outline-color": (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const type = ele.data("type") as NodeType;
          return nodeColorMap[type] || "#9ca3af";
        },
      },
    },
    // Selected node style
    {
      selector: "node:selected",
      style: {
        "border-width": 3,
        "border-color": "#2563eb",
        "z-index": 1000,
      },
    },
    // Edge styles
    {
      selector: "edge",
      style: {
        width: (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const weight = ele.data("weight");
          const weightNum = typeof weight === "number" ? weight : 1;
          return Math.max(1, Math.min(weightNum * 2, 8));
        },
        "line-color": (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const type = ele.data("type") as RelationshipType;
          return edgeColorMap[type] || "#9ca3af";
        },
        "target-arrow-color": (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const type = ele.data("type") as RelationshipType;
          return edgeColorMap[type] || "#9ca3af";
        },
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "line-style": (ele: {
          data: (key: string) => string | number | undefined;
        }) => {
          const type = ele.data("type") as RelationshipType;
          return edgeStyleMap[type] || "solid";
        },
      },
    },
    // Hover styles
    {
      selector: "node:hover",
      style: {
        cursor: "pointer",
        opacity: 0.9,
      },
    },
    {
      selector: "edge:hover",
      style: {
        cursor: "pointer",
        opacity: 0.9,
      },
    },
  ];

  // Layout options
  const layoutOptions = {
    name: layout,
    // Common layout options
    animate: true,
    animationDuration: 800,
    // Specific layout options
    ...(layout === "cose" && {
      randomize: true,
      idealEdgeLength: 100,
      nodeOverlap: 20,
    }),
    ...(layout === "circle" && {
      radius: 200,
      startAngle: Math.PI * 0.5,
      sweep: Math.PI * 2,
    }),
    ...(layout === "grid" && {
      rows: Math.ceil(Math.sqrt(nodes.length)),
    }),
    ...(layout === "dagre" && {
      rankDir: "TB",
      nodeSep: 50,
      edgeSep: 10,
    }),
  } as const;

  // Handle node click
  const handleTap = (event: {
    target: { isNode: () => boolean; id: () => string };
  }) => {
    const node = event.target;
    if (node.isNode()) {
      onNodeClick?.(node.id());
    }
  };

  // Handle node hover
  const handleMouseOver = (event: {
    target: { isNode: () => boolean; id: () => string };
  }) => {
    const node = event.target;
    if (node.isNode()) {
      onNodeHover?.(node.id());
    }
  };

  const handleMouseOut = () => {
    onNodeHover?.(null);
  };

  // Select node when selectedNodeId changes
  useEffect(() => {
    const cy = cytoscapeRef.current?.cy;
    if (!cy) return;

    // Deselect all nodes
    cy.nodes().unselect();

    // Select the specified node if it exists
    if (selectedNodeId) {
      const node = cy.getElementById(selectedNodeId);
      if (node.length > 0) {
        node.select();
        // Center the selected node
        cy.center(selectedNodeId);
      }
    }
  }, [selectedNodeId]);

  // Fit all nodes in view when data changes
  useEffect(() => {
    const cy = cytoscapeRef.current?.cy;
    if (!cy) return;

    // Wait for the layout to complete
    setTimeout(() => {
      cy.fit(undefined, 50);
    }, 1000);
  }, [nodes, edges]);

  return (
    <CytoscapeComponent
      ref={cytoscapeRef}
      elements={{
        nodes: cyNodes,
        edges: cyEdges,
      }}
      style={cyStyles}
      layout={layoutOptions}
      className={className}
      cy={{}}
      events={{
        tap: handleTap,
        mouseover: handleMouseOver,
        mouseout: handleMouseOut,
      }}
    />
  );
}
