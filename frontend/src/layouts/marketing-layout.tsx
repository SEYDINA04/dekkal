import { Camera, MessageCircle, Music2, Play, Radio } from "lucide-react";
import { motion } from "motion/react";
import { NavLink, Outlet } from "react-router";
import { BrandMark } from "@/components/brand-mark";
import { Button } from "@/components/ui/button";
import { VIDEO_SRC } from "@/lib/constants";
import logoWhite from "@/assets/logo_web_white.png";

export function MarketingLayout() {
  return (
    <main className="relative flex min-h-[115vh] w-full flex-col items-center overflow-x-hidden font-sans selection:bg-white/20 selection:text-white">
      <video
        className="fixed inset-0 z-0 h-full w-full object-cover"
        src={VIDEO_SRC}
        autoPlay
        loop
        muted
        playsInline
      />
      <div className="fixed inset-0 z-[1] bg-[linear-gradient(180deg,rgba(8,10,18,0.84)_0%,rgba(8,10,18,0.72)_52%,rgba(8,10,18,0.8)_100%)]" />

      <div className="relative z-10 flex min-h-screen w-full flex-col items-center px-4 py-4">
        <header className="sticky top-4 z-30 mx-auto flex w-full max-w-7xl items-center justify-between gap-3 rounded-full border border-white/15 bg-black/35 px-3 py-2 backdrop-blur-2xl sm:px-4 sm:py-3 md:px-5">
          <BrandMark light />
          <nav className="hidden items-center gap-7 text-sm text-white md:flex">
            <NavLink to="/" end className={({ isActive }) => (isActive ? "opacity-100" : "opacity-75 hover:opacity-100")}>
              Platform
            </NavLink>
            <NavLink to="/onboarding" className={({ isActive }) => (isActive ? "opacity-100" : "opacity-75 hover:opacity-100")}>
              Onboarding
            </NavLink>
            <NavLink to="/dashboard" className="opacity-75 hover:opacity-100">
              Dashboard
            </NavLink>
          </nav>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" className="hidden rounded-full bg-white/15 text-white hover:bg-white/25 hover:text-white sm:inline-flex">
              <NavLink to="/login">Sign in</NavLink>
            </Button>
            <Button asChild className="rounded-full bg-mercury-blue px-3 text-xs text-white hover:bg-mercury-blue/90 sm:px-4 sm:text-sm">
              <NavLink to="/onboarding">Start pilot</NavLink>
            </Button>
          </div>
        </header>
        <nav className="mt-4 flex w-full max-w-7xl justify-center gap-2 rounded-full border border-white/10 bg-black/25 p-1 text-xs text-white backdrop-blur-xl md:hidden">
          {[
            ["/", "Platform"],
            ["/onboarding", "Onboarding"],
            ["/dashboard", "Dashboard"],
          ].map(([to, label]) => (
            <NavLink
              to={to}
              end={to === "/"}
              key={to}
              className={({ isActive }) =>
                `rounded-full px-3 py-2 ${isActive ? "bg-white/15" : "opacity-75"}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="w-full max-w-7xl">
          <Outlet />
          <MarketingFooter />
        </div>
      </div>
    </main>
  );
}

function MarketingFooter() {
  const groups = [
    { title: "Platform", links: ["Risk scoring", "Portfolio screening", "Decision reports", "API access", "Coverage roadmap"] },
    { title: "The Mission", links: ["About Dëkkal", "Insurance partners", "Research sources", "Responsible AI"] },
    { title: "Concierge", links: ["Get in touch", "Privacy", "User agreement", "Report concern"] },
  ];

  return (
    <motion.footer
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, delay: 0.4, ease: "easeOut" }}
      className="liquid-glass mt-32 w-full rounded-3xl p-6 text-white/70 md:mt-64 md:p-10"
    >
      <div className="mb-10 grid grid-cols-1 gap-10 md:grid-cols-12 md:gap-12">
        <div className="md:col-span-5">
          <img src={logoWhite} alt="Dëkkal" className="mb-5 h-20 w-auto object-contain" />
          <p className="max-w-sm text-sm leading-relaxed">
            Dëkkal gives insurers clear, explainable flood-risk intelligence for Dakar underwriting and portfolio review.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-8 md:col-span-7 md:grid-cols-3">
          {groups.map((group) => (
            <div key={group.title}>
              <h3 className="mb-4 text-sm font-medium uppercase tracking-wider text-white">{group.title}</h3>
              <div className="space-y-2">
                {group.links.map((link) => (
                  <a className="block text-xs transition-colors hover:text-white" href="#" key={link}>
                    {link}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-col items-center justify-between gap-6 border-t border-white/10 pt-6 md:flex-row md:gap-4">
        <p className="text-[10px] uppercase tracking-widest opacity-50">Built for Senegal flood-risk underwriting</p>
        <div className="flex items-center gap-4">
          <span className="text-[10px] uppercase tracking-widest opacity-50">Join the Journey:</span>
          {[Music2, Radio, MessageCircle, Play, Camera].map((Icon, index) => (
            <a className="opacity-70 transition-colors hover:text-white hover:opacity-100" href="#" key={index}>
              <Icon size={16} />
            </a>
          ))}
        </div>
      </div>
    </motion.footer>
  );
}
