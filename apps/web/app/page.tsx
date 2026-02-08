export default function HomePage() {
  return (
    <main style={{ maxWidth: 960, margin: '0 auto', padding: '48px 24px' }}>
      <h1 style={{ fontSize: 32, marginBottom: 16 }}>FinOps Platform</h1>
      <p style={{ fontSize: 18, lineHeight: 1.6 }}>
        Platform scaffold is active. Use the API at <code>http://localhost:8000</code> and start building
        deterministic ingestion, signal, and agent workflows.
      </p>
    </main>
  );
}