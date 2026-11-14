import type { Decision, Priority } from "@/lib/sample-decisions";
import { cn } from "@/lib/utils";

export const prioTextClass: Record<Priority, string> = {
  critical: "text-critical-text",
  high: "text-high-text",
  medium: "text-medium-text",
  low: "text-low-text",
};
export const prioBarClass: Record<Priority, string> = {
  critical: "bg-critical/80 group-hover:bg-critical",
  high: "bg-high group-hover:bg-high-text",
  medium: "bg-medium/80 group-hover:bg-medium",
  low: "bg-low-bar group-hover:bg-low-bar",
};
export const PRIORITY_ORDER: Priority[] = ["critical", "high", "medium", "low"];
export const PRIORITY_LEVELS: Record<Priority, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
};
const priorityLineClass: Record<Priority, string> = {
  critical: "border-critical bg-critical",
  high: "border-high bg-high",
  medium: "border-medium bg-medium",
  low: "border-low bg-low",
};

export function PriorityLines({ p, className }: { p: Priority; className?: string }) {
  const filled = PRIORITY_LEVELS[p];
  const description = `${p.charAt(0).toUpperCase()}${p.slice(1)} priority: ${filled} of 4 lines filled`;

  return (
    <span
      role="img"
      aria-label={description}
      title={description}
      className={cn("inline-flex h-4 shrink-0 items-center gap-[3px] align-middle", className)}
    >
      {Array.from({ length: 4 }, (_, index) => (
        <span
          key={index}
          aria-hidden="true"
          className={cn(
            "block h-3.5 w-1 rounded-[1px] border",
            index < filled ? priorityLineClass[p] : "border-border bg-card",
          )}
        />
      ))}
    </span>
  );
}

/** Highest priority present in a group of incidents, or null when the group is empty. */
export function highestPriority(list: Decision[]): Priority | null {
  return PRIORITY_ORDER.find((p) => list.some((d) => d.priority === p)) ?? null;
}

export function ApprovalStatus({
  d,
  approved,
  consent,
}: {
  d: Decision;
  approved: boolean;
  consent: boolean;
}) {
  if (!d.requires_human_approval)
    return <p className="text-sm text-low-text">Eligible for mock autonomous execution.</p>;
  const ok = approved && (!d.requires_guest_consent || consent);
  return (
    <p className={cn("text-sm", ok ? "text-low-text" : "text-high-text")}>
      {ok
        ? "Mock execution eligible — no real action performed."
        : "Waiting for required approval / consent."}
    </p>
  );
}
