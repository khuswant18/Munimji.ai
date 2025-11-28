import React from 'react';
import { MessageSquare, FileText, BarChart3 } from 'lucide-react';

const HowItWorks: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">How Munimji Works</h1>
        <p className="text-xl text-gray-500">Three simple steps to automate your bookkeeping.</p>
      </div>

      <div className="space-y-24">
        {/* Step 1 */}
        <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
                <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mb-6">
                    <MessageSquare size={32} />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">1. Send a message</h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                    Open Munimji on WhatsApp and type your transaction just like you would to a friend. 
                    <br/><br/>
                    Example: <i>"Sold 20 bags of cement to Rajesh for ₹8000"</i> or <i>"Paid electricity bill ₹1200"</i>.
                </p>
            </div>
            <div className="order-1 md:order-2 bg-gray-50 rounded-3xl h-64 md:h-80 flex items-center justify-center border border-gray-100">
                <span className="text-gray-400">Illustration: WhatsApp Chat Interface</span>
            </div>
        </div>

        {/* Step 2 */}
         <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-2">
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
                    <FileText size={32} />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">2. We process & organize</h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                    Our smart engine extracts the date, amount, category, and person involved. It automatically updates your sales register, expense log, or udhaar ledger.
                </p>
            </div>
            <div className="order-1 md:order-1 bg-gray-50 rounded-3xl h-64 md:h-80 flex items-center justify-center border border-gray-100">
                <span className="text-gray-400">Illustration: Data Processing</span>
            </div>
        </div>

        {/* Step 3 */}
         <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
                <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-2xl flex items-center justify-center mb-6">
                    <BarChart3 size={32} />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">3. Get Insights</h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                    Receive a daily summary every evening. See your total profit, outstanding collections, and cash flow without opening any spreadsheets.
                </p>
            </div>
            <div className="order-1 md:order-2 bg-gray-50 rounded-3xl h-64 md:h-80 flex items-center justify-center border border-gray-100">
                <span className="text-gray-400">Illustration: Reports</span>
            </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks;