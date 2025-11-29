import React from 'react';
import { Mail, MessageCircle, MapPin } from 'lucide-react';

const Contact: React.FC = () => {
  return (
    <section className="pt-8 pb-16 md:pt-16 md:pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="bg-[#f2f4f3] rounded-[2.5rem] p-8 md:p-16 lg:p-24 relative overflow-hidden text-center md:text-left">
        <div className="max-w-4xl mx-auto">
          <div className="mb-16 text-center">
            <h1 className="text-h1-mobile md:text-5xl font-bold text-gray-900 mb-6">Get in touch</h1>
            <p className="text-xl text-gray-500 font-light">We're here to help streamline your business accounts.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* WhatsApp Card */}
            <a href="https://wa.me/+15551971304" target="_blank" rel="noopener noreferrer" className="group block">
              <div className="bg-white rounded-[2rem] p-8 shadow-soft hover:shadow-card transition-all duration-300 h-full flex flex-col items-center justify-center text-center border border-transparent hover:border-green-100 relative overflow-hidden">
                <div className="w-14 h-14 bg-green-50 text-brand-green rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <MessageCircle size={28} strokeWidth={1.5} />
                </div>
                <h3 className="font-bold text-xl text-gray-900 mb-2">WhatsApp</h3>
                <p className="text-gray-500 mb-6 text-sm">Chat directly with support </p>
                <span className="text-brand-green font-semibold text-sm group-hover:underline">Start Chat</span>
              </div>
            </a>

            {/* Email Card */}
            <a href="mailto:support@munimji.com" className="group block">
              <div className="bg-white rounded-[2rem] p-8 shadow-soft hover:shadow-card transition-all duration-300 h-full flex flex-col items-center justify-center text-center border border-transparent hover:border-green-100">
                <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Mail size={28} strokeWidth={1.5} />
                </div>
                <h3 className="font-bold text-xl text-gray-900 mb-2">Email</h3>
                <p className="text-gray-500 mb-6 text-sm">For general inquiries</p>
                <span className="text-blue-600 font-semibold text-sm group-hover:underline">Send Email</span>
              </div>
            </a>

            {/* Office Card */}
            <div className="bg-white rounded-[2rem] p-8 shadow-soft h-full flex flex-col items-center justify-center text-center cursor-default">
              <div className="w-14 h-14 bg-gray-50 text-gray-600 rounded-2xl flex items-center justify-center mb-6">
                <MapPin size={28} strokeWidth={1.5} />
              </div>
              <h3 className="font-bold text-xl text-gray-900 mb-2">Office</h3>
              <p className="text-gray-500 text-sm">Bangalore, India</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
