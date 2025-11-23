import React from "react";
import { Link } from "react-router-dom";
import { TrendingUp } from "lucide-react";

const Footer: React.FC = () => {
  return (
    <footer id="footer" className="max-w-7xl mx-auto px-4 sm:px-6 pb-6">
      <div className="bg-gray-100 rounded-[1.5rem] py-8 md:py-10 px-8 md:px-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12 mb-10">
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 bg-black rounded-lg flex items-center justify-center text-white rotate-3">
                <img
                  src="./logo.png"
                  alt="Munimji logo"
                  className="h-10 w-auto object-contain"
                />
              </div>
              <span className="text-xl font-bold text-gray-900">Munimji</span>
            </div>
            <p className="text-gray-600 text-[0.95rem] leading-relaxed max-w-sm mb-4">
              Munimji helps businesses track sales, purchases and udhaar via
              WhatsApp. We are not a financial service provider.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-gray-900 mb-4 text-[0.95rem]">
              Resources
            </h4>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/about"
                  className="text-gray-600 hover:text-brand-green transition-colors text-[0.95rem]"
                >
                  About
                </Link>
              </li>
              <li>
                <Link
                  to="/pricing"
                  className="text-gray-600 hover:text-brand-green transition-colors text-[0.95rem]"
                >
                  Pricing
                </Link>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="text-gray-600 hover:text-brand-green transition-colors text-[0.95rem]"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  to="/terms"
                  className="text-gray-600 hover:text-brand-green transition-colors text-[0.95rem]"
                >
                  Terms & Conditions
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-gray-900 mb-4 text-[0.95rem]">
              Support
            </h4>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/contact"
                  className="text-gray-600 hover:text-brand-green transition-colors text-[0.95rem]"
                >
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-500">
          <p>Copyright © 2025 Munimji</p>
          <div className="flex gap-6">
            <Link to="/privacy" className="hover:text-gray-900">
              Privacy Policy
            </Link>
            <Link to="/terms" className="hover:text-gray-900">
              Terms & Conditions
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
