import React from 'react';

const Privacy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
      <p className="text-sm text-gray-500 mb-10">Effective date: November 29, 2025</p>
      
      <div className="space-y-8 text-gray-600">
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">1. Controller and Contact</h2>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Data Controller:</strong> Munimji</li>
            <li><strong>Contact:</strong> <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a></li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">2. Information We Collect</h2>
          <p>We collect information you provide directly when using Munimji via WhatsApp and our web interfaces, including:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Account information:</strong> Name and phone number (used to identify your account).</li>
            <li><strong>Messages and media:</strong> Text messages, photos, PDFs, and voice notes you send to the Munimji WhatsApp number.</li>
            <li><strong>Extracted transaction data:</strong> Structured information extracted from your messages and media (e.g., transaction dates, amounts, merchant names, categories).</li>
            <li><strong>Transaction metadata:</strong> Timestamps, message IDs, basic device/platform metadata provided by WhatsApp for message delivery.</li>
          </ul>
          <p className="mt-2">We may also collect usage and diagnostic data from the web app (e.g., page views, errors) for analytics and product improvement.</p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">3. How We Access WhatsApp Data</h2>
          <p>
            WhatsApp messages and media are delivered to Munimji through the <strong>WhatsApp Business API</strong> (a Meta service). Messages you send to our WhatsApp number pass through Meta's infrastructure. We do not scrape or access your personal WhatsApp conversations outside the messages you explicitly send to our Munimji number.
          </p>
          <p className="mt-2">
            When you contact Munimji via WhatsApp, Meta (WhatsApp) may process message metadata and content as described in their policies. Please review <a href="https://www.whatsapp.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">WhatsApp's Privacy Policy</a> for details.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">4. Purposes of Processing and Lawful Bases</h2>
          <p>We process your data for the following purposes:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Account creation & service delivery</strong> (performance of contract / consent): To create and operate your Munimji account and provide ledger services.</li>
            <li><strong>Transaction extraction & categorization</strong> (consent / legitimate interest): To extract transaction details from your messages and present them in your ledger, dashboards, and reports.</li>
            <li><strong>Analytics & product improvement</strong> (legitimate interest): To improve OCR/text recognition and product features.</li>
            <li><strong>Legal obligations & fraud prevention</strong> (legal compliance / legitimate interest): To comply with applicable laws and protect against fraud or abuse.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">5. Data Sharing and Disclosure</h2>
          <p><strong>We do not sell personal data.</strong></p>
          <p className="mt-2">We share data only as necessary to operate the service:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>WhatsApp/Meta:</strong> Messages are routed through Meta's WhatsApp Business API. Meta may process messaging data for delivery, spam detection, and platform analytics.</li>
            <li><strong>Third-party processors:</strong> We use trusted service providers (cloud hosting, file storage, OCR providers, analytics) bound by contract and security obligations.</li>
            <li><strong>Legal requests:</strong> We may disclose data to comply with lawful requests (court orders, law enforcement).</li>
            <li><strong>Aggregated data:</strong> We may use or share aggregated insights that do not identify you.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">6. International Transfers</h2>
          <p>
            Some processors and Meta services may store or process data outside your country. Where data is transferred cross-border, we use legal safeguards as required (e.g., standard contractual clauses).
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">7. Data Retention</h2>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Raw media</strong> (photos, voice notes, PDFs): Automatically deleted from our servers after 30 days.</li>
            <li><strong>Extracted transaction data:</strong> Retained until you request deletion of your account or as required by law.</li>
            <li><strong>Backup copies:</strong> May be retained briefly for disaster recovery with the same retention rationale.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">8. Your Rights and Choices</h2>
          <p>Depending on your jurisdiction, you may have the following rights:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Access:</strong> Request a copy of personal data we hold about you.</li>
            <li><strong>Rectification:</strong> Correct inaccurate personal data.</li>
            <li><strong>Data portability:</strong> Obtain your transaction data in machine-readable format (CSV).</li>
            <li><strong>Erasure:</strong> Request deletion of your account and personal data.</li>
            <li><strong>Restriction / objection:</strong> Restrict or object to certain processing.</li>
            <li><strong>Withdraw consent:</strong> For non-essential processing where consent was the lawful basis.</li>
          </ul>
          <p className="mt-2">To exercise these rights, contact: <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a></p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">9. Security</h2>
          <p>
            We implement administrative, physical, and technical safeguards to protect personal data (encryption in transit, limited access controls, secure storage). However, no system is completely secure; if a breach occurs we will notify affected users and authorities as required by law.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">10. Automated Decision-Making</h2>
          <p>
            We use automated processing (OCR, parsing, categorization) to extract and classify transaction data. These processes populate your ledger and produce summaries. We do not make high-risk automated decisions about you solely on automated processing without human review.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">11. Children</h2>
          <p>
            Our service is not intended for children under the applicable age (e.g., 13/16 depending on jurisdiction). We do not knowingly collect data from children. If you believe a child has provided us with personal data, contact <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">12. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy periodically. We will post the revised date and, where required, seek consent for material changes.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">13. Platform-Specific Note for Meta/WhatsApp</h2>
          <p>
            Because Munimji uses the WhatsApp Business API, Meta's policies and processing apply to messages you send through WhatsApp. By using Munimji via WhatsApp, you consent to the transfer and processing of your messages by Meta. Review <a href="https://www.whatsapp.com/legal/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">WhatsApp's Legal Information</a> and <a href="https://www.facebook.com/privacy/policy/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Meta's Privacy Policy</a> for more details.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">14. Contact</h2>
          <p>
            For privacy questions or requests, please email us at <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a>.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Privacy;
