'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import { NavLinks } from '@/components/shell/nav-links';
import { Button } from '@/components/ui/button';

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen hero-gradient selection:bg-emerald-100">
      <header className="sticky top-0 z-50 w-full px-6 py-4">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-12">
            <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight text-black">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              FinOps
            </Link>
            <div className="hidden md:block">
              <NavLinks />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="hidden font-medium md:flex btn-pill">
              Sign In
            </Button>
            <Button className="bg-black text-white hover:bg-zinc-800 btn-pill px-6">
              Free Trial
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6">{children}</main>
    </div>
  );
}