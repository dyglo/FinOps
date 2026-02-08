import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Microscope, Beaker, Zap } from 'lucide-react';

export default function ResearchPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-[var(--text-strong)]">Research Room</h1>
        <p className="text-[var(--text-muted)] mt-1">Advanced AI-driven market research and intelligence reports.</p>
      </header>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="opacity-60 grayscale">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Microscope className="h-5 w-5" />
              Agentic Search
            </CardTitle>
            <CardDescription>Deep recursive search across multiple providers.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Coming Soon</Badge>
          </CardContent>
        </Card>

        <Card className="opacity-60 grayscale">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Beaker className="h-5 w-5" />
              Alpha Tester
            </CardTitle>
            <CardDescription>Backtest hypotheses with historical intelligence.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Coming Soon</Badge>
          </CardContent>
        </Card>

        <Card className="opacity-60 grayscale">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Live Intel
            </CardTitle>
            <CardDescription>Real-time stream of high-confidence signals.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Coming Soon</Badge>
          </CardContent>
        </Card>
      </div>

      <div className="flex h-[400px] items-center justify-center rounded-xl border-2 border-dashed border-[var(--line-soft)] bg-[var(--surface-0)]">
        <div className="text-center">
          <p className="text-sm font-medium text-[var(--text-muted)]">Research Lab Interface is being finalized.</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Wiring into /v1/intel/runs endpoints.</p>
        </div>
      </div>
    </div>
  );
}