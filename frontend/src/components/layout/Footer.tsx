import { Link } from 'react-router-dom';
import { ShieldCheck, ExternalLink } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-navy-950 text-gray-300 pt-16 pb-12 border-t border-navy-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 lg:gap-12 pb-12 border-b border-navy-800/80">
          {/* Brand Column */}
          <div className="col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-2xl bg-gradient-brand flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
                <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2v20" />
                  <path d="m17 5-5-3-5 3" />
                  <path d="M4.5 9h15" />
                  <path d="M6 16.5a6 6 0 0 0 12 0" />
                </svg>
              </div>
              <span className="text-2xl font-black text-white tracking-tight">Price<span className="text-indigo-400">Ping</span></span>
            </Link>

            <p className="text-gray-400 text-sm max-w-sm leading-relaxed">
              Track prices. Compare stores. Buy smarter. Instant price drop alerts across India's leading shopping platforms.
            </p>

            <div className="flex items-center gap-2 text-xs text-indigo-400 font-semibold pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% Free & Genuine Price Tracking</span>
            </div>
          </div>

          {/* Column 1: Product */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Product</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/add-product" className="hover:text-white transition-colors">Track Prices</Link></li>
              <li><Link to="/history" className="hover:text-white transition-colors">Price History</Link></li>
              <li><Link to="/compare" className="hover:text-white transition-colors">Compare Stores</Link></li>
              <li><Link to="/alerts" className="hover:text-white transition-colors">Smart Alerts</Link></li>
            </ul>
          </div>

          {/* Column 2: Supported Stores */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Supported Stores</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="https://www.amazon.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Amazon India <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.flipkart.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Flipkart <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.ajio.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">AJIO <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.myntra.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Myntra <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.nykaa.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Nykaa <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
            </ul>
          </div>

          {/* Column 3: Account & Support */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Account</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              <li><Link to="/products" className="hover:text-white transition-colors">My Products</Link></li>
              <li><Link to="/notifications" className="hover:text-white transition-colors">Notifications</Link></li>
              <li><Link to="/settings" className="hover:text-white transition-colors">Settings</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-400">
          <div>
            © 2026 PricePing. All rights reserved.
          </div>

          <div className="flex items-center gap-6">
            <span className="hover:text-white cursor-pointer transition-colors">Privacy Policy</span>
            <span className="hover:text-white cursor-pointer transition-colors">Terms of Service</span>
            <span className="hover:text-white cursor-pointer transition-colors">Contact Support</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
