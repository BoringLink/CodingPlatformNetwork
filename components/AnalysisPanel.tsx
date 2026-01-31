import React, { useMemo, useState, useEffect } from 'react';
import { GraphData, NodeType, Resource, CognitiveAttributes, GraphNode, InteractionType } from '../types';
import { PieChart, Users, Book, Activity, ThumbsUp, Send, CheckCircle, BarChart3, X, GitGraph, Share2, Target, TrendingUp, Layers, Database } from 'lucide-react';

interface AnalysisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  data: GraphData;
  resources: Resource[];
  defaultTab?: 'overview' | 'subgraph';
}

// Simple SVG Donut Chart
interface DonutChartProps {
  data: { label: string; value: number; color: string }[];
  size?: number;
}

const DonutChart: React.FC<DonutChartProps> = ({ data, size = 120 }) => {
  const total = data.reduce((acc, cur) => acc + cur.value, 0);
  let cumulativeAngle = 0;
  
  // If no data, show gray circle
  if (total === 0) {
      return (
          <div className="flex flex-col items-center justify-center">
             <div className="rounded-full border-4 border-gray-100" style={{width: size, height: size}}></div>
             <span className="text-xs text-gray-400 mt-2">暂无数据</span>
          </div>
      )
  }

  const paths = data.map((slice, i) => {
    const angle = (slice.value / total) * 360;
    const x1 = 50 + 40 * Math.cos(Math.PI * (cumulativeAngle - 90) / 180);
    const y1 = 50 + 40 * Math.sin(Math.PI * (cumulativeAngle - 90) / 180);
    const x2 = 50 + 40 * Math.cos(Math.PI * (cumulativeAngle + angle - 90) / 180);
    const y2 = 50 + 40 * Math.sin(Math.PI * (cumulativeAngle + angle - 90) / 180);
    const largeArcFlag = angle > 180 ? 1 : 0;
    
    const d = `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
    cumulativeAngle += angle;
    
    return <path key={i} d={d} fill={slice.color} stroke="white" strokeWidth="2" />;
  });

  return (
    <div className="flex items-center gap-6">
      <svg viewBox="0 0 100 100" width={size} height={size} className="transform -rotate-90">
        {paths}
        <circle cx="50" cy="50" r="25" fill="white" />
      </svg>
      <div className="space-y-2">
        {data.map((d, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="w-3 h-3 rounded-full" style={{backgroundColor: d.color}}></span>
            <span className="text-gray-600">{d.label}</span>
            <span className="font-bold text-gray-800">{Math.round(d.value / total * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Simple Bar Chart Row
interface BarRowProps {
  label: string;
  value: number;
  max: number;
  color: string;
}

const BarRow: React.FC<BarRowProps> = ({ label, value, max, color }) => (
    <div className="flex items-center gap-3 text-xs mb-2 last:mb-0">
      <span className="w-24 text-gray-500 truncate text-right shrink-0" title={label}>{label}</span>
      <div className="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
         <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${max > 0 ? (value / max) * 100 : 0}%` }}></div>
      </div>
      <span className="w-8 font-medium text-gray-700 text-right">{value}</span>
    </div>
);

// Simulated Line Chart
const TrendChart = () => {
  const points = [20, 35, 30, 45, 60, 55, 75, 80, 70, 85];
  const max = Math.max(...points);
  const min = Math.min(...points);
  const width = 100;
  const height = 40;
  
  const pathData = points.map((p, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - ((p - min) / (max - min)) * height;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  return (
    <div className="w-full h-24 relative mt-2">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible" preserveAspectRatio="none">
         {/* Grid lines */}
         <line x1="0" y1="0" x2="100" y2="0" stroke="#f3f4f6" strokeWidth="0.5" />
         <line x1="0" y1="20" x2="100" y2="20" stroke="#f3f4f6" strokeWidth="0.5" />
         <line x1="0" y1="40" x2="100" y2="40" stroke="#f3f4f6" strokeWidth="0.5" />
         
         {/* Area fill */}
         <path d={`${pathData} L ${width} ${height} L 0 ${height} Z`} fill="url(#gradient)" opacity="0.2" />
         
         {/* Line */}
         <path d={pathData} fill="none" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
         
         <defs>
            <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
            </linearGradient>
         </defs>
      </svg>
      <div className="flex justify-between text-[10px] text-gray-400 mt-1">
          <span>课前 (0min)</span>
          <span>课中 (20min)</span>
          <span>当前 (40min)</span>
      </div>
    </div>
  );
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ isOpen, onClose, data, resources, defaultTab = 'overview' }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'subgraph'>('overview');

  // Sync activeTab with defaultTab when panel opens
  useEffect(() => {
    if (isOpen) {
        setActiveTab(defaultTab);
    }
  }, [isOpen, defaultTab]);

  // --- Data Calculations ---
  
  // 1. General Stats
  const stats = useMemo(() => {
    const students = data.nodes.filter(n => n.type === NodeType.STUDENT);
    const teachers = data.nodes.filter(n => n.type === NodeType.TEACHER);
    const knowledge = data.nodes.filter(n => n.type === NodeType.KNOWLEDGE);
    return { total: data.nodes.length, studentCount: students.length, teacherCount: teachers.length, knowledgeCount: knowledge.length, students };
  }, [data]);

  // 2. Cognitive Stats
  const cognitiveAverages = useMemo(() => {
    if (stats.studentCount === 0) return null;
    const keys: (keyof CognitiveAttributes)[] = ['knowledgeReserve', 'learningEngagement', 'cognitiveLoad', 'learningMotivation', 'computationalThinking', 'humanAiTrust', 'learningMethod', 'learningAttitude'];
    const sums = keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {} as Record<keyof CognitiveAttributes, number>);
    stats.students.forEach((s: GraphNode) => { if (s.studentProfile) keys.forEach(key => sums[key] += s.studentProfile![key]); });
    return keys.map(key => ({
      key,
      label: { knowledgeReserve: '知识储备', learningEngagement: '学习投入', cognitiveLoad: '认知负荷', learningMotivation: '学习动机', computationalThinking: '计算思维', humanAiTrust: '人机信任度', learningMethod: '学习方法', learningAttitude: '学习态度' }[key],
      value: (sums[key] / stats.studentCount).toFixed(1)
    }));
  }, [stats]);

  // 3. Resource Stats
  const resourceStats = useMemo(() => ({
    total: resources.length,
    avgAccuracy: resources.length > 0 ? (resources.reduce((acc, r) => acc + r.accuracy, 0) / resources.length).toFixed(1) : '0'
  }), [resources]);

  // 4. Satisfaction Stats
  const satisfactionStats = useMemo(() => {
    const pushed = stats.studentCount;
    const filled = Math.floor(pushed * (0.85 + Math.random() * 0.1)); 
    const score = (4.2 + Math.random() * 0.6).toFixed(1); 
    return { pushed, filled, score, percentage: ((parseFloat(score) / 5) * 100).toFixed(0) };
  }, [stats.studentCount]);

  // --- Subgraph Analysis Data ---

  // A. Knowledge Heatmap (Hotspots)
  const knowledgeHotspots = useMemo(() => {
      const kNodes = data.nodes.filter(n => n.type === NodeType.KNOWLEDGE);
      const degreeMap = new Map<string, number>();
      
      data.links.forEach(l => {
          const targetId = typeof l.target === 'object' ? l.target.id : l.target as string;
          const sourceId = typeof l.source === 'object' ? l.source.id : l.source as string;
          
          if (targetId.startsWith('K')) degreeMap.set(targetId, (degreeMap.get(targetId) || 0) + 1);
          if (sourceId.startsWith('K')) degreeMap.set(sourceId, (degreeMap.get(sourceId) || 0) + 1);
      });

      return kNodes
        .map(n => ({ label: n.name, value: degreeMap.get(n.id) || 0 }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 6);
  }, [data]);

  // B. Learning Mode (Interaction Types)
  const interactionTypes = useMemo(() => {
      let ts = 0, ss = 0, sk = 0;
      data.links.forEach(l => {
          const sType = typeof l.source === 'object' ? l.source.type : (l.source as string).startsWith('T') ? NodeType.TEACHER : (l.source as string).startsWith('S') ? NodeType.STUDENT : NodeType.KNOWLEDGE;
          const tType = typeof l.target === 'object' ? l.target.type : (l.target as string).startsWith('T') ? NodeType.TEACHER : (l.target as string).startsWith('S') ? NodeType.STUDENT : NodeType.KNOWLEDGE;

          if ((sType === NodeType.TEACHER && tType === NodeType.STUDENT) || (sType === NodeType.STUDENT && tType === NodeType.TEACHER)) ts++;
          else if (sType === NodeType.STUDENT && tType === NodeType.STUDENT) ss++;
          else if ((sType === NodeType.STUDENT && tType === NodeType.KNOWLEDGE) || (sType === NodeType.KNOWLEDGE && tType === NodeType.STUDENT)) sk++;
      });
      return [
          { label: '师生互动 (指导)', value: ts, color: '#7c3aed' },
          { label: '生生协作 (研讨)', value: ss, color: '#f59e0b' },
          { label: '人机/自主 (探索)', value: sk, color: '#059669' }
      ];
  }, [data]);

  // C. Group Attention (Student Degree Distribution)
  const groupAttention = useMemo(() => {
      const counts = { high: 0, medium: 0, low: 0 };
      const sNodes = data.nodes.filter(n => n.type === NodeType.STUDENT);
      
      const degreeMap = new Map<string, number>();
      data.links.forEach(l => {
        const ids = [typeof l.source === 'object' ? l.source.id : l.source, typeof l.target === 'object' ? l.target.id : l.target];
        ids.forEach((id: any) => {
            if (typeof id === 'string' && id.startsWith('S')) degreeMap.set(id, (degreeMap.get(id) || 0) + 1);
        });
      });

      sNodes.forEach(n => {
          const d = degreeMap.get(n.id) || 0;
          if (d >= 8) counts.high++;
          else if (d >= 5) counts.medium++;
          else counts.low++;
      });
      
      const total = sNodes.length || 1;
      return [
          { label: '高活跃核心圈', value: counts.high, max: total, color: 'bg-indigo-500' },
          { label: '中活跃协作圈', value: counts.medium, max: total, color: 'bg-blue-400' },
          { label: '低活跃边缘圈', value: counts.low, max: total, color: 'bg-gray-400' }
      ];
  }, [data]);

  // D. Interaction Source (New for Interaction Type classification)
  const interactionSources = useMemo(() => {
    let physical = 0, platform = 0;
    data.links.forEach(l => {
        if (l.type === InteractionType.PHYSICAL) physical++;
        else platform++;
    });
    return [
        { label: '物理空间采集', value: physical, color: '#475569' }, // Matches Slate-600
        { label: '平台数据采集', value: platform, color: '#3b82f6' }  // Matches Blue-500
    ];
  }, [data]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-2xl w-[900px] h-[85vh] flex flex-col relative overflow-hidden">
        
        {/* Header with Tabs */}
        <div className="border-b border-gray-100 bg-white z-10">
            <div className="flex justify-between items-center p-4 pb-0 bg-indigo-600 text-white rounded-t-xl">
                <div className="flex items-center gap-2 mb-4">
                    <PieChart className="w-6 h-6" />
                    <h2 className="text-xl font-bold">全域数据统计分析 Dashboard</h2>
                </div>
                <button onClick={onClose} className="text-white/80 hover:text-white transition-colors mb-4">
                    <X className="w-6 h-6" />
                </button>
            </div>
            
            {/* Tabs */}
            <div className="flex px-6 bg-indigo-600/5 pt-2">
                <button 
                    onClick={() => setActiveTab('overview')}
                    className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                >
                    <Activity className="w-4 h-4" /> 全局概览
                </button>
                <button 
                    onClick={() => setActiveTab('subgraph')}
                    className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'subgraph' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                >
                    <GitGraph className="w-4 h-4" /> 子图透视
                </button>
            </div>
        </div>

        {/* Content Area */}
        <div className="p-6 bg-gray-50 flex-1 overflow-y-auto">
            
            {/* TAB 1: OVERVIEW */}
            {activeTab === 'overview' && (
                <div className="grid grid-cols-2 gap-6 animate-in slide-in-from-bottom-2 duration-300">
                    {/* 1. Node Statistics */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-4 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-indigo-500" /> 节点概况统计
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-indigo-50 rounded-lg text-center flex flex-col justify-center">
                            <span className="block text-3xl font-bold text-indigo-700">{stats.total}</span>
                            <span className="text-xs text-indigo-500 font-medium">网络节点总数</span>
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between items-center p-2 bg-gray-50 rounded border border-gray-100">
                                <span className="text-xs text-gray-500 flex items-center gap-1"><Users className="w-3 h-3"/> 学生节点</span>
                                <span className="font-bold text-gray-700">{stats.studentCount}</span>
                            </div>
                            <div className="flex justify-between items-center p-2 bg-gray-50 rounded border border-gray-100">
                                <span className="text-xs text-gray-500 flex items-center gap-1"><Users className="w-3 h-3 text-violet-500"/> 教师节点</span>
                                <span className="font-bold text-gray-700">{stats.teacherCount}</span>
                            </div>
                            <div className="flex justify-between items-center p-2 bg-gray-50 rounded border border-gray-100">
                                <span className="text-xs text-gray-500 flex items-center gap-1"><Book className="w-3 h-3 text-emerald-500"/> 知识点节点</span>
                                <span className="font-bold text-gray-700">{stats.knowledgeCount}</span>
                            </div>
                        </div>
                        </div>
                    </div>

                    {/* 3. Resource Analysis */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-4 flex items-center gap-2">
                        <Book className="w-4 h-4 text-amber-500" /> 资源推荐分析
                        </h3>
                        <div className="flex gap-4 items-center justify-around h-full pb-4">
                            <div className="text-center">
                                <div className="w-24 h-24 rounded-full border-4 border-amber-100 flex items-center justify-center mx-auto mb-2 bg-amber-50">
                                    <span className="text-3xl font-bold text-amber-600">{resourceStats.total}</span>
                                </div>
                                <span className="text-sm text-gray-500 font-medium">推荐资源总量</span>
                            </div>
                            <div className="h-16 w-px bg-gray-200"></div>
                            <div className="text-center">
                                <div className="w-24 h-24 rounded-full border-4 border-green-100 flex items-center justify-center mx-auto mb-2 bg-green-50">
                                    <span className="text-3xl font-bold text-green-600">{resourceStats.avgAccuracy}<span className="text-sm text-green-500">%</span></span>
                                </div>
                                <span className="text-sm text-gray-500 font-medium">平均推荐准确率</span>
                            </div>
                        </div>
                    </div>

                    {/* 2. Cognitive Analysis */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm col-span-2">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-4 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-emerald-500" /> 班级群体认知模版分析 (平均分/5分)
                        </h3>
                        <div className="grid grid-cols-2 gap-x-12 gap-y-5">
                            {cognitiveAverages?.map((item) => {
                                const val = parseFloat(item.value);
                                return (
                                    <div key={item.key} className="space-y-1">
                                        <div className="flex justify-between text-xs font-medium text-gray-600">
                                            <span>{item.label}</span>
                                            <span>{item.value}</span>
                                        </div>
                                        <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden">
                                            <div 
                                                className={`h-full rounded-full ${val >= 4 ? 'bg-emerald-500' : val >= 3 ? 'bg-indigo-500' : 'bg-amber-500'}`}
                                                style={{ width: `${(val / 5) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* 4. Satisfaction Analysis */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm col-span-2">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-4 flex items-center gap-2">
                        <ThumbsUp className="w-4 h-4 text-pink-500" /> 满意度调查分析
                        </h3>
                        <div className="grid grid-cols-3 gap-6">
                            <div className="bg-blue-50 p-4 rounded-xl flex items-center gap-4 border border-blue-100">
                                <div className="p-3 bg-white rounded-full text-blue-500 shadow-sm">
                                    <Send className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="text-xs text-blue-500 font-medium uppercase">问卷推送人数</p>
                                    <p className="text-2xl font-bold text-blue-900">{satisfactionStats.pushed} 人</p>
                                </div>
                            </div>

                            <div className="bg-violet-50 p-4 rounded-xl flex items-center gap-4 border border-violet-100">
                                <div className="p-3 bg-white rounded-full text-violet-500 shadow-sm">
                                    <CheckCircle className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="text-xs text-violet-500 font-medium uppercase">问卷填写人数</p>
                                    <p className="text-2xl font-bold text-violet-900">{satisfactionStats.filled} 人</p>
                                </div>
                            </div>

                            <div className="bg-pink-50 p-4 rounded-xl flex items-center gap-4 border border-pink-100">
                                <div className="p-3 bg-white rounded-full text-pink-500 shadow-sm">
                                    <ThumbsUp className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="text-xs text-pink-500 font-medium uppercase">整体满意度</p>
                                    <div className="flex items-baseline gap-2">
                                        <p className="text-2xl font-bold text-pink-900">{satisfactionStats.score}/5.0</p>
                                        <span className="text-xs text-pink-600 font-medium">({satisfactionStats.percentage}%)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* TAB 2: SUBGRAPH */}
            {activeTab === 'subgraph' && (
                <div className="grid grid-cols-2 gap-6 animate-in slide-in-from-right-4 duration-300">
                    
                    {/* Knowledge Heatmap */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-6 flex items-center gap-2">
                             <Target className="w-4 h-4 text-rose-500" /> 知识热点图 (高频交互节点)
                        </h3>
                        <div className="space-y-2">
                            {knowledgeHotspots.map((k, i) => (
                                <BarRow key={i} label={k.label} value={k.value} max={knowledgeHotspots[0]?.value || 1} color="bg-rose-500" />
                            ))}
                            {knowledgeHotspots.length === 0 && <p className="text-xs text-gray-400">暂无交互数据</p>}
                        </div>
                        <p className="text-[10px] text-gray-400 mt-4 text-center">基于网络度中心性 (Degree Centrality) 计算</p>
                    </div>

                    {/* Learning Patterns & Source Analysis */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm font-bold text-gray-500 uppercase flex items-center gap-2">
                                <Share2 className="w-4 h-4 text-indigo-500" /> 交互模式与来源
                            </h3>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div className="flex flex-col items-center">
                                <span className="text-[10px] font-semibold text-gray-400 mb-2 uppercase">模式结构</span>
                                <DonutChart data={interactionTypes} size={100} />
                            </div>
                            <div className="flex flex-col items-center border-l border-gray-100">
                                <span className="text-[10px] font-semibold text-gray-400 mb-2 uppercase">数据来源</span>
                                <DonutChart data={interactionSources} size={100} />
                            </div>
                        </div>

                        <div className="mt-4 p-2 bg-gray-50 rounded text-[10px] text-gray-500 leading-relaxed border border-gray-100">
                            <strong>分析：</strong> 
                            {interactionSources[0].value > interactionSources[1].value 
                                ? "网络数据主要来源于物理空间中的师生/生生互动，体现了课堂现场的高频交流。" 
                                : "网络交互高度依赖线上平台，体现了混合式或远程学习的特征。"
                            }
                        </div>
                    </div>

                    {/* Group Attention */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-6 flex items-center gap-2">
                             <Layers className="w-4 h-4 text-blue-500" /> 群体关注度分布
                        </h3>
                        <div className="space-y-3">
                             {groupAttention.map((g, i) => (
                                <BarRow key={i} label={g.label} value={g.value} max={g.max} color={g.color} />
                             ))}
                        </div>
                         <p className="text-[10px] text-gray-400 mt-4 text-center">基于学生节点活跃度聚类分析</p>
                    </div>

                    {/* Evolution Trend */}
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <h3 className="text-sm font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                             <TrendingUp className="w-4 h-4 text-indigo-500" /> 学习模式演化趋势
                        </h3>
                        <TrendChart />
                        <div className="mt-3 flex gap-4 text-xs">
                            <div className="flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                                <span className="text-gray-600">交互密度</span>
                            </div>
                            <p className="text-gray-400 flex-1 text-right">模拟最近40分钟数据</p>
                        </div>
                    </div>
                </div>
            )}

        </div>
      </div>
    </div>
  );
};

export default AnalysisPanel;