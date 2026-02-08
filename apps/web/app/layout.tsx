import './globals.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { AppShell } from '@/components/shell/app-shell';

export const metadata: Metadata = {
  title: 'FinOps',
  description: 'Institutional-grade finance intelligence platform',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
