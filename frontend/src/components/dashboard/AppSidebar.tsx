import { Link, useRouterState } from "@tanstack/react-router";
import { Activity, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { dashboardNavigation, dashboardPages } from "@/lib/dashboard-navigation";
import { cn } from "@/lib/utils";

export function AppSidebar({ pending }: { pending: number }) {
  const pathname = useRouterState({ select: (router) => router.location.pathname });
  const { setOpenMobile } = useSidebar();

  return (
    <Sidebar collapsible="icon" className="border-sidebar-border">
      <SidebarHeader className="h-16 shrink-0 justify-center border-b border-sidebar-border px-5 group-data-[collapsible=icon]:px-2">
        <div className="flex items-center justify-between gap-2">
          <Button
            asChild
            variant="ghost"
            className="h-auto justify-start rounded-sm p-0 text-sidebar-foreground hover:bg-transparent hover:text-sidebar-foreground"
          >
            <Link
              to={dashboardPages.overview.to}
              aria-label="PLATO-40 Overview"
              title={dashboardPages.overview.label}
              onClick={() => setOpenMobile(false)}
              className="gap-3"
            >
              <span className="flex size-9 shrink-0 items-center justify-center rounded-sm bg-sidebar-primary text-sidebar-primary-foreground">
                <Activity className="size-5" />
              </span>
              <span className="flex min-w-0 flex-col text-left group-data-[collapsible=icon]:hidden">
                <span className="text-lg font-semibold leading-tight">PLATO-40</span>
                <span className="mt-0.5 text-xs font-normal text-sidebar-muted">CLARA Future</span>
              </span>
            </Link>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Close navigation"
            title="Close navigation"
            onClick={() => setOpenMobile(false)}
            className="shrink-0 text-sidebar-muted hover:bg-sidebar-accent hover:text-sidebar-foreground md:hidden"
          >
            <X />
          </Button>
        </div>
      </SidebarHeader>

      <SidebarContent className="pt-5">
        <SidebarGroup className="px-3 group-data-[collapsible=icon]:px-2">
          <SidebarGroupLabel className="mb-2 px-3 text-[10px] font-semibold uppercase text-sidebar-muted">
            Workspace
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <nav aria-label="Main navigation">
              <SidebarMenu className="gap-1.5">
                {dashboardNavigation.map(({ to, label, icon: Icon }) => (
                  <SidebarMenuItem key={to}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname === to}
                      tooltip={label}
                      className={cn(
                        "h-11 gap-3 rounded-sm px-3 text-sm font-medium text-sidebar-muted hover:text-sidebar-foreground data-[active=true]:bg-sidebar-primary data-[active=true]:text-sidebar-primary-foreground group-data-[collapsible=icon]:mx-auto",
                        to === dashboardPages.approvals.to && "pr-12",
                      )}
                    >
                      <Link
                        to={to}
                        activeOptions={{ exact: true }}
                        aria-label={label}
                        aria-current={pathname === to ? "page" : undefined}
                        onClick={() => setOpenMobile(false)}
                      >
                        <Icon />
                        <span>{label}</span>
                      </Link>
                    </SidebarMenuButton>
                    {to === dashboardPages.approvals.to && (
                      <SidebarMenuBadge className="right-3 top-1/2 -translate-y-1/2 bg-sidebar-accent px-1.5 font-mono text-[10px] leading-none text-sidebar-foreground peer-data-[size=default]/menu-button:top-1/2 peer-data-[active=true]/menu-button:bg-sidebar-primary-foreground/15 peer-data-[active=true]/menu-button:text-sidebar-primary-foreground">
                        {pending}
                      </SidebarMenuBadge>
                    )}
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </nav>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-5 group-data-[collapsible=icon]:items-center group-data-[collapsible=icon]:px-2">
        <div
          className="flex items-center gap-2.5 text-xs text-sidebar-foreground"
          title="Sample workspace"
        >
          <span className="size-1.5 shrink-0 rounded-full bg-sidebar-muted" />
          <span className="group-data-[collapsible=icon]:hidden">Sample workspace</span>
        </div>
        <span className="pl-4 text-[11px] text-sidebar-muted group-data-[collapsible=icon]:hidden">
          Incident replay · 2026
        </span>
      </SidebarFooter>
    </Sidebar>
  );
}
