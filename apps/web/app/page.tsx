import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, BarChart3, Globe, Shield, Zap } from 'lucide-react';

const features = [
  {
    icon: <Globe className="h-6 w-6 text-sky-500" />,
    title: 'Global Intelligence',
    description: 'Real-time ingestion from premium news providers and market data feeds.'
  },
  {
    icon: <Zap className="h-6 w-6 text-amber-500" />,
    title: 'Instant Normalization',
    description: 'Raw data is instantly cleaned and structured for institutional analysis.'
  },
  {
    icon: <BarChart3 className="h-6 w-6 text-emerald-500" />,
    title: 'Advanced Analytics',
    description: 'Powerful visualization tools and sentiment analysis at your fingertips.'
  },
  {
    icon: <Shield className="h-6 w-6 text-purple-500" />,
    title: 'Enterprise Grade',
    description: 'Multi-tenant architecture with strict data isolation and audit logs.'
  }
];

export default function HomePage() {
  return (
    <div className="flex flex-col gap-20 py-10">
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <div className="inline-flex items-center rounded-full border border-[var(--line-soft)] bg-[var(--surface-1)] px-3 py-1 text-sm font-medium text-[var(--text-muted)]">
          <Badge className="mr-2" variant="secondary">New</Badge>
          Phase 2: Intelligence Runtime is now live
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-[var(--text-strong)]">
          Institutional Finance <br /> 
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-indigo-600">
            Intelligence Platform
          </span>
        </h1>
        <p className="text-xl text-[var(--text-muted)] max-w-2xl mx-auto">
          Streamline your investment research with automated data ingestion, 
          real-time sentiment analysis, and agentic intelligence.
        </p>
        <div className="flex items-center justify-center gap-4 pt-4">
          <Link href="/dashboard">
            <Button size="lg" className="gap-2">
              Enter Dashboard <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/settings">
            <Button size="lg" variant="outline">
              Configure Org
            </Button>
          </Link>
        </div>
      </section>

      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, i) => (
          <Card key={i} className="border-none bg-transparent shadow-none">
            <CardContent className="pt-6 space-y-4 px-0">
              <div className="p-3 rounded-lg bg-[var(--surface-1)] border border-[var(--line-soft)] w-fit">
                {feature.icon}
              </div>
              <h3 className="text-lg font-bold text-[var(--text-strong)]">{feature.title}</h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed">
                {feature.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="rounded-2xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-8 md:p-12 overflow-hidden relative">
        <div className="relative z-10 grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-[var(--text-strong)]">
              Developer-First Architecture
            </h2>
            <p className="text-[var(--text-muted)] leading-relaxed">
              Our platform is built with extensibility in mind. Hook into our 
              REST API, utilize our typed clients, and scale your intelligence 
              operations with ease.
            </p>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                <span className="text-sm font-medium text-[var(--text-base)]">Fully typed OpenAPI schemas</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                <span className="text-sm font-medium text-[var(--text-base)]">Multi-tenant X-Org-Id scoping</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                <span className="text-sm font-medium text-[var(--text-base)]">Asynchronous job processing</span>
              </div>
            </div>
          </div>
          <div className="bg-[var(--surface-2)] rounded-xl border border-[var(--line-soft)] p-1 h-64 shadow-inner">
             <div className="bg-[#0F0F0F] rounded-lg h-full p-4 font-mono text-[10px] text-emerald-400 overflow-hidden whitespace-pre">
{`$ curl -X POST "http://api.finops.io/v1/ingestion/jobs" \\
  -H "X-Org-Id: dev-org-123" \\
  -d '{"provider": "tavily", "q": "NVIDIA"}'

// Response 201 Created
{
  "id": "job_98234...",
  "status": "pending",
  "meta": { "request_id": "req_..." }
}`}
             </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function Badge({ children, className, variant }: { children: React.ReactNode, className?: string, variant?: any }) {
  return (
    <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase", 
      variant === 'secondary' ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-700",
      className)}>
      {children}
    </span>
  )
}