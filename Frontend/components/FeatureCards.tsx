import React from 'react';
import { TrendingUp, PieChart, BookOpen } from 'lucide-react';

const FeatureCards: React.FC = () => {
  const features = [
    {
      icon: TrendingUp,
      title: "Track",
      desc: "Record every sale, purchase, and udhaar directly from WhatsApp. Munimji extracts details automatically and organizes your books."
    },
    {
      icon: PieChart,
      title: "Insights",
      desc: "Get daily and monthly summaries that clearly show how much you earned, what you bought, and how your business is performing."
    },
    {
      icon: BookOpen,
      title: "Udhaar Ledger",
      desc: "Maintain a simple, reliable ledger of who owes you and whom you owe — updated instantly every time you send a WhatsApp message."
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {features.map((feature, i) => {
        const Icon = feature.icon;
        return (
          <div key={i} className="bg-gray-50 rounded-3xl p-6 hover:bg-[#F3F6F4] transition-colors duration-300">
            <div className="w-10 h-10 text-brand-green mb-4">
              <Icon size={36} strokeWidth={1.5} />
            </div>
            <h3 className="text-card-title font-bold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-card-body text-gray-600 leading-relaxed">
              {feature.desc}
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default FeatureCards;