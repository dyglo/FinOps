import Link from 'next/link';
import type { ReactNode } from 'react';

import { NavLinks } from '@/components/shell/nav-links';

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(100rem_50rem_at_100%_-10%,rgba(26,81,132,0.16),transparent),linear-gradient(180deg,var(--bg-top),var(--bg-bottom))] text-[var(--text-base)]">
      <header className="sticky top-0 z-20 border-b border-[var(--line-soft)] bg-[color:var(--surface-0)]/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 md:px-8">
          <Link href="/" className="font-semibold tracking-wide text-[var(--text-strong)]">
            FinOps Intelligence
          </Link>
          <NavLinks />
        </div>
      </header>
      <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">{children}</div>
    </div>
  );
}
