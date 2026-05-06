import { Route, Routes } from "react-router";
import { MarketingLayout } from "@/layouts/marketing-layout";
import { DashboardLayout } from "@/layouts/dashboard-layout";
import { HomePage } from "@/pages/home";
import { LoginPage } from "@/pages/login";
import { OnboardingPage } from "@/pages/onboarding";
import { UnderwritingDashboardPage } from "@/pages/dashboard/underwriting-dashboard";
import { PortfolioPage } from "@/pages/dashboard/portfolio";
import { AiToolsPage } from "@/pages/dashboard/ai-tools";
import { ReportsPage } from "@/pages/dashboard/reports";
import { SettingsPage } from "@/pages/dashboard/settings";
import { NotFoundPage } from "@/pages/not-found";

export default function App() {
  return (
    <Routes>
      <Route element={<MarketingLayout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="onboarding" element={<OnboardingPage />} />
      </Route>

      <Route path="dashboard" element={<DashboardLayout />}>
        <Route index element={<UnderwritingDashboardPage />} />
        <Route path="portfolio" element={<PortfolioPage />} />
        <Route path="ai-tools" element={<AiToolsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
