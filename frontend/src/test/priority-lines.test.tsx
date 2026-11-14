import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { PriorityLines } from "@/components/samples/shared";

afterEach(cleanup);

describe("Priority lines", () => {
  it("fills all four lines red for critical priority", () => {
    render(<PriorityLines p="critical" />);
    const indicator = screen.getByRole("img", { name: "Critical priority: 4 of 4 lines filled" });

    expect(indicator.querySelectorAll(".bg-critical")).toHaveLength(4);
    expect(indicator.querySelectorAll(".bg-card")).toHaveLength(0);
  });

  it("fills three lines yellow and leaves one white for high priority", () => {
    render(<PriorityLines p="high" />);
    const indicator = screen.getByRole("img", { name: "High priority: 3 of 4 lines filled" });

    expect(indicator.querySelectorAll(".bg-high")).toHaveLength(3);
    expect(indicator.querySelectorAll(".bg-card")).toHaveLength(1);
  });

  it("fills two lines blue and leaves two white for medium priority", () => {
    render(<PriorityLines p="medium" />);
    const indicator = screen.getByRole("img", { name: "Medium priority: 2 of 4 lines filled" });

    expect(indicator.querySelectorAll(".bg-medium")).toHaveLength(2);
    expect(indicator.querySelectorAll(".bg-card")).toHaveLength(2);
  });

  it("fills one line lime green and leaves three white for low priority", () => {
    render(<PriorityLines p="low" />);
    const indicator = screen.getByRole("img", { name: "Low priority: 1 of 4 lines filled" });

    expect(indicator.querySelectorAll(".bg-low")).toHaveLength(1);
    expect(indicator.querySelectorAll(".bg-card")).toHaveLength(3);
  });
});
