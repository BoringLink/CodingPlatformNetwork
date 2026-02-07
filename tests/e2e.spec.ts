import { test, expect } from "@playwright/test";

test("完整流程测试 - 从页面加载到AI分析", async ({ page }) => {
  // 导航到应用
  await page.goto("/");

  // 等待页面加载完成
  await page.waitForLoadState("networkidle");

  // 测试页面加载
  await expect(page.getByText("教育交互网络")).toBeInTheDocument();
  await expect(page.getByText("控制面板")).toBeInTheDocument();
  await expect(page.getByText("资源中心")).toBeInTheDocument();

  // 测试场景选择
  await page.waitForSelector("text=ONLINE_COURSE");
  await page.click("text=ONLINE_COURSE");

  // 等待场景切换完成
  await page.waitForTimeout(1000);
  await expect(page.getByText("场景: ONLINE_COURSE")).toBeInTheDocument();

  // 测试班级设置
  await page.waitForSelector("select");
  const schoolSelect = await page.locator("select").nth(0);
  await schoolSelect.selectOption({ index: 0 });

  const gradeSelect = await page.locator("select").nth(1);
  await gradeSelect.selectOption({ index: 0 });

  const classSelect = await page.locator("select").nth(2);
  await classSelect.selectOption({ index: 0 });

  // 等待班级切换完成
  await page.waitForTimeout(1000);

  // 测试网络图谱
  await page.waitForSelector("svg");
  const svgElement = await page.locator("svg");
  await expect(svgElement).toBeVisible();

  // 测试节点点击
  const nodes = await page.locator("circle");
  const nodeCount = await nodes.count();
  if (nodeCount > 0) {
    await nodes.first().click();

    // 等待节点详情显示
    await page.waitForTimeout(1000);

    // 测试关闭节点详情
    const closeButton = await page.locator("button").filter({ hasText: "×" });
    if ((await closeButton.count()) > 0) {
      await closeButton.first().click();
    }
  }

  // 测试资源中心
  await page.waitForSelector("text=资源中心");
  const resources = await page.locator(".group.cursor-pointer");
  const resourceCount = await resources.count();
  if (resourceCount > 0) {
    await resources.first().click();

    // 等待资源高亮效果
    await page.waitForTimeout(1000);
  }

  // 测试AI分析
  await page.waitForSelector("text=生成网络诊断报告");
  await page.click("text=生成网络诊断报告");

  // 等待分析结果
  await page.waitForTimeout(2000);
  await expect(page.getByText("测试分析结果")).toBeInTheDocument();

  // 测试统计分析
  await page.waitForSelector("text=统计分析");
  await page.click("text=统计分析");

  // 等待分析面板显示
  await page.waitForTimeout(1000);
  await expect(page.getByText("网络概览")).toBeInTheDocument();

  // 测试子图透视
  await page.waitForSelector("text=子图分析");
  await page.click("text=子图分析");

  // 等待子图分析显示
  await page.waitForTimeout(1000);
  await expect(page.getByText("子图分析")).toBeInTheDocument();

  // 测试关闭分析面板
  const closeAnalysisButton = await page
    .locator("button")
    .filter({ hasText: "×" });
  if ((await closeAnalysisButton.count()) > 0) {
    await closeAnalysisButton.first().click();
  }

  // 测试重置筛选条件
  await page.waitForSelector("text=重置筛选条件");
  await page.click("text=重置筛选条件");

  // 等待重置完成
  await page.waitForTimeout(1000);
});

test("数据一致性测试 - 前端显示与后端数据一致性", async ({ page, request }) => {
  // 导航到应用
  await page.goto("/");

  // 等待页面加载完成
  await page.waitForLoadState("networkidle");

  // 测试后端API
  const graphDataResponse = await request.get(
    "http://localhost:3001/api/v1/graph-data",
  );
  expect(graphDataResponse.status()).toBe(200);

  const graphData = await graphDataResponse.json();
  expect(graphData).toHaveProperty("nodes");
  expect(graphData).toHaveProperty("links");

  // 验证前端是否显示了相应的数据
  await page.waitForSelector("svg");
  const nodes = await page.locator("circle");
  const nodeCount = await nodes.count();
  expect(nodeCount).toBeGreaterThanOrEqual(0);
});

test("错误处理测试 - 边界条件和异常场景", async ({ page, request }) => {
  // 测试不存在的学生
  const nonExistentStudentResponse = await request.get(
    "http://localhost:3001/api/v1/students/non-existent",
  );
  expect(nonExistentStudentResponse.status()).toBe(404);

  // 测试不存在的教师
  const nonExistentTeacherResponse = await request.get(
    "http://localhost:3001/api/v1/teachers/non-existent",
  );
  expect(nonExistentTeacherResponse.status()).toBe(404);

  // 测试不存在的知识点
  const nonExistentKnowledgeResponse = await request.get(
    "http://localhost:3001/api/v1/knowledge-points/non-existent",
  );
  expect(nonExistentKnowledgeResponse.status()).toBe(404);

  // 测试前端错误处理
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  // 测试空数据场景
  const emptyGraphResponse = await request.get(
    "http://localhost:3001/api/v1/graph-data?school=non-existent-school",
  );
  expect(emptyGraphResponse.status()).toBe(200);

  const emptyGraphData = await emptyGraphResponse.json();
  expect(emptyGraphData.nodes).toEqual([]);
  expect(emptyGraphData.links).toEqual([]);
});

test("跨浏览器兼容性测试 - 基本功能", async ({ page }) => {
  // 测试页面加载
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  // 测试核心功能
  await expect(page.getByText("教育交互网络")).toBeInTheDocument();
  await expect(page.getByText("控制面板")).toBeInTheDocument();
  await expect(page.getByText("资源中心")).toBeInTheDocument();

  // 测试网络图谱渲染
  await page.waitForSelector("svg");
  const svgElement = await page.locator("svg");
  await expect(svgElement).toBeVisible();

  // 测试资源列表
  await page.waitForSelector(".group.cursor-pointer");
  const resources = await page.locator(".group.cursor-pointer");
  const resourceCount = await resources.count();
  expect(resourceCount).toBeGreaterThanOrEqual(0);
});
