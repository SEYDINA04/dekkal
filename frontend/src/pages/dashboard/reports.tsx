export function ReportsPage() {
  return (
    <section className="mx-auto w-full max-w-7xl px-3 py-6 sm:px-4 sm:py-8 lg:px-8">
      <p className="text-sm uppercase tracking-[0.25em] text-lead">Reports</p>
      <h2 className="mt-2 text-3xl font-light text-ink sm:text-4xl md:text-5xl">Decision exports</h2>
      <div className="mt-8 rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
        <h3 className="text-xl font-medium text-ink">Generated reports appear here</h3>
        <p className="mt-3 max-w-2xl text-slate-600">
          Use the underwriting screen to export text reports for pilot files. This route is ready for a future persisted report history.
        </p>
      </div>
    </section>
  );
}
