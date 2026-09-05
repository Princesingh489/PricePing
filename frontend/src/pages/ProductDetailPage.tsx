import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsApi } from '../services/api';
import toast from 'react-hot-toast';
import type { ProductDetail, RealPriceHistoryPoint } from '../types';
import PricePingProductView from '../components/product/PricePingProductView';
import { ProductCardSkeleton } from '../components/common/SkeletonLoader';

export default function ProductDetailPage() {
  const { trackerId } = useParams<{ trackerId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [historyPoints, setHistoryPoints] = useState<RealPriceHistoryPoint[]>([]);
  const [coverageLabel, setCoverageLabel] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);

  const fetchDetail = async () => {
    if (!trackerId) return;
    try {
      const res = await productsApi.getDetail(Number(trackerId));
      setDetail(res.data);

      if (res.data?.product?.id) {
        try {
          const histRes = await productsApi.getPriceHistory(res.data.product.id, 'all', 'all');
          if (histRes.data) {
            setHistoryPoints(histRes.data.data || []);
            setCoverageLabel(histRes.data.coverage_label || '');
          }
        } catch {
          // Secondary fetch fallback
        }
      }
    } catch {
      toast.error('Could not load product details.');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trackerId]);

  const handleSearchNewProduct = async (newUrl: string) => {
    if (!newUrl.trim()) return;
    setIsSearching(true);
    try {
      let cleanQuery = newUrl.trim();
      if (!cleanQuery.startsWith('http://') && !cleanQuery.startsWith('https://')) {
        if (cleanQuery.includes('amazon.') || cleanQuery.includes('amzn.') || cleanQuery.includes('flipkart.') || cleanQuery.includes('myntra.') || cleanQuery.includes('ajio.') || cleanQuery.includes('nykaa.')) {
          cleanQuery = 'https://' + cleanQuery;
        }
      }
      const res = await productsApi.resolveUrl(cleanQuery);
      if (res.data?.tracker_id) {
        navigate(`/product/${res.data.tracker_id}`);
      } else if (res.data?.product) {
        setDetail((prev) => prev ? {
          ...prev,
          product: res.data.product,
          cross_store_offers: res.data.comparison || [],
          real_statistics: res.data.statistics,
        } : {
          tracker_id: 0,
          product: res.data.product,
          price_history: [],
          deal_score: {
            recommendation: 'FAIR_PRICE',
            confidence: 0.9,
            percentile: null,
            avg_price: null,
            lowest_price: null,
            highest_price: null,
            data_points: 1,
            tracking_days: 1,
            message: '',
          },
          stats: {
            lowest_ever: null,
            highest_ever: null,
            average_price: null,
            data_points: 1,
            tracking_days: 1,
          },
          existing_alert: null,
          cross_store_offers: res.data.comparison || [],
          real_statistics: res.data.statistics,
        });
        toast.success(`Loaded verified details for ${res.data.product.product_name.slice(0, 30)}...`);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to fetch new product URL');
    } finally {
      setIsSearching(false);
    }
  };

  if (loading || !detail) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ProductCardSkeleton />
          <ProductCardSkeleton />
          <ProductCardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <PricePingProductView
      product={detail.product}
      trackerId={detail.tracker_id}
      crossStoreOffers={detail.cross_store_offers || []}
      canonicalProduct={detail.canonical_product}
      availabilitySummary={detail.availability_summary}
      statistics={detail.real_statistics}
      historyPoints={historyPoints}
      coverageLabel={coverageLabel}
      onSearchUrl={handleSearchNewProduct}
      isSearching={isSearching}
    />
  );
}
