import React, { useState, useRef, useEffect } from 'react';
import { User, LogOut, Settings, ChevronDown, CreditCard, HelpCircle } from 'lucide-react';
import { useNavigate, NavLink } from 'react-router-dom';
import { logout } from '../utils/auth';

const ProfileDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 text-slate-700 hover:text-[#006A4E] transition-colors focus:outline-none"
      >
        <div className="w-10 h-10 bg-[#006A4E]/10 rounded-full flex items-center justify-center border border-[#006A4E]/20">
          <User className="w-5 h-5 text-[#006A4E]" />
        </div>
        <span className="font-medium hidden md:block font-manrope">My Business</span>
        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-3xl shadow-soft py-2 border border-slate-100 z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-50">
            <p className="text-sm font-medium text-slate-900 font-manrope">Ravi Kirana Store</p>
            <p className="text-xs text-slate-500 font-manrope">+91 98765 43210</p>
          </div>
          
          <div className="py-1">
            <NavLink to="/dashboard/settings#profile" onClick={() => setIsOpen(false)} className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 flex items-center space-x-2 transition-colors font-manrope">
              <User className="w-4 h-4" />
              <span>Profile</span>
            </NavLink>
            <NavLink to="/dashboard/settings#business" onClick={() => setIsOpen(false)} className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 flex items-center space-x-2 transition-colors font-manrope">
              <Settings className="w-4 h-4" />
              <span>Business Info</span>
            </NavLink>
            <NavLink to="/dashboard/settings#billing" onClick={() => setIsOpen(false)} className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 flex items-center space-x-2 transition-colors font-manrope">
              <CreditCard className="w-4 h-4" />
              <span>Billing</span>
            </NavLink>
            <NavLink to="/dashboard/help" onClick={() => setIsOpen(false)} className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 flex items-center space-x-2 transition-colors font-manrope">
              <HelpCircle className="w-4 h-4" />
              <span>Help & Support</span>
            </NavLink>
            <button 
              onClick={handleLogout}
              className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2 transition-colors font-manrope"
            >
              <LogOut className="w-4 h-4" />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileDropdown;
