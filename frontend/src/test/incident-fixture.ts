/** Deterministic UI-only fixture; never shipped as operational decision data. */
export function seedIncidentFixture() {
  const make = (event_id: string, day: string) => ({
    event_id,
    timestamp_utc: `${day}T12:00:00Z`,
    episode_id: `episode-${event_id}`,
    issue_type: "room_readiness",
    priority: "high",
    action: "request_human_approval",
    requires_human_approval: true,
    requires_guest_consent: false,
    reason: "Test fixture for incident UI interactions",
    evidence: ["Synthetic test fixture"],
    confidence: 0.9,
    verification_plan: "Check the UI selection state",
    affected_assets: ["R101"],
  });
  localStorage.setItem("plato40-decisions-v3", JSON.stringify({
    rows: [make("event-1000", "2026-01-01"), make("event-1001", "2026-01-02"), make("event-1035", "2026-01-03")],
    name: "UI test fixtures",
  }));
}
