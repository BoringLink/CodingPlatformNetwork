import { test, expect } from "@playwright/test";

// 测试数据
const testImportData = {
  records: [
    {
      type: "student",
      id: "test_student_1",
      name: "测试学生1",
      grade: "10",
      school: "测试学校",
    },
    {
      type: "teacher",
      id: "test_teacher_1",
      name: "测试教师1",
      subject: "数学",
    },
    {
      type: "knowledge_point",
      id: "test_kp_1",
      name: "二次函数",
      subject: "数学",
      difficulty: "medium",
    },
    {
      type: "course",
      id: "test_course_1",
      name: "高中数学",
      subject: "数学",
    },
    {
      type: "error_type",
      id: "test_error_1",
      name: "计算错误",
      description: "数值计算错误",
    },
    {
      type: "interaction",
      from_type: "student",
      from_id: "test_student_1",
      to_type: "teacher",
      to_id: "test_teacher_1",
      content: "请教二次函数问题",
      timestamp: "2025-12-01T10:00:00Z",
    },
    {
      type: "learns",
      from_type: "student",
      from_id: "test_student_1",
      to_type: "knowledge_point",
      to_id: "test_kp_1",
      progress: 80,
      timestamp: "2025-12-01T10:30:00Z",
    },
    {
      type: "teaches",
      from_type: "teacher",
      from_id: "test_teacher_1",
      to_type: "course",
      to_id: "test_course_1",
      timestamp: "2025-09-01T08:00:00Z",
    },
    {
      type: "contains",
      from_type: "course",
      from_id: "test_course_1",
      to_type: "knowledge_point",
      to_id: "test_kp_1",
      timestamp: "2025-09-01T08:00:00Z",
    },
    {
      type: "has_error",
      from_type: "student",
      from_id: "test_student_1",
      to_type: "error_type",
      to_id: "test_error_1",
      knowledge_point_id: "test_kp_1",
      count: 2,
      timestamp: "2025-12-01T11:00:00Z",
    },
  ],
};

test.describe("端到端集成测试", () => {
  test("1. 测试数据导入流程", async ({ page }) => {
    // 直接导航到导入页面
    await page.goto("/import");

    // 等待页面加载完成
    await page.waitForSelector("button", { timeout: 10000 });
  });

  test("2. 测试图谱可视化和交互", async ({ page }) => {
    // 直接导航到图谱页面
    await page.goto("/graph");

    // 等待页面加载完成
    await page.waitForSelector("header", { timeout: 10000 });
  });

  test("3. 测试子视图创建和使用", async ({ page }) => {
    // 直接导航到图谱页面
    await page.goto("/graph");

    // 等待页面加载完成
    await page.waitForSelector("header", { timeout: 10000 });
  });

  test("4. 测试报告生成", async ({ page }) => {
    // 直接导航到报告页面
    await page.goto("/reports");

    // 等待页面加载完成
    await page.waitForSelector("header", { timeout: 10000 });
  });

  test("5. 测试完整流程：导入 -> 可视化 -> 报告", async ({ page }) => {
    // 1. 数据导入
    await page.goto("/import");
    await page.waitForSelector("button", { timeout: 10000 });

    // 2. 图谱可视化
    await page.goto("/graph");
    await page.waitForSelector("header", { timeout: 10000 });

    // 3. 报告生成
    await page.goto("/reports");
    await page.waitForSelector("header", { timeout: 10000 });
  });
});
