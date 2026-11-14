import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowUpRight, Check, CheckCircle2, ChevronRight, Clock3, ShieldCheck } from "lucide-react";
import { PageHeading } from "@/components/dashboard/PageHeading";
import { useIncidentState } from "@/components/dashboard/IncidentState";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ApprovalStatus, PriorityLines, prioTextClass } from "@/components/samples/shared";
import { label } from "@/lib/sample-decisions";
import { cn } from "@/lib/utils";
import { dashboardPages } from "@/lib/dashboard-navigation";

export const Route = createFileRoute("/approvals")({
  head: () => ({
    meta: [
      { title: "Approvals | PLATO-40 Control Room" },
      {
        name: "description",
        content:
          "Review PLATO-40 event evidence, recommended actions, confidence, and simulated approval or guest consent.",
      },
      { property: "og:title", content: "Approvals | PLATO-40 Control Room" },
      {
        property: "og:description",
        content:
          "A focused view of each incident and the approvals needed for simulated execution.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: ApprovalsPage,
});

function ApprovalsPage() {
  const state = useIncidentState();
  const { decisions } = state;
  const [showAll, setShowAll] = useState(false);
  const d = state.d;
  const execution = d ? state.executionById[d.event_id] : undefined;
  if (!d) return <div className="p-10">No incident selected.</div>;
  const needsReview = (eventId: string) => {
    const incident = decisions.find((item) => item.event_id === eventId);
    return Boolean(
      incident?.requires_human_approval &&
      (!state.approved[eventId] || (incident.requires_guest_consent && !state.consent[eventId])),
    );
  };
  const pending = decisions.filter((incident) => needsReview(incident.event_id));
  const queue = showAll ? decisions : pending;
  const approved = Boolean(state.approved[d.event_id]);
  const consent = Boolean(state.consent[d.event_id]);
  const eligible =
    !d.requires_human_approval || (approved && (!d.requires_guest_consent || consent));

  return (
    <div className="page-enter">
      <PageHeading
        number="03"
        title={dashboardPages.approvals.label}
        subtitle="Review queue · Incident evidence and recommended actions"
        action={
          <Button asChild variant="outline">
            <Link to={dashboardPages.incidents.to}>
              {dashboardPages.incidents.label}
              <ArrowUpRight />
            </Link>
          </Button>
        }
      />
      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-6 sm:px-6 lg:grid-cols-[220px_minmax(0,1fr)] lg:px-8">
        <aside className="order-2 min-w-0 lg:order-1" aria-label="Incident review queue">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold">Review queue</h2>
            <span className="font-mono text-xs text-primary">{pending.length} pending</span>
          </div>
          <div className="mb-4 flex gap-1 border-b border-border pb-3">
            <Button
              size="sm"
              variant={showAll ? "ghost" : "default"}
              onClick={() => setShowAll(false)}
              aria-pressed={!showAll}
              className="rounded-sm shadow-none"
            >
              Pending
            </Button>
            <Button
              size="sm"
              variant={showAll ? "default" : "ghost"}
              onClick={() => setShowAll(true)}
              aria-pressed={showAll}
              className="rounded-sm shadow-none"
            >
              All incidents
            </Button>
          </div>
          <div className="max-h-[560px] overflow-y-auto">
            {queue.map((incident) => (
              <Button
                key={incident.event_id}
                variant="ghost"
                onClick={() => state.setId(incident.event_id)}
                aria-pressed={state.id === incident.event_id}
                aria-label={`Select ${incident.event_id}`}
                className={cn(
                  "flex h-auto w-full justify-start gap-3 whitespace-normal rounded-none border-b border-border px-3 py-4 text-left",
                  state.id === incident.event_id && "border-l-2 border-l-primary bg-card",
                )}
              >
                <PriorityLines p={incident.priority} />
                <span className="min-w-0 flex-1">
                  <span className="block font-mono text-[10px] font-normal text-muted-foreground">
                    {incident.event_id}
                  </span>
                  <span
                    className={cn(
                      "mt-1 block text-sm capitalize",
                      prioTextClass[incident.priority],
                    )}
                  >
                    {label(incident.issue_type)}
                  </span>
                </span>
                <ChevronRight className="size-4 shrink-0 text-muted-foreground" />
              </Button>
            ))}
          </div>
          {queue.length === 0 && (
            <div className="py-8 text-center text-sm text-muted-foreground">
              <CheckCircle2 className="mx-auto mb-3 size-6 text-low-text" />
              No approvals waiting.
            </div>
          )}
        </aside>

        <article className="order-1 min-w-0 lg:order-2" aria-label="Selected incident">
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-5">
            <div>
              <span className="font-mono text-[11px] uppercase text-muted-foreground">
                Selected event · {d.episode_id}
              </span>
              <h2 className="mt-2 font-mono text-2xl font-medium leading-tight sm:text-3xl">
                {d.event_id}
              </h2>
              <div className="mt-3 font-mono text-xs text-muted-foreground">
                {d.timestamp_utc} UTC
              </div>
            </div>
            <div className="flex items-center gap-3 border border-border bg-card px-4 py-3">
              <PriorityLines p={d.priority} />
              <span className={cn("text-sm font-medium capitalize", prioTextClass[d.priority])}>
                {d.priority}
              </span>
            </div>
          </div>
          <div className="py-5">
            <div className="mb-2 font-mono text-[11px] uppercase text-primary">What happened</div>
            <h3
              className={cn(
                "font-display text-xl font-semibold capitalize",
                prioTextClass[d.priority],
              )}
            >
              {label(d.issue_type)}
            </h3>
            {d.action === "notify_guest" && d.reason.startsWith("PROPOSED") ? (
              <section className="mt-4 rounded-lg border border-primary/30 bg-card p-5">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div>
                    <h3 className="font-display text-lg font-semibold">
                      ✨ CLARA Suggestion
                    </h3>
                    <p className="text-xs text-muted-foreground">
                    Guest communication · Multilingual templates by Adaption
                    </p>
                  </div>
                  <span className="rounded border px-2 py-1 text-xs">
                    Draft · Not sent
                  </span>
                </div>

                <p className="mb-2 text-xs text-muted-foreground">
                  Recommended guest message
                </p>

                <p className="whitespace-pre-wrap rounded-md bg-muted p-4 text-sm leading-relaxed">
                  {d.reason}
                </p>

                <p className="mt-3 text-xs text-muted-foreground">
                  CLARA selected a message template for the guest's recorded
                  language. Room readiness must be independently verified.
                  No message has been delivered.
                </p>
              </section>
            ) : (
              <p className="mt-3 max-w-2xl text-sm leading-relaxed">
                {d.reason}
              </p>
            )}
            
          </div>
          <div className="grid gap-7 border-y border-border py-6 sm:grid-cols-[1fr_160px]">
            <div>
              <h3 className="mb-3 font-mono text-[11px] uppercase text-muted-foreground">
                Evidence
              </h3>
              <ul className="space-y-3">
                {d.evidence.map((e) => (
                  <li key={e} className="flex gap-3 text-sm">
                    <Check className="mt-0.5 size-4 shrink-0 text-primary" />
                    <span>{e}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="border-border sm:border-l sm:pl-6">
              <span className="font-mono text-[11px] uppercase text-muted-foreground">
                Confidence
              </span>
              <div className="mt-2 font-display text-3xl font-semibold tabular-nums">
                {Math.round(d.confidence * 100)}
                <span className="text-2xl text-muted-foreground">%</span>
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">
                Heuristic estimate
              </span>
            </div>
          </div>
          <section className="mt-5 border-l-2 border-primary bg-card p-4 sm:p-5">
            <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase text-primary">
              <ShieldCheck className="size-4" />
              Recommended action
            </h3>
            <p className="text-base font-semibold leading-relaxed">{d.action}</p>
            <div className="mt-5 border-t border-border pt-4">
              <span className="font-mono text-[10px] uppercase text-muted-foreground">
                Verification plan
              </span>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {d.verification_plan}
              </p>
            </div>
          </section>
          <section className="mt-5 border border-border bg-card p-4" aria-label="Mock execution status">
            <h3 className="font-display text-base font-semibold">Recorded mock-execution status</h3>
            {execution ? <>
              <p className="mt-2 text-sm"><strong>{label(execution.status)}</strong> · {execution.reason || "No reason supplied"}</p>
              <p className="mt-2 text-xs text-muted-foreground">Outstanding safety requirements: {execution.missing_requirements?.length ? execution.missing_requirements.join(", ") : "None recorded"}</p>
              <p className="mt-2 text-xs text-muted-foreground">Verification: {execution.verification?.status || "Not independently verified"}</p>
            </> : <p className="mt-2 text-sm text-muted-foreground">No matching execution log loaded for this decision. Importing a new decision file does not imply that the bundled execution log applies.</p>}
            <p className="mt-2 text-xs text-muted-foreground">Read-only historical simulation. UI approval toggles do not rerun the executor or change this recorded status.</p>
          </section>
          <section className="mt-5 border-t border-border pt-5" aria-label="Approval controls">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <h3 className="font-display text-lg font-semibold">Approval & consent</h3>
              <span className="font-mono text-[10px] uppercase text-muted-foreground">
                Simulation only
              </span>
            </div>
            {d.requires_human_approval && (
              <div className="mb-5 space-y-4">
                <label className="flex cursor-pointer items-center gap-3 text-sm">
                  <Checkbox
                    checked={approved}
                    onCheckedChange={(checked) => state.setApproval(d.event_id, checked === true)}
                    aria-label="Simulate human approval"
                  />
                  Simulate human approval
                </label>
                {d.requires_guest_consent && (
                  <label className="flex cursor-pointer items-center gap-3 text-sm">
                    <Checkbox
                      checked={consent}
                      onCheckedChange={(checked) => state.setConsent(d.event_id, checked === true)}
                      aria-label="Simulate guest consent"
                    />
                    Simulate guest consent
                  </label>
                )}
              </div>
            )}
            <div
              className={cn(
                "flex items-start gap-3 border border-border bg-card p-4",
                eligible ? "text-low-text" : "text-high-text",
              )}
            >
              {eligible ? (
                <CheckCircle2 className="mt-0.5 size-4 shrink-0" />
              ) : (
                <Clock3 className="mt-0.5 size-4 shrink-0" />
              )}
              <ApprovalStatus d={d} approved={approved} consent={consent} />
            </div>
          </section>
        </article>
      </div>
    </div>
  );
}
