import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface FAQItemProps {
  question: string;
  answer: string;
  isOpen: boolean;
  onClick: () => void;
}

const FAQItem: React.FC<FAQItemProps> = ({ question, answer, isOpen, onClick }) => {
  return (
    <div className="border-b border-gray-100 last:border-0">
      <button
        className="w-full py-6 flex items-center justify-between text-left focus:outline-none group"
        onClick={onClick}
        aria-expanded={isOpen}
      >
        <span className="text-lg font-medium text-gray-900 group-hover:text-brand-green transition-colors">
          {question}
        </span>
        <ChevronDown 
          className={`w-5 h-5 text-gray-500 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-48 opacity-100 pb-6' : 'max-h-0 opacity-0'}`}
      >
        <p className="text-gray-600 leading-relaxed">
          {answer}
        </p>
      </div>
    </div>
  );
};

const faqs = [
  {
    question: "How do I get access?",
    answer: "Tap Try Now to message us on WhatsApp. We’ll activate your account instantly and guide you through your first entry."
  },
  {
    question: "Is Munimji free?",
    answer: "Munimji is free during beta. We will introduce paid plans later with advanced summaries and export options."
  },
  {
    question: "How do I record sales or purchases?",
    answer: "Just send a WhatsApp message like “₹2500 sale from Rohan” or “Bought materials ₹1800”. You can also send a photo or PDF. Munimji extracts and logs everything."
  },
  {
    question: "How does udhaar tracking work?",
    answer: "Mention who owes whom in your message (e.g. “Udhaar ₹1500 from Aman”). Munimji keeps a running ledger of all credit given or received."
  },
  {
    question: "What kind of summaries do I get?",
    answer: "Daily and monthly overviews showing total sales, total purchases, outstanding udhaar, and net position."
  },
  {
    question: "Can I export my records?",
    answer: "Yes. You can download your data as a CSV for your accountant or GST filing."
  }
];

const FAQAccordion: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="bg-gray-50 rounded-[2rem] p-8 md:p-12">
      {faqs.map((faq, index) => (
        <FAQItem
          key={index}
          question={faq.question}
          answer={faq.answer}
          isOpen={openIndex === index}
          onClick={() => setOpenIndex(openIndex === index ? null : index)}
        />
      ))}
    </div>
  );
};

export default FAQAccordion;