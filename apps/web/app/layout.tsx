import './globals.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { AppShell } from '@/components/shell/app-shell';
import { AppQueryProvider } from '@/providers/query-provider';

export const metadata: Metadata = {
  title: 'FinOps',
  description: 'Institutional-grade finance intelligence platform',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppQueryProvider>
          <AppShell>{children}</AppShell>
        </AppQueryProvider>
      </body>
    </html>
  );
}
