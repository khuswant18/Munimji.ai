import React from 'react';

const Privacy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-10">Privacy Policy</h1>
      
      <div className="space-y-8 text-gray-600">
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">1. Information We Collect</h2>
          <p>
            We collect information you expressly provide to use via WhatsApp, including:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
             <li>Your name and phone number (to create your account).</li>
             <li>Text messages, photos, PDFs, and voice notes sent to the Munimji WhatsApp number.</li>
             <li>Transaction details extracted from the above media (dates, amounts, merchant names).</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">2. How We Use Your Data</h2>
          <p>
            Your data is used solely for:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
             <li>Logging your sales, purchases, and udhaar records.</li>
             <li>Generating daily and monthly financial summaries.</li>
             <li>Improving our text and image recognition (OCR) accuracy.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">3. Data Sharing</h2>
          <p>
            We do not sell your personal data. We share data only with trusted third-party service providers necessary to operate our service (e.g., cloud hosting, WhatsApp API providers).
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">4. Data Retention</h2>
          <p>
            Raw media files (images of receipts, voice notes) are automatically deleted from our servers after 30 days. We retain the extracted transaction data to maintain your ledger history until you delete your account.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">5. Your Rights</h2>
          <p>
            You can request an export of your data (CSV format), correction of records, or complete deletion of your account and data at any time by contacting support.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">6. Contact</h2>
          <p>
            For any privacy concerns, please email us at <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a>.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Privacy;