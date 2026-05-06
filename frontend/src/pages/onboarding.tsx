import { ArrowRight, ShieldCheck, Upload, UserRound } from "lucide-react";
import { Link } from "react-router";
import { Button } from "@/components/ui/button";

export function OnboardingPage() {
  const steps = [
    { title: "Team profile", body: "Choose insurer, broker, or bancassurance workflow.", Icon: UserRound },
    { title: "Coverage appetite", body: "Set review rules for Dakar property, SME, and renewal files.", Icon: ShieldCheck },
    { title: "Pilot portfolio", body: "Upload a small CSV or start with sample Dakar locations.", Icon: Upload },
  ];

  return (
    <section className="mx-auto w-full max-w-7xl px-3 py-16 sm:px-4 sm:py-24">
      <div className="glass-panel rounded-[1.5rem] p-5 sm:rounded-[2rem] sm:p-6 md:p-10">
        <div className="grid gap-10 md:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="mb-4 text-sm uppercase tracking-[0.25em] text-lead">Onboarding</p>
            <h1 className="text-balance text-3xl font-light leading-tight text-ink sm:text-4xl md:text-6xl">
              Configure a pilot in minutes, then validate with real underwriting files.
            </h1>
            <p className="mt-5 text-base leading-7 text-slate-600 sm:text-lg sm:leading-8">
              This prototype keeps setup intentionally light: identify your workflow, define how high-risk files should be handled, then open the scoring desk.
            </p>
            <Button asChild className="mt-8 rounded-full bg-mercury-blue px-6 py-6 text-white hover:bg-mercury-blue/90">
              <Link to="/dashboard">
                Finish setup <ArrowRight size={18} />
              </Link>
            </Button>
          </div>
          <div className="grid gap-4">
            {steps.map(({ title, body, Icon }, index) => (
              <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6" key={title}>
                <div className="mb-6 flex items-center justify-between">
                  <div className="grid h-12 w-12 place-items-center rounded-full bg-ghost-blue/40 text-mercury-blue">
                    <Icon size={22} />
                  </div>
                  <span className="text-sm text-lead">0{index + 1}</span>
                </div>
                <h2 className="text-2xl font-light text-ink">{title}</h2>
                <p className="mt-2 text-slate-600">{body}</p>
                <div className="mt-6 h-2 rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-mercury-blue" style={{ width: `${(index + 1) * 30}%` }} />
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
