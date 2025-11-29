import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const Overview = lazy(() => import('./dashboard/Overview'));
const Parties = lazy(() => import('./dashboard/Parties'));
const Expenses = lazy(() => import('./dashboard/Expenses'));
const LedgerView = lazy(() => import('./dashboard/Finance').then(module => ({ default: module.LedgerView })));
const CashbookView = lazy(() => import('./dashboard/Finance').then(module => ({ default: module.CashbookView })));
const SettingsView = lazy(() => import('./dashboard/Misc').then(module => ({ default: module.SettingsView })));
const HelpView = lazy(() => import('./dashboard/Misc').then(module => ({ default: module.HelpView })));
const ReportsView = lazy(() => import('./dashboard/Misc').then(module => ({ default: module.ReportsView })));

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 pt-8 pb-12 px-4 md:px-8 max-w-[1600px] mx-auto font-manrope">
      <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Loading...</div>}>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="ledger" element={<LedgerView />} />
          <Route path="customers" element={<Parties type="CUSTOMER" />} />
          <Route path="suppliers" element={<Parties type="SUPPLIER" />} />
          <Route path="cashbook" element={<CashbookView />} />
          <Route path="expenses" element={<Expenses />} />
          <Route path="reports" element={<ReportsView />} />
          <Route path="settings" element={<SettingsView />} />
          <Route path="help" element={<HelpView />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </div>
  );
};

export default DashboardPage;
