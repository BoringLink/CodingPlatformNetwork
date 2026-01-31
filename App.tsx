import React, { useState, useEffect, useCallback } from 'react';
import { Settings, Users, Network, BookOpen, BarChart3, RefreshCw, Wand2, X, User, Lightbulb, Book, Link as LinkIcon, ExternalLink, GraduationCap, PieChart, GitGraph, ChevronRight, LayoutDashboard, Layers, Activity } from 'lucide-react';
import NetworkGraph from './components/NetworkGraph';
import AnalysisPanel from './components/AnalysisPanel';
import { generateGraphData, generateResources, getClassOptions } from './services/dataService';
import { analyzeNetwork } from './services/geminiService';
import { getStrategy } from './services/strategies';
import { Scenario, GraphData, Resource, ClassInfo, NodeType, GraphNode, CognitiveAttributes } from './types';

const App: React.FC = () => {
    // State
    const [scenario, setScenario] = useState<Scenario>(Scenario.ONLINE_COURSE);
    const [classInfo, setClassInfo] = useState<ClassInfo>({
        school: '三墩小学',
        grade: '五年级',
        classId: '2班'
    });

    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
    const [resources, setResources] = useState<Resource[]>([]);
    const [selectedResource, setSelectedResource] = useState<string | null>(null);
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
    const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
    const [studentAcceptance, setStudentAcceptance] = useState<Record<string, 'accept' | 'reject'>>({});
    const [aiAnalysis, setAiAnalysis] = useState<string>("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isDataLoading, setIsDataLoading] = useState(false);

    // Analysis Panel State
    const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);
    const [analysisDefaultTab, setAnalysisDefaultTab] = useState<'overview' | 'subgraph'>('overview');

    // Tooltip State
    const [hoveredAttribute, setHoveredAttribute] = useState<{ key: keyof CognitiveAttributes, score: number } | null>(null);
    const [tooltipPosition, setTooltipPosition] = useState<{ x: number, y: number } | null>(null);

    // Class options state (loaded async)
    const [classOptions, setClassOptions] = useState<{ schools: string[], grades: string[], classes: string[] }>({
        schools: [],
        grades: [],
        classes: []
    });

    // Constants
    const scenarios = Object.values(Scenario);

    // Cognitive attribute labels
    const cognitiveLabels: Record<keyof CognitiveAttributes, string> = {
        knowledgeReserve: '知识储备',
        learningEngagement: '学习投入',
        cognitiveLoad: '认知负荷',
        learningMotivation: '学习动机',
        computationalThinking: '计算思维',
        humanAiTrust: '人机信任度',
        learningMethod: '学习方法倾向',
        learningAttitude: '学习态度'
    };

    // Reset filters function - clears all selection states
    const resetFilters = useCallback(() => {
        if (classOptions.schools.length > 0 && classOptions.grades.length > 0 && classOptions.classes.length > 0) {
            setClassInfo({
                school: classOptions.schools[0],
                grade: classOptions.grades[0],
                classId: classOptions.classes[0]
            });
        }
        setScenario(Scenario.ONLINE_COURSE);
    }, [classOptions]);

    // Load class options on mount
    useEffect(() => {
        const options = getClassOptions();
        setClassOptions(options);

        // Set initial class info to first available option
        if (options.schools.length > 0 && options.grades.length > 0 && options.classes.length > 0) {
            setClassInfo({
                school: options.schools[0],
                grade: options.grades[0],
                classId: options.classes[0]
            });
        }
    }, []);

    // Load Data Effect
    const loadData = useCallback(() => {
        // Skip if classOptions not loaded yet
        if (classOptions.schools.length === 0) return;

        const data = generateGraphData(scenario, classInfo);
        setGraphData(data);

        // Generate resources based on new knowledge points
        const kNodes = data.nodes.filter(n => n.type === NodeType.KNOWLEDGE);
        const newResources = generateResources(kNodes);
        setResources(newResources);
    }, [scenario, classInfo, classOptions.schools.length]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    // Handlers
    const openAnalysis = (tab: 'overview' | 'subgraph') => {
        setAnalysisDefaultTab(tab);
        setIsAnalysisOpen(true);
    };

    const handleResourceClick = (resource: Resource) => {
        // If clicking the same resource, toggle off
        if (selectedResource === resource.id) {
            setSelectedResource(null);
            setHighlightedNodeIds([]);
            setStudentAcceptance({});
        } else {
            setSelectedResource(resource.id);
            setSelectedNode(null); // Clear specific node selection to show network effect

            // Calculate highlighting
            const kIds = resource.relatedKnowledgeIds;
            const connectedStudentIds: string[] = [];

            graphData.links.forEach(link => {
                const sourceId = typeof link.source === 'object' ? (link.source as any).id : link.source;
                const targetId = typeof link.target === 'object' ? (link.target as any).id : link.target;

                if (kIds.includes(sourceId)) {
                    if (targetId.startsWith('S')) connectedStudentIds.push(targetId);
                } else if (kIds.includes(targetId)) {
                    if (sourceId.startsWith('S')) connectedStudentIds.push(sourceId);
                }
            });

            // Calculate acceptance for connected students based on resource accuracy
            const newAcceptance: Record<string, 'accept' | 'reject'> = {};
            connectedStudentIds.forEach(sid => {
                // Probability based on accuracy (e.g., 90% accuracy = 0.9 chance of acceptance)
                const isAccepted = Math.random() * 100 <= resource.accuracy;
                newAcceptance[sid] = isAccepted ? 'accept' : 'reject';
            });
            setStudentAcceptance(newAcceptance);

            setHighlightedNodeIds([...kIds, ...connectedStudentIds]);
        }
    };

    const handleNodeClick = (node: GraphNode) => {
        setSelectedNode(node);
        setSelectedResource(null);
        setHighlightedNodeIds([node.id]);
        setStudentAcceptance({});
    };

    const closeNodeDetail = () => {
        setSelectedNode(null);
        setHighlightedNodeIds([]);
        setStudentAcceptance({});
        setHoveredAttribute(null); // Clear tooltip
    };

    const handleAIAnalyze = async () => {
        setIsAnalyzing(true);
        const sCount = graphData.nodes.filter(n => n.type === NodeType.STUDENT).length;
        const tCount = graphData.nodes.filter(n => n.type === NodeType.TEACHER).length;
        const avgAcc = Math.floor(resources.reduce((acc, r) => acc + r.accuracy, 0) / resources.length);

        const analysis = await analyzeNetwork(scenario, sCount, tCount, avgAcc);
        setAiAnalysis(analysis);
        setIsAnalyzing(false);
    };

    const handleAttributeEnter = (e: React.MouseEvent, key: keyof CognitiveAttributes, score: number) => {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        setTooltipPosition({ x: rect.left - 340, y: rect.top }); // Position to the left of the bar
        setHoveredAttribute({ key, score });
    };

    const handleAttributeLeave = () => {
        setHoveredAttribute(null);
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50 text-slate-800 overflow-hidden relative font-sans selection:bg-indigo-100 selection:text-indigo-900">
            {/* Header */}
            <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-6 z-30 shrink-0 sticky top-0">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl shadow-lg shadow-indigo-200">
                        <Network className="text-white w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-slate-800 tracking-tight">教育交互网络</h1>
                        <p className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">交互式学习网络可视化</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => openAnalysis('overview')}
                        className="group flex items-center gap-2 bg-white text-slate-600 px-4 py-2 rounded-lg hover:bg-slate-50 transition-all border border-slate-200 shadow-sm hover:shadow text-sm font-medium active:scale-95"
                    >
                        <PieChart className="w-4 h-4 text-indigo-500 group-hover:scale-110 transition-transform" />
                        <span>统计分析</span>
                    </button>
                    <button
                        onClick={() => openAnalysis('subgraph')}
                        className="group flex items-center gap-2 bg-white text-slate-600 px-4 py-2 rounded-lg hover:bg-slate-50 transition-all border border-slate-200 shadow-sm hover:shadow text-sm font-medium active:scale-95"
                    >
                        <GitGraph className="w-4 h-4 text-violet-500 group-hover:scale-110 transition-transform" />
                        <span>子图透视</span>
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">

                {/* Left Control Panel */}
                <aside className="w-64 bg-white border-r border-slate-200 flex flex-col z-20 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.05)]">
                    <div className="p-5 border-b border-slate-100 flex-1 overflow-y-auto custom-scrollbar">
                        <div className="flex items-center gap-2 mb-6">
                            <Settings className="w-4 h-4 text-slate-400" />
                            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">控制面板</h2>
                        </div>

                        {/* Scenario Selection */}
                        <div className="mb-8">
                            <label className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-3 uppercase tracking-wide">
                                <LayoutDashboard className="w-3 h-3" /> 学习场景
                            </label>
                            <div className="space-y-1">
                                {scenarios.map((s) => (
                                    <button
                                        key={s}
                                        onClick={() => setScenario(s)}
                                        className={`w-full text-left px-3 py-2.5 rounded-lg text-xs transition-all duration-200 flex items-center justify-between group ${scenario === s
                                            ? 'bg-indigo-50 text-indigo-700 font-medium ring-1 ring-indigo-200'
                                            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
                                            }`}
                                    >
                                        <span>{s}</span>
                                        {scenario === s && <ChevronRight className="w-3 h-3 text-indigo-500" />}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Class Selection */}
                        <div>
                            <label className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-3 uppercase tracking-wide">
                                <Users className="w-3 h-3" /> 班级设置
                            </label>
                            <div className="space-y-3">
                                <div className="relative">
                                    <select
                                        className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer hover:border-slate-300"
                                        value={classInfo.school}
                                        onChange={(e) => setClassInfo({ ...classInfo, school: e.target.value })}
                                    >
                                        {classOptions.schools.map(o => <option key={o} value={o}>{o}</option>)}
                                    </select>
                                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                                        <ChevronRight className="w-3 h-3 rotate-90" />
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <div className="relative w-1/2">
                                        <select
                                            className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer hover:border-slate-300"
                                            value={classInfo.grade}
                                            onChange={(e) => setClassInfo({ ...classInfo, grade: e.target.value })}
                                        >
                                            {classOptions.grades.map(o => <option key={o} value={o}>{o}</option>)}
                                        </select>
                                        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                                            <ChevronRight className="w-3 h-3 rotate-90" />
                                        </div>
                                    </div>
                                    <div className="relative w-1/2">
                                        <select
                                            className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer hover:border-slate-300"
                                            value={classInfo.classId}
                                            onChange={(e) => setClassInfo({ ...classInfo, classId: e.target.value })}
                                        >
                                            {classOptions.classes.map(o => <option key={o} value={o}>{o}</option>)}
                                        </select>
                                        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                                            <ChevronRight className="w-3 h-3 rotate-90" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 mt-auto bg-slate-50 border-t border-slate-200">
                        <button
                            onClick={resetFilters}
                            className="w-full flex items-center justify-center gap-2 bg-white border border-slate-300 text-slate-600 px-4 py-2.5 rounded-lg shadow-sm hover:bg-white hover:text-indigo-600 hover:border-indigo-300 hover:shadow transition-all text-xs font-semibold active:translate-y-0.5"
                        >
                            <RefreshCw className="w-3 h-3" /> 重置筛选条件
                        </button>
                    </div>
                </aside>

                {/* Center Visualization */}
                <main className="flex-1 bg-slate-100/50 p-4 relative flex flex-col">
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 flex-1 relative flex flex-col overflow-hidden ring-1 ring-slate-900/5">
                        {/* Canvas Header overlay */}
                        <div className="absolute top-5 left-5 z-10 pointer-events-none">
                            <h3 className="text-xl font-bold text-slate-800 tracking-tight">{classInfo.school} {classInfo.grade}{classInfo.classId}</h3>
                            <div className="flex items-center gap-2 mt-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                <p className="text-xs font-medium text-slate-500">
                                    场景: <span className="text-indigo-600">{scenario}</span>
                                </p>
                            </div>
                        </div>

                        <div className="flex-1 overflow-hidden p-0 relative bg-slate-50/30">
                            <NetworkGraph
                                data={graphData}
                                highlightedNodeIds={highlightedNodeIds}
                                studentAcceptance={studentAcceptance}
                                onNodeClick={handleNodeClick}
                            />

                            {/* Floating Node Detail Card */}
                            {selectedNode && (
                                <div className="absolute top-5 right-5 w-80 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 ring-1 ring-slate-900/10 overflow-hidden animate-in fade-in slide-in-from-right-8 duration-300 z-20">
                                    {/* Header based on Node Type */}
                                    <div className={`p-5 flex justify-between items-start text-white bg-gradient-to-br ${selectedNode.type === NodeType.STUDENT ? 'from-indigo-500 to-blue-600' :
                                        selectedNode.type === NodeType.KNOWLEDGE ? 'from-emerald-500 to-teal-600' :
                                            'from-violet-500 to-purple-600'
                                        }`}>
                                        <div>
                                            <div className="flex items-center gap-2 opacity-90 mb-1">
                                                <span className="text-[10px] font-bold uppercase tracking-widest border border-white/30 px-1.5 py-0.5 rounded">
                                                    {selectedNode.type === NodeType.STUDENT ? 'STUDENT' : selectedNode.type === NodeType.KNOWLEDGE ? 'KNOWLEDGE' : 'TEACHER'}
                                                </span>
                                            </div>
                                            <h4 className="font-bold text-lg flex items-center gap-2 drop-shadow-sm">
                                                {selectedNode.type === NodeType.STUDENT && <User className="w-5 h-5" />}
                                                {selectedNode.type === NodeType.KNOWLEDGE && <Book className="w-5 h-5" />}
                                                {selectedNode.type === NodeType.TEACHER && <GraduationCap className="w-5 h-5" />}
                                                {selectedNode.name}
                                            </h4>
                                            <p className="text-white/80 text-xs mt-1 font-medium">
                                                {selectedNode.type === NodeType.STUDENT && `${selectedNode.studentProfile?.school} ${selectedNode.studentProfile?.grade}${selectedNode.studentProfile?.classId}`}
                                                {selectedNode.type === NodeType.KNOWLEDGE && selectedNode.knowledgeProfile?.category}
                                                {selectedNode.type === NodeType.TEACHER && "授课教师"}
                                            </p>
                                        </div>
                                        <button onClick={closeNodeDetail} className="text-white/60 hover:text-white bg-white/10 hover:bg-white/20 rounded-full p-1 transition-colors">
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>

                                    <div className="p-5 max-h-[calc(100vh-280px)] overflow-y-auto custom-scrollbar">
                                        {/* Student Profile Content */}
                                        {selectedNode.type === NodeType.STUDENT && selectedNode.studentProfile && (
                                            <>
                                                <div className="flex items-center gap-2 mb-4 pb-2 border-b border-slate-100">
                                                    <Activity className="w-4 h-4 text-indigo-500" />
                                                    <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider">认知维度分析</h5>
                                                </div>
                                                <div className="space-y-4">
                                                    {Object.entries(cognitiveLabels).map(([key, label]) => {
                                                        const attributeKey = key as keyof CognitiveAttributes;
                                                        const value = selectedNode.studentProfile![attributeKey];
                                                        return (
                                                            <div
                                                                key={key}
                                                                className="space-y-1.5 group relative cursor-help"
                                                                onMouseEnter={(e) => handleAttributeEnter(e, attributeKey, value)}
                                                                onMouseLeave={handleAttributeLeave}
                                                            >
                                                                <div className="flex justify-between text-xs text-slate-600">
                                                                    <span>{label}</span>
                                                                    <span className="font-bold text-slate-800">{value}/5</span>
                                                                </div>
                                                                <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                                                    <div
                                                                        className={`h-full rounded-full transition-all duration-500 ease-out ${value >= 4 ? 'bg-emerald-500' : value >= 3 ? 'bg-indigo-500' : 'bg-amber-500'} group-hover:brightness-95`}
                                                                        style={{ width: `${(value / 5) * 100}%` }}
                                                                    ></div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                                <div className="mt-5 p-3 bg-indigo-50 rounded-lg border border-indigo-100 flex gap-2 items-start">
                                                    <Lightbulb className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                                                    <p className="text-[10px] text-indigo-700 leading-relaxed">
                                                        提示：鼠标悬停在上方属性条上，可查看针对该维度的专家干预策略建议。
                                                    </p>
                                                </div>
                                            </>
                                        )}

                                        {/* Knowledge Profile Content */}
                                        {selectedNode.type === NodeType.KNOWLEDGE && selectedNode.knowledgeProfile && (
                                            <div className="space-y-5">
                                                <div>
                                                    <h5 className="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">知识点内容</h5>
                                                    <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100 shadow-sm">
                                                        {selectedNode.knowledgeProfile.content}
                                                    </p>
                                                </div>

                                                <div>
                                                    <h5 className="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">关联推荐资源</h5>
                                                    <div className="space-y-2">
                                                        {resources
                                                            .filter(r => r.relatedKnowledgeIds.includes(selectedNode.id))
                                                            .map(res => (
                                                                <div
                                                                    key={res.id}
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        handleResourceClick(res);
                                                                    }}
                                                                    className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/50 cursor-pointer transition-all group shadow-sm hover:shadow-md bg-white"
                                                                >
                                                                    <div className="p-1.5 rounded-md bg-slate-100 text-slate-400 group-hover:bg-emerald-100 group-hover:text-emerald-600 transition-colors">
                                                                        <LinkIcon className="w-3.5 h-3.5" />
                                                                    </div>
                                                                    <span className="text-xs font-medium text-slate-700 group-hover:text-emerald-800 truncate flex-1">
                                                                        {res.title}
                                                                    </span>
                                                                    {res.url && <ExternalLink className="w-3 h-3 text-slate-300" />}
                                                                </div>
                                                            ))
                                                        }
                                                        {resources.filter(r => r.relatedKnowledgeIds.includes(selectedNode.id)).length === 0 && (
                                                            <p className="text-xs text-slate-400 italic text-center py-4 bg-slate-50 rounded-lg border border-dashed border-slate-200">暂无相关资源</p>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Teacher Profile Content */}
                                        {selectedNode.type === NodeType.TEACHER && selectedNode.teacherProfile && (
                                            <div className="space-y-4">
                                                <div className="bg-gradient-to-r from-violet-50 to-indigo-50 p-4 rounded-xl border border-violet-100 italic text-violet-800 text-sm text-center font-medium shadow-sm">
                                                    "{selectedNode.teacherProfile.slogan}"
                                                </div>

                                                <div className="grid grid-cols-2 gap-3 text-xs">
                                                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                                        <span className="text-slate-400 block mb-1 scale-90 origin-top-left">工号</span>
                                                        <span className="font-semibold text-slate-700">{selectedNode.teacherProfile.employeeId}</span>
                                                    </div>
                                                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                                        <span className="text-slate-400 block mb-1 scale-90 origin-top-left">性别/年龄</span>
                                                        <span className="font-semibold text-slate-700">{selectedNode.teacherProfile.gender} / {selectedNode.teacherProfile.age}岁</span>
                                                    </div>
                                                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                                        <span className="text-slate-400 block mb-1 scale-90 origin-top-left">职称</span>
                                                        <span className="font-semibold text-slate-700">{selectedNode.teacherProfile.title}</span>
                                                    </div>
                                                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                                        <span className="text-slate-400 block mb-1 scale-90 origin-top-left">学科</span>
                                                        <span className="font-semibold text-slate-700">{selectedNode.teacherProfile.subject}</span>
                                                    </div>
                                                    <div className="col-span-2 p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                                                        <span className="text-slate-400 block mb-1 scale-90 origin-top-left">学校/班级</span>
                                                        <span className="font-semibold text-slate-700">{selectedNode.teacherProfile.school} {selectedNode.teacherProfile.teachingGrade}{selectedNode.teacherProfile.teachingClass}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </main>

                {/* Tooltip Portal */}
                {hoveredAttribute && tooltipPosition && (
                    <div
                        className="absolute z-50 w-80 bg-white/95 backdrop-blur-md p-4 rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.2)] border border-slate-100 ring-1 ring-slate-900/5 animate-in fade-in zoom-in-95 duration-200 pointer-events-none"
                        style={{
                            left: `${tooltipPosition.x}px`,
                            top: `${tooltipPosition.y}px`,
                            transform: 'translateY(-20%)'
                        }}
                    >
                        <div className="flex items-start gap-3 mb-3 pb-3 border-b border-slate-100">
                            <div className="p-1.5 bg-amber-50 rounded-lg text-amber-500">
                                <Lightbulb className="w-4 h-4" />
                            </div>
                            <div>
                                <h4 className="text-sm font-bold text-slate-800">
                                    {cognitiveLabels[hoveredAttribute.key]}
                                </h4>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded text-white ${hoveredAttribute.score >= 4 ? 'bg-emerald-500' : hoveredAttribute.score >= 3 ? 'bg-indigo-500' : 'bg-amber-500'}`}>
                                        {hoveredAttribute.score >= 4 ? '高水平' : hoveredAttribute.score >= 3 ? '中等水平' : '低水平'}
                                    </span>
                                    <span className="text-[10px] text-slate-400">专家干预策略</span>
                                </div>
                            </div>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-wrap">
                            {getStrategy(scenario, hoveredAttribute.key, hoveredAttribute.score)}
                        </p>
                    </div>
                )}

                {/* Right Resource Panel */}
                <aside className="w-80 bg-white border-l border-slate-200 flex flex-col shadow-[-4px_0_24px_-12px_rgba(0,0,0,0.05)] z-20">
                    <div className="p-5 border-b border-slate-100 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <BookOpen className="w-4 h-4 text-slate-400" />
                            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">资源中心</h2>
                        </div>
                        <span className="flex h-2 w-2 relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-slate-50/50">
                        {resources.map((res) => (
                            <div
                                key={res.id}
                                onClick={() => handleResourceClick(res)}
                                className={`group cursor-pointer rounded-xl border p-4 transition-all duration-300 relative overflow-hidden ${selectedResource === res.id
                                    ? 'border-indigo-500 bg-white shadow-lg shadow-indigo-100 scale-[1.02] ring-1 ring-indigo-500/20'
                                    : 'border-slate-200 hover:border-indigo-300 hover:shadow-md bg-white hover:-translate-y-0.5'
                                    }`}
                            >
                                {selectedResource === res.id && <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>}
                                <div className="flex justify-between items-start mb-2.5">
                                    <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-600 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                                        {res.type}
                                    </span>
                                    <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-100">
                                        <BarChart3 className="w-3 h-3" />
                                        <span className={res.accuracy > 90 ? 'text-emerald-600' : 'text-amber-600'}>接受度 {res.accuracy}%</span>
                                    </div>
                                </div>
                                <h3 className="text-sm font-bold text-slate-800 group-hover:text-indigo-600 mb-1.5 leading-tight transition-colors">
                                    {res.title}
                                </h3>
                                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-2">
                                    {res.description}
                                </p>
                                {selectedResource === res.id && (
                                    <div className="mt-3 pt-3 border-t border-indigo-50 animate-in fade-in duration-300">
                                        <div className="flex items-center gap-1 text-[10px] text-indigo-600 font-medium bg-indigo-50/50 p-1.5 rounded">
                                            <Layers className="w-3 h-3" />
                                            关联知识点: {res.relatedKnowledgeIds.join(', ')}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Gemini AI Analysis Section */}
                    <div className="p-5 bg-white border-t border-slate-200">
                        <div className="mb-3 flex items-center justify-between">
                            <h4 className="text-xs font-bold text-slate-400 uppercase flex items-center gap-2 tracking-wider">
                                <Wand2 className="w-3 h-3" /> AI 智能拓扑分析
                            </h4>
                        </div>

                        {aiAnalysis ? (
                            <div className="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-xl p-4 shadow-sm relative group">
                                <p className="text-xs text-slate-600 leading-relaxed font-medium">
                                    {aiAnalysis}
                                </p>
                                <button onClick={() => setAiAnalysis("")} className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-slate-200 rounded text-slate-400">
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        ) : (
                            <button
                                onClick={handleAIAnalyze}
                                disabled={isAnalyzing}
                                className="w-full py-2.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold rounded-xl shadow-lg shadow-slate-200 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed hover:translate-y-[-1px] active:translate-y-[1px]"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> 正在分析网络拓扑...
                                    </>
                                ) : (
                                    <>
                                        生成网络诊断报告
                                    </>
                                )}
                            </button>
                        )}
                    </div>
                </aside>
            </div>

            {/* Analysis Modal */}
            <AnalysisPanel
                isOpen={isAnalysisOpen}
                onClose={() => setIsAnalysisOpen(false)}
                data={graphData}
                resources={resources}
                defaultTab={analysisDefaultTab}
            />

        </div>
    );
};

export default App;