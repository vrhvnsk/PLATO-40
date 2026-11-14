import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { IncidentTimeline } from "@/components/samples/IncidentTimeline";
import { decisions, type Decision, type Priority } from "@/lib/sample-decisions";

afterEach(cleanup);

function incident(index: number, priority: Priority, issueType: string, day: number): Decision {
  return {
    event_id: `event-test-${index}`,
    timestamp_utc: `2026-03-${String(day).padStart(2, "0")} 09:0${index}`,
    episode_id: "ep-test",
    issue_type: issueType,
    priority,
    action: "Mock action",
    requires_human_approval: false,
    reason: "Test reason",
    evidence: [],
    confidence: 0.9,
    verification_plan: "Test plan",
  };
}

describe("Incident timeline", () => {
  it("labels the yearly view 2026 and provides all twelve month controls", () => {
    render(<IncidentTimeline incidents={decisions} />);

    expect(screen.getByRole("heading", { name: "2026" })).toBeInTheDocument();
    [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ].forEach((month) => {
      expect(screen.getByRole("button", { name: `Show ${month} 2026` })).toBeInTheDocument();
    });
  });

  it("shows Monday-to-Sunday days and changes the selected week with the arrows", () => {
    render(<IncidentTimeline incidents={decisions} />);
    fireEvent.click(screen.getByRole("button", { name: "Show March 2026" }));
    fireEvent.click(screen.getByRole("button", { name: /^week$/i }));

    expect(screen.getByText("23 Feb – 1 Mar 2026")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous week" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Next week" }));

    expect(screen.getByText("2–8 March 2026")).toBeInTheDocument();
    expect(screen.getByText("Mon · 2 Mar")).toBeInTheDocument();
    expect(screen.getByText("Sun · 8 Mar")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous week" })).toBeEnabled();
  });

  it("leaves all twelve months unselected in year view, including after returning from March", () => {
    render(<IncidentTimeline incidents={decisions} />);
    const months = within(screen.getByLabelText("Months in 2026"));
    const assertUnselected = () => {
      const controls = months.getAllByRole("button");
      expect(controls).toHaveLength(12);
      controls.forEach((control) => expect(control).toHaveAttribute("aria-pressed", "false"));
    };

    assertUnselected();
    fireEvent.click(months.getByRole("button", { name: "Show March 2026" }));
    expect(months.getByRole("button", { name: "Show March 2026" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    fireEvent.click(screen.getByRole("button", { name: /^year$/i }));
    assertUnselected();
    fireEvent.click(screen.getByRole("button", { name: /^month$/i }));
    expect(months.getByRole("button", { name: "Show March 2026" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("reaches the final March week and stops at the month boundary", () => {
    render(<IncidentTimeline incidents={decisions} />);
    fireEvent.click(screen.getByRole("button", { name: "Show March 2026" }));
    fireEvent.click(screen.getByRole("button", { name: /^week$/i }));

    for (let index = 0; index < 5; index += 1) {
      fireEvent.click(screen.getByRole("button", { name: "Next week" }));
    }

    expect(screen.getByText("30 Mar – 5 Apr 2026")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next week" })).toBeDisabled();
  });

  it("colors incident types and incident counts by priority", () => {
    const list = [
      incident(1, "critical", "water_leak", 4),
      incident(2, "low", "hvac_drift", 4),
      incident(3, "medium", "energy_spike", 5),
      incident(4, "high", "gas_leak", 6),
    ];
    render(<IncidentTimeline incidents={list} />);

    const marchBar = screen.getByRole("button", { name: "Open March 2026: 4 incidents" });
    expect(within(marchBar).getByText("4")).toHaveClass("text-critical-text");
    expect(marchBar.querySelector("span[style]")).toHaveClass("bg-critical/80");

    fireEvent.click(screen.getByRole("button", { name: "Show March 2026" }));

    const march4Cell = screen.getByRole("button", { name: "Open week containing 4 March 2026" });
    expect(within(march4Cell).getByText("2")).toHaveClass("text-critical-text");

    const march6Cell = screen.getByRole("button", { name: "Open week containing 6 March 2026" });
    expect(within(march6Cell).getByText("1")).toHaveClass("text-high-text");

    fireEvent.click(screen.getByRole("button", { name: /^week$/i }));
    fireEvent.click(screen.getByRole("button", { name: "Next week" }));

    const wednesdayCard = screen.getByText("Wed · 4 Mar").closest("article");
    if (!wednesdayCard) throw new Error("Wednesday incident card is missing");
    const wednesday = within(wednesdayCard);
    expect(wednesday.getByText("2")).toHaveClass("text-critical-text");
    expect(wednesday.getByText("water leak")).toHaveClass("text-critical-text");
    expect(wednesday.getByText("hvac drift")).toHaveClass("text-low-text");

    const thursdayCard = screen.getByText("Thu · 5 Mar").closest("article");
    if (!thursdayCard) throw new Error("Thursday incident card is missing");
    const thursday = within(thursdayCard);
    expect(thursday.getByText("1")).toHaveClass("text-medium-text");
    expect(thursday.getByText("energy spike")).toHaveClass("text-medium-text");

    const fridayCard = screen.getByText("Fri · 6 Mar").closest("article");
    if (!fridayCard) throw new Error("Friday incident card is missing");
    const friday = within(fridayCard);
    expect(friday.getByText("1")).toHaveClass("text-high-text");
    expect(friday.getByText("gas leak")).toHaveClass("text-high-text");
  });
});
