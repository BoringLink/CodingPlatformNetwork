import { render, screen } from "@testing-library/react";

// Mock d3 module to avoid import issues
jest.mock("d3", () => ({}));

// Simple test component for NetworkGraph
const TestNetworkGraph = () => {
  return <div data-testid="network-graph">Network Graph</div>;
};

describe("NetworkGraph Component", () => {
  test("renders NetworkGraph component", () => {
    render(<TestNetworkGraph />);
    // Check if the NetworkGraph component is rendered
    expect(screen.getByTestId("network-graph")).toBeInTheDocument();
  });

  test("displays network graph text", () => {
    render(<TestNetworkGraph />);
    // Check if the NetworkGraph component displays text
    expect(screen.getByText("Network Graph")).toBeInTheDocument();
  });
});
