import React from 'react';
import { MOCK_TRANSACTIONS } from '../../utils/constants';
import { PaymentMethod } from '../../utils/types';
import LedgerTable from '../../components/LedgerTable';
import { Filter, Calendar } from 'lucide-react';

export const LedgerView: React.FC = () => {
  return (
    <div className="space-y-6 animate-in fade-in font-manrope">
       <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
         <div>
            <h2 className="text-2xl font-bold text-slate-800">General Ledger</h2>
            <p className="text-slate-500">All business transactions in one place.</p>
         </div>
         <div className="flex gap-2">
            <button className="flex items-center gap-2 bg-white border border-slate-200 text-slate-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-slate-50">
               <Calendar size={16} /> Date Range
            </button>
            <button className="flex items-center gap-2 bg-white border border-slate-200 text-slate-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-slate-50">
               <Filter size={16} /> Filter
            </button>
         </div>
       </div>
       <LedgerTable transactions={MOCK_TRANSACTIONS} title="All Transactions" />
    </div>
  );
};

export const CashbookView: React.FC = () => {
  const cashTxns = MOCK_TRANSACTIONS.filter(t => t.paymentMethod === PaymentMethod.CASH);
  
  return (
    <div className="space-y-6 animate-in fade-in font-manrope">
       <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-3xl shadow-soft border border-slate-100">
             <p className="text-slate-500 text-sm font-bold uppercase mb-1">Opening Cash</p>
             <h3 className="text-3xl font-bold text-slate-800">₹12,400</h3>
          </div>
          <div className="bg-white p-6 rounded-3xl shadow-soft border border-slate-100">
             <p className="text-slate-500 text-sm font-bold uppercase mb-1">Cash In</p>
             <h3 className="text-3xl font-bold text-green-600">+₹8,500</h3>
          </div>
          <div className="bg-white p-6 rounded-3xl shadow-soft border border-slate-100">
             <p className="text-slate-500 text-sm font-bold uppercase mb-1">Closing Cash</p>
             <h3 className="text-3xl font-bold text-[#0F172A]">₹16,900</h3>
          </div>
       </div>
       <LedgerTable transactions={cashTxns} title="Cashbook Entries" />
    </div>
  );
};

export const TransactionsView: React.FC = () => {
    return (
        <div className="space-y-6 animate-in fade-in font-manrope">
             <div className="flex justify-between items-center">
                 <h2 className="text-2xl font-bold text-slate-800">Transaction History</h2>
                 <button className="bg-[#006A4E] text-white px-6 py-2.5 rounded-full text-sm font-bold shadow-lg shadow-[#006A4E]/20 hover:bg-[#005a42] transition-colors">
                    + New Entry
                 </button>
             </div>
             <LedgerTable transactions={MOCK_TRANSACTIONS} title="History" />
        </div>
    )
}
