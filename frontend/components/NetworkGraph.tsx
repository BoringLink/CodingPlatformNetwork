import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { GraphData, GraphNode, NodeType, InteractionType } from '../types';

interface NetworkGraphProps {
  data: GraphData;
  highlightedNodeIds: string[];
  studentAcceptance?: Record<string, 'accept' | 'reject'>;
  onNodeClick: (node: GraphNode) => void;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ data, highlightedNodeIds, studentAcceptance, onNodeClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data.nodes.length || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // Clear previous
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height]);

    // Color scale for Nodes
    const color = (d: GraphNode) => {
      switch (d.type) {
        case NodeType.TEACHER: return "#7c3aed"; // Violet 600
        case NodeType.KNOWLEDGE: return "#059669"; // Emerald 600
        case NodeType.STUDENT: return "#94a3b8"; // Slate 400
        default: return "#ccc";
      }
    };

    // Color logic for Links
    const linkColor = (type: InteractionType) => {
        return type === InteractionType.PHYSICAL ? "#64748b" : "#3b82f6"; // Slate-500 vs Blue-500
    };

    // Simulation setup
    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id((d: any) => d.id).distance(60))
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius((d: any) => d.val + 5));

    // Links
    const link = svg.append("g")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke-width", (d) => Math.sqrt(d.value))
      .attr("stroke", (d) => linkColor(d.type)) // Apply dynamic color
      // Visual difference for Interaction Type
      .attr("stroke-dasharray", (d) => d.type === InteractionType.PLATFORM ? "4, 2" : null)
      .attr("class", (d) => d.type === InteractionType.PLATFORM ? "platform-link" : "physical-link");

    // Nodes
    const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", (d) => d.val)
      .attr("fill", (d) => color(d))
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation(); // Prevent container click from firing if we had one
        onNodeClick(d);
      })
      .call(drag(simulation) as any);

    // Labels (only for Teachers and Knowledge to avoid clutter)
    const labels = svg.append("g")
      .selectAll("text")
      .data(data.nodes.filter(n => n.type !== NodeType.STUDENT))
      .join("text")
      .text(d => d.name)
      .attr("font-size", 11)
      .attr("font-weight", 500)
      .attr("fill", "#334155")
      .attr("dx", 14)
      .attr("dy", 4)
      .style("pointer-events", "none")
      .style("text-shadow", "0 1px 2px rgba(255,255,255,0.8)"); 
      
    node.append("title")
      .text(d => d.name);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);

      labels
        .attr("x", (d: any) => d.x)
        .attr("y", (d: any) => d.y);
    });

    // Zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
            svg.selectAll("g").attr("transform", event.transform);
        });
        
    svg.call(zoom as any);

    // Drag behavior helper
    function drag(sim: any) {
      function dragstarted(event: any) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event: any) {
        if (!event.active) sim.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }

    // Clean up
    return () => {
      simulation.stop();
    };
  }, [data]);

  // Effect for highlighting
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    
    const getColor = (d: any) => {
        if (d.type === NodeType.STUDENT && studentAcceptance?.[d.id]) {
            return studentAcceptance[d.id] === 'accept' ? '#22c55e' : '#ef4444';
        }
        switch (d.type) {
            case NodeType.TEACHER: return "#7c3aed";
            case NodeType.KNOWLEDGE: return "#059669";
            case NodeType.STUDENT: return "#94a3b8";
            default: return "#ccc";
        }
    };
    
    // Dim everyone first if something is highlighted
    if (highlightedNodeIds.length > 0) {
        svg.selectAll("circle")
           .transition().duration(300)
           .attr("opacity", 0.1)
           .attr("stroke-width", 0);
           
        svg.selectAll("line")
           .transition().duration(300)
           .attr("opacity", 0.05);

        // Highlight specific nodes
        svg.selectAll("circle")
           .filter((d: any) => highlightedNodeIds.includes(d.id))
           .transition().duration(300)
           .attr("opacity", 1)
           .attr("r", (d: any) => d.val * 1.3) // Pulse effect
           .attr("stroke", "#fff")
           .attr("stroke-width", 2)
           .attr("filter", "drop-shadow(0px 4px 4px rgba(0,0,0,0.2))")
           .attr("fill", (d: any) => getColor(d));
    } else {
        // Reset
        svg.selectAll("circle")
           .transition().duration(300)
           .attr("opacity", 1)
           .attr("r", (d: any) => d.val)
           .attr("stroke", "#fff")
           .attr("stroke-width", 2)
           .attr("filter", null)
           .attr("fill", (d: any) => getColor(d));
           
        svg.selectAll("line")
           .transition().duration(300)
           .attr("opacity", 0.6);
    }
    
  }, [highlightedNodeIds, data, studentAcceptance]);

  return (
    <div ref={containerRef} className="w-full h-full rounded-lg overflow-hidden relative">
        <svg ref={svgRef} className="w-full h-full"></svg>
        
        {/* Glassmorphism Legend */}
        <div className="absolute bottom-5 right-5 bg-white/80 backdrop-blur-md p-4 rounded-xl shadow-lg border border-white/50 text-xs space-y-3 z-10 ring-1 ring-slate-900/5 select-none">
            <div>
                <div className="font-bold text-slate-500 mb-2 uppercase tracking-wider text-[10px]">节点类型</div>
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-violet-600 shadow-sm"></span> 
                        <span className="text-slate-600 font-medium">教师 (Teacher)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-600 shadow-sm"></span> 
                        <span className="text-slate-600 font-medium">知识点 (Knowledge)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-slate-400 shadow-sm"></span> 
                        <span className="text-slate-600 font-medium">学生 (Student)</span>
                    </div>
                </div>
            </div>
            
            <div className="pt-2 border-t border-slate-200/60">
                <div className="font-bold text-slate-500 mb-2 uppercase tracking-wider text-[10px]">交互类型</div>
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                        <span className="w-8 h-0.5 bg-slate-500 rounded-full"></span> 
                        <span className="text-slate-600 font-medium">物理空间采集</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                            <span className="w-2 h-0.5 bg-blue-500 rounded-full"></span>
                            <span className="w-2 h-0.5 bg-blue-500 rounded-full"></span>
                            <span className="w-2 h-0.5 bg-blue-500 rounded-full"></span>
                        </div>
                        <span className="text-slate-600 font-medium">平台采集</span>
                    </div>
                </div>
            </div>

            {studentAcceptance && Object.keys(studentAcceptance).length > 0 && (
                <div className="pt-2 border-t border-slate-200/60 animate-in fade-in">
                    <div className="font-bold text-slate-500 mb-2 uppercase tracking-wider text-[10px]">资源反馈</div>
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] ring-2 ring-green-100"></span> 
                            <span className="text-slate-700 font-bold">高接受度</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)] ring-2 ring-red-100"></span> 
                            <span className="text-slate-700 font-bold">低接受度</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    </div>
  );
};

export default NetworkGraph;