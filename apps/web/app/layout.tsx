import './globals.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { AppShell } from '@/components/shell/app-shell';
import { AppQueryProvider } from '@/providers/query-provider';
import { ThemeProvider } from '@/providers/theme-provider';

export const metadata: Metadata = {
  title: 'FinOps',
  description: 'Institutional-grade finance intelligence platform',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AppQueryProvider>
            <AppShell>{children}</AppShell>
          </AppQueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}