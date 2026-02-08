'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/news', label: 'News' },
  { href: '/research', label: 'Research' },
  { href: '/tickers', label: 'Tickers' },
];

export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav aria-label="Primary" className="flex flex-wrap items-center gap-2">
      {navItems.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={
              active
                ? 'rounded-md border border-[var(--line-strong)] bg-[var(--surface-2)] px-3 py-1.5 text-sm text-[var(--text-strong)]'
                : 'rounded-md border border-transparent px-3 py-1.5 text-sm text-[var(--text-muted)] hover:border-[var(--line-soft)] hover:bg-[var(--surface-1)] hover:text-[var(--text-strong)]'
            }
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
