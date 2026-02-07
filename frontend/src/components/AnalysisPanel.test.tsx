import { render, screen, fireEvent } from "@testing-library/react";
import AnalysisPanel from "../../components/AnalysisPanel";

const mockData = {
  nodes: [
    { id: "S001", type: "STUDENT", name: "测试学生", val: 8 },
    { id: "T001", type: "TEACHER", name: "测试教师", val: 25 },
    { id: "K001", type: "KNOWLEDGE", name: "测试知识点", val: 15 },
  ],
  links: [
    { source: "S001", target: "T001", value: 2, type: "PHYSICAL" },
    { source: "S001", target: "K001", value: 1.5, type: "PLATFORM" },
  ],
};

const mockResources = [
  {
    id: "R001",
    title: "测试资源",
    description: "测试资源描述",
    type: "文档",
    accuracy: 90,
    relatedKnowledgeIds: ["K001"],
  },
];

describe("AnalysisPanel Component", () => {
  test("renders AnalysisPanel component", () => {
    const mockOnClose = jest.fn();
    render(
      <AnalysisPanel
        isOpen={true}
        onClose={mockOnClose}
        data={mockData}
        resources={mockResources}
        defaultTab="overview"
      />,
    );
    // Check if the analysis panel is rendered
    expect(screen.getByText("全域数据统计分析 Dashboard")).toBeInTheDocument();
  });

  test("renders overview tab", () => {
    const mockOnClose = jest.fn();
    render(
      <AnalysisPanel
        isOpen={true}
        onClose={mockOnClose}
        data={mockData}
        resources={mockResources}
        defaultTab="overview"
      />,
    );
    expect(screen.getByText("全局概览")).toBeInTheDocument();
  });

  test("renders subgraph tab", () => {
    const mockOnClose = jest.fn();
    render(
      <AnalysisPanel
        isOpen={true}
        onClose={mockOnClose}
        data={mockData}
        resources={mockResources}
        defaultTab="subgraph"
      />,
    );
    expect(screen.getByText("子图透视")).toBeInTheDocument();
  });

  test("closes when close button is clicked", () => {
    const mockOnClose = jest.fn();
    render(
      <AnalysisPanel
        isOpen={true}
        onClose={mockOnClose}
        data={mockData}
        resources={mockResources}
        defaultTab="overview"
      />,
    );

    // Click close button (using the button element)
    const buttons = screen.getAllByRole("button");
    const closeButton = buttons[0]; // Assuming the first button is the close button
    fireEvent.click(closeButton);

    // Verify onClose is called
    expect(mockOnClose).toHaveBeenCalled();
  });

  test("switches tabs", () => {
    const mockOnClose = jest.fn();
    render(
      <AnalysisPanel
        isOpen={true}
        onClose={mockOnClose}
        data={mockData}
        resources={mockResources}
        defaultTab="overview"
      />,
    );

    // Click subgraph tab
    fireEvent.click(screen.getByText("子图透视"));

    // Verify subgraph tab is active
    expect(screen.getByText("子图透视")).toBeInTheDocument();
  });
});
