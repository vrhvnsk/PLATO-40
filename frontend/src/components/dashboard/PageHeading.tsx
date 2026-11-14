import type { ReactNode } from "react";

export function PageHeading({
  number,
  title,
  subtitle,
  action,
}: {
  number: string;
  title: string;
  subtitle: string;
  action?: ReactNode;
}) {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto max-w-7xl px-5 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="min-w-0 flex-1 basis-60">
            <div className="mb-2 flex items-center gap-2 text-[10px] font-medium uppercase text-muted-foreground">
              <span className="text-primary">{number}</span>
              <span className="h-px w-4 bg-border" />
              PLATO-40
            </div>
            <h1 className="font-display text-2xl font-semibold leading-tight text-foreground sm:text-3xl">
              {title}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
          </div>
          {action}
        </div>
      </div>
    </header>
  );
}
