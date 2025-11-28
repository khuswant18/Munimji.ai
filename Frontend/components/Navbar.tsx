import React, { useState, useEffect } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { isAuthenticated, logout } from "../utils/auth";
import ProfileDropdown from "./ProfileDropdown";

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  // Keeping existing links as requested
  const isDashboard = location.pathname.startsWith('/dashboard');

  const navLinks = !isDashboard ? [
    { name: "Home", path: "/" },
    { name: "About", path: "/about" },
    { name: "Dashboard", path: isAuthenticated() ? "/dashboard" : "/login" },
  ] : [
    { name: 'Overview', path: '/dashboard' },
    { name: 'Ledger', path: '/dashboard/ledger' },
    { name: 'Customers', path: '/dashboard/customers' },
    { name: 'Suppliers', path: '/dashboard/suppliers' },
    { name: 'Cashbook', path: '/dashboard/cashbook' },
    { name: 'Expenses', path: '/dashboard/expenses' },
    { name: 'Reports', path: '/dashboard/reports' },
  ];

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 px-4 pt-4 ${
        isScrolled ? "pt-2" : "pt-6"
      }`}
    >
      <nav
        className={`mx-auto max-w-6xl bg-white/90 backdrop-blur-md border border-gray-100 rounded-full px-6 py-3 flex items-center justify-between shadow-sm transition-all duration-300 ${
          isScrolled ? "py-2" : "py-3"
        }`}
      >
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 cursor-pointer">
          <img
            src="./logo.png"
            alt="Munimji logo"
            className="h-10 w-auto object-contain"
          />
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <NavLink
              key={link.name}
              to={link.path}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors ${
                  isActive
                    ? "text-brand-green font-bold"
                    : "text-gray-600 hover:text-gray-900"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </div>

        {/* Right CTA */}
        <div className="hidden md:flex items-center">
          {isAuthenticated() ? (
            <ProfileDropdown />
          ) : (
            <a
              href="https://wa.me/1234567890?text=I%20want%20to%20try%20Munimji"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#006A4E] hover:bg-[#005a42] text-white text-sm font-semibold py-2.5 px-6 rounded-full transition-colors flex items-center gap-2 shadow-md shadow-green-900/10"
            >
              Try Now
              <img src="./whatsapp.png" className="h-5 w-auto" />
            </a>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden text-gray-600 p-1"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="absolute top-full left-4 right-4 mt-2 bg-white rounded-2xl shadow-xl border border-gray-100 p-4 md:hidden flex flex-col gap-2">
          {navLinks.map((link) => (
            <NavLink
              key={link.name}
              to={link.path}
              className={({ isActive }) =>
                `p-3 text-left rounded-xl transition-colors font-medium ${
                  isActive
                    ? "bg-green-50 text-brand-green"
                    : "text-gray-700 hover:bg-gray-50"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
          <hr className="my-2 border-gray-100" />
          {isAuthenticated() ? (
             <button
                onClick={() => {
                   logout();
                   navigate('/login');
                }}
                className="w-full bg-red-50 text-red-600 font-semibold py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-red-100 transition-colors"
             >
                Sign Out
             </button>
          ) : (
            <a
              href="https://wa.me/1234567890?text=I%20want%20to%20try%20Munimji"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-[#006A4E] text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-[#005a42] transition-colors"
            >
              Try Now <img src="./whatsapp.png" className="h-5 w-auto" />
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default Navbar;
