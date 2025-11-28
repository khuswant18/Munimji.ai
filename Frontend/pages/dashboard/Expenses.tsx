import React from 'react';
import { MOCK_TRANSACTIONS } from '../../utils/constants';
import { TransactionType } from '../../utils/types';
import LedgerTable from '../../components/LedgerTable';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const Expenses: React.FC = () => {
  const expenses = MOCK_TRANSACTIONS.filter(t => t.type === TransactionType.EXPENSE);
  
  const categoryData = [
     { name: 'Rent', value: 15000, color: '#006A4E' },
     { name: 'Transport', value: 2000, color: '#f59e0b' },
     { name: 'Refreshments', value: 150, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in font-manrope">
       <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1 bg-[#0F172A] rounded-3xl p-8 text-white relative overflow-hidden shadow-card">
              <div className="relative z-10">
                <h2 className="text-2xl font-bold mb-2">Total Spend (Oct)</h2>
                <p className="text-5xl font-bold mb-6">₹17,150</p>
                <div className="flex gap-4">
                    <button className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl text-sm font-bold transition-colors">Add Receipt</button>
                    <button className="bg-white text-[#0F172A] px-4 py-2 rounded-xl text-sm font-bold">Analytics</button>
                </div>
              </div>
              <div className="absolute right-[-40px] top-1/2 -translate-y-1/2 w-48 h-48 opacity-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={categoryData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
          </div>
       </div>
       <LedgerTable transactions={expenses} title="Expense Log" />
    </div>
  );
};

export default Expenses;
