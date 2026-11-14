import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Decision, Priority } from "@/lib/sample-decisions";
import {
  PRIORITY_ORDER,
  PriorityLines,
  highestPriority,
  prioBarClass,
  prioTextClass,
} from "./shared";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];
const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
type ViewMode = "year" | "month" | "week";

const dateKey = (date: Date) => date.toISOString().slice(0, 10);
const addDays = (date: Date, days: number) => new Date(date.getTime() + days * 86_400_000);

function getMonthWeeks(year: number, month: number) {
  const first = new Date(Date.UTC(year, month, 1));
  const last = new Date(Date.UTC(year, month + 1, 0));
  let cursor = addDays(first, -((first.getUTCDay() + 6) % 7));
  const weeks: Date[][] = [];

  while (cursor <= last) {
    weeks.push(Array.from({ length: 7 }, (_, index) => addDays(cursor, index)));
    cursor = addDays(cursor, 7);
  }
  return weeks;
}

function formatWeekRange(week: Date[]) {
  const start = week[0];
  const end = week[6];
  if (!start || !end) return "";
  if (start.getUTCMonth() === end.getUTCMonth()) {
    return `${start.getUTCDate()}–${end.getUTCDate()} ${MONTHS[start.getUTCMonth()]} ${start.getUTCFullYear()}`;
  }
  return `${start.getUTCDate()} ${MONTHS[start.getUTCMonth()]?.slice(0, 3)} – ${end.getUTCDate()} ${MONTHS[end.getUTCMonth()]?.slice(0, 3)} ${start.getUTCFullYear()}`;
}

export function IncidentTimeline({ incidents }: { incidents: Decision[] }) {
  const [view, setView] = useState<ViewMode>("year");
  const [selectedMonth, setSelectedMonth] = useState(0);
  const [weekIndex, setWeekIndex] = useState(0);

  const year = 2026;

  const yearIncidents = useMemo(
    () => incidents.filter((incident) => Number(incident.timestamp_utc.slice(0, 4)) === year),
    [incidents, year],
  );
  const byDay = useMemo(() => {
    const grouped = new Map<string, Decision[]>();
    yearIncidents.forEach((incident) => {
      const key = incident.timestamp_utc.slice(0, 10);
      grouped.set(key, [...(grouped.get(key) ?? []), incident]);
    });
    return grouped;
  }, [yearIncidents]);
  const monthCounts = MONTHS.map(
    (_, month) =>
      yearIncidents.filter((incident) => Number(incident.timestamp_utc.slice(5, 7)) === month + 1)
        .length,
  );
  const byMonth = useMemo(() => {
    const grouped: Decision[][] = MONTHS.map(() => []);
    yearIncidents.forEach((incident) => {
      grouped[Number(incident.timestamp_utc.slice(5, 7)) - 1]?.push(incident);
    });
    return grouped;
  }, [yearIncidents]);
  const monthTopPrio: (Priority | null)[] = byMonth.map(highestPriority);
  const monthIncidents = yearIncidents.filter(
    (incident) => Number(incident.timestamp_utc.slice(5, 7)) === selectedMonth + 1,
  );
  const weeks = useMemo(() => getMonthWeeks(year, selectedMonth), [year, selectedMonth]);
  const activeWeekIndex = Math.min(weekIndex, weeks.length - 1);
  const activeWeek = weeks[activeWeekIndex] ?? [];
  const maxMonthCount = Math.max(...monthCounts, 1);

  function selectMonth(month: number, alwaysShowMonth = false) {
    setSelectedMonth(month);
    setWeekIndex(0);
    setView((current) => (alwaysShowMonth || current === "year" ? "month" : current));
  }

  return (
    <section
      className="@container border border-border bg-card p-4 sm:p-5"
      aria-label="Incident timeline explorer"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold text-foreground">
            {view === "year" ? year : `${MONTHS[selectedMonth]} ${year}`}
          </h2>
          <p className="mt-1.5 text-xs text-muted-foreground">
            {view === "year" && `${yearIncidents.length} incidents recorded`}
            {view === "month" && `${monthIncidents.length} incidents · ${weeks.length} weeks`}
            {view === "week" &&
              `Week ${activeWeekIndex + 1} of ${weeks.length} · ${formatWeekRange(activeWeek)}`}
          </p>
        </div>
        <div className="flex rounded-sm border border-border p-1" aria-label="Timeline view">
          {(["year", "month", "week"] as ViewMode[]).map((mode) => (
            <Button
              key={mode}
              variant="ghost"
              type="button"
              onClick={() => setView(mode)}
              aria-pressed={view === mode}
              className={cn(
                "h-8 rounded-sm px-3 py-1 font-mono text-[11px] uppercase shadow-none",
                view === mode
                  ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent",
              )}
            >
              {mode}
            </Button>
          ))}
        </div>
      </div>

      <div
        className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] capitalize text-muted-foreground"
        aria-label="Priority colors"
      >
        {PRIORITY_ORDER.map((p) => (
          <span key={p} className="inline-flex items-center gap-2">
            <PriorityLines p={p} />
            {p}
          </span>
        ))}
      </div>

      <div
        className="mt-5 grid grid-cols-3 gap-2 @min-[500px]:grid-cols-6 @min-[760px]:grid-cols-12 @min-[760px]:gap-1"
        aria-label={`Months in ${year}`}
      >
        {MONTHS.map((month, index) => (
          <Button
            key={month}
            variant="ghost"
            type="button"
            aria-label={`Show ${month} ${year}`}
            aria-pressed={view !== "year" && selectedMonth === index}
            title={`${month}: ${monthCounts[index]} incidents`}
            onClick={() => selectMonth(index)}
            className={cn(
              "h-10 min-w-0 rounded-sm border px-2 py-2 text-xs shadow-none @min-[760px]:h-9 @min-[760px]:px-1",
              view !== "year" && selectedMonth === index
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            <span className="@min-[760px]:hidden">{month}</span>
            <span className="hidden @min-[760px]:inline">{month.slice(0, 3)}</span>
          </Button>
        ))}
      </div>

      {view === "year" && (
        <div
          className="mt-6 grid grid-cols-12 gap-1 border-b border-border pb-1 @min-[640px]:gap-3"
          aria-label={`Monthly incidents in ${year}`}
        >
          {MONTHS.map((month, index) => {
            const count = monthCounts[index] ?? 0;
            const top = monthTopPrio[index];
            return (
              <Button
                key={month}
                variant="ghost"
                type="button"
                aria-label={`Open ${month} ${year}: ${count} incidents`}
                onClick={() => selectMonth(index, true)}
                className="group flex h-44 min-w-0 flex-col justify-end gap-0 rounded-none px-0.5 py-0 shadow-none hover:bg-accent/50 @min-[640px]:h-56"
              >
                <span
                  className={cn(
                    "mb-1 text-[11px] font-semibold",
                    top ? prioTextClass[top] : "text-muted-foreground",
                    "group-hover:text-foreground",
                  )}
                >
                  {count}
                </span>
                <span
                  className={cn(
                    "mx-auto w-full max-w-10 transition-colors",
                    top ? prioBarClass[top] : "bg-muted-foreground/25",
                  )}
                  style={{
                    height: `${count === 0 ? 2 : Math.max(12, (count / maxMonthCount) * 100)}%`,
                  }}
                />
                <span className="mt-3 font-mono text-[10px] uppercase text-muted-foreground group-hover:text-foreground">
                  {month.slice(0, 3)}
                </span>
              </Button>
            );
          })}
        </div>
      )}

      {view === "month" && (
        <div className="mt-5">
          <div className="grid grid-cols-7 gap-1">
            {WEEKDAYS.map((day) => (
              <div key={day} className="pb-1 text-center text-[11px] text-muted-foreground">
                {day}
              </div>
            ))}
            {weeks.flatMap((week, index) =>
              week.map((date) => {
                const dayIncidents = byDay.get(dateKey(date)) ?? [];
                const inMonth = date.getUTCMonth() === selectedMonth;
                const top = highestPriority(dayIncidents);
                return (
                  <Button
                    key={dateKey(date)}
                    variant="ghost"
                    type="button"
                    aria-label={`Open week containing ${date.getUTCDate()} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`}
                    onClick={() => {
                      setWeekIndex(index);
                      setView("week");
                    }}
                    className={cn(
                      "flex h-16 min-w-0 flex-col items-start gap-0 rounded-sm border border-border p-1.5 text-left shadow-none hover:border-primary hover:bg-accent @min-[640px]:h-20 @min-[640px]:p-2",
                      !inMonth && "border-border/40 bg-muted/20",
                    )}
                  >
                    <span
                      className={cn("text-[11px] text-muted-foreground", !inMonth && "opacity-50")}
                    >
                      {date.getUTCDate()}
                    </span>
                    {dayIncidents.length > 0 ? (
                      <span
                        className={cn(
                          "mt-auto text-[13px] font-semibold",
                          top ? prioTextClass[top] : "text-muted-foreground",
                        )}
                      >
                        {dayIncidents.length}{" "}
                        <span className="hidden @min-[720px]:inline">
                          incident{dayIncidents.length === 1 ? "" : "s"}
                        </span>
                      </span>
                    ) : (
                      <span className="mt-auto text-xs text-muted-foreground">—</span>
                    )}
                  </Button>
                );
              }),
            )}
          </div>
        </div>
      )}

      {view === "week" && (
        <div className="mt-5" aria-live="polite">
          <div className="mb-3 flex items-center justify-between gap-3">
            <Button
              variant="outline"
              size="icon"
              type="button"
              aria-label="Previous week"
              disabled={activeWeekIndex === 0}
              onClick={() => setWeekIndex(activeWeekIndex - 1)}
              title="Previous week"
              className="rounded-sm text-muted-foreground shadow-none"
            >
              <ChevronLeft className="size-4" />
            </Button>
            <div className="text-center">
              <div className="text-sm text-foreground">{formatWeekRange(activeWeek)}</div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">Monday to Sunday</div>
            </div>
            <Button
              variant="outline"
              size="icon"
              type="button"
              aria-label="Next week"
              disabled={activeWeekIndex === weeks.length - 1}
              onClick={() => setWeekIndex(activeWeekIndex + 1)}
              title="Next week"
              className="rounded-sm text-muted-foreground shadow-none"
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-2 @min-[520px]:grid-cols-4 @min-[960px]:grid-cols-7">
            {activeWeek.map((date) => {
              const dayIncidents = byDay.get(dateKey(date)) ?? [];
              const top = highestPriority(dayIncidents);
              return (
                <article
                  key={dateKey(date)}
                  className={cn(
                    "min-h-36 min-w-0 rounded-sm border border-border bg-background/40 p-3",
                    date.getUTCMonth() !== selectedMonth && "border-border/40 bg-muted/20",
                  )}
                >
                  <div
                    className={cn(
                      "text-[11px] text-muted-foreground",
                      date.getUTCMonth() !== selectedMonth && "opacity-50",
                    )}
                  >
                    {WEEKDAYS[(date.getUTCDay() + 6) % 7]} · {date.getUTCDate()}{" "}
                    {MONTHS[date.getUTCMonth()]?.slice(0, 3)}
                  </div>
                  <div
                    className={cn(
                      "mt-2 text-2xl",
                      top ? prioTextClass[top] : "text-muted-foreground",
                    )}
                  >
                    {dayIncidents.length}
                  </div>
                  <div className="text-[10px] text-muted-foreground">
                    incident{dayIncidents.length === 1 ? "" : "s"}
                  </div>
                  <ul className="mt-2 space-y-1 text-[11px] font-medium">
                    {dayIncidents.map((incident) => (
                      <li
                        key={incident.event_id}
                        className={cn("capitalize", prioTextClass[incident.priority])}
                      >
                        {incident.issue_type.replaceAll("_", " ")}
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
