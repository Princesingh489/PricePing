import { useEffect, useState, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { productsApi } from '../services/api';
import type { TrackedProduct } from '../types';
import toast from 'react-hot-toast';
import {
  PlusCircle, ShoppingBag
} from 'lucide-react';
import ProductCard from '../components/products/ProductCard';
import ProductFilters from '../components/products/ProductFilters';
import { ProductCardSkeleton } from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';
import PriceHistoryModal from '../components/modals/PriceHistoryModal';

import DeleteTrackingModal from '../components/modals/DeleteTrackingModal';

export default function MyProducts() {
  const [products, setProducts] = useState<TrackedProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [selectedProductForHistory, setSelectedProductForHistory] = useState<any>(null);
  const [trackerToDelete, setTrackerToDelete] = useState<TrackedProduct | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchProducts = useCallback(() => {
    setLoading(true);
    productsApi.list({
      search: search || undefined,
      platform: platformFilter !== 'all' ? platformFilter : undefined,
    })
      .then((res) => setProducts(res.data || []))
      .catch(() => toast.error('Failed to load products'))
      .finally(() => setLoading(false));
  }, [search, platformFilter]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const filteredProducts = useMemo(() => {
    if (statusFilter === 'all') return products;
    if (statusFilter === 'active') return products.filter((p) => p.tracking_status === 'active');
    if (statusFilter === 'paused') return products.filter((p) => p.tracking_status === 'paused');
    return products;
  }, [products, statusFilter]);

  const handlePause = async (id: number) => {
    setActionLoadingId(id);
    try {
      await productsApi.pause(id);
      setProducts((prev) => prev.map((p) => (p.id === id ? { ...p, tracking_status: 'paused' } : p)));
      toast.success('Tracking paused');
    } catch {
      toast.error('Failed to pause tracking');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleResume = async (id: number) => {
    setActionLoadingId(id);
    try {
      await productsApi.resume(id);
      setProducts((prev) => prev.map((p) => (p.id === id ? { ...p, tracking_status: 'active' } : p)));
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
      setProducts((prev) => prev.filter((p) => p.id !== trackerId));
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
      setTimeout(fetchProducts, 2500);
    } catch {
      toast.error('Failed to refresh price');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">My Products</h1>
          <p className="text-gray-500 text-sm mt-1">
            {products.length} product{products.length !== 1 ? 's' : ''} actively tracked across stores
          </p>
        </div>

        <Link to="/add-product" className="btn-primary flex items-center gap-2 w-fit">
          <PlusCircle className="w-4 h-4" />
          <span>Add New Product</span>
        </Link>
      </div>

      {/* Filter Toolbar */}
      <ProductFilters
        search={search}
        onSearchChange={setSearch}
        selectedPlatform={platformFilter}
        onPlatformChange={setPlatformFilter}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
      />

      {/* Product Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {[...Array(6)].map((_, i) => (
            <ProductCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredProducts.length === 0 ? (
        <EmptyState
          icon={ShoppingBag}
          title={search || platformFilter !== 'all' || statusFilter !== 'all' ? 'No products found' : 'No tracked products yet.'}
          description={
            search || platformFilter !== 'all' || statusFilter !== 'all'
              ? 'Try adjusting your search query or filter options to see more products.'
              : 'Track a product to get price alerts and price history across Amazon, Flipkart, AJIO, Myntra, or Nykaa.'
          }
          actionText="Track a Product"
          actionHref="/add-product"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredProducts.map((tracker) => (
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

      {/* Detailed Price History Modal */}
      {selectedProductForHistory && (
        <PriceHistoryModal
          product={selectedProductForHistory}
          onClose={() => setSelectedProductForHistory(null)}
        />
      )}

      {/* Delete Confirmation Modal */}
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
    </div>
  );
}
