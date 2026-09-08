import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage, SUPPORTED_LANGUAGES } from '../contexts/LanguageContext';
import { notificationsApi } from '../services/api';
import {
  Tag, Scale, Sparkles, Bell, Users,
  Heart, Palette, LogOut,
  ShieldCheck, Package, LayoutDashboard, Settings as SettingsIcon, Menu, X, Home as HomeIcon,
  Globe, ChevronDown
} from 'lucide-react';
import ThemeCustomizerModal from './ThemeCustomizerModal';

interface Props {
  onOpenDeals?: () => void;
  onOpenCompare?: () => void;
  onOpenRefer?: () => void;
  mobileMenuOpen?: boolean;
  onToggleMobileMenu?: () => void;
  onCloseMobileMenu?: () => void;
}

export default function PricePingHeader({
  onOpenDeals,
  onOpenCompare,
  onOpenRefer,
  mobileMenuOpen: externalMobileMenuOpen,
  onToggleMobileMenu,
  onCloseMobileMenu,
}: Props) {
  const { user, logout } = useAuth();
  const { currentLang, setLanguage, t } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [themeModalOpen, setThemeModalOpen] = useState(false);
  const [internalMobileMenuOpen, setInternalMobileMenuOpen] = useState(false);

  const isMenuOpen = externalMobileMenuOpen !== undefined ? externalMobileMenuOpen : internalMobileMenuOpen;
  const toggleMobileMenu = () => {
    if (onToggleMobileMenu) {
      onToggleMobileMenu();
    } else {
      setInternalMobileMenuOpen((prev) => !prev);
    }
  };
  const closeMobileMenu = () => {
    if (onCloseMobileMenu) {
      onCloseMobileMenu();
    } else {
      setInternalMobileMenuOpen(false);
    }
  };

  useEffect(() => {
    if (user) {
      notificationsApi.unreadCount()
        .then((res) => setUnreadCount(res.data.unread_count || 0))
        .catch(() => {});
    }
  }, [user]);

  const handleNavAction = (action?: () => void, fallbackPath?: string) => {
    closeMobileMenu();
    if (fallbackPath === '/') {
      if (location.pathname === '/') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        navigate('/');
      }
      return;
    }
    if (fallbackPath?.startsWith('/#')) {
      const targetId = fallbackPath.replace('/#', '');
      if (location.pathname === '/') {
        const el = document.getElementById(targetId);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
        return;
      } else {
        navigate('/');
        setTimeout(() => {
          const el = document.getElementById(targetId);
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }, 200);
        return;
      }
    }
    if (location.pathname === '/' || location.pathname === '/dashboard') {
      if (action) {
        action();
        return;
      }
    }
    if (fallbackPath) {
      navigate(fallbackPath);
    } else if (action) {
      navigate('/');
      setTimeout(() => {
        action();
      }, 150);
    }
  };

  return (
    <>
      {/* 1. Top Announcement Blue Strip */}
      <div className="bg-[#24128c] text-white text-[11px] sm:text-[12px] py-1 sm:py-1.5 px-3 sm:px-4 z-40 relative border-b border-indigo-900/40">
        <div className="max-w-7xl mx-auto flex flex-row items-center justify-between gap-2 text-left">
          <div className="flex items-center gap-1.5 sm:gap-2 font-normal tracking-wide min-w-0">
            <span className="hidden sm:inline">{t('announcement_text', 'Track real-time price drops across Amazon, Flipkart, Myntra, AJIO & Nykaa.')}</span>
            <span className="sm:hidden font-medium text-[11px] truncate">Track Amazon, Flipkart, Myntra &amp; AJIO</span>
            <button
              onClick={() => handleNavAction(onOpenDeals, '/#trending-deals')}
              className="inline-flex items-center gap-1 px-2 sm:px-3 py-0.5 rounded-full bg-amber-400 hover:bg-amber-300 text-gray-950 font-bold text-[10px] sm:text-[11px] shadow-sm transition-all hover:scale-105 cursor-pointer shrink-0"
            >
              <Sparkles className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-amber-900 fill-amber-900" />
              <span>{t('explore_deals', 'Explore Deals')}</span>
            </button>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 text-[10px] sm:text-[11px] font-medium text-gray-200 shrink-0">
            <button
              onClick={() => setThemeModalOpen(true)}
              className="hidden sm:flex items-center gap-1 hover:text-white transition-colors bg-white/10 hover:bg-white/20 px-2 py-0.5 rounded-full border border-white/20 cursor-pointer"
              title="Change Background Theme"
            >
              <Palette className="w-3 h-3 text-amber-300" />
              <span>{t('theme', 'Theme')}</span>
            </button>

            {/* Interactive Language Selector */}
            <div className="relative flex items-center gap-1 sm:gap-1.5">
              <span className="hidden sm:inline">🇮🇳 India</span>
              <span className="hidden sm:inline opacity-40">|</span>
              <div className="relative flex items-center bg-white/15 hover:bg-white/25 rounded-full px-2 py-0.5 border border-white/25 transition-all">
                <Globe className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-cyan-300 mr-1 shrink-0" />
                <select
                  id="language-selector"
                  value={currentLang}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-transparent text-white font-bold text-[10px] sm:text-xs cursor-pointer focus:outline-none appearance-none pr-3"
                  title="Select Language / भाषा चुनें"
                >
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code} className="bg-[#12162a] text-white py-1">
                      {lang.flag} {lang.nativeName}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-2 h-2 sm:w-2.5 sm:h-2.5 opacity-70 pointer-events-none absolute right-1" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Main Navigation Bar */}
      <header className="bg-white text-gray-800 sticky top-0 z-30 shadow-sm border-b border-gray-200/80">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 sm:h-[72px] flex items-center justify-between gap-2 sm:gap-4">
          {/* Logo */}
          <div className="flex items-center gap-4 sm:gap-6">
            <Link
              to="/"
              onClick={(e) => {
                if (location.pathname === '/') {
                  e.preventDefault();
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }
              }}
              className="flex items-center gap-2 sm:gap-2.5 group cursor-pointer"
              title="Price Ping Home"
            >
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-[#2e1aa6] flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform duration-200 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
                  <path d="M3 6h18" />
                  <circle cx="9" cy="12" r="1" fill="currentColor" />
                  <circle cx="15" cy="12" r="1" fill="currentColor" />
                  <path d="M10 16a3 3 0 0 0 4 0" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-xl sm:text-[22px] font-black text-[#24128c] tracking-tight">Price Ping</span>
              </div>
            </Link>
          </div>

          {/* Center Navigation: Home, Deals, Compare, Alerts, Refer & win */}
          <nav className="hidden lg:flex items-center gap-1.5 xl:gap-3">
            {/* Home */}
            <button
              onClick={() => handleNavAction(undefined, '/')}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer group ${
                location.pathname === '/'
                  ? 'bg-indigo-50 text-[#24128c] font-bold shadow-2xs'
                  : 'hover:bg-gray-100/80 text-gray-700'
              }`}
            >
              <div className="w-6 h-6 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600 group-hover:scale-110 transition-transform">
                <HomeIcon className="w-3.5 h-3.5" />
              </div>
              <span>{t('home', 'Home')}</span>
            </button>

            {/* My Tracked Products (Right side of Home button) */}
            <Link
              to="/products"
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer group ${
                location.pathname === '/products' || location.pathname === '/dashboard'
                  ? 'bg-indigo-50 text-[#24128c] font-bold shadow-2xs'
                  : 'hover:bg-gray-100/80 text-gray-700'
              }`}
            >
              <div className="w-6 h-6 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600 group-hover:scale-110 transition-transform">
                <Package className="w-3.5 h-3.5" />
              </div>
              <span>{t('my_products', 'My Tracked Products')}</span>
            </Link>

            {/* Deals */}
            <button
              onClick={() => handleNavAction(onOpenDeals, '/#trending-deals')}
              className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-gray-100/80 text-gray-700 font-semibold text-xs transition-all cursor-pointer group"
            >
              <div className="w-6 h-6 rounded-lg bg-pink-100 flex items-center justify-center text-pink-600 group-hover:scale-110 transition-transform">
                <Tag className="w-3.5 h-3.5" />
              </div>
              <span>{t('deals', 'Deals')}</span>
            </button>

            {/* Compare */}
            <button
              onClick={() => handleNavAction(onOpenCompare, '/#cross-compare')}
              className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-gray-100/80 text-gray-700 font-semibold text-xs transition-all cursor-pointer group"
            >
              <div className="w-6 h-6 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform">
                <Scale className="w-3.5 h-3.5" />
              </div>
              <span>{t('compare', 'Compare')}</span>
            </button>

            {/* Alerts */}
            <Link
              to="/alerts"
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer group ${
                location.pathname === '/alerts'
                  ? 'bg-indigo-50 text-[#24128c] font-bold shadow-2xs'
                  : 'hover:bg-gray-100/80 text-gray-700'
              }`}
            >
              <div className="w-6 h-6 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600 group-hover:scale-110 transition-transform">
                <Bell className="w-3.5 h-3.5" />
              </div>
              <span>{t('alerts', 'Alerts')}</span>
            </Link>

            {/* Refer & win */}
            <button
              onClick={() => handleNavAction(onOpenRefer, '/dashboard')}
              className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-gray-100/80 text-gray-700 font-semibold text-xs transition-all cursor-pointer group"
            >
              <div className="w-6 h-6 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600 group-hover:scale-110 transition-transform">
                <Users className="w-3.5 h-3.5" />
              </div>
              <span>{t('refer_win', 'Refer & win')}</span>
            </button>
          </nav>

          {/* Right Header Actions (Theme + Heart + Bell + Avatar + Mobile Hamburger) */}
          <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
            {/* Theme Customizer Button (Visible on sm+ screens, in drawer on mobile) */}
            <button
              onClick={() => setThemeModalOpen(true)}
              className="hidden sm:flex w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 items-center justify-center transition-all shadow-xs cursor-pointer hover:scale-105 shrink-0"
              title="Theme Customizer & Backdrops"
            >
              <Palette className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
            </button>

            {/* Wishlist Heart button (Visible on sm+ screens, in drawer on mobile) */}
            <Link
              to="/products"
              className="hidden sm:flex w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-50 hover:bg-gray-100 text-gray-500 hover:text-rose-600 border border-gray-200 items-center justify-center transition-all shadow-xs shrink-0"
              title="My Watchlist"
            >
              <Heart className="w-4 h-4 sm:w-5 sm:h-5 fill-gray-200 hover:fill-rose-500" />
            </Link>

            {/* Notifications Bell (Always visible, compact on mobile) */}
            <Link
              to="/notifications"
              className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-indigo-600 border border-gray-200 flex items-center justify-center transition-all relative shadow-xs shrink-0"
              title="Notifications"
            >
              <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-600 text-white rounded-full text-[9px] font-black flex items-center justify-center ring-2 ring-white">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Link>

            {/* User Avatar with Dropdown */}
            {user ? (
              <div className="relative shrink-0">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-tr from-amber-600 to-indigo-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center border-2 border-white shadow-md hover:scale-105 transition-all cursor-pointer overflow-hidden shrink-0"
                  title={user.name}
                >
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
                    alt={user.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                  <span>{user.name?.charAt(0).toUpperCase()}</span>
                </button>

                {/* Dropdown Menu */}
                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-2xl border border-gray-150 py-2.5 z-50 animate-slide-in text-gray-800">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <div className="font-extrabold text-sm text-gray-900 truncate">{user.name}</div>
                      <div className="text-xs text-gray-500 truncate">{user.email}</div>
                    </div>

                    <Link
                      to="/"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-indigo-700 hover:bg-indigo-50"
                    >
                      <HomeIcon className="w-4 h-4 text-indigo-600" />
                      Home
                    </Link>

                    <Link
                      to="/dashboard"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-gray-50 hover:text-blue-600"
                    >
                      <LayoutDashboard className="w-4 h-4 text-blue-500" />
                      Dashboard
                    </Link>

                    <Link
                      to="/products"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-gray-50 hover:text-blue-600"
                    >
                      <Package className="w-4 h-4 text-purple-500" />
                      My Tracked Products
                    </Link>

                    <Link
                      to="/settings"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-gray-50 hover:text-blue-600"
                    >
                      <SettingsIcon className="w-4 h-4 text-gray-500" />
                      Settings &amp; Preferences
                    </Link>

                    {user.is_admin && (
                      <Link
                        to="/admin"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-amber-700 hover:bg-amber-50"
                      >
                        <ShieldCheck className="w-4 h-4 text-amber-600" />
                        Admin Control Panel
                      </Link>
                    )}

                    <div className="border-t border-gray-100 my-1.5" />

                    <button
                      onClick={() => {
                        setUserDropdownOpen(false);
                        logout();
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-rose-600 hover:bg-rose-50 cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      Log Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <Link
                  to="/login"
                  className="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#24128c] hover:bg-[#1a0c69] text-white shadow-xs transition-all shrink-0"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="hidden sm:inline-flex px-3.5 py-1.5 rounded-xl text-xs font-bold border border-gray-300 text-gray-700 hover:bg-gray-100 transition-all shrink-0"
                >
                  Sign Up
                </Link>
              </div>
            )}

            {/* Mobile Menu Button - Guaranteed never clipped */}
            <button
              onClick={toggleMobileMenu}
              className={`lg:hidden w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center transition-colors shrink-0 ${
                isMenuOpen
                  ? 'bg-indigo-100 text-[#24128c]'
                  : 'text-gray-700 hover:bg-gray-100 bg-gray-50 border border-gray-200/80'
              }`}
              aria-label="Toggle Mobile Navigation Menu"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav Drawer Backdrop & Panel */}
        {isMenuOpen && (
          <div
            className="lg:hidden fixed inset-x-0 top-[105px] sm:top-[115px] bottom-16 z-40 bg-black/40 backdrop-blur-xs animate-fade-in flex flex-col justify-start"
            onClick={closeMobileMenu}
          >
            <div
              className="bg-white border-b border-gray-200 px-4 py-4 space-y-2 shadow-2xl overflow-y-auto max-h-[calc(100vh-175px)] animate-slide-in"
              onClick={(e) => e.stopPropagation()}
            >
              {/* User Profile Card (if logged in) or Login Card (if logged out) */}
              {user ? (
                <div className="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-full bg-[#24128c] text-white font-bold flex items-center justify-center shrink-0">
                      {user.name?.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <div className="font-black text-sm text-gray-900 truncate">{user.name}</div>
                      <div className="text-[11px] text-gray-500 truncate">{user.email}</div>
                    </div>
                  </div>
                  <Link
                    to="/dashboard"
                    onClick={closeMobileMenu}
                    className="px-2.5 py-1 rounded-lg bg-[#24128c] text-white text-[11px] font-bold shrink-0 hover:bg-indigo-900"
                  >
                    Dashboard
                  </Link>
                </div>
              ) : (
                <div className="p-3 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-2xl border border-indigo-100 flex items-center justify-between mb-3">
                  <div>
                    <div className="font-extrabold text-xs text-gray-900">Welcome to PricePing!</div>
                    <div className="text-[10px] text-gray-500">Track prices &amp; get instant alerts</div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <Link
                      to="/login"
                      onClick={closeMobileMenu}
                      className="px-3 py-1.5 rounded-xl bg-[#24128c] text-white text-xs font-bold shadow-xs"
                    >
                      Log In
                    </Link>
                    <Link
                      to="/register"
                      onClick={closeMobileMenu}
                      className="px-3 py-1.5 rounded-xl border border-gray-300 text-gray-700 text-xs font-semibold hover:bg-white"
                    >
                      Sign Up
                    </Link>
                  </div>
                </div>
              )}

              {/* Home Button - Highlighted & Prominent */}
              <button
                onClick={() => handleNavAction(undefined, '/')}
                className={`flex items-center justify-between w-full p-3 rounded-2xl font-bold text-xs transition-all cursor-pointer ${
                  location.pathname === '/'
                    ? 'bg-indigo-50 text-[#24128c] border border-indigo-200/80 shadow-2xs'
                    : 'hover:bg-gray-50 text-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0">
                    <HomeIcon className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">{t('home', 'Home')}</div>
                    <div className="text-[10px] text-gray-500 font-normal">Price tracker &amp; live search</div>
                  </div>
                </div>
                {location.pathname === '/' && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-[#24128c]">Active</span>
                )}
              </button>

              {/* My Tracked Products */}
              <Link
                to="/products"
                onClick={closeMobileMenu}
                className={`flex items-center justify-between w-full p-3 rounded-2xl font-bold text-xs transition-all ${
                  location.pathname === '/products' || location.pathname === '/dashboard'
                    ? 'bg-purple-50 text-purple-900 border border-purple-200/80'
                    : 'hover:bg-purple-50/50 text-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center shrink-0">
                    <Package className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">{t('my_products', 'My Tracked Products')}</div>
                    <div className="text-[10px] text-gray-500 font-normal">View your watchlist &amp; price drops</div>
                  </div>
                </div>
              </Link>

              {/* Trending Deals */}
              <button
                onClick={() => handleNavAction(onOpenDeals, '/#trending-deals')}
                className="flex items-center justify-between w-full p-3 rounded-2xl hover:bg-pink-50 text-gray-800 font-bold text-xs transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-pink-100 text-pink-700 flex items-center justify-center shrink-0">
                    <Tag className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">Trending Deals</div>
                    <div className="text-[10px] text-gray-500 font-normal">Amazon, Flipkart, Myntra, AJIO, Nykaa</div>
                  </div>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-pink-100 text-pink-700">Live 🔥</span>
              </button>

              {/* Compare Prices */}
              <button
                onClick={() => handleNavAction(onOpenCompare, '/#cross-compare')}
                className="flex items-center justify-between w-full p-3 rounded-2xl hover:bg-blue-50 text-gray-800 font-bold text-xs transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
                    <Scale className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">Compare Stores</div>
                    <div className="text-[10px] text-gray-500 font-normal">Cross-store real-time price matrix</div>
                  </div>
                </div>
              </button>

              {/* Price Drop Alerts */}
              <Link
                to="/alerts"
                onClick={closeMobileMenu}
                className={`flex items-center justify-between w-full p-3 rounded-2xl font-bold text-xs transition-all ${
                  location.pathname === '/alerts' ? 'bg-indigo-50 text-[#24128c]' : 'hover:bg-indigo-50/50 text-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
                    <Bell className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">Price Drop Alerts</div>
                    <div className="text-[10px] text-gray-500 font-normal">Get instant notification on drops</div>
                  </div>
                </div>
              </Link>

              {/* Refer & Win */}
              <button
                onClick={() => handleNavAction(onOpenRefer, '/dashboard')}
                className="flex items-center justify-between w-full p-3 rounded-2xl hover:bg-emerald-50 text-gray-800 font-bold text-xs transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                    <Users className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">Refer &amp; Win</div>
                    <div className="text-[10px] text-gray-500 font-normal">Invite friends &amp; earn rewards</div>
                  </div>
                </div>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">₹500 Cash</span>
              </button>

              {/* Theme Customizer */}
              <button
                onClick={() => {
                  closeMobileMenu();
                  setThemeModalOpen(true);
                }}
                className="flex items-center justify-between w-full p-3 rounded-2xl hover:bg-purple-50 text-gray-800 font-bold text-xs transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center shrink-0">
                    <Palette className="w-4 h-4" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-xs">Theme Customizer</div>
                    <div className="text-[10px] text-gray-500 font-normal">Festive, Cyberpunk, AMOLED backdrops</div>
                  </div>
                </div>
              </button>

              {/* Settings / Dashboard / Admin */}
              {user && (
                <>
                  <div className="border-t border-gray-100 my-2 pt-2" />
                  <Link
                    to="/dashboard"
                    onClick={closeMobileMenu}
                    className="flex items-center gap-3 w-full p-2.5 rounded-xl hover:bg-blue-50 text-gray-800 font-bold text-xs"
                  >
                    <LayoutDashboard className="w-4 h-4 text-blue-600" />
                    <span>User Dashboard</span>
                  </Link>
                  <Link
                    to="/settings"
                    onClick={closeMobileMenu}
                    className="flex items-center gap-3 w-full p-2.5 rounded-xl hover:bg-gray-50 text-gray-800 font-bold text-xs"
                  >
                    <SettingsIcon className="w-4 h-4 text-gray-600" />
                    <span>Settings &amp; Preferences</span>
                  </Link>
                  {user.is_admin && (
                    <Link
                      to="/admin"
                      onClick={closeMobileMenu}
                      className="flex items-center gap-3 w-full p-2.5 rounded-xl hover:bg-amber-50 text-amber-800 font-bold text-xs"
                    >
                      <ShieldCheck className="w-4 h-4 text-amber-600" />
                      <span>Admin Control Panel</span>
                    </Link>
                  )}
                  <button
                    onClick={() => {
                      closeMobileMenu();
                      logout();
                    }}
                    className="flex items-center gap-3 w-full p-2.5 rounded-xl hover:bg-rose-50 text-rose-600 font-bold text-xs cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Log Out</span>
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Theme Customizer Modal */}
      <ThemeCustomizerModal
        isOpen={themeModalOpen}
        onClose={() => setThemeModalOpen(false)}
      />
    </>
  );
}
