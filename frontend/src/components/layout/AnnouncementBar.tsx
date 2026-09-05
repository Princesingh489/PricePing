import { Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function AnnouncementBar() {
  return (
    <div className="bg-gradient-to-r from-indigo-900 via-purple-900 to-indigo-950 text-white text-[12px] py-2 px-4 z-40 relative border-b border-indigo-800/40">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
        <div className="flex items-center justify-center gap-2 flex-wrap font-medium">
          <span className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
            <span>Never miss a price drop — Track products across <strong>Amazon, Flipkart, AJIO, Myntra & Nykaa</strong></span>
          </span>
          <Link
            to="/add-product"
            className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-400 hover:bg-amber-300 text-gray-950 font-bold text-[11px] shadow-sm transition-all hover:scale-105 cursor-pointer ml-1"
          >
            Track Now
          </Link>
        </div>

        <div className="flex items-center gap-3 text-[11px] font-medium text-gray-300">
          <div className="flex items-center gap-1.5">
            <span>🇮🇳 India</span>
            <span className="opacity-40">|</span>
            <span>🌐 English</span>
          </div>
        </div>
      </div>
    </div>
  );
}
