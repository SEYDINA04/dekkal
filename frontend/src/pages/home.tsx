import { ArrowRight, ChevronRight } from "lucide-react";
import { motion } from "motion/react";
import { Link } from "react-router";
import { Button } from "@/components/ui/button";

export function HomePage() {
  const features = [
    ["Address intelligence", "Score a property by address or GPS and understand where the risk comes from."],
    ["Human decision support", "Route files to accept, review, field verification, pricing action, or decline."],
    ["Portfolio screening", "Upload renewals or SME books and surface flood concentration before it becomes claims pressure."],
  ];

  return (
    <div className="flex min-h-screen w-full flex-col">
      <section className="flex min-h-[78vh] items-center sm:min-h-[82vh]">
        <div className="max-w-4xl pt-16 text-white sm:pt-20">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-5 w-fit rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs backdrop-blur-xl sm:text-sm"
          >
            Dakar flood-risk intelligence for IARD insurers
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 }}
            className="text-balance text-4xl font-light leading-[1.06] tracking-wide sm:text-5xl md:text-7xl"
          >
            Know the ground before you bind the risk.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.16 }}
            className="mt-6 max-w-2xl text-base leading-7 text-white/80 sm:mt-7 sm:text-lg sm:leading-8 md:text-xl"
          >
            Dëkkal turns terrain, rainfall, satellite, and drainage signals into explainable underwriting actions for property and SME insurance teams.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.24 }}
            className="mt-9 flex flex-col gap-3 sm:flex-row"
          >
            <Button asChild className="rounded-full bg-mercury-blue px-6 py-6 text-white hover:bg-mercury-blue/90">
              <Link to="/onboarding">
                Start insurer onboarding <ArrowRight size={18} />
              </Link>
            </Button>
            <Button asChild variant="ghost" className="rounded-full bg-white/15 px-6 py-6 text-white backdrop-blur-xl hover:bg-white/25 hover:text-white">
              <Link to="/dashboard">Open dashboard</Link>
            </Button>
          </motion.div>
        </div>
      </section>

      <section className="rounded-[1.5rem] bg-midnight-slate/80 p-5 text-starlight backdrop-blur-xl sm:rounded-[2rem] sm:p-6 md:p-10">
        <div className="grid gap-8 md:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="mb-4 text-sm uppercase tracking-[0.25em] text-silver">Validation MVP</p>
            <h2 className="text-balance text-3xl font-light leading-tight sm:text-4xl md:text-5xl">
              Built around the underwriter’s actual question: what should I do with this file?
            </h2>
          </div>
          <div className="grid gap-3">
            {features.map(([title, body], index) => (
              <motion.article
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="border-b border-white/15 py-6"
                key={title}
              >
                <div className="flex items-start justify-between gap-5">
                  <div>
                    <h3 className="text-2xl font-light">{title}</h3>
                    <p className="mt-2 max-w-2xl text-silver">{body}</p>
                  </div>
                  <ChevronRight className="mt-1 hidden shrink-0 text-mercury-blue sm:block" />
                </div>
              </motion.article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
