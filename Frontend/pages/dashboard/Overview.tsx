import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Wallet, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { CHART_DATA_WEEKLY, MOCK_TRANSACTIONS } from '../../utils/constants';
import { TransactionType } from '../../utils/types';

const Overview: React.FC = () => {
  return (
    <div className="space-y-8 animate-in fade-in duration-500 font-manrope">
      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#0F172A] rounded-3xl p-6 text-white shadow-card relative overflow-hidden group hover:shadow-xl transition-all">
           <div className="absolute -right-4 -top-4 w-32 h-32 bg-[#1E293B] rounded-full blur-2xl opacity-50 group-hover:scale-110 transition-transform"></div>
           <div className="relative z-10">
              <p className="text-slate-300 text-sm font-medium mb-1">Net Income (Oct)</p>
              <h3 className="text-3xl font-bold">₹24,500</h3>
              <div className="mt-4 flex gap-2">
                 <span className="bg-white/10 px-2 py-1 rounded-lg text-xs flex items-center gap-1"><ArrowUpRight size={12} /> +12%</span>
              </div>
           </div>
        </div>
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 hover:border-[#006A4E]/20 transition-colors">
           <div className="flex justify-between items-start mb-2">
              <p className="text-slate-500 text-sm font-medium">Total Sales</p>
              <div className="p-2 bg-green-50 text-green-600 rounded-lg"><Wallet size={18} /></div>
           </div>
           <h3 className="text-3xl font-bold text-slate-800">₹42,000</h3>
           <p className="text-xs text-slate-400 mt-2">Vs ₹38,000 last month</p>
        </div>
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 hover:border-[#006A4E]/20 transition-colors">
           <div className="flex justify-between items-start mb-2">
              <p className="text-slate-500 text-sm font-medium">Expenses</p>
              <div className="p-2 bg-red-50 text-red-600 rounded-lg"><ArrowDownLeft size={18} /></div>
           </div>
           <h3 className="text-3xl font-bold text-slate-800">₹17,500</h3>
           <p className="text-xs text-slate-400 mt-2">Mostly: Rent & Inventory</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 shadow-soft border border-slate-100">
           <div className="flex justify-between items-center mb-6">
              <h3 className="font-bold text-lg text-slate-800">Cash Flow</h3>
              <select className="text-sm bg-slate-50 border-none rounded-lg text-slate-500 font-medium py-1 px-3 outline-none focus:ring-2 focus:ring-[#006A4E]/20">
                <option>This Week</option>
                <option>Last Week</option>
              </select>
           </div>
           <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={CHART_DATA_WEEKLY}>
                  <defs>
                    <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#006A4E" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#006A4E" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <Tooltip contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 40px -10px rgba(0,0,0,0.1)'}} />
                  <Area type="monotone" dataKey="income" stroke="#006A4E" strokeWidth={3} fillOpacity={1} fill="url(#colorIncome)" />
                  <Area type="monotone" dataKey="expense" stroke="#ef4444" strokeWidth={3} fillOpacity={0} />
                </AreaChart>
              </ResponsiveContainer>
           </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col">
          <h3 className="font-bold text-lg text-slate-800 mb-6">Recent Activity</h3>
          <div className="space-y-6 flex-1 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar">
            {MOCK_TRANSACTIONS.slice(0, 5).map(t => (
              <div key={t.id} className="flex items-center justify-between group">
                <div className="flex items-center gap-3">
                   <div className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-colors ${t.type === TransactionType.EXPENSE || t.type === TransactionType.PAYMENT_OUT ? 'bg-red-50 text-red-500 group-hover:bg-red-100' : 'bg-green-50 text-green-600 group-hover:bg-green-100'}`}>
                      {t.type === TransactionType.EXPENSE || t.type === TransactionType.PAYMENT_OUT ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                   </div>
                   <div>
                     <p className="font-bold text-sm text-slate-800 line-clamp-1">{t.partyName}</p>
                     <p className="text-xs text-slate-400">{t.date}</p>
                   </div>
                </div>
                <span className={`font-bold text-sm ${t.type === TransactionType.EXPENSE || t.type === TransactionType.PAYMENT_OUT ? 'text-red-500' : 'text-green-600'}`}>
                  {t.type === TransactionType.EXPENSE || t.type === TransactionType.PAYMENT_OUT ? '-' : '+'}₹{t.amount.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
          <button className="w-full text-center text-sm text-[#006A4E] font-bold hover:underline mt-4 pt-4 border-t border-slate-50">View All Transactions</button>
        </div>
      </div>
    </div>
  );
};

export default Overview;
