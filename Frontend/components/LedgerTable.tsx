import React, { useMemo } from 'react';
import { Transaction, TransactionType } from '../utils/types';
import { Download } from 'lucide-react';

interface LedgerTableProps {
  transactions: Transaction[];
  title: string;
}

const LedgerTable: React.FC<LedgerTableProps> = ({ transactions, title }) => {
  
  const handleExport = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Date,Party,Type,Amount,Status,Note\n"
      + transactions.map(t => `${t.date},${t.partyName},${t.type},${t.amount},${t.status},${t.note || ''}`).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${title.toLowerCase().replace(' ', '_')}_ledger.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const runningBalance = useMemo(() => {
    let balance = 0;
    return transactions.map(t => {
       if (t.type === TransactionType.SALE || t.type === TransactionType.UDHAAR_RECEIVED) balance += t.amount;
       else balance -= t.amount;
       return balance;
    });
  }, [transactions]);

  return (
    <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 font-manrope">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h3 className="text-xl font-bold text-slate-800">{title}</h3>
        <button onClick={handleExport} className="text-sm flex items-center gap-2 text-[#006A4E] font-medium bg-[#006A4E]/5 px-3 py-1.5 rounded-lg hover:bg-[#006A4E]/10 transition-colors">
          <Download size={16} /> Export CSV
        </button>
      </div>

      <div className="overflow-x-auto no-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-slate-400 text-xs uppercase tracking-wider border-b border-slate-100">
              <th className="pb-3 pl-2">Date</th>
              <th className="pb-3">Details</th>
              <th className="pb-3 text-right">Credit (+)</th>
              <th className="pb-3 text-right">Debit (-)</th>
              <th className="pb-3 text-right pr-2">Balance</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {transactions.map((t, idx) => {
              const isCredit = t.type === TransactionType.SALE || t.type === TransactionType.UDHAAR_RECEIVED;
              return (
                <tr key={t.id} className="group hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0">
                  <td className="py-4 pl-2 text-slate-500 font-medium whitespace-nowrap">{t.date}</td>
                  <td className="py-4">
                    <p className="font-bold text-slate-800">{t.partyName}</p>
                    <p className="text-xs text-slate-400 truncate max-w-[150px]">{t.note || t.category || t.type.replace('_', ' ')}</p>
                  </td>
                  <td className="py-4 text-right font-medium text-green-600">
                    {isCredit ? `₹${t.amount.toLocaleString()}` : '-'}
                  </td>
                  <td className="py-4 text-right font-medium text-red-500">
                    {!isCredit ? `₹${t.amount.toLocaleString()}` : '-'}
                  </td>
                  <td className="py-4 text-right font-bold text-slate-700 pr-2">
                    ₹{Math.abs(runningBalance[idx]).toLocaleString()}
                    <span className="text-[10px] ml-1 text-slate-400">{runningBalance[idx] >= 0 ? 'Cr' : 'Dr'}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LedgerTable;
