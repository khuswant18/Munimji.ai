import React from 'react';
import { FileText, Camera, Mic, Mail } from 'lucide-react';

const LogItYourWay: React.FC = () => {
  const chips = [
    { icon: FileText, label: 'PDF Bill', desc: 'Auto-parse totals, dates, and merchants.' },
    { icon: Camera, label: 'Receipt Photo', desc: 'Snap and we\'ll do the rest.' },
    { 
      icon: Mail, 
      label: 'Email Forward', 
      desc: 'Forward bills to bills@munimji.ai.', 
      badge: 'soon' 
    },
    { icon: Mic, label: 'Voice Note', desc: 'Say "₹620 taxi yesterday" (beta).' },
  ];

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {chips.map((chip, idx) => {
          const Icon = chip.icon;
          return (
            <div key={idx} className="bg-gray-50 hover:bg-white hover:shadow-lg transition-all duration-300 border border-gray-100 rounded-2xl p-6 group cursor-default relative">
              {chip.badge && (
                <span className="absolute top-4 right-4 bg-green-100 text-brand-green text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide">
                  {chip.badge}
                </span>
              )}
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center text-brand-green group-hover:scale-110 transition-transform">
                  <Icon size={20} />
                </div>
              </div>
              <h4 className="font-bold text-gray-900 text-card-title mb-2">{chip.label}</h4>
              <p className="text-card-body text-gray-500 leading-relaxed">{chip.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LogItYourWay;