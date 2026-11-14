import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowUpRight, ChevronRight } from "lucide-react";
import type { CSSProperties, ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { SidebarProvider, SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { AppSidebar } from "./AppSidebar";
import { useIncidentState } from "./IncidentState";

import { dashboardNavigation, dashboardPages } from "@/lib/dashboard-navigation";

function WorkspaceHeader() {
  const pathname = useRouterState({ select: (router) => router.location.pathname });
  const current = dashboardNavigation.find((page) => page.to === pathname);
  const { open, openMobile, isMobile } = useSidebar();
  const expanded = isMobile ? openMobile : open;
  const toggleLabel = isMobile
    ? expanded
      ? "Close navigation"
      : "Open navigation"
    : expanded
      ? "Collapse navigation"
      : "Expand navigation";

  return (
    <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between gap-3 border-b border-border bg-card px-4 sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <Tooltip>
          <TooltipTrigger asChild>
            <SidebarTrigger
              aria-label={toggleLabel}
              aria-expanded={expanded}
              className="size-9 shrink-0 text-muted-foreground hover:text-foreground"
            />
          </TooltipTrigger>
          <TooltipContent side="bottom">{toggleLabel}</TooltipContent>
        </Tooltip>
        <span className="h-5 w-px bg-border" />
        <div className="flex min-w-0 items-center gap-2 text-sm">
          <span className="hidden text-muted-foreground sm:inline">Control room</span>
          <ChevronRight className="hidden size-3.5 text-muted-foreground sm:block" />
          <span className="truncate font-medium">{current?.label ?? "PLATO-40"}</span>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-4">
        <span className="hidden font-mono text-xs text-muted-foreground lg:inline">
          2026 archive
        </span>
        <span className="flex items-center gap-2 rounded-sm border border-border bg-background px-2.5 py-1.5 text-[11px] text-muted-foreground">
          <span className="size-1.5 rounded-full bg-primary" />
          Backend replay
        </span>
      </div>
    </header>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const state = useIncidentState();
  const pending = state.decisions.filter(
    (d) =>
      d.requires_human_approval &&
      (!state.approved[d.event_id] || (d.requires_guest_consent && !state.consent[d.event_id])),
  ).length;

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "var(--dashboard-sidebar-width)",
          "--sidebar-width-icon": "var(--dashboard-sidebar-icon-width)",
        } as CSSProperties
      }
      className="bg-background text-foreground"
    >
      <AppSidebar pending={pending} />
      <div className="flex min-h-dvh min-w-0 flex-1 flex-col">
        <WorkspaceHeader />
        <main id="main-content" className="min-w-0 flex-1">
          {children}
        </main>
        <footer className="border-t border-border bg-card">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-4 text-[11px] text-muted-foreground sm:px-6 lg:px-8">
            <span>PLATO-40 / CLARA Future</span>
            <span className="hidden sm:inline">Incident replay · Backend replay</span>
            <Button asChild variant="link" className="h-auto p-0 text-[11px]">
              <Link to={dashboardPages.overview.to}>
                {dashboardPages.overview.label}
                <ArrowUpRight />
              </Link>
            </Button>
          </div>
        </footer>
      </div>
    </SidebarProvider>
  );
}
