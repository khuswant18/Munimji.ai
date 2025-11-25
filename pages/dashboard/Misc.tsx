import React from 'react';
import { User, CreditCard, MessageCircle, FileText, Download } from 'lucide-react';

export const SettingsView: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in font-manrope">
       <h2 className="text-2xl font-bold text-slate-800">Settings</h2>
       
       <div id="profile" className="bg-white rounded-3xl p-8 shadow-soft border border-slate-100">
          <div className="flex items-center gap-4 mb-6">
             <div className="w-16 h-16 bg-[#006A4E]/5 text-[#006A4E] rounded-full flex items-center justify-center">
                <User size={32} />
             </div>
             <div>
                <h3 className="text-xl font-bold text-slate-800">Rohan's Store</h3>
                <p className="text-slate-500">+91 98765 43210</p>
             </div>
             <button className="ml-auto text-[#006A4E] font-bold text-sm">Edit</button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Business Name</label>
                <input type="text" value="Rohan's General Store" disabled className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-slate-600" />
             </div>
             <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Email</label>
                <input type="text" value="rohan@example.com" disabled className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-slate-600" />
             </div>
          </div>
       </div>

       <div id="billing" className="bg-white rounded-3xl p-8 shadow-soft border border-slate-100">
          <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2"><CreditCard size={20} /> Subscription</h3>
          <div className="bg-[#006A4E]/5 rounded-2xl p-6 flex justify-between items-center">
             <div>
                <p className="font-bold text-[#0F172A]">Free Plan</p>
                <p className="text-sm text-[#006A4E]">Basic ledger features</p>
             </div>
             <button className="bg-[#006A4E] text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-[#005a42]">Upgrade</button>
          </div>
       </div>
    </div>
  );
};

export const HelpView: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in text-center py-12 font-manrope">
        <div className="w-24 h-24 bg-green-50 text-green-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
            <MessageCircle size={48} />
        </div>
        <h2 className="text-3xl font-bold text-slate-800">How can we help?</h2>
        <p className="text-slate-500">Our support team is available on WhatsApp 24/7.</p>
        
        <button 
           onClick={() => window.open('https://wa.me/919876543210', '_blank')}
           className="bg-[#25D366] text-white text-lg font-bold px-8 py-4 rounded-full shadow-lg hover:bg-[#20bd5a] transition-all flex items-center gap-2 mx-auto"
        >
            <MessageCircle size={24} /> Chat with Support
        </button>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left mt-12">
           <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <h4 className="font-bold text-slate-800 mb-2">Documentation</h4>
              <p className="text-sm text-slate-500">Read guides on how to use Munimji effectively.</p>
           </div>
           <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <h4 className="font-bold text-slate-800 mb-2">Video Tutorials</h4>
              <p className="text-sm text-slate-500">Watch step-by-step videos.</p>
           </div>
        </div>
    </div>
  );
};

export const ReportsView: React.FC = () => {
    const reports = [
        { title: 'Profit & Loss', desc: 'Monthly summary of income and expenses' },
        { title: 'Sales by Customer', desc: 'Detailed breakdown of sales per client' },
        { title: 'Expense Category', desc: 'Where is your money going?' },
        { title: 'Udhaar Aging', desc: 'Pending payments overdue by time' },
    ];

    return (
        <div className="space-y-8 animate-in fade-in font-manrope">
             <h2 className="text-2xl font-bold text-slate-800">Financial Reports</h2>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 {reports.map((r, i) => (
                    <div key={i} className="bg-white p-6 rounded-3xl shadow-soft border border-slate-100 flex justify-between items-center group cursor-pointer hover:border-[#006A4E]/20 transition-all">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-slate-50 text-[#006A4E] rounded-xl flex items-center justify-center group-hover:bg-[#006A4E]/5 transition-colors">
                                <FileText size={24} />
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-800">{r.title}</h4>
                                <p className="text-xs text-slate-500">{r.desc}</p>
                            </div>
                        </div>
                        <button className="text-slate-300 group-hover:text-[#006A4E] transition-colors">
                            <Download size={20} />
                        </button>
                    </div>
                 ))}
             </div>
        </div>
    );
};
