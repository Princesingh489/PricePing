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
              Price Ping is India&apos;s intelligent price comparison and tracking platform. Monitor price drops across Amazon, Flipkart, Myntra, Ajio, and Nykaa with real-time alerts and verified price history.
            </p>

            <div className="flex items-center gap-2 text-xs text-indigo-400 font-semibold pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% Free & Genuine Real-Time Price Tracking</span>
            </div>
          </div>

          {/* Column 1: Explore & Tools */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Features</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/price-comparison" className="hover:text-white transition-colors">Price Comparison</Link></li>
              <li><Link to="/price-tracker" className="hover:text-white transition-colors">Price Tracker</Link></li>
              <li><Link to="/deals" className="hover:text-white transition-colors">Live Trending Deals</Link></li>
              <li><Link to="/categories" className="hover:text-white transition-colors">All Categories</Link></li>
              <li><Link to="/compare" className="hover:text-white transition-colors">Compare Stores</Link></li>
              <li><Link to="/history" className="hover:text-white transition-colors">Price History Search</Link></li>
            </ul>
          </div>

          {/* Column 2: Supported Stores */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Stores Tracked</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="https://www.amazon.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Amazon India <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.flipkart.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Flipkart <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.ajio.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">AJIO <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.myntra.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Myntra <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
              <li><a href="https://www.nykaa.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">Nykaa <ExternalLink className="w-3 h-3 opacity-60" /></a></li>
            </ul>
          </div>

          {/* Column 3: Company & Trust */}
          <div className="space-y-3">
            <h4 className="text-xs font-black text-white uppercase tracking-wider">Price Ping</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/about" className="hover:text-white transition-colors">About Price Ping</Link></li>
              <li><Link to="/how-it-works" className="hover:text-white transition-colors">How It Works</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact Support</Link></li>
              <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-400">
          <div>
            © {new Date().getFullYear()} Price Ping (priceping.store). All rights reserved.
          </div>

          <div className="flex items-center gap-6">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms</Link>
            <Link to="/contact" className="hover:text-white transition-colors">Contact</Link>
            <Link to="/about" className="hover:text-white transition-colors">About</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
