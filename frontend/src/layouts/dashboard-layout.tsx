import { useState } from "react";
import { BarChart3, Brain, FileText, Gauge, Layers3, LogOut, PanelLeftClose, PanelLeftOpen, Settings } from "lucide-react";
import { NavLink, Outlet } from "react-router";
import { BrandMark } from "@/components/brand-mark";
import { Button } from "@/components/ui/button";

const navItems = [
  { to: "/dashboard", label: "Underwriting", icon: Gauge, end: true },
  { to: "/dashboard/portfolio", label: "Portfolio", icon: Layers3 },
  { to: "/dashboard/ai-tools", label: "AI Tools", icon: Brain },
  { to: "/dashboard/reports", label: "Reports", icon: FileText },
  { to: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function DashboardLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <main className="min-h-screen bg-porcelain text-ink">
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 sm:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <div className={`grid min-h-screen transition-[grid-template-columns] duration-300 ${sidebarCollapsed ? "grid-cols-[76px_1fr]" : "grid-cols-[1fr] sm:grid-cols-[280px_1fr]"}`}>
        {/* Sidebar — drawer on mobile, inline on sm+ */}
        <aside className={`
          fixed inset-y-0 left-0 z-50 flex h-screen flex-col border-r border-slate-200 bg-white/95 backdrop-blur-xl transition-transform duration-300
          sm:sticky sm:translate-x-0 sm:bg-white/90
          ${sidebarCollapsed ? "sm:w-[76px] sm:p-3" : "w-[280px] p-4 sm:p-5"}
          ${mobileOpen ? "translate-x-0" : "-translate-x-full sm:translate-x-0"}
        `}>
          <SidebarContent
            collapsed={sidebarCollapsed}
            onToggle={() => { setSidebarCollapsed((c) => !c); setMobileOpen(false); }}
          />
        </aside>

        <section className="min-w-0">
          <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-slate-200 bg-porcelain/90 px-4 py-4 backdrop-blur-xl lg:px-8">
            <div className="flex min-w-0 items-center gap-3">
              <Button
                aria-label="Open navigation"
                className="shrink-0 rounded-full sm:hidden"
                size="icon"
                variant="outline"
                onClick={() => setMobileOpen((o) => !o)}
              >
                {mobileOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
              </Button>
              <div className="min-w-0">
              <p className="text-xs uppercase tracking-[0.24em] text-lead">Dëkkal Command Center</p>
                <h1 className="mt-1 truncate text-lg font-medium text-ink sm:text-xl">Flood-risk underwriting</h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button className="hidden rounded-full bg-mercury-blue text-white hover:bg-mercury-blue/90 sm:inline-flex">
                <BarChart3 size={16} />
                Pilot mode
              </Button>
            </div>
          </header>
          <Outlet />
        </section>
      </div>
    </main>
  );
}

function SidebarContent({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <div className={`flex items-center ${collapsed ? "justify-center" : "justify-between gap-3"}`}>
        {collapsed ? (
          <NavLink
            aria-label="Dëkkal home"
            className="grid h-11 w-11 place-items-center rounded-2xl bg-ghost-blue/40 text-lg font-semibold text-mercury-blue"
            to="/"
            title="Dëkkal"
          >
            D
          </NavLink>
        ) : (
          <BrandMark />
        )}
        <Button
          aria-label={collapsed ? "Expand dashboard navigation" : "Collapse dashboard navigation"}
          className={`${collapsed ? "absolute left-1/2 top-[70px] h-8 w-8 -translate-x-1/2 rounded-full bg-white shadow-sm" : "rounded-full"}`}
          size="icon"
          variant="outline"
          onClick={onToggle}
        >
          {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
        </Button>
      </div>
      <nav className={`${collapsed ? "mt-14" : "mt-10"} grid gap-2`}>
        {navItems.map((item) => (
          <NavLink
            to={item.to}
            end={item.end}
            key={item.to}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              `flex items-center rounded-3xl text-sm transition ${collapsed ? "h-12 justify-center px-0" : "gap-3 px-4 py-3"} ${
                isActive ? "bg-ghost-blue/50 text-mercury-blue" : "text-slate-600 hover:bg-slate-100 hover:text-ink"
              }`
            }
          >
            <item.icon className="shrink-0" size={18} />
            {collapsed ? <span className="sr-only">{item.label}</span> : item.label}
          </NavLink>
        ))}
      </nav>
      <Button asChild variant="outline" className={`mt-auto rounded-full ${collapsed ? "h-12 w-full px-0" : "w-full"}`}>
        <NavLink to="/" title={collapsed ? "Back to site" : undefined}>
          <LogOut size={16} />
          {collapsed ? <span className="sr-only">Back to site</span> : "Back to site"}
        </NavLink>
      </Button>
    </>
  );
}
