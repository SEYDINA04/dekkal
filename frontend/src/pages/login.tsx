import { LockKeyhole } from "lucide-react";
import { Link, useNavigate } from "react-router";
import { BrandMark } from "@/components/brand-mark";
import { Button } from "@/components/ui/button";

export function LoginPage() {
  const navigate = useNavigate();

  return (
    <section className="mx-auto flex min-h-[78vh] w-full max-w-6xl items-center justify-center px-3 py-16 sm:px-4 sm:py-24">
      <div className="glass-panel grid w-full max-w-5xl overflow-hidden rounded-[1.5rem] sm:rounded-[2rem] md:grid-cols-[0.9fr_1.1fr]">
        <div className="bg-midnight-slate p-6 text-starlight sm:p-8 md:p-12">
          <BrandMark light />
          <h1 className="mt-12 text-3xl font-light leading-tight sm:mt-20 sm:text-4xl md:text-5xl">
            Access your underwriting command center.
          </h1>
          <p className="mt-5 text-silver">
            Prototype authentication for insurer teams. Use any email to enter the dashboard.
          </p>
        </div>
        <form
          className="grid gap-5 bg-white p-6 sm:p-8 md:p-12"
          onSubmit={(event) => {
            event.preventDefault();
            navigate("/dashboard");
          }}
        >
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-lead">Sign in</p>
            <h2 className="mt-3 text-2xl font-light text-ink sm:text-3xl">Continue to Dëkkal</h2>
          </div>
          <label className="grid gap-2 text-sm text-slate-700">
            Work email
            <input className="rounded-full border border-slate-300 px-5 py-3 outline-none focus:border-mercury-blue" placeholder="underwriter@insurer.sn" type="email" />
          </label>
          <label className="grid gap-2 text-sm text-slate-700">
            Password
            <input className="rounded-full border border-slate-300 px-5 py-3 outline-none focus:border-mercury-blue" placeholder="Prototype password" type="password" />
          </label>
          <Button className="mt-2 rounded-full bg-mercury-blue px-6 py-6 text-white hover:bg-mercury-blue/90" type="submit">
            Sign in <LockKeyhole size={18} />
          </Button>
          <Link className="text-sm text-slate-500" to="/onboarding">
            New insurer team? Start onboarding instead.
          </Link>
        </form>
      </div>
    </section>
  );
}
