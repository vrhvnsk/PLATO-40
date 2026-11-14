import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowUpRight, CalendarDays } from "lucide-react";
import { useIncidentState } from "@/components/dashboard/IncidentState";
import { PageHeading } from "@/components/dashboard/PageHeading";
import { Button } from "@/components/ui/button";
import { IncidentTimeline } from "@/components/samples/IncidentTimeline";

import { dashboardPages } from "@/lib/dashboard-navigation";

export const Route = createFileRoute("/timeline")({
  head: () => ({
    meta: [
      { title: "Records | PLATO-40 Control Room" },
      {
        name: "description",
        content:
          "Explore the PLATO-40 incident records by year, month, and week with clear severity indicators and daily incident counts.",
      },
      { property: "og:title", content: "Records | PLATO-40 Control Room" },
      {
        property: "og:description",
        content:
          "Explore the 2026 incident timeline, monthly calendar, and weekly incident breakdown.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: TimelinePage,
});

function TimelinePage() {
  const { decisions } = useIncidentState();
  return (
    <div className="page-enter">
      <PageHeading
        number="01"
        title={dashboardPages.timeline.label}
        subtitle="Incident activity by year, month, and week"
        action={
          <Button asChild variant="outline">
            <Link to={dashboardPages.incidents.to}>
              {dashboardPages.incidents.label}
              <ArrowUpRight />
            </Link>
          </Button>
        }
      />
      <div className="mx-auto max-w-7xl px-5 py-6 sm:px-6 lg:px-8">
        <div className="mb-4 flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-2">
            <CalendarDays className="size-4" />
            2026 incident archive
          </span>
          <span>{decisions.length} records</span>
        </div>
        <IncidentTimeline incidents={decisions} />
      </div>
    </div>
  );
}
