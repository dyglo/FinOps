import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'destructive';
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-black text-white dark:bg-white dark:text-black',
    secondary: 'bg-gray-100 text-gray-900 dark:bg-zinc-800 dark:text-zinc-100',
    outline: 'border border-gray-200 text-gray-500 dark:border-zinc-800 dark:text-zinc-400',
    success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border dark:border-emerald-900/50',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 dark:border dark:border-amber-900/50',
    destructive: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 dark:border dark:border-red-900/50',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
