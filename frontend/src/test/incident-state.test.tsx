import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { useState } from "react";
import { IncidentProvider, useIncidentState } from "@/components/dashboard/IncidentState";

afterEach(cleanup);

function StateProbe() {
  const state = useIncidentState();
  return (
    <>
      <output data-testid="event">{state.d?.event_id}</output>
      <output data-testid="approved">{String(Boolean(state.approved["event-1001"]))}</output>
      <output data-testid="consent">{String(Boolean(state.consent["event-1001"]))}</output>
      <button onClick={() => state.setId("event-1001")}>Select</button>
      <button onClick={() => state.setApproval("event-1001", true)}>Approve</button>
      <button onClick={() => state.setConsent("event-1001", true)}>Consent</button>
    </>
  );
}

function NavigationProbe() {
  const [page, setPage] = useState("selection");
  return (
    <IncidentProvider>
      <button
        onClick={() => setPage((current) => (current === "selection" ? "review" : "selection"))}
      >
        Change page
      </button>
      <StateProbe key={page} />
    </IncidentProvider>
  );
}

describe("Shared sample incident state", () => {
  it("keeps the selected event when a section unmounts and the next section opens", async () => {
    render(<NavigationProbe />);

    await waitFor(() => {
      expect(screen.getByTestId("event")).toHaveTextContent("event-1000");
    });

    fireEvent.click(screen.getByRole("button", { name: "Select" }));
    fireEvent.click(screen.getByRole("button", { name: "Change page" }));

    expect(screen.getByTestId("event")).toHaveTextContent("event-1001");
  });

  it("keeps simulated human approval when switching sections", () => {
    render(<NavigationProbe />);
    expect(screen.getByTestId("approved").textContent).toBe("false");
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    fireEvent.click(screen.getByRole("button", { name: "Change page" }));
    expect(screen.getByTestId("approved").textContent).toBe("true");
    expect(screen.getByTestId("consent").textContent).toBe("false");
  });

  it("keeps simulated guest consent separately from human approval", () => {
    render(<NavigationProbe />);
    fireEvent.click(screen.getByRole("button", { name: "Consent" }));
    fireEvent.click(screen.getByRole("button", { name: "Change page" }));
    expect(screen.getByTestId("consent").textContent).toBe("true");
    expect(screen.getByTestId("approved").textContent).toBe("false");
  });
});
