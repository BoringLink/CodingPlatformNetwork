declare module "react-cytoscapejs" {
  import React from "react";
  import {
    Core,
    ElementDefinition,
    LayoutOptions,
    StylesheetJsonBlock,
  } from "cytoscape";

  interface CytoscapeComponentProps {
    /**
     * 图元素数组（节点和边）。
     * 注意：react-cytoscapejs 要求这是一个扁平的数组，而不是 {nodes, edges} 对象。
     */
    elements: ElementDefinition[];

    /**
     * 样式表配置
     */
    stylesheet?: StylesheetJsonBlock[] | any; // 允许更宽松的样式定义以兼容不同版本

    /**
     * 布局配置
     */
    layout?: LayoutOptions;

    /**
     * 获取 Cytoscape 核心实例的回调函数
     */
    cy?: (cy: Core) => void;

    /**
     * 容器的类名
     */
    className?: string;

    /**
     * 容器的内联样式
     */
    style?: React.CSSProperties;

    /**
     * 事件监听器
     */
    events?: {
      [key: string]: (event: any) => void;
    };

    /**
     * 初始缩放级别
     */
    zoom?: number;
    /**
     * 初始平移位置
     */
    pan?: { x: number; y: number };
    /**
     * 最小缩放级别
     */
    minZoom?: number;
    /**
     * 最大缩放级别
     */
    maxZoom?: number;
    /**
     * 是否启用缩放
     */
    zoomingEnabled?: boolean;
    /**
     * 是否启用用户缩放
     */
    userZoomingEnabled?: boolean;
    /**
     * 是否启用框选
     */
    boxSelectionEnabled?: boolean;
    /**
     * 是否自动 ungrabify 元素
     */
    autoungrabify?: boolean;
    /**
     * 是否自动 unselectify 元素
     */
    autounselectify?: boolean;
  }

  // 组件引用的接口（如果使用了 ref 转发）
  interface CytoscapeRef {
    cy: Core | null;
  }

  const CytoscapeComponent: React.ForwardRefExoticComponent<
    CytoscapeComponentProps & React.RefAttributes<CytoscapeRef>
  >;

  export default CytoscapeComponent;
}
