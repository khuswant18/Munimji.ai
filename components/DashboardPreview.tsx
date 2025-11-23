import React, { useRef, useState, useEffect } from 'react';
import { TrendingUp, User, Receipt, FileText, Mic, MessageCircle } from 'lucide-react';

const DashboardPreview: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);
    
    const handler = (e: MediaQueryListEvent) => setIsReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isReducedMotion || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    // Calculate rotation (-5deg to +5deg)
    const rotateY = ((x - centerX) / centerX) * 5; 
    const rotateX = ((y - centerY) / centerY) * -5;
    
    setRotation({ x: rotateX, y: rotateY });
  };

  const handlePointerEnter = () => setIsHovered(true);
  
  const handlePointerLeave = () => {
    setIsHovered(false);
    setRotation({ x: 0, y: 0 });
  };

  // Parallax transform calculation helper
  const getParallaxStyle = (depth: number) => {
    if (isReducedMotion) return {};
    return {
      transform: `translate(${rotation.y * depth}px, ${rotation.x * depth}px)`,
      transition: 'transform 0.1s ease-out'
    };
  };

  return (
    <div 
      className="relative w-full h-full min-h-[400px] flex items-center justify-center select-none perspective-1000"
      ref={containerRef}
      onPointerMove={handlePointerMove}
      onPointerEnter={handlePointerEnter}
      onPointerLeave={handlePointerLeave}
      style={{ perspective: '1000px' }}
      role="img"
      aria-label="Interactive dashboard preview showing charts and transactions"
    >
      {/* Background Decorative Blob - Static opacity change on hover */}
      <div 
        className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-br from-green-50 to-emerald-100/50 rounded-full blur-3xl transition-opacity duration-500 ${isHovered ? 'opacity-80' : 'opacity-60'}`} 
      />

      {/* Main Rotation Container */}
      <div 
        className="relative w-full max-w-sm transition-transform duration-300 ease-out"
        style={{ 
          transform: isReducedMotion ? 'none' : `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(${isHovered ? 1.02 : 1})`,
          transformStyle: 'preserve-3d'
        }}
      >
        
        {/* Floating Notification - Top Right */}
        <div 
          className="absolute -top-12 -right-4 bg-primary text-white p-4 rounded-xl shadow-xl shadow-green-900/10 z-20"
          style={getParallaxStyle(1.5)}
        >
            <div className="text-xs opacity-90 mb-1">WhatsApp message received</div>
            <div className="font-semibold text-sm">"Sold 50kg rice to Ravi ₹2500"</div>
        </div>

        {/* Card 1: Recent Log (Top Left) */}
        <div 
          className="absolute -top-4 -left-8 bg-white p-4 rounded-2xl shadow-lg border border-gray-100 z-10 w-48 transition-transform duration-500"
          style={{
            ...getParallaxStyle(1.2),
            transform: isReducedMotion ? 'rotate(-2deg)' : `${getParallaxStyle(1.2).transform} rotate(${isHovered ? 0 : -2}deg)`
          }}
        >
           <div className="flex items-center gap-3 mb-2">
             <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-primary">
               <TrendingUp size={16} />
             </div>
             <div>
               <div className="text-xs text-gray-500">Sale Logged</div>
               <div className="text-sm font-bold text-gray-900">₹2,500</div>
             </div>
           </div>
           <div className="text-[10px] bg-gray-50 px-2 py-1 rounded text-gray-500 inline-block">
             Extracted from text
           </div>
        </div>

        {/* Card 2: Main Chart Card (Center) */}
        <div className="bg-white rounded-3xl p-6 shadow-2xl border border-gray-100 relative z-0 mt-8 w-full bg-opacity-95 backdrop-blur-sm">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-lg font-bold text-gray-800">Monthly Profit</h3>
                    <p className="text-xs text-gray-500">Daily breakdown of your net income.</p>
                </div>
                <div className="bg-green-50 text-primary text-xs font-bold px-2 py-1 rounded-lg">
                    +15%
                </div>
            </div>

            {/* Simulated Chart */}
            <div className="h-32 flex items-end justify-between gap-2 px-2">
                {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
                    <div key={i} className="w-full bg-gray-100 rounded-t-lg relative group overflow-hidden" style={{height: '100%'}}>
                        <div 
                            className="absolute bottom-0 left-0 w-full bg-primary rounded-t-lg transition-colors duration-300 group-hover:bg-primary-dark"
                            style={{ height: `${h}%` }}
                        ></div>
                    </div>
                ))}
            </div>
             <div className="flex justify-between mt-2 text-[10px] text-gray-400 font-medium">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
            </div>
        </div>

        {/* Card 3: Udhaar Transaction (Bottom Right) */}
        <div 
          className="absolute -bottom-6 -right-6 bg-white p-4 rounded-2xl shadow-lg border border-gray-100 z-10 w-64 transition-transform duration-500"
          style={{
            ...getParallaxStyle(1.8),
            transform: isReducedMotion ? 'rotate(1deg)' : `${getParallaxStyle(1.8).transform} rotate(${isHovered ? 0 : 1}deg)`
          }}
        >
            <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
                        <User size={16} />
                    </div>
                    <span className="font-bold text-sm text-gray-800">Rohan (Udhaar)</span>
                </div>
                <span className="font-bold text-red-500 text-sm">₹1,200</span>
            </div>
            <div className="flex gap-2">
                 <span className="px-2 py-1 bg-gray-50 rounded-md text-[10px] text-gray-500 flex items-center gap-1">
                    <MessageCircle size={10} className="text-green-500" /> via WhatsApp
                 </span>
                 <span className="px-2 py-1 bg-gray-50 rounded-md text-[10px] text-gray-500">
                    #auto-reminder
                 </span>
            </div>
        </div>

        {/* Input Types Pills (Floating left/bottom) */}
         <div 
            className="absolute top-1/2 -left-12 flex flex-col gap-2"
            style={getParallaxStyle(0.8)}
         >
            <div className="bg-white px-3 py-2 rounded-lg shadow-md border border-gray-50 flex items-center gap-2 text-xs font-medium text-gray-600 transition-transform hover:scale-105 cursor-default">
                <FileText size={14} className="text-blue-500"/> PDF Bill
            </div>
            <div className="bg-white px-3 py-2 rounded-lg shadow-md border border-gray-50 flex items-center gap-2 text-xs font-medium text-gray-600 transition-transform hover:scale-105 cursor-default">
                <Receipt size={14} className="text-purple-500"/> Receipt Photo
            </div>
            <div className="bg-white px-3 py-2 rounded-lg shadow-md border border-gray-50 flex items-center gap-2 text-xs font-medium text-gray-600 transition-transform hover:scale-105 cursor-default">
                <Mic size={14} className="text-red-500"/> Voice Note
            </div>
         </div>

      </div>
    </div>
  );
};

export default DashboardPreview;