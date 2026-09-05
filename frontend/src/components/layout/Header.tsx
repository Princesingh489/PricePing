import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { notificationsApi } from '../../services/api';
import {
  Scale, LineChart, Bell, Heart,
  LayoutDashboard, Settings, ShieldCheck, Package,
  LogOut, PlusCircle, Menu, X
} from 'lucide-react';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (user) {
      notificationsApi.unreadCount()
        .then((res) => setUnreadCount(res.data?.unread_count || 0))
        .catch(() => {});
    }
  }, [user, location.pathname]);

  const isActive = (path: string) => location.pathname === path;

  const handleNavClick = (path: string) => {
    setMobileMenuOpen(false);
    navigate(path);
  };

  return (
    <header className="bg-white/95 backdrop-blur-md text-navy-900 sticky top-0 z-40 border-b border-gray-200/80 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-[72px] flex items-center justify-between gap-4">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-brand flex items-center justify-center text-white shadow-md shadow-indigo-500/30 group-hover:scale-105 transition-transform duration-200">
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1">
                <span className="text-2xl font-black text-indigo-900 tracking-tight">Price<span className="text-indigo-600">Ping</span></span>
                <span className="px-1.5 py-0.2 text-[9px] font-black uppercase rounded bg-indigo-100 text-indigo-700 tracking-wider">IN</span>
              </div>
            </div>
          </Link>
        </div>

        {/* Center Desktop Navigation */}
        <nav className="hidden lg:flex items-center gap-1.5">
          <Link
            to="/dashboard"
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              isActive('/dashboard') || isActive('/')
                ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                : 'text-navy-700 hover:text-indigo-600 hover:bg-gray-50'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 text-indigo-600" />
            <span>Home</span>
          </Link>

          <Link
            to="/compare"
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              isActive('/compare')
                ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                : 'text-navy-700 hover:text-indigo-600 hover:bg-gray-50'
            }`}
          >
            <Scale className="w-4 h-4 text-blue-600" />
            <span>Compare</span>
          </Link>

          <Link
            to="/history"
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              isActive('/history')
                ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                : 'text-navy-700 hover:text-indigo-600 hover:bg-gray-50'
            }`}
          >
            <LineChart className="w-4 h-4 text-cyan-600" />
            <span>Price History</span>
          </Link>

          <Link
            to="/alerts"
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              isActive('/alerts')
                ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                : 'text-navy-700 hover:text-indigo-600 hover:bg-gray-50'
            }`}
          >
            <Bell className="w-4 h-4 text-amber-600" />
            <span>Alerts</span>
          </Link>

          <Link
            to="/products"
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              isActive('/products')
                ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                : 'text-navy-700 hover:text-indigo-600 hover:bg-gray-50'
            }`}
          >
            <Package className="w-4 h-4 text-purple-600" />
            <span>My Products</span>
          </Link>
        </nav>

        {/* Right Header Actions */}
        <div className="flex items-center gap-2.5">
          {/* Quick Track Search Button */}
          <Link
            to="/add-product"
            className="hidden sm:inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold border border-indigo-200/80 transition-all hover:scale-[1.02]"
          >
            <PlusCircle className="w-3.5 h-3.5 text-indigo-600" />
            <span>Track Product</span>
          </Link>

          {/* Wishlist Heart button */}
          <Link
            to="/products"
            className="w-10 h-10 rounded-full bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-rose-600 border border-gray-200 flex items-center justify-center transition-all shadow-xs"
            title="My Tracked Wishlist"
          >
            <Heart className="w-4.5 h-4.5 hover:fill-rose-500 transition-colors" />
          </Link>

          {/* Notifications Bell */}
          <Link
            to="/notifications"
            className="w-10 h-10 rounded-full bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-indigo-600 border border-gray-200 flex items-center justify-center transition-all relative shadow-xs"
            title="Price Drop Notifications"
          >
            <Bell className="w-4.5 h-4.5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4.5 h-4.5 bg-rose-600 text-white rounded-full text-[10px] font-black flex items-center justify-center ring-2 ring-white animate-pulse">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Link>

          {/* User Profile Avatar with Dropdown / Login Button */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="w-10 h-10 rounded-full bg-gradient-brand text-white font-bold text-sm flex items-center justify-center border-2 border-white shadow-md hover:scale-105 transition-all cursor-pointer overflow-hidden"
              >
                <span>{user.name?.charAt(0).toUpperCase() || 'U'}</span>
              </button>

              {/* Dropdown Menu */}
              {userDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-gray-150 py-2.5 z-50 animate-slide-in text-navy-800">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <div className="font-extrabold text-sm text-navy-900 truncate">{user.name}</div>
                    <div className="text-xs text-gray-500 truncate">{user.email}</div>
                  </div>

                  <Link
                    to="/dashboard"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-indigo-50 hover:text-indigo-600"
                  >
                    <LayoutDashboard className="w-4 h-4 text-indigo-500" />
                    Dashboard
                  </Link>

                  <Link
                    to="/products"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-indigo-50 hover:text-indigo-600"
                  >
                    <Package className="w-4 h-4 text-purple-500" />
                    My Tracked Products
                  </Link>

                  <Link
                    to="/alerts"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-indigo-50 hover:text-indigo-600"
                  >
                    <Bell className="w-4 h-4 text-amber-500" />
                    Price Alerts
                  </Link>

                  <Link
                    to="/settings"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-gray-700 hover:bg-indigo-50 hover:text-indigo-600"
                  >
                    <Settings className="w-4 h-4 text-gray-500" />
                    Settings & Profile
                  </Link>

                  {user.is_admin && (
                    <Link
                      to="/admin"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-xs font-bold text-amber-700 hover:bg-amber-50"
                    >
                      <ShieldCheck className="w-4 h-4 text-amber-600" />
                      Admin Panel
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
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-navy-700 hover:text-indigo-600 hover:bg-gray-100 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="btn-primary text-xs px-4 py-2"
              >
                Get Started
              </Link>
            </div>
          )}

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-gray-600 hover:bg-gray-100"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-gray-200 bg-white px-4 py-4 space-y-2 shadow-xl animate-slide-in">
          <button
            onClick={() => handleNavClick('/dashboard')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-xl text-xs font-bold ${
              isActive('/dashboard') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-800 hover:bg-gray-50'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 text-indigo-600" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => handleNavClick('/compare')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-xl text-xs font-bold ${
              isActive('/compare') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-800 hover:bg-gray-50'
            }`}
          >
            <Scale className="w-4 h-4 text-blue-600" />
            <span>Compare Stores</span>
          </button>

          <button
            onClick={() => handleNavClick('/history')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-xl text-xs font-bold ${
              isActive('/history') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-800 hover:bg-gray-50'
            }`}
          >
            <LineChart className="w-4 h-4 text-cyan-600" />
            <span>Price History</span>
          </button>

          <button
            onClick={() => handleNavClick('/alerts')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-xl text-xs font-bold ${
              isActive('/alerts') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-800 hover:bg-gray-50'
            }`}
          >
            <Bell className="w-4 h-4 text-amber-600" />
            <span>Price Alerts</span>
          </button>

          <button
            onClick={() => handleNavClick('/products')}
            className={`flex items-center gap-3 w-full p-2.5 rounded-xl text-xs font-bold ${
              isActive('/products') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-800 hover:bg-gray-50'
            }`}
          >
            <Package className="w-4 h-4 text-purple-600" />
            <span>My Products</span>
          </button>

          <div className="pt-2 border-t border-gray-100">
            <Link
              to="/add-product"
              onClick={() => setMobileMenuOpen(false)}
              className="btn-primary w-full py-2.5 text-xs"
            >
              <PlusCircle className="w-4 h-4" /> Track New Product
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
