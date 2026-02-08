'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/news', label: 'News' },
  { href: '/research', label: 'Research' },
  { href: '/tickers', label: 'Tickers' },
  { href: '/settings', label: 'Settings' },
];

export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav aria-label="Primary" className="flex items-center gap-8">
      {navItems.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`text-sm font-medium transition-colors hover:text-black ${
              active ? 'text-black' : 'text-gray-500'
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}