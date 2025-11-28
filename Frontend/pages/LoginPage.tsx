import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../utils/auth';
import { MessageCircle, ArrowRight } from 'lucide-react';
import HeroVisual from '../components/HeroVisual';

const LoginPage: React.FC = () => {
  const [phone, setPhone] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const navigate = useNavigate();

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.length >= 10) {
      setOtpSent(true);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp === '1234') { 
      login(phone);
      navigate('/dashboard');
    } else {
      alert('Invalid OTP. Use 1234');
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
             <h1 className="text-3xl md:text-4xl font-bold text-[#0F172A] mb-3">Welcome back</h1>
             <p className="text-slate-500 leading-relaxed">
               You were onboarded via WhatsApp — please use the same phone number to access your dashboard.
             </p>
           </div>

           {!otpSent ? (
            <form onSubmit={handleSendOtp} className="space-y-6 max-w-sm">
              <div>
                <label className="block text-sm font-bold text-[#0F172A] mb-2">Phone Number</label>
                <div className="relative group">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium group-focus-within:text-[#006A4E] transition-colors">+91</span>
                  <input 
                    type="tel" 
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006A4E]/20 focus:border-[#006A4E] transition-all font-bold text-lg text-slate-800"
                    placeholder="98765 43210"
                    required
                  />
                </div>
              </div>
              
              <button type="submit" className="w-full bg-[#0F172A] hover:bg-slate-800 text-white font-bold py-4 rounded-2xl transition-all shadow-lg flex items-center justify-center gap-2">
                Send OTP <ArrowRight size={18} />
              </button>

              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
                <div className="relative flex justify-center"><span className="bg-white px-4 text-xs text-slate-400 uppercase tracking-wider font-medium">Or</span></div>
              </div>

              <button 
                type="button"
                onClick={handleWhatsAppLogin}
                className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold py-4 rounded-2xl transition-all shadow-lg flex items-center justify-center gap-2"
              >
                <MessageCircle size={20} /> Sign in with WhatsApp
              </button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-6 max-w-sm animate-in fade-in slide-in-from-right-4">
              <div>
                 <div className="flex justify-between items-center mb-2">
                   <label className="block text-sm font-bold text-[#0F172A]">Enter OTP</label>
                   <button type="button" onClick={() => setOtpSent(false)} className="text-xs text-[#006A4E] font-bold hover:underline">Change Number</button>
                 </div>
                <input 
                  type="text" 
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full px-4 py-4 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006A4E]/20 focus:border-[#006A4E] transition-all font-bold text-center text-3xl tracking-[0.5em] text-slate-800"
                  placeholder="••••"
                  maxLength={4}
                  required
                />
                <p className="text-xs text-slate-400 mt-2 text-center">Use OTP: 1234</p>
              </div>
              
              <button type="submit" className="w-full bg-[#006A4E] hover:bg-[#005a42] text-white font-bold py-4 rounded-2xl transition-all shadow-lg flex items-center justify-center gap-2">
                Verify & Login <ArrowRight size={18} />
              </button>
            </form>
          )}
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
