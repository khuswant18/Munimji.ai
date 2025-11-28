import React from 'react';
import FAQAccordion from '../components/FAQAccordion';

const FAQPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h1>
      <FAQAccordion />
    </div>
  );
};

export default FAQPage;