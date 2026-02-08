import Link from 'next/link';

const sections = [
  { href: '/dashboard', title: 'Dashboard', description: 'Portfolio intelligence overview and analytics surfaces.' },
  { href: '/news', title: 'News Pipeline', description: 'Ingestion job controls and normalized news datasets.' },
  { href: '/research', title: 'Research Room', description: 'Deterministic agent runs, citations, and replay ledger.' },
  { href: '/tickers', title: 'Ticker Lab', description: 'Market/ticker placeholders for upcoming contract lanes.' },
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <header className="mb-8">
        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">FinOps Platform</p>
        <h1 className="mt-3 text-4xl font-semibold text-slate-900">Premium Intelligence UI</h1>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow-md"
          >
            <h2 className="text-xl font-medium text-slate-900">{section.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{section.description}</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
