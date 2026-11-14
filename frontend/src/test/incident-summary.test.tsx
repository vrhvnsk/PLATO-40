import type { AnchorHTMLAttributes } from "react";
import { cleanup, fireEvent, render, screen, within, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { IncidentProvider, useIncidentState } from "@/components/dashboard/IncidentState";
import { IncidentsPage } from "@/routes/incidents";

const { navigate } = vi.hoisted(() => ({ navigate: vi.fn() }));

vi.mock("@tanstack/react-router", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-router")>();
  return {
    ...actual,
    Link: ({
      to,
      children,
      onClick,
      ...props
    }: AnchorHTMLAttributes<HTMLAnchorElement> & { to: string }) => (
      <a
        {...props}
        href={to}
        onClick={(event) => {
          event.preventDefault();
          onClick?.(event);
          navigate(to);
        }}
      >
        {children}
      </a>
    ),
  };
});

function SelectionProbe() {
  const state = useIncidentState();
  return <output data-testid="selected-event">{state.id}</output>;
}

async function setup() {
  render(
    <IncidentProvider>
      <IncidentsPage />
      <SelectionProbe />
    </IncidentProvider>,
  );

  await waitFor(() => {
    expect(screen.getByTestId("selected-event").textContent).not.toBe("");
  });

  fireEvent.change(screen.getByRole("textbox"), {
    target: { value: "event-1035" },
  });

  await screen.findAllByRole("button", {
    name: "Summary for event-1035",
  });
}

function openSummary(index = 0) {
  const trigger = screen.getAllByRole("button", { name: "Summary for event-1035" })[index];
  if (!trigger) throw new Error("Incident summary trigger missing");
  fireEvent.click(trigger);
}

afterEach(cleanup);
beforeEach(() => navigate.mockClear());

describe("Incident summaries", () => {
  it.each([0, 1])(
    "opens from incident control %i without replacing the selected approval record",
    async (index) => {
      await setup();
      openSummary(index);
      expect(screen.getByRole("dialog")).toBeInTheDocument();
      expect(screen.getByTestId("selected-event")).toHaveTextContent("event-1000");
      expect(navigate).not.toHaveBeenCalled();
    },
  );

  it("dismisses with the close control without navigating", async () => {
    await setup();
    openSummary();
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByTestId("selected-event")).toHaveTextContent("event-1000");
    expect(navigate).not.toHaveBeenCalled();
  });

  it("dismisses with Escape", async () => {
    await setup();
    openSummary();
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("sets event-1035 before following the approvals link and closes the preview", async () => {
    await setup();
    openSummary();
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("link"));
    expect(screen.getByTestId("selected-event")).toHaveTextContent("event-1035");
    expect(navigate).toHaveBeenCalledExactlyOnceWith("/approvals");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
