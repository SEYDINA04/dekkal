import { Link } from "react-router";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-porcelain p-6 text-center text-ink">
      <div>
        <p className="text-sm uppercase tracking-[0.25em] text-lead">404</p>
        <h1 className="mt-3 text-5xl font-light">Page not found</h1>
        <p className="mt-4 text-slate-600">The route you requested does not exist in this prototype.</p>
        <Button asChild className="mt-8 rounded-full bg-mercury-blue text-white hover:bg-mercury-blue/90">
          <Link to="/">Return home</Link>
        </Button>
      </div>
    </main>
  );
}
