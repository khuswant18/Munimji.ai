import React from 'react';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';
import { User, Receipt, FileText, Mic, MessageCircle } from 'lucide-react';

const data = [
  { name: 'Mon', val: 40 },
  { name: 'Tue', val: 30 },
  { name: 'Wed', val: 60 },
  { name: 'Thu', val: 45 },
  { name: 'Fri', val: 80 },
  { name: 'Sat', val: 55 },
];

const HeroVisual: React.FC = () => {
  return (
    <div className="relative w-full h-full min-h-[400px] flex items-center justify-center font-manrope">
      {/* Background Shapes */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-tr from-[#006A4E]/5 to-transparent rounded-full opacity-60 blur-3xl -z-10"></div>

      {/* Main Dashboard Card Replica */}
      <div className="bg-white rounded-3xl p-6 shadow-card w-full max-w-sm relative z-10 border border-slate-50/50">
        
        {/* Floating Notification */}
        <div className="absolute -top-12 -right-4 bg-[#006A4E] text-white p-4 rounded-2xl shadow-xl max-w-[220px] animate-bounce-slow">
           <p className="text-xs opacity-80 mb-1">WhatsApp message received</p>
           <p className="font-bold text-sm">"Sold 50kg rice to Ravi ₹2500"</p>
        </div>

        <div className="mb-6">
          <p className="text-slate-500 text-xs font-medium uppercase tracking-wide mb-1">Total Sales</p>
          <h3 className="text-3xl font-bold text-slate-800">₹84,500</h3>
          <div className="inline-block bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full mt-2">+15%</div>
        </div>

        {/* Chart */}
        <div className="h-32 mb-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <Bar dataKey="val" radius={[4, 4, 4, 4]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 4 ? '#006A4E' : '#E2E8F0'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Feature Icons Row */}
        <div className="flex justify-between items-center gap-2">
            <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center">
                    <FileText size={18} />
                </div>
                <span className="text-[10px] text-slate-500 font-medium">PDF Bill</span>
            </div>
            <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center">
                    <Receipt size={18} />
                </div>
                <span className="text-[10px] text-slate-500 font-medium">Receipt</span>
            </div>
            <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 bg-orange-50 text-orange-600 rounded-xl flex items-center justify-center">
                    <Mic size={18} />
                </div>
                <span className="text-[10px] text-slate-500 font-medium">Voice</span>
            </div>
        </div>
      </div>

      {/* Floating Card: User */}
      <div className="absolute -bottom-6 -right-2 md:right-8 bg-white p-4 rounded-2xl shadow-lg border border-slate-100 flex items-center gap-3 animate-pulse-slow">
        <div className="w-10 h-10 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center">
            <User size={20} />
        </div>
        <div>
            <p className="font-bold text-sm text-slate-800">Rohan (Udhaar)</p>
            <p className="text-[#006A4E] font-bold text-sm">₹1,200</p>
        </div>
      </div>

      {/* Floating Pill: Actions */}
      <div className="absolute bottom-20 -left-6 bg-white py-2 px-4 rounded-full shadow-lg border border-slate-100 flex items-center gap-2 text-xs text-slate-500">
         <MessageCircle size={14} className="text-green-500" /> via WhatsApp
         <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px]">#auto-reminder</span>
      </div>

    </div>
  );
};

export default HeroVisual;
