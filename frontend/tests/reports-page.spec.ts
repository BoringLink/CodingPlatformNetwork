import { test, expect } from "@playwright/test";

test.describe("Reports Page", () => {
  test.beforeEach(async ({ page }) => {
    // Start from the home page
    await page.goto("/");
  });

  test("should navigate to reports page without crashing", async ({ page }) => {
    // Mock the API response to return valid data with correct format
    await page.route("**/api/reports", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: {
            graphStatistics: {
              totalNodes: 100,
              nodesByType: {
                Student: 50,
                Teacher: 10,
                Course: 20,
                KnowledgePoint: 15,
                ErrorType: 5,
              },
              totalRelationships: 200,
              relationshipsByType: {
                CHAT_WITH: 80,
                TEACHES: 20,
                LEARNS: 60,
                CONTAINS: 30,
                HAS_ERROR: 10,
              },
            },
            studentPerformance: {
              highFrequencyErrors: [],
              studentsNeedingAttention: [],
            },
            courseEffectiveness: {
              courseMetrics: [],
            },
            interactionPatterns: {
              activeCommunities: [],
              isolatedStudents: [],
            },
            generatedAt: new Date().toISOString(),
          },
        }),
      });
    });

    // Click the "了解更多" button
    await page.getByRole("link", { name: "了解更多" }).click();

    // Wait for the page to load
    await expect(page).toHaveURL("/reports");

    // Wait for the page to render
    await page.waitForTimeout(1000);

    // Verify the page doesn't crash by checking if the main container exists
    await expect(page.locator("body")).toBeVisible();

    // Verify that the report statistics component is rendered
    await expect(page.getByText("Graph Statistics")).toBeVisible();
  });

  test("should handle empty report data gracefully", async ({ page }) => {
    // Mock the API response to return empty data with correct format
    await page.route("**/api/reports", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: {
            graphStatistics: {},
            studentPerformance: {},
            courseEffectiveness: {},
            interactionPatterns: {},
            generatedAt: new Date().toISOString(),
          },
        }),
      });
    });

    // Click the "了解更多" button
    await page.getByRole("link", { name: "了解更多" }).click();

    // Wait for the page to load
    await expect(page).toHaveURL("/reports");

    // Wait for the page to render
    await page.waitForTimeout(1000);

    // Verify the page doesn't crash by checking if the main container exists
    await expect(page.locator("body")).toBeVisible();
  });

  test("should handle missing graphStatistics gracefully", async ({ page }) => {
    // Mock the API response to return missing graphStatistics with correct format
    await page.route("**/api/reports", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: {
            studentPerformance: {
              highFrequencyErrors: [],
              studentsNeedingAttention: [],
            },
            courseEffectiveness: {
              courseMetrics: [],
            },
            interactionPatterns: {
              activeCommunities: [],
              isolatedStudents: [],
            },
            generatedAt: new Date().toISOString(),
          },
        }),
      });
    });

    // Click the "了解更多" button
    await page.getByRole("link", { name: "了解更多" }).click();

    // Wait for the page to load
    await expect(page).toHaveURL("/reports");

    // Wait for the page to render
    await page.waitForTimeout(1000);

    // Verify the page doesn't crash by checking if the main container exists
    await expect(page.locator("body")).toBeVisible();
  });

  test("should handle malformed report data gracefully", async ({ page }) => {
    // Mock the API response to return malformed data with correct format
    await page.route("**/api/reports", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          success: true,
          data: {
            graphStatistics: {
              totalNodes: 100,
              // Missing nodesByType
              totalRelationships: 200,
              relationshipsByType: {},
            },
            studentPerformance: null,
            courseEffectiveness: undefined,
            interactionPatterns: {},
            generatedAt: new Date().toISOString(),
          },
        }),
      });
    });

    // Click the "了解更多" button
    await page.getByRole("link", { name: "了解更多" }).click();

    // Wait for the page to load
    await expect(page).toHaveURL("/reports");

    // Wait for the page to render
    await page.waitForTimeout(1000);

    // Verify the page doesn't crash by checking if the main container exists
    await expect(page.locator("body")).toBeVisible();
  });
});
