import React, { useState } from 'react';
import PricePingHeader from './PricePingHeader';
import MobileBottomNav from './MobileBottomNav';
import FloatingChatAssistant from './FloatingChatAssistant';
import ReferAndWinModal from './ReferAndWinModal';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [referModalOpen, setReferModalOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-gray-900 flex flex-col antialiased selection:bg-indigo-500/30 selection:text-indigo-900">
      {/* 1. Price Ping Top Header Bar */}
      <PricePingHeader
        onOpenDeals={() => scrollToSection('trending-deals')}
        onOpenCompare={() => scrollToSection('cross-compare')}
        onOpenRefer={() => setReferModalOpen(true)}
        mobileMenuOpen={mobileMenuOpen}
        onToggleMobileMenu={() => setMobileMenuOpen((prev) => !prev)}
        onCloseMobileMenu={() => setMobileMenuOpen(false)}
      />

      {/* 2. Main Page Content (with mobile safe-area padding for sticky bottom navigation) */}
      <main className="flex-1 w-full pb-20 lg:pb-0 animate-fade-in">
        {children}
      </main>

      {/* 3. Sticky Mobile Bottom Navigation Bar (Home, Deals, Compare, Tracked, Menu) */}
      <MobileBottomNav
        onOpenDeals={() => scrollToSection('trending-deals')}
        onOpenCompare={() => scrollToSection('cross-compare')}
        onToggleMenu={() => setMobileMenuOpen((prev) => !prev)}
        isMenuOpen={mobileMenuOpen}
      />

      {/* 4. Floating Price Assistant Chatbot */}
      <FloatingChatAssistant />

      {/* 5. Refer & Win Modal */}
      <ReferAndWinModal
        isOpen={referModalOpen}
        onClose={() => setReferModalOpen(false)}
      />

      {/* 6. Modern Footer */}
      <footer className="mt-16 bg-[#0e1322] border-t border-gray-800 text-gray-400 text-xs py-10 px-4 sm:px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
          <div className="space-y-1">
            <div className="flex items-center justify-center md:justify-start gap-2">
              <span className="text-base font-black text-white">Price Ping</span>
              <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-bold border border-indigo-500/30">
                PRO
              </span>
            </div>
            <p className="text-gray-400">
              India's Smartest Price Comparison, Drop Alert & Savings Platform
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4 sm:gap-6 text-gray-400 font-medium">
            <span>Amazon India</span>
            <span>•</span>
            <span>Flipkart</span>
            <span>•</span>
            <span>AJIO</span>
            <span>•</span>
            <span>Myntra</span>
            <span>•</span>
            <span>Nykaa</span>
            <span>•</span>
            <span>100+ Stores</span>
          </div>

          <div className="text-gray-500">
            © 2026 Price Ping Technologies. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
