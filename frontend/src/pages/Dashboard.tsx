import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi, productsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { DashboardStats, TrackedProduct } from '../types';
import {
  Package, Bell, TrendingDown, CheckCircle2,
  PlusCircle, Sparkles, ArrowRight, ShoppingBag
} from 'lucide-react';
import ProductCard from '../components/products/ProductCard';
import StatCard from '../components/common/StatCard';
import { ProductCardSkeleton, StatCardSkeleton } from '../components/common/SkeletonLoader';
import PriceHistoryModal from '../components/modals/PriceHistoryModal';
import QuickTrackModal from '../components/common/QuickTrackModal';
import DeleteTrackingModal from '../components/modals/DeleteTrackingModal';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentProducts, setRecentProducts] = useState<TrackedProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProductForHistory, setSelectedProductForHistory] = useState<any>(null);
  const [trackerToDelete, setTrackerToDelete] = useState<TrackedProduct | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [quickTrackOpen, setQuickTrackOpen] = useState(false);
  const [quickTrackUrl, setQuickTrackUrl] = useState('');

  const fetchDashboardData = () => {
    setLoading(true);
    Promise.all([dashboardApi.stats(), productsApi.list()])
      .then(([statsRes, productsRes]) => {
        setStats(statsRes.data);
        setRecentProducts(productsRes.data || []);
      })
      // BUG-014 FIX: Always show an error to the user on fetch failure.
      // The old .catch(() => {}) silently swallowed errors, leaving users with blank data and no explanation.
      .catch(() => toast.error('Failed to load dashboard data. Please refresh the page.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handlePause = async (trackerId: number) => {
    setActionLoadingId(trackerId);
    try {
      await productsApi.pause(trackerId);
      setRecentProducts((prev) =>
        prev.map((p) => (p.id === trackerId ? { ...p, tracking_status: 'paused' } : p))
      );
      toast.success('Tracking paused');
    } catch {
      toast.error('Failed to pause tracking');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleResume = async (trackerId: number) => {
    setActionLoadingId(trackerId);
    try {
      await productsApi.resume(trackerId);
      setRecentProducts((prev) =>
        prev.map((p) => (p.id === trackerId ? { ...p, tracking_status: 'active' } : p))
      );
      toast.success('Tracking resumed');
    } catch {
      toast.error('Failed to resume tracking');
    } finally {
      setActionLoadingId(null);
    }
  };

  const promptDelete = (tracker: TrackedProduct) => {
    setTrackerToDelete(tracker);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async (trackerId: number) => {
    setDeleteLoading(true);
    try {
      await productsApi.delete(trackerId);
      setRecentProducts((prev) => prev.filter((p) => p.id !== trackerId));
      setStats((prev) => prev ? { ...prev, total_tracked: Math.max(0, prev.total_tracked - 1) } : null);
      toast.success('Product removed from tracking');
      setIsDeleteModalOpen(false);
      setTrackerToDelete(null);
    } catch {
      toast.error('Failed to delete product');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleRefresh = async (productId: number, trackerId: number) => {
    setActionLoadingId(trackerId);
    try {
      await productsApi.refresh(productId);
      toast.success('Price refresh queued!');
      setTimeout(fetchDashboardData, 2500);
    } catch {
      toast.error('Failed to refresh price');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleQuickUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickTrackUrl.trim()) return;
    setQuickTrackOpen(true);
  };

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="max-w-7xl mx-auto px-3.5 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-8 sm:space-y-10">
      {/* 1. Header Banner & Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 font-extrabold text-xs uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Smart Shopping Overview</span>
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-black text-navy-900 tracking-tight">
            {getTimeGreeting()}, {user?.name ? user.name.split(' ')[0] : 'Shopper'}! 👋
          </h1>
          <p className="text-xs sm:text-sm md:text-base text-gray-500 mt-1">
            Here's what's happening with your tracked products across Amazon, Flipkart, AJIO & more.
          </p>
        </div>

        <Link to="/add-product" className="btn-primary w-full sm:w-fit text-xs sm:text-sm px-4 sm:px-5 py-2.5 sm:py-3 flex-shrink-0">
          <PlusCircle className="w-4 h-4" />
          <span>Track New Product</span>
        </Link>
      </div>

      {/* 2. Quick Track Bar */}
      <div className="p-2 sm:p-2.5 rounded-3xl bg-[#24128c] text-white shadow-xl">
        <form onSubmit={handleQuickUrlSubmit} className="flex items-center bg-white rounded-2xl p-1 sm:p-1.5 focus-within:ring-2 focus-within:ring-amber-400 transition-all">
          <div className="relative flex-1 min-w-0">
            <input
              type="text"
              placeholder="Paste any Amazon, Flipkart, AJIO, Myntra or Nykaa link to track instantly..."
              value={quickTrackUrl}
              onChange={(e) => setQuickTrackUrl(e.target.value)}
              className="w-full bg-transparent text-navy-900 placeholder-gray-400 px-3 sm:px-4 py-2 sm:py-2.5 text-xs sm:text-sm font-medium focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 sm:px-8 py-2.5 sm:py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-navy-950 font-black text-xs sm:text-sm tracking-wide transition-all shadow-sm cursor-pointer flex-shrink-0 whitespace-nowrap"
          >
            Track Price
          </button>
        </form>
      </div>

      {/* 3. Stats Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-black text-navy-900">Your Activity</h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
            {[...Array(4)].map((_, i) => (
              <StatCardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
            <StatCard
              icon={Package}
              label="Tracked Products"
              value={stats?.total_tracked ?? recentProducts.length}
              sublabel="Active scrapers"
              gradient="bg-gradient-brand"
            />
            <StatCard
              icon={Bell}
              label="Active Alerts"
              value={stats?.active_alerts ?? 0}
              sublabel="Watching target prices"
              gradient="bg-gradient-to-tr from-amber-500 to-orange-600"
            />
            <StatCard
              icon={TrendingDown}
              label="Price Drops"
              value={stats?.alerts_triggered_today ?? 0}
              sublabel="Triggered drops"
              gradient="bg-gradient-danger"
            />
            <StatCard
              icon={CheckCircle2}
              label="In Stock Status"
              value={stats?.products_in_stock ?? recentProducts.length}
              sublabel="Ready to buy"
              gradient="bg-gradient-success"
            />
          </div>
        )}
      </div>

      {/* 4. Tracked Products Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-black text-navy-900 tracking-tight">Your Tracked Products</h2>
            <p className="text-xs text-gray-500">Live prices and historical drop graphs</p>
          </div>

          {recentProducts.length > 0 && (
            <Link
              to="/products"
              className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            >
              <span>View All ({stats?.total_tracked ?? recentProducts.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
            {[...Array(4)].map((_, i) => (
              <ProductCardSkeleton key={i} />
            ))}
          </div>
        ) : recentProducts.length === 0 ? (
          <div className="card p-8 sm:p-16 text-center border-dashed border-2 border-gray-200">
            <div className="w-16 h-16 rounded-3xl bg-indigo-50 flex items-center justify-center mx-auto mb-4 border border-indigo-100 text-indigo-600 shadow-xs">
              <ShoppingBag className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-black text-navy-900 mb-2">No tracked products yet</h3>
            <p className="text-gray-500 mb-6 text-sm max-w-sm mx-auto leading-relaxed">
              Track a product to get price alerts and price history across Amazon, Flipkart, AJIO, Myntra, or Nykaa.
            </p>
            <Link to="/add-product" className="btn-primary inline-flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              <span>Track a Product</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
            {recentProducts.map((tracker) => (
              <ProductCard
                key={tracker.id}
                tracker={tracker}
                onViewHistory={(t) => setSelectedProductForHistory(t.product)}
                onRefresh={handleRefresh}
                onPause={handlePause}
                onResume={handleResume}
                onDelete={promptDelete}
                isLoading={actionLoadingId === tracker.id}
              />
            ))}
          </div>
        )}
      </div>

      {/* 5. Historical Price Modal */}
      {selectedProductForHistory && (
        <PriceHistoryModal
          product={selectedProductForHistory}
          onClose={() => setSelectedProductForHistory(null)}
        />
      )}

      {/* 6. Delete Confirmation Modal */}
      {trackerToDelete && (
        <DeleteTrackingModal
          tracker={trackerToDelete}
          isOpen={isDeleteModalOpen}
          onClose={() => {
            setIsDeleteModalOpen(false);
            setTrackerToDelete(null);
          }}
          onConfirm={handleConfirmDelete}
          isLoading={deleteLoading}
        />
      )}

      {/* 6. Quick Track Modal */}
      {quickTrackOpen && (
        <QuickTrackModal
          isOpen={quickTrackOpen}
          searchedUrl={quickTrackUrl}
          onClose={() => {
            setQuickTrackOpen(false);
            setQuickTrackUrl('');
          }}
          onSuccessTrack={() => {
            fetchDashboardData();
          }}
        />
      )}
    </div>
  );
}
