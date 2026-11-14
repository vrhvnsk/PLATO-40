import "@testing-library/jest-dom/vitest";

import { beforeEach, vi } from "vitest";

Object.defineProperty(window, "scrollTo", {
  writable: true,
  value: () => {},
});

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

beforeEach(() => {
  localStorage.clear();

  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);

      if (url.includes("decisions.jsonl")) {
        const events = Array.from({ length: 40 }, (_, i) => ({
          event_id: `event-${1000 + i}`,
          episode_id: `episode-${1000 + i}`,
          timestamp_utc: "2026-11-14T10:00:00Z",
          issue_type: "occupancy_surge",
          priority: "high",
          action: "notify_guest",
          reason: "Test incident",
          requires_human_approval: false,
        }));

        return {
          ok: true,
          text: async () => events.map((event) => JSON.stringify(event)).join("\n"),
        };
      }

      return { ok: false, status: 404 };
    }),
  );
});