import React from 'react';

const Terms: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-10">Terms & Conditions</h1>
      
      <div className="space-y-8 text-gray-600">
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">1. Acceptance of Terms</h2>
          <p>
            By using Munimji via WhatsApp or our website, you agree to these Terms and Conditions. If you do not agree, please do not use our services.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">2. Description of Service</h2>
          <p>
            Munimji is a digital bookkeeping tool that allows users to record business transactions via WhatsApp. We are a technology provider, not a financial institution, bank, or lender.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">3. User Responsibilities</h2>
          <p>
            You are responsible for the accuracy of the data you submit. You must not use the service for any illegal activities. You are responsible for maintaining the security of your WhatsApp account.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">4. No Financial Advice</h2>
          <p>
            Munimji provides data organization and summaries. We do not provide financial, tax, or legal advice. Please consult a qualified professional for such needs.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">5. Limitation of Liability</h2>
          <p>
            To the fullest extent permitted by law, Munimji shall not be liable for any indirect, incidental, or consequential damages arising from the use or inability to use the service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">6. Termination</h2>
          <p>
            We reserve the right to suspend or terminate your access to Munimji at our sole discretion, without notice, for conduct that we believe violates these Terms.
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">7. Governing Law</h2>
          <p>
            These terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of the courts in India.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">8. Contact</h2>
          <p>
            Questions about the Terms of Service should be sent to us at <a href="mailto:support@munimji.com" className="text-primary hover:underline">support@munimji.com</a>.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Terms;