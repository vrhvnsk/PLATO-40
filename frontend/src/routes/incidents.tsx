import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Eye, Search, X } from "lucide-react";
import { PageHeading } from "@/components/dashboard/PageHeading";
import { useIncidentState } from "@/components/dashboard/IncidentState";
import { IncidentSummaryDialog } from "@/components/dashboard/IncidentSummaryDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PriorityLines, PRIORITY_ORDER, prioTextClass } from "@/components/samples/shared";
import { label, type Decision, type Priority } from "@/lib/sample-decisions";
import { cn } from "@/lib/utils";
import { dashboardPages } from "@/lib/dashboard-navigation";

export const Route = createFileRoute("/incidents")({
  head: () => ({
    meta: [
      { title: "Incidents | PLATO-40 Control Room" },
      {
        name: "description",
        content:
          "Browse PLATO-40 incident records, filter by severity, and select an event for detailed review and approval.",
      },
      { property: "og:title", content: "Incidents | PLATO-40 Control Room" },
      {
        property: "og:description",
        content:
          "Find incident records, inspect severity and actions, and open an event for review.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: IncidentsPage,
});

export function IncidentsPage() {
  const state = useIncidentState();
  const { decisions } = state;
  const [query, setQuery] = useState("");
  const [priority, setPriority] = useState<Priority | "all">("all");
  const [preview, setPreview] = useState<Decision | null>(null);
  const filtered = [...decisions]
    .sort((a, b) => b.timestamp_utc.localeCompare(a.timestamp_utc))
    .filter(
      (d) =>
        (priority === "all" || priority === d.priority) &&
        `${d.event_id} ${d.episode_id} ${label(d.issue_type)} ${d.action} ${d.timestamp_utc}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    );

  return (
    <div className="page-enter">
      <PageHeading
        number="02"
        title={dashboardPages.incidents.label}
        subtitle="Incident register · All episodes and severity levels"
      />
      <div className="@container mx-auto max-w-7xl px-5 py-6 sm:px-6 lg:px-8">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-3 size-4 text-muted-foreground" />
            <Input
              aria-label="Search incidents"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search incidents…"
              className="h-10 rounded-sm bg-card pl-10 pr-10 shadow-none"
            />
            {query && (
              <Button
                variant="ghost"
                size="icon"
                aria-label="Clear search"
                className="absolute right-1 top-0.5"
                onClick={() => setQuery("")}
              >
                <X />
              </Button>
            )}
          </div>
          <div className="space-y-2">
            <div id="severity-filter-label" className="text-[11px] text-muted-foreground">
              Filter by severity
            </div>
            <div
              className="flex flex-wrap gap-1"
              role="group"
              aria-labelledby="severity-filter-label"
            >
              {(["all", ...PRIORITY_ORDER] as const).map((p) => (
                <Button
                  key={p}
                  variant={priority === p ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setPriority(p)}
                  aria-pressed={priority === p}
                  className="rounded-sm capitalize shadow-none"
                >
                  {p === "all" ? (
                    "All incidents"
                  ) : (
                    <>
                      <PriorityLines p={p} />
                      {p}
                    </>
                  )}
                </Button>
              ))}
            </div>
          </div>
        </div>
        <div className="mb-3 flex items-center justify-between font-mono text-[11px] uppercase text-muted-foreground">
          <span>
            {filtered.length} incident{filtered.length === 1 ? "" : "s"}
          </span>
          <span>Latest first · UTC</span>
        </div>
        <div className="hidden overflow-x-auto border border-border bg-card @min-[760px]:block">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-border bg-muted/50 font-mono text-[10px] uppercase text-muted-foreground">
              <tr>
                {["Event / Date", "Episode", "Issue", "Severity", "Action", "Summary"].map(
                  (heading) => (
                    <th key={heading} className="px-3 py-3 font-medium">
                      {heading}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr
                  key={d.event_id}
                  className={cn(
                    "relative border-b border-border hover:bg-background",
                    state.id === d.event_id && "bg-accent/40",
                  )}
                >
                  <td className="px-3 py-4">
                    <Button
                      variant="ghost"
                      aria-label={`Summary for ${d.event_id}`}
                      aria-haspopup="dialog"
                      onClick={() => setPreview(d)}
                      className="absolute inset-0 z-10 h-full w-full rounded-none p-0 hover:bg-transparent focus-visible:ring-2 focus-visible:ring-inset"
                    >
                      <span className="sr-only">Summary for {d.event_id}</span>
                    </Button>
                    <div className="font-mono text-xs font-medium">{d.event_id}</div>
                    <div className="mt-1 font-mono text-[10px] text-muted-foreground">
                      {d.timestamp_utc}
                    </div>
                  </td>
                  <td className="px-3 py-4 font-mono text-xs text-muted-foreground">
                    {d.episode_id}
                  </td>
                  <td className={cn("px-3 py-4 font-medium capitalize", prioTextClass[d.priority])}>
                    {label(d.issue_type)}
                  </td>
                  <td className="px-3 py-4">
                    <PriorityLines p={d.priority} />
                  </td>
                  <td className="max-w-64 px-3 py-4 text-xs leading-relaxed text-muted-foreground">
                    {d.action}
                  </td>
                  <td className="px-3 py-4">
                    <Eye className="mx-auto size-4 text-muted-foreground" aria-hidden="true" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="border-t border-border @min-[760px]:hidden">
          {filtered.map((d) => (
            <Button
              key={d.event_id}
              variant="ghost"
              onClick={() => setPreview(d)}
              aria-label={`Summary for ${d.event_id}`}
              aria-haspopup="dialog"
              className="block h-auto w-full whitespace-normal rounded-none border-b border-border bg-card px-3 py-5 text-left shadow-none hover:bg-background hover:text-foreground"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-mono text-xs">{d.event_id}</span>
                <PriorityLines p={d.priority} />
              </div>
              <div className="mt-3 flex items-center justify-between gap-3">
                <span
                  className={cn("text-base font-semibold capitalize", prioTextClass[d.priority])}
                >
                  {label(d.issue_type)}
                </span>
                <Eye className="size-4 text-muted-foreground" aria-hidden="true" />
              </div>
              <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[10px] font-normal text-muted-foreground">
                <span>{d.timestamp_utc}</span>
                <span>{d.episode_id}</span>
              </div>
              <p className="mt-2 text-xs font-normal leading-relaxed text-muted-foreground">
                {d.action}
              </p>
            </Button>
          ))}
        </div>
        {filtered.length === 0 && (
          <div className="border-y border-border py-16 text-center">
            <Search className="mx-auto mb-4 size-6 text-muted-foreground" />
            <h2 className="text-lg font-semibold">No matching incidents</h2>
            <Button
              variant="link"
              onClick={() => {
                setQuery("");
                setPriority("all");
              }}
            >
              Clear filters
            </Button>
          </div>
        )}
      </div>
      <IncidentSummaryDialog incident={preview} onClose={() => setPreview(null)} />
    </div>
  );
}
