import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MOCK_CUSTOMERS, MOCK_SUPPLIERS } from '../utils/constants';
import Overview from './dashboard/Overview';
import Parties from './dashboard/Parties';
import Expenses from './dashboard/Expenses';
import { LedgerView, CashbookView } from './dashboard/Finance';
import { SettingsView, HelpView, ReportsView } from './dashboard/Misc';

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 pt-8 pb-12 px-4 md:px-8 max-w-[1600px] mx-auto font-manrope">
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="ledger" element={<LedgerView />} />
        <Route path="customers" element={<Parties type="CUSTOMER" data={MOCK_CUSTOMERS} />} />
        <Route path="suppliers" element={<Parties type="SUPPLIER" data={MOCK_SUPPLIERS} />} />
        <Route path="cashbook" element={<CashbookView />} />
        <Route path="expenses" element={<Expenses />} />
        <Route path="reports" element={<ReportsView />} />
        <Route path="settings" element={<SettingsView />} />
        <Route path="help" element={<HelpView />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
};

export default DashboardPage;
