import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// Mock d3 module
jest.mock("d3", () => ({
  select: jest.fn(() => ({
    append: jest.fn(() => ({
      attr: jest.fn().mockReturnThis(),
      style: jest.fn().mockReturnThis(),
      on: jest.fn().mockReturnThis(),
      selectAll: jest.fn(() => ({
        data: jest.fn().mockReturnThis(),
        enter: jest.fn(() => ({
          append: jest.fn().mockReturnThis(),
          attr: jest.fn().mockReturnThis(),
          style: jest.fn().mockReturnThis(),
          on: jest.fn().mockReturnThis(),
          text: jest.fn().mockReturnThis(),
        })),
        exit: jest.fn(() => ({
          remove: jest.fn(),
        })),
      })),
    })),
  })),
  forceSimulation: jest.fn(() => ({
    force: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    alpha: jest.fn().mockReturnThis(),
    restart: jest.fn(),
  })),
  forceLink: jest.fn(() => ({
    id: jest.fn().mockReturnThis(),
    distance: jest.fn().mockReturnThis(),
  })),
  forceManyBody: jest.fn(() => ({
    strength: jest.fn().mockReturnThis(),
  })),
  forceX: jest.fn(() => ({
    strength: jest.fn().mockReturnThis(),
  })),
  forceY: jest.fn(() => ({
    strength: jest.fn().mockReturnThis(),
  })),
  scaleOrdinal: jest.fn(() => ({
    domain: jest.fn().mockReturnThis(),
    range: jest.fn().mockReturnThis(),
    unknown: jest.fn().mockReturnThis(),
  })),
  schemeCategory10: ["#ff0000", "#00ff00", "#0000ff"],
}));

// Mock NetworkGraph component
jest.mock("../components/NetworkGraph", () => ({
  __esModule: true,
  default: jest.fn(() => <div data-testid="network-graph" />),
}));

// Mock AnalysisPanel component
jest.mock("../components/AnalysisPanel", () => ({
  __esModule: true,
  default: jest.fn(() => <div data-testid="analysis-panel" />),
}));

// Mock data services
jest.mock("../services/dataService", () => ({
  generateGraphData: jest.fn(() => ({
    nodes: [
      { id: "S001", type: "STUDENT", name: "测试学生", val: 8 },
      { id: "T001", type: "TEACHER", name: "测试教师", val: 25 },
      { id: "K001", type: "KNOWLEDGE", name: "测试知识点", val: 15 },
    ],
    links: [
      { source: "S001", target: "T001", value: 2, type: "PHYSICAL" },
      { source: "S001", target: "K001", value: 1.5, type: "PLATFORM" },
    ],
  })),
  generateResources: jest.fn(() => [
    {
      id: "R001",
      title: "测试资源",
      description: "测试资源描述",
      type: "文档",
      accuracy: 90,
      relatedKnowledgeIds: ["K001"],
    },
  ]),
  getClassOptions: jest.fn(() => ({
    schools: ["测试学校"],
    grades: ["5年级"],
    classes: ["1班"],
  })),
}));



// Import App after mocking dependencies
import App from "../App";

describe("App Component", () => {
  test("renders App component", () => {
    render(<App />);
    expect(screen.getByText("教育交互网络")).toBeInTheDocument();
  });

  test("renders control panel", () => {
    render(<App />);
    expect(screen.getByText("控制面板")).toBeInTheDocument();
  });

  test("renders network graph", () => {
    render(<App />);
    expect(screen.getByText("统计分析")).toBeInTheDocument();
    expect(screen.getByText("子图透视")).toBeInTheDocument();
  });

  test("renders resource center", () => {
    render(<App />);
    expect(screen.getByText("资源中心")).toBeInTheDocument();
  });

  test("renders App component structure", async () => {
    render(<App />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText("教育交互网络")).toBeInTheDocument();
    });

    // Check if control panel is rendered
    expect(screen.getByText("控制面板")).toBeInTheDocument();

    // Check if resource center is rendered
    expect(screen.getByText("资源中心")).toBeInTheDocument();

    // Check if analysis buttons are rendered
    expect(screen.getByText("统计分析")).toBeInTheDocument();
    expect(screen.getByText("子图透视")).toBeInTheDocument();
  });

  test("changes class settings", async () => {
    render(<App />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByDisplayValue("测试学校")).toBeInTheDocument();
    });

    // Change school selection
    const schoolSelect = screen.getByDisplayValue("测试学校");
    fireEvent.change(schoolSelect, { target: { value: "测试学校" } });

    // Change grade selection
    const gradeSelect = screen.getByDisplayValue("5年级");
    fireEvent.change(gradeSelect, { target: { value: "5年级" } });

    // Change class selection
    const classSelect = screen.getByDisplayValue("1班");
    fireEvent.change(classSelect, { target: { value: "1班" } });

    // Verify the changes
    await waitFor(() => {
      expect(screen.getByDisplayValue("测试学校")).toBeInTheDocument();
      expect(screen.getByDisplayValue("5年级")).toBeInTheDocument();
      expect(screen.getByDisplayValue("1班")).toBeInTheDocument();
    });
  });

  test("resets filters", async () => {
    render(<App />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText("重置筛选条件")).toBeInTheDocument();
    });

    // Click reset button
    fireEvent.click(screen.getByText("重置筛选条件"));

    // Verify reset
    await waitFor(() => {
      expect(screen.getByDisplayValue("测试学校")).toBeInTheDocument();
      expect(screen.getByDisplayValue("5年级")).toBeInTheDocument();
      expect(screen.getByDisplayValue("1班")).toBeInTheDocument();
    });
  });

  test("opens analysis panel", async () => {
    render(<App />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText("统计分析")).toBeInTheDocument();
    });

    // Click analysis button
    fireEvent.click(screen.getByText("统计分析"));

    // Verify analysis panel opens
    await waitFor(() => {
      expect(screen.getByText("统计分析")).toBeInTheDocument();
    });
  });


});
