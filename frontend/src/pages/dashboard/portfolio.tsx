export function PortfolioPage() {
  return (
    <section className="mx-auto w-full max-w-7xl px-3 py-6 sm:px-4 sm:py-8 lg:px-8">
      <p className="text-sm uppercase tracking-[0.25em] text-lead">Portfolio</p>
      <h2 className="mt-2 text-3xl font-light text-ink sm:text-4xl md:text-5xl">Book-level flood concentration</h2>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          ["Policies screened", "0", "Upload a CSV from the underwriting screen to start."],
          ["High risk share", "Sample", "Use pilot files to benchmark appetite rules."],
          ["Next action", "Batch scoring", "Prioritize renewals in flood-prone communes."],
        ].map(([label, value, body]) => (
          <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6" key={label}>
            <span className="text-sm text-slate-500">{label}</span>
            <strong className="mt-3 block text-3xl font-light text-ink">{value}</strong>
            <p className="mt-3 text-sm leading-6 text-slate-600">{body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
