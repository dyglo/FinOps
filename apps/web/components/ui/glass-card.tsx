import * as React from 'react';
import { cn } from '@/lib/utils';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'highlight' | 'dark';
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'glass-card text-black',
      highlight: 'bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 text-emerald-900',
      dark: 'bg-black text-white border border-white/10',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-[32px] p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl',
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);
GlassCard.displayName = 'GlassCard';

export { GlassCard };
