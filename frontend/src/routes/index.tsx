import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import architecture from "@/assets/control-room-architecture.jpg";
import { Button } from "@/components/ui/button";
import { useIncidentState } from "@/components/dashboard/IncidentState";
import { PriorityLines, prioTextClass } from "@/components/samples/shared";
import { label } from "@/lib/sample-decisions";
import { dashboardPages } from "@/lib/dashboard-navigation";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Overview | PLATO-40 Control Room" },
      {
        name: "description",
        content:
          "Your PLATO-40 control room overview, incident summary, and direct access to Records, Incidents, and Approvals.",
      },
      { property: "og:title", content: "Overview | PLATO-40 Control Room" },
      {
        property: "og:description",
        content:
          "Your PLATO-40 control room overview, incident summary, and direct access to Records, Incidents, and Approvals.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Index,
});

function Index() {
  const state = useIncidentState();
  const { decisions } = state;
  const pending = decisions.filter(
    (d) =>
      d.requires_human_approval &&
      (!state.approved[d.event_id] || (d.requires_guest_consent && !state.consent[d.event_id])),
  );
  const latest = [...decisions]
    .sort((a, b) => b.timestamp_utc.localeCompare(a.timestamp_utc))
    .slice(0, 3);
  const stats = [
    { value: decisions.length, label: "Total incidents" },
    {
      value: new Set(decisions.map((d) => d.episode_id)).size,
      label: "Episodes",
    },
    { value: pending.length, label: "Need approval" },
    {
      value: decisions.filter((d) => d.priority === "critical").length,
      label: "Critical incidents",
    },
  ] as const;
  const shortcuts = [
    {
      number: "01",
      ...dashboardPages.timeline,
      meta: "Backend replay · 2026",
      accent: "bg-primary text-primary-foreground",
    },
    {
      number: "02",
      ...dashboardPages.incidents,
      meta: `${decisions.length} incident records`,
      accent: "bg-inverse text-inverse-foreground",
    },
    {
      number: "03",
      ...dashboardPages.approvals,
      meta: `${pending.length} awaiting review`,
      accent: "bg-muted text-foreground",
    },
  ] as const;
  return (
    <div className="page-enter">
      <div className="mx-auto max-w-7xl px-5 py-3 sm:px-6 lg:px-8 border-b border-border flex flex-wrap items-center gap-3 text-xs">
        <span className="font-medium">Replay data: {state.loading ? "Loading…" : state.source}</span>
        <span>{decisions.length} decisions</span>
        {state.error && <span role="alert" className="text-destructive">{state.error}</span>}
        <label className="cursor-pointer underline">Import backend ZIP or JSONL
          <input type="file" accept=".zip,.jsonl,.json,.txt" className="sr-only" onChange={e=>{const file=e.target.files?.[0];if(file)void state.loadFile(file);e.target.value="";}} />
        </label>
        <button type="button" className="underline" onClick={()=>void state.reload()}>Reload URL</button>
        <span className="text-muted-foreground">Read-only simulated approvals; no real execution</span>
      </div>
      <section
        className="overview-summary relative isolate overflow-hidden bg-primary text-primary-foreground"
        aria-label="Dashboard summary"
      >
        <img
          src={architecture}
          alt=""
          width={1920}
          height={1024}
          fetchPriority="high"
          className="absolute inset-0 -z-10 h-full w-full object-cover object-right opacity-35"
        />
        <div className="mx-auto max-w-7xl px-5 pt-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-4 border-b border-primary-foreground/30 pb-3 text-[11px] font-medium">
            <span>CLARA Future / Building operations</span>
            <span className="shrink-0">2026</span>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-5 py-6">
            <div className="min-w-0">
              <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">
                PLATO-40 Control room
              </h1>
              <p className="mt-2 text-sm text-primary-foreground">
                {dashboardPages.overview.label} · {pending.length} incidents awaiting review
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                asChild
                className="rounded-sm bg-card px-4 text-foreground shadow-none hover:bg-card/90"
              >
                <Link to={dashboardPages.approvals.to}>
                  {dashboardPages.approvals.label}
                  <ArrowUpRight />
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="rounded-sm border-primary-foreground/60 bg-transparent px-4 text-primary-foreground shadow-none hover:bg-primary-foreground/10 hover:text-primary-foreground"
              >
                <Link to={dashboardPages.timeline.to}>
                  {dashboardPages.timeline.label}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
          <dl className="grid grid-cols-2 border-t border-primary-foreground/30 sm:grid-cols-4">
            {stats.map((stat, index) => (
              <div
                key={stat.label}
                className={cn(
                  "min-w-0 py-5 pr-3 text-primary-foreground",
                  index % 2 === 1 && "border-l border-primary-foreground/30 pl-4",
                  index > 1 && "border-t border-primary-foreground/30 sm:border-t-0",
                  index === 2 && "sm:border-l sm:pl-4",
                )}
              >
                <dt className="min-h-8 text-xs font-medium sm:min-h-5">{stat.label}</dt>
                <dd className="mt-1 font-display text-4xl font-semibold leading-none tabular-nums">
                  {String(stat.value).padStart(2, "0")}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="border-b border-border bg-background">
        <div className="mx-auto max-w-7xl px-5 py-6 sm:px-6 lg:px-8">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="font-display text-base font-semibold">Workspace</h2>
            <span className="text-xs text-muted-foreground">2026 incident archive</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-4">
            {shortcuts.map((shortcut) => (
              <Button
                key={shortcut.to}
                asChild
                variant="ghost"
                className="group block h-auto min-w-0 whitespace-normal rounded-sm border border-border bg-card p-4 text-left shadow-none transition-colors hover:border-primary hover:bg-card"
              >
                <Link to={shortcut.to}>
                  <div className="mb-4 flex items-center justify-between">
                    <span
                      className={cn(
                        "flex size-8 items-center justify-center rounded-sm",
                        shortcut.accent,
                      )}
                    >
                      <shortcut.icon className="size-4" />
                    </span>
                    <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-primary" />
                  </div>
                  <h3 className="font-display text-lg font-semibold leading-tight group-hover:text-primary">
                    {shortcut.label}
                  </h3>
                  <div className="mt-2">
                    <span className="text-xs font-normal text-muted-foreground">
                      {shortcut.meta}
                    </span>
                  </div>
                </Link>
              </Button>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-card">
        <div className="mx-auto max-w-7xl px-5 py-6 sm:px-6 lg:px-8">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="font-display text-base font-semibold">Latest activity</h2>
            <Button asChild variant="link" className="h-auto p-0 text-xs">
              <Link to={dashboardPages.incidents.to}>
                {dashboardPages.incidents.label}
                <ArrowRight />
              </Link>
            </Button>
          </div>
          <div className="border-t border-border">
            {latest.map((d) => (
              <Button
                key={d.event_id}
                asChild
                variant="ghost"
                className="group flex h-auto w-full justify-start whitespace-normal rounded-none border-b border-border px-0 py-4 text-left hover:bg-background"
              >
                <Link
                  to={dashboardPages.approvals.to}
                  onClick={() => state.setId(d.event_id)}
                  aria-label={`${dashboardPages.approvals.label} for ${d.event_id}`}
                  className="gap-3"
                >
                  <PriorityLines p={d.priority} />
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[10px] font-normal text-muted-foreground">
                      <span>{d.event_id}</span>
                      <span>{d.timestamp_utc} UTC</span>
                    </div>
                    <span
                      className={cn("text-sm font-semibold capitalize", prioTextClass[d.priority])}
                    >
                      {label(d.issue_type)}
                    </span>
                  </div>
                  <span className="hidden items-center gap-2 text-xs text-muted-foreground group-hover:text-primary sm:inline-flex">
                    {dashboardPages.approvals.label}
                    <ArrowUpRight className="size-4" />
                  </span>
                  <ArrowUpRight className="size-4 shrink-0 text-muted-foreground sm:hidden" />
                </Link>
              </Button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
