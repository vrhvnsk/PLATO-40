import { CalendarDays, LayoutDashboard, ListFilter, ShieldCheck, Presentation } from "lucide-react";

/** One destination name for sidebar entries, headings, and cross-page actions. */
export const dashboardPages = {
  demo: { to: "/demo", label: "Live demo", icon: Presentation },
  overview: { to: "/", label: "Overview", icon: LayoutDashboard },
  timeline: { to: "/timeline", label: "Records", icon: CalendarDays },
  incidents: { to: "/incidents", label: "Incidents", icon: ListFilter },
  approvals: { to: "/approvals", label: "Approvals", icon: ShieldCheck, Presentation },
} as const;

export const dashboardNavigation = Object.values(dashboardPages);
