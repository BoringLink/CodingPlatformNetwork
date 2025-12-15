# 教育知识图谱系统 - 前端

基于 Next.js 15 的教育知识图谱可视化前端应用。

## 技术栈

- **框架**: Next.js 16.0.6 (React 19)
- **语言**: TypeScript 5.x
- **样式**: Tailwind CSS 4.0
- **UI 组件**: shadcn/ui
- **状态管理**: Zustand 5.x
- **数据获取**: TanStack Query v5
- **图可视化**: Cytoscape.js 3.33 + react-cytoscapejs

## 项目结构

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── ui/               # shadcn/ui 组件
│   └── providers/        # Context Providers
├── hooks/                # 自定义 Hooks
│   └── use-graph-data.ts # 图数据查询 Hooks
├── lib/                  # 工具函数
│   ├── utils.ts         # 通用工具
│   └── api-client.ts    # API 客户端
├── store/               # Zustand 状态管理
│   ├── graph-store.ts   # 图状态
│   └── ui-store.ts      # UI 状态
├── types/               # TypeScript 类型定义
│   └── api.ts          # API 类型
└── public/             # 静态资源

```

## 开发指南

### 安装依赖

```bash
npm install
```

### 环境变量

复制 `.env.local.example` 到 `.env.local` 并配置：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 启动开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000)

### 构建生产版本

```bash
npm run build
npm start
```

### 代码检查

```bash
npm run lint
```

## 核心功能模块

### 1. 状态管理 (Zustand)

#### Graph Store
管理图谱数据和选择状态：
- 节点和边数据
- 选中的节点
- 高亮的节点
- 筛选条件
- 当前子视图

```typescript
import { useGraphStore } from "@/store/graph-store";

function MyComponent() {
  const { nodes, setSelectedNode } = useGraphStore();
  // ...
}
```

#### UI Store
管理 UI 状态：
- 主题设置
- 侧边栏状态
- 筛选面板状态
- 加载状态

```typescript
import { useUIStore } from "@/store/ui-store";

function MyComponent() {
  const { theme, toggleSidebar } = useUIStore();
  // ...
}
```

### 2. 数据获取 (TanStack Query)

使用自定义 Hooks 获取数据：

```typescript
import { useNodes, useVisualization } from "@/hooks/use-graph-data";

function GraphView() {
  const { data: nodes, isLoading } = useNodes();
  const { data: vizData } = useVisualization();
  // ...
}
```

### 3. API 客户端

统一的 API 调用接口：

```typescript
import { apiClient } from "@/lib/api-client";

// GET 请求
const nodes = await apiClient.get("/api/nodes", { type: "Student" });

// POST 请求
const result = await apiClient.post("/api/subviews", { name: "My View" });
```

### 4. UI 组件 (shadcn/ui)

使用预构建的 UI 组件：

```typescript
import { Button } from "@/components/ui/button";

function MyComponent() {
  return (
    <Button variant="outline" size="lg">
      点击我
    </Button>
  );
}
```

## 添加新的 shadcn/ui 组件

shadcn/ui 组件需要手动添加到项目中。使用以下命令：

```bash
npx shadcn@latest add [component-name]
```

例如：
```bash
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

## 性能优化

- 使用 React Server Components (RSC) 减少客户端 JavaScript
- TanStack Query 自动缓存和重新验证
- Zustand persist 中间件持久化状态
- Next.js 自动代码分割和优化

## 开发规范

### 组件命名
- 使用 PascalCase: `GraphVisualization.tsx`
- 文件名与组件名一致

### 类型定义
- 所有 API 响应都有类型定义在 `types/api.ts`
- 使用 TypeScript 严格模式

### 样式
- 优先使用 Tailwind CSS 类
- 使用 `cn()` 工具函数合并类名
- 遵循 shadcn/ui 的设计系统

### 状态管理
- 全局状态使用 Zustand
- 服务端状态使用 TanStack Query
- 本地组件状态使用 React useState

## 待实现功能

根据任务列表，以下功能待实现：

- [ ] 图可视化组件 (Cytoscape.js)
- [ ] 交互功能（悬停、点击、高亮）
- [ ] 筛选和子视图 UI
- [ ] 数据导入 UI
- [ ] 报告展示 UI
- [ ] 响应式设计和暗色模式

## 相关文档

- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [shadcn/ui 文档](https://ui.shadcn.com)
- [TanStack Query 文档](https://tanstack.com/query/latest)
- [Zustand 文档](https://zustand-demo.pmnd.rs)
- [Cytoscape.js 文档](https://js.cytoscape.org)
