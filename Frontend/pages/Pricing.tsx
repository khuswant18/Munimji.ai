import React from 'react';
import { Check } from 'lucide-react';

const Pricing: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h1>
      <p className="text-xl text-gray-500 mb-16">Munimji is currently in Beta and completely free.</p>

      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-[2rem] p-8 shadow-xl border-2 border-primary relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-primary text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
            CURRENT PLAN
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Beta Access</h2>
          <div className="text-5xl font-bold text-gray-900 mb-6">Free</div>
          <p className="text-gray-500 mb-8">Everything you need to manage your business books.</p>
          
          <ul className="text-left space-y-4 mb-8">
            <li className="flex items-center gap-3">
              <span className="bg-green-100 text-green-600 rounded-full p-1"><Check size={14}/></span>
              Unlimited Transactions
            </li>
            <li className="flex items-center gap-3">
              <span className="bg-green-100 text-green-600 rounded-full p-1"><Check size={14}/></span>
              Daily & Monthly Reports
            </li>
            <li className="flex items-center gap-3">
              <span className="bg-green-100 text-green-600 rounded-full p-1"><Check size={14}/></span>
              Udhaar Ledger
            </li>
            <li className="flex items-center gap-3">
              <span className="bg-green-100 text-green-600 rounded-full p-1"><Check size={14}/></span>
              PDF/Image Scanning
            </li>
          </ul>

          <a href="https://wa.me/1234567890" className="block w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-xl transition-colors">
            Get Started Free
          </a>
        </div>
      </div>
    </div>
  );
};

export default Pricing;