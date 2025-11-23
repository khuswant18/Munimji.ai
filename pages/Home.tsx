import React from "react";
import { Link } from "react-router-dom";
import { MessageCircle } from "lucide-react";
import DashboardPreview from "../components/DashboardPreview";
import FeatureCards from "../components/FeatureCards";
import FAQAccordion from "../components/FAQAccordion";
import LogItYourWay from "../components/LogItYourWay";

const Home: React.FC = () => {
  return (
    <>
      {/* Hero Section */}
      <section className="pt-8 pb-16 md:pt-16 md:pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="bg-[#f2f4f3] rounded-[2.5rem] p-5 md:p-8 lg:p-12 relative overflow-hidden">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            {/* Left Content */}
            <div className="relative z-10 max-w-[720px] mx-auto lg:mx-0 text-center lg:text-left pt-6 lg:pt-0">
              {/* Badge Removed */}

              <h1 className="text-h1-mobile md:text-5xl lg:text-h1-desktop font-bold text-gray-900 leading-tight mb-5">
                Your business accounts, simplified.
                <br className="hidden md:block" />
                <span className="block mt-2">
                  Log sales, buys, and udhaar — right from WhatsApp.
                </span>
              </h1>

              <p className="text-base md:text-lg text-gray-600 mb-8 leading-relaxed max-w-[560px] mx-auto lg:mx-0">
                Send a text, photo, PDF, or voice note — Munimji logs it and
                keeps your books updated automatically.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <a
                  href="https://wa.me/1234567890"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-brand-green hover:bg-brand-dark text-white px-6 py-3 min-h-[44px] rounded-full font-semibold text-base transition-all flex items-center justify-center gap-2 shadow-xl shadow-green-900/10 hover:shadow-primary/20 transform hover:-translate-y-0.5"
                >
                  {/* <MessageCircle size={18} />  */}
                  <img src="./whatsapp.png" className="h-5 w-auto" />
                  Try on WhatsApp
                </a>
                <Link
                  to="/about"
                  className="bg-white hover:bg-gray-50 text-gray-900 px-6 py-3 min-h-[44px] rounded-full font-semibold text-base transition-all border border-gray-200 flex items-center justify-center hover:shadow-md"
                >
                  Read our story
                </Link>
              </div>
            </div>

            {/* Right Content - Visual */}
            <div className="relative z-10 lg:w-[80%] mx-auto lg:ml-auto lg:mr-0 h-[400px] md:h-[500px] flex items-center justify-center">
              <DashboardPreview />
            </div>
          </div>
        </div>
      </section>

      {/* Log it your way Section */}
      <section className="max-w-7xl mx-auto mt-24 mb-20 px-4 md:px-12">
        <div className="text-center mb-12">
          <h2 className="text-h1-mobile md:text-h2 font-bold mb-4 tracking-tight text-gray-900">
            Log it your way
          </h2>
          <p className="text-lg text-gray-500 max-w-[70ch] mx-auto">
            Text files or photos - Munimji understands them all.
          </p>
        </div>
        <LogItYourWay />
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto mb-32 px-4 md:px-12">
        <div className="mb-16 text-center md:text-left">
          <h2 className="text-h1-mobile md:text-h2 font-bold mb-6 tracking-tight text-gray-900">
            Everything your records need, <br />
            nothing extra
          </h2>
          <p className="text-lg text-gray-500 max-w-[70ch]">
            A simple WhatsApp-based workflow that keeps your sales, buys, and
            udhaar organized — without apps, spreadsheets, or after-hours
            bookkeeping.
          </p>
        </div>
        <img
          src="./banner.png"
          
        ></img>
        <br></br>
        <FeatureCards />
      </section>

      {/* FAQ Section */}
      <section id="faq" className="max-w-7xl mx-auto mb-32 px-4 md:px-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24">
          <div className="lg:col-span-4">
            <h2 className="text-h1-mobile md:text-h2 font-bold mb-6 tracking-tight text-gray-900">
              Frequently <br />
              Asked Questions
            </h2>
            <p className="text-lg text-gray-500 mb-8">
              Quick answers about how Munimji works today.
            </p>
            <div className="hidden lg:block bg-gray-50 p-8 rounded-3xl">
              <h4 className="font-bold text-lg mb-2 text-gray-900">
                Still have a question?
              </h4>
              <p className="text-gray-600 mb-6 text-sm">
                Can't find what you're looking for? Contact us, and we'll be
                happy to help!
              </p>
              <Link
                to="/contact"
                className="inline-block bg-brand-green text-white font-semibold px-6 py-3 min-h-[44px] rounded-full hover:bg-brand-dark transition-colors"
              >
                Contact Us
              </Link>
            </div>
          </div>

          <div className="lg:col-span-8">
            <FAQAccordion />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto mb-20 px-4 md:px-12">
        <div className="relative bg-brand-green/10 bg-gradient-to-br from-[#A0C4BC] to-[#5E9C8F] rounded-[3rem] px-6 py-20 text-center overflow-hidden">
          <div
            className="absolute inset-0 opacity-20 mix-blend-overlay"
            style={{
              backgroundImage:
                "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
            }}
          ></div>

          <div className="relative z-10">
            <h2 className="text-2xl md:text-4xl font-bold text-white mb-8 drop-shadow-md">
              Be the first to experience smarter business money!
            </h2>
            <a
              href="https://wa.me/1234567890?text=I%20want%20to%20try%20Munimji"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-[#006A4E] hover:bg-[#004D38] text-white text-lg font-bold px-8 py-4 min-h-[44px] rounded-full transition-transform hover:scale-105 shadow-xl"
            >
              Try Munimji on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </>
  );
};

export default Home;
