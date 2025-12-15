## 修改计划

### 1. 移除无效样式定义
- **目标**：删除所有包含`:hover`伪类和`cursor`属性的样式规则
- **修改位置**：
  - 移除第429-442行的`:hover`样式规则（node:hover和edge:hover）
  - 确保所有样式定义中不再包含`cursor`属性

### 2. 重构高亮逻辑
- **目标**：替换使用`:not(.highlighted)`选择器的样式规则，改为通过JavaScript动态添加/移除`.faded`类
- **修改内容**：
  - 移除第415-426行的`:not(.highlighted)`样式规则
  - 添加新的`.faded`类样式定义，用于设置非高亮元素的透明度
  - 修改高亮逻辑，在激活高亮模式时为非高亮节点添加`.faded`类

### 3. 实现JavaScript悬停交互
- **目标**：通过事件监听器实现悬停效果，替代CSS伪类
- **修改内容**：
  - 扩展`handleMouseOver`函数，添加动态cursor样式修改和.hovered类添加
  - 扩展`handleMouseOut`函数，恢复默认cursor样式和移除.hovered类
  - 在事件回调中操作DOM容器的cursor样式

### 4. 具体修改步骤

#### 步骤1：修改样式定义（cyStyles）
- 添加`.faded`类样式规则
- 移除`:hover`和`:not(.highlighted)`相关样式

#### 步骤2：扩展悬停事件处理
- 更新`handleMouseOver`函数：
  ```javascript
  const handleMouseOver = (event: cytoscape.EventObject) => {
    const target = event.target;
    const cy = cytoscapeRef.current?.cy;
    if (cy) {
      const container = cy.container();
      container.style.cursor = 'pointer';
    }
    if (target.isNode()) {
      onNodeHover?.(target.id());
      target.addClass('hovered');
    }
  };
  ```

- 更新`handleMouseOut`函数：
  ```javascript
  const handleMouseOut = () => {
    const cy = cytoscapeRef.current?.cy;
    if (cy) {
      const container = cy.container();
      container.style.cursor = 'default';
    }
    onNodeHover?.(null);
    cy?.elements().removeClass('hovered');
  };
  ```

#### 步骤3：重构高亮逻辑
- 修改高亮相关的useEffect，添加.faded类管理：
  ```javascript
  useEffect(() => {
    const cy = cytoscapeRef.current?.cy;
    if (!cy) return;

    // Remove all highlighted and faded classes
    cy.elements().removeClass('highlighted faded');

    if (highlightedNodeIds.length > 0) {
      // Highlight specified nodes
      highlightedNodeIds.forEach((nodeId) => {
        const node = cy.getElementById(nodeId);
        if (node.length > 0) {
          node.addClass('highlighted');
        }
      });

      // Highlight edges that connect highlighted nodes
      highlightedNodeIds.forEach((sourceId) => {
        const sourceNode = cy.getElementById(sourceId);
        if (sourceNode.length > 0) {
          const connectedEdges = sourceNode.connectedEdges();
          connectedEdges.forEach((edge: EdgeSingular) => {
            const targetId = edge.target().id();
            if (highlightedNodeIds.includes(targetId)) {
              edge.addClass('highlighted');
            }
          });
        }
      });

      // Add faded class to non-highlighted, non-selected elements
      cy.nodes().not('.highlighted').not(':selected').addClass('faded');
      cy.edges().not('.highlighted').addClass('faded');
    }
  }, [highlightedNodeIds]);
  ```

#### 步骤4：添加.faded类样式
- 在cyStyles中添加：
  ```javascript
  // Faded elements (non-highlighted)
  {
    selector: 'node.faded',
    style: {
      opacity: 0.3,
    },
  },
  {
    selector: 'edge.faded',
    style: {
      opacity: 0.2,
    },
  },
  ```

### 5. 测试与验证
- **编译测试**：确保项目能够成功编译，无语法错误
- **功能测试**：验证悬停效果和高亮功能正常工作
- **警告检查**：确保在各种交互场景下均不会出现Cytoscape相关警告信息
- **组件测试**：执行全面的组件测试，确保所有测试用例通过

## 预期效果
- ✅ 消除所有Cytoscape选择器和样式属性相关警告
- ✅ 保持原有的视觉效果和交互体验
- ✅ 提高代码的可维护性和兼容性
- ✅ 确保在各种浏览器和Cytoscape版本下正常工作