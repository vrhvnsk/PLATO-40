import { Link } from "@tanstack/react-router";
import { ArrowUpRight } from "lucide-react";
import { useIncidentState } from "./IncidentState";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PriorityLines, prioTextClass } from "@/components/samples/shared";
import { dashboardPages } from "@/lib/dashboard-navigation";
import { label, type Decision } from "@/lib/sample-decisions";
import { cn } from "@/lib/utils";

export function IncidentSummaryDialog({
  incident,
  onClose,
}: {
  incident: Decision | null;
  onClose: () => void;
}) {
  const state = useIncidentState();

  return (
    <Dialog
      open={incident !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      {incident && (
        <DialogContent className="max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-md gap-0 overflow-y-auto rounded-sm bg-card p-0 text-card-foreground">
          <DialogHeader className="space-y-0 border-b border-border px-5 pb-5 pt-6 text-left sm:text-left">
            <span className="pr-8 font-mono text-[11px] text-muted-foreground">
              {incident.event_id}
            </span>
            <div className="mt-4 flex items-center gap-2.5">
              <PriorityLines p={incident.priority} />
              <span
                className={cn("text-xs font-semibold capitalize", prioTextClass[incident.priority])}
              >
                {incident.priority} priority
              </span>
            </div>
            <DialogTitle className="mt-3 font-display text-xl font-semibold capitalize leading-snug">
              {label(incident.issue_type)}
            </DialogTitle>
            <DialogDescription className="mt-2 text-sm leading-relaxed">
              {incident.reason}
            </DialogDescription>
          </DialogHeader>
          <div className="px-5 py-5">
            <h3 className="text-[11px] font-semibold uppercase text-muted-foreground">
              Administrator action
            </h3>
            <p className="mt-2 text-sm font-medium leading-relaxed">{incident.action}</p>
            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
              {incident.requires_human_approval
                ? "Review and approve the recommended action."
                : "Review the action and monitor the outcome."}
              {incident.requires_human_approval &&
                incident.requires_guest_consent &&
                " Confirm guest consent before proceeding."}
            </p>
          </div>
          <DialogFooter className="border-t border-border px-5 py-4">
            <Button asChild className="w-full rounded-sm shadow-none sm:w-auto">
              <Link
                to={dashboardPages.approvals.to}
                onClick={() => {
                  state.setId(incident.event_id);
                  onClose();
                }}
                aria-label={`${dashboardPages.approvals.label} for ${incident.event_id}`}
              >
                {dashboardPages.approvals.label}
                <ArrowUpRight />
              </Link>
            </Button>
          </DialogFooter>
        </DialogContent>
      )}
    </Dialog>
  );
}
