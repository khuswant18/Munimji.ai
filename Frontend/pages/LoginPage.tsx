import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../utils/auth';
import { authAPI } from '../utils/api';
import { MessageCircle, ArrowRight, Loader2 } from 'lucide-react';
import HeroVisual from '../components/HeroVisual';

const LoginPage: React.FC = () => {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (phone.length < 10) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    
    try {
      // Format phone number with +91
      const formattedPhone = phone.startsWith('+91') ? phone : `+91${phone}`;
      
      const response = await authAPI.login(formattedPhone);

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      if (response.data?.success && response.data.token && response.data.user) {
        console.log('✅ Login successful, token:', response.data.token);
        // Store token and user info
        login(response.data.token, response.data.user);
        console.log('✅ Token stored in localStorage');
        // Small delay to ensure localStorage is written
        setTimeout(() => {
          navigate('/dashboard');
        }, 100);
      } else {
        setError('Login failed. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  const handleWhatsAppLogin = () => {
    const text = `Login Request - ${phone || 'My Account'}`;
    window.open(`https://wa.me/919876543210?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-24 font-manrope">
      <div className="bg-white rounded-[3rem] shadow-soft max-w-5xl w-full overflow-hidden flex flex-col md:flex-row min-h-[600px] border border-white/50">
        
        {/* Left: Login Form */}
        <div className="w-full md:w-1/2 p-8 md:p-16 flex flex-col justify-center">
           <div className="mb-8">
             <div className="flex items-center gap-2 mb-6">
                <div className="w-8 h-8 bg-[#0F172A] rounded-full flex items-center justify-center text-white font-bold text-sm">M</div>
                <span className="font-bold text-xl text-[#0F172A]">Munimji</span>
             </div>
             <h1 className="text-3xl md:text-4xl font-bold text-[#0F172A] mb-3">Welcome to Munimji</h1>
             <p className="text-slate-500 leading-relaxed">
               Enter your phone number to instantly access your dashboard and view all your business transactions.
             </p>
           </div>

           <form onSubmit={handleLogin} className="space-y-6 max-w-sm">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-bold text-[#0F172A] mb-2">Phone Number</label>
                <div className="relative group">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium group-focus-within:text-[#006A4E] transition-colors">+91</span>
                  <input 
                    type="tel" 
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006A4E]/20 focus:border-[#006A4E] transition-all font-bold text-lg text-slate-800"
                    placeholder="98765 43210"
                    required
                    disabled={loading}
                  />
                </div>
              </div>
              
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-[#006A4E] hover:bg-[#005a42] text-white font-bold py-4 rounded-2xl transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" /> Loading your dashboard...
                  </>
                ) : (
                  <>
                    Continue <ArrowRight size={18} />
                  </>
                )}
              </button>

              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
                <div className="relative flex justify-center"><span className="bg-white px-4 text-xs text-slate-400 uppercase tracking-wider font-medium">Or</span></div>
              </div>

              <button 
                type="button"
                onClick={handleWhatsAppLogin}
                disabled={loading}
                className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold py-4 rounded-2xl transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <MessageCircle size={20} /> Sign in with WhatsApp
              </button>
            </form>
        </div>

        {/* Right: Visual */}
        <div className="hidden md:block w-1/2 bg-slate-50 relative overflow-hidden">
           <div className="absolute inset-0 bg-gradient-to-br from-[#006A4E]/5 to-slate-100"></div>
           <div className="relative h-full flex items-center justify-center p-12">
              <HeroVisual />
           </div>
        </div>

      </div>
    </div>
  );
};

export default LoginPage;
