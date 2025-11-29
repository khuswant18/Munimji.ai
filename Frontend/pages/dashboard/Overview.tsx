import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Wallet, ArrowUpRight, ArrowDownLeft, Loader2 } from 'lucide-react';
import { dashboardAPI, OverviewData } from '../../utils/api';
import { CHART_DATA_WEEKLY } from '../../utils/constants';

const Overview: React.FC = () => {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    setLoading(true);
    const response = await dashboardAPI.getOverview();
    setLoading(false);

    if (response.error) {
      setError(response.error);
      return;
    }

    if (response.data) {
      setData(response.data);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin text-[#006A4E]" size={40} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-600">
        <p className="font-bold mb-2">Error loading dashboard</p>
        <p className="text-sm">{error}</p>
        <button 
          onClick={loadOverview}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500 font-manrope">
      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#0F172A] rounded-3xl p-6 text-white shadow-card relative overflow-hidden group hover:shadow-xl transition-all">
           <div className="absolute -right-4 -top-4 w-32 h-32 bg-[#1E293B] rounded-full blur-2xl opacity-50 group-hover:scale-110 transition-transform"></div>
           <div className="relative z-10">
              <p className="text-slate-300 text-sm font-medium mb-1">Net Income</p>
              <h3 className="text-3xl font-bold">₹{data.net_income.toLocaleString()}</h3>
              <div className="mt-4 flex gap-2">
                 <span className="bg-white/10 px-2 py-1 rounded-lg text-xs flex items-center gap-1">
                   <ArrowUpRight size={12} /> Current Period
                 </span>
              </div>
           </div>
        </div>
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 hover:border-[#006A4E]/20 transition-colors">
           <div className="flex justify-between items-start mb-2">
              <p className="text-slate-500 text-sm font-medium">Total Sales</p>
              <div className="p-2 bg-green-50 text-green-600 rounded-lg"><Wallet size={18} /></div>
           </div>
           <h3 className="text-3xl font-bold text-slate-800">₹{data.total_sales.toLocaleString()}</h3>
           <p className="text-xs text-slate-400 mt-2">Revenue from sales</p>
        </div>
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 hover:border-[#006A4E]/20 transition-colors">
           <div className="flex justify-between items-start mb-2">
              <p className="text-slate-500 text-sm font-medium">Total Expenses</p>
              <div className="p-2 bg-red-50 text-red-600 rounded-lg"><ArrowDownLeft size={18} /></div>
           </div>
           <h3 className="text-3xl font-bold text-slate-800">₹{data.total_expenses.toLocaleString()}</h3>
           <p className="text-xs text-slate-400 mt-2">Purchases: ₹{data.total_purchases.toLocaleString()}</p>
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
            {data.recent_activity && data.recent_activity.length > 0 ? (
              data.recent_activity.map(t => (
                <div key={t.id} className="flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                     <div className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-colors ${
                       t.type === 'expense' || t.type === 'purchase' || t.type === 'payment' 
                         ? 'bg-red-50 text-red-500 group-hover:bg-red-100' 
                         : 'bg-green-50 text-green-600 group-hover:bg-green-100'
                     }`}>
                        {t.type === 'expense' || t.type === 'purchase' || t.type === 'payment' 
                          ? <ArrowDownLeft size={18} /> 
                          : <ArrowUpRight size={18} />}
                     </div>
                     <div>
                       <p className="font-bold text-sm text-slate-800 line-clamp-1">
                         {t.counterparty_name || t.description || t.type}
                       </p>
                       <p className="text-xs text-slate-400">{t.date || 'Recent'}</p>
                     </div>
                  </div>
                  <span className={`font-bold text-sm ${
                    t.type === 'expense' || t.type === 'purchase' || t.type === 'payment'
                      ? 'text-red-500' 
                      : 'text-green-600'
                  }`}>
                    {t.type === 'expense' || t.type === 'purchase' || t.type === 'payment' ? '-' : '+'}₹{t.amount.toLocaleString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-center py-8">No recent transactions</p>
            )}
          </div>
          <button className="w-full text-center text-sm text-[#006A4E] font-bold hover:underline mt-4 pt-4 border-t border-slate-50">View All Transactions</button>
        </div>
      </div>
    </div>
  );
};

export default Overview;
