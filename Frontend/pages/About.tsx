import React from 'react';

const About: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-8">About Munimji</h1>
      
      <div className="prose prose-lg text-gray-600">
        <p className="mb-6 text-xl leading-relaxed">
          Running a small business means juggling suppliers, customers, payments, and udhaar every day. 
          Most business owners rely on memory, scattered slips, and mental accounting — until numbers stop matching.
        </p>
        
        <p className="mb-6">
          Munimji was built to remove that headache. Instead of asking you to learn accounting software or open a separate app, 
          Munimji lets you update your books through the one place you already use daily: WhatsApp.
        </p>

        <div className="bg-green-50 border-l-4 border-primary p-6 my-8 rounded-r-xl">
          <p className="font-medium text-green-900 italic">
            Send “₹2000 sale to Ramesh”, snap a receipt, or forward a PDF challan — Munimji extracts and records everything instantly.
          </p>
        </div>

        <ul className="space-y-4 mb-8">
          <li className="flex items-center gap-3">
            <span className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold">✕</span>
            No spreadsheets.
          </li>
          <li className="flex items-center gap-3">
             <span className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold">✕</span>
            No late-night bookkeeping.
          </li>
          <li className="flex items-center gap-3">
             <span className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold">✕</span>
            No forgotten udhaar.
          </li>
        </ul>

        <p className="mb-8 font-semibold text-gray-900">
          Just clean, reliable records handled by your digital munim.
        </p>

        <hr className="my-8 border-gray-200" />

        <p className="text-sm text-gray-500">
          Munimji is not a bank and does not offer loans or financial products. 
          It simply keeps your business records accurate, simple, and stress-free without any Hustle.
        </p>
      </div>
    </div>
  );
};

export default About;
