import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Tag, Scale, Package, Menu } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface Props {
  onOpenDeals?: () => void;
  onOpenCompare?: () => void;
  onToggleMenu: () => void;
  isMenuOpen: boolean;
}

export default function MobileBottomNav({
  onOpenDeals,
  onOpenCompare,
  onToggleMenu,
  isMenuOpen,
}: Props) {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const isHome = location.pathname === '/';
  const isCompare = location.pathname === '/compare';
  const isProducts = location.pathname === '/products' || location.pathname === '/dashboard';

  const handleHomeClick = () => {
    if (isHome) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      navigate('/');
    }
  };

  const handleDealsClick = () => {
    if (isHome) {
      const el = document.getElementById('trending-deals');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
        return;
      }
      if (onOpenDeals) onOpenDeals();
    } else {
      navigate('/');
      setTimeout(() => {
        const el = document.getElementById('trending-deals');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 200);
    }
  };

  const handleCompareClick = () => {
    if (isHome) {
      const el = document.getElementById('cross-compare');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
        return;
      }
      if (onOpenCompare) onOpenCompare();
    } else {
      navigate('/compare');
    }
  };

  const handleProductsClick = () => {
    navigate('/products');
  };

  return (
    <nav
      aria-label="Mobile Navigation"
      className="fixed bottom-0 inset-x-0 z-30 lg:hidden bg-white/95 backdrop-blur-xl border-t border-gray-200/90 shadow-[0_-4px_24px_rgba(0,0,0,0.08)] pb-safe transition-all"
    >
      <div className="grid grid-cols-5 h-16 max-w-lg mx-auto items-center px-1">
        {/* 1. Home */}
        <button
          onClick={handleHomeClick}
          className={`flex flex-col items-center justify-center py-1 px-1 transition-all cursor-pointer group relative ${
            isHome && !isMenuOpen ? 'text-[#24128c]' : 'text-gray-500 hover:text-gray-800'
          }`}
          title="PricePing Home"
        >
          <div
            className={`w-10 h-7 rounded-full flex items-center justify-center transition-all ${
              isHome && !isMenuOpen
                ? 'bg-indigo-100 text-[#24128c] shadow-xs'
                : 'group-hover:scale-105 text-gray-500'
            }`}
          >
            <Home className="w-5 h-5 stroke-[2.2]" />
          </div>
          <span
            className={`text-[11px] mt-0.5 tracking-tight ${
              isHome && !isMenuOpen ? 'font-black text-[#24128c]' : 'font-semibold'
            }`}
          >
            {t('home', 'Home')}
          </span>
          {isHome && !isMenuOpen && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#24128c] absolute bottom-1" />
          )}
        </button>

        {/* 2. Deals */}
        <button
          onClick={handleDealsClick}
          className="flex flex-col items-center justify-center py-1 px-1 transition-all cursor-pointer group text-gray-500 hover:text-pink-600"
          title="Trending Deals Across 5 Stores"
        >
          <div className="w-10 h-7 rounded-full flex items-center justify-center transition-all group-hover:scale-105 group-hover:bg-pink-50">
            <Tag className="w-5 h-5 stroke-[2.2] group-hover:text-pink-600" />
          </div>
          <span className="text-[11px] font-semibold mt-0.5 tracking-tight group-hover:text-pink-600">
            {t('deals', 'Deals')}
          </span>
        </button>

        {/* 3. Compare */}
        <button
          onClick={handleCompareClick}
          className={`flex flex-col items-center justify-center py-1 px-1 transition-all cursor-pointer group relative ${
            isCompare && !isMenuOpen ? 'text-blue-700' : 'text-gray-500 hover:text-blue-600'
          }`}
          title="Compare Prices Across Amazon, Flipkart, Myntra, AJIO & Nykaa"
        >
          <div
            className={`w-10 h-7 rounded-full flex items-center justify-center transition-all ${
              isCompare && !isMenuOpen
                ? 'bg-blue-100 text-blue-700 shadow-xs'
                : 'group-hover:scale-105 group-hover:bg-blue-50'
            }`}
          >
            <Scale className="w-5 h-5 stroke-[2.2]" />
          </div>
          <span
            className={`text-[11px] mt-0.5 tracking-tight ${
              isCompare && !isMenuOpen ? 'font-black text-blue-700' : 'font-semibold'
            }`}
          >
            {t('compare', 'Compare')}
          </span>
          {isCompare && !isMenuOpen && (
            <span className="w-1.5 h-1.5 rounded-full bg-blue-700 absolute bottom-1" />
          )}
        </button>

        {/* 4. Tracked Products */}
        <button
          onClick={handleProductsClick}
          className={`flex flex-col items-center justify-center py-1 px-1 transition-all cursor-pointer group relative ${
            isProducts && !isMenuOpen ? 'text-purple-700' : 'text-gray-500 hover:text-purple-600'
          }`}
          title="My Tracked Products"
        >
          <div
            className={`w-10 h-7 rounded-full flex items-center justify-center transition-all ${
              isProducts && !isMenuOpen
                ? 'bg-purple-100 text-purple-700 shadow-xs'
                : 'group-hover:scale-105 group-hover:bg-purple-50'
            }`}
          >
            <Package className="w-5 h-5 stroke-[2.2]" />
          </div>
          <span
            className={`text-[11px] mt-0.5 tracking-tight ${
              isProducts && !isMenuOpen ? 'font-black text-purple-700' : 'font-semibold'
            }`}
          >
            Tracked
          </span>
          {isProducts && !isMenuOpen && (
            <span className="w-1.5 h-1.5 rounded-full bg-purple-700 absolute bottom-1" />
          )}
        </button>

        {/* 5. Menu / All Features */}
        <button
          onClick={onToggleMenu}
          className={`flex flex-col items-center justify-center py-1 px-1 transition-all cursor-pointer group relative ${
            isMenuOpen ? 'text-[#24128c]' : 'text-gray-500 hover:text-gray-800'
          }`}
          title="All Features & Menu"
        >
          <div
            className={`w-10 h-7 rounded-full flex items-center justify-center transition-all ${
              isMenuOpen
                ? 'bg-indigo-100 text-[#24128c] shadow-xs'
                : 'group-hover:scale-105 group-hover:bg-gray-100'
            }`}
          >
            <Menu className="w-5 h-5 stroke-[2.2]" />
          </div>
          <span
            className={`text-[11px] mt-0.5 tracking-tight ${
              isMenuOpen ? 'font-black text-[#24128c]' : 'font-semibold'
            }`}
          >
            Menu
          </span>
          {isMenuOpen && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#24128c] absolute bottom-1" />
          )}
        </button>
      </div>
    </nav>
  );
}
