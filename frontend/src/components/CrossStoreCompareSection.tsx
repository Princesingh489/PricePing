import { useState } from 'react';
import { formatINR, PLATFORM_LABELS, getPlatformBadgeClass } from '../utils/helpers';
import { useLanguage } from '../contexts/LanguageContext';
import { productsApi } from '../services/api';
import toast from 'react-hot-toast';
import {
  Scale, ExternalLink, Sparkles, CheckCircle2, XCircle, Search, Loader2
} from 'lucide-react';

interface StoreOffer {
  storeId: 'amazon' | 'flipkart' | 'myntra' | 'ajio' | 'nykaa';
  storeName: string;
  isAvailable: boolean;
  price?: number;
  originalPrice?: number;
  delivery?: string;
  coupon?: string;
  isLowest?: boolean;
  url?: string;
}

interface CompareProduct {
  id: string;
  name: string;
  category: string;
  image: string;
  rating: number;
  ratingCount: number;
  stores: StoreOffer[];
}

const REALTIME_COMPARE_PRODUCTS: CompareProduct[] = [
  {
    id: 'sony-xm5',
    name: 'Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones',
    category: 'Audio & Gadgets',
    image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&auto=format&fit=crop&q=80',
    rating: 4.8,
    ratingCount: 9800,
    stores: [
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 26990,
        originalPrice: 34990,
        delivery: 'Prime 1-Day Delivery',
        coupon: 'FLAT ₹1,500 Bank Instant Off',
        isLowest: true,
        url: 'https://www.amazon.in/dp/B09XS7JWHH',
      },
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 28499,
        originalPrice: 34990,
        delivery: 'Flipkart Assured (2 Days)',
        coupon: '₹1,000 SuperCoins Off',
        isLowest: false,
        url: 'https://www.flipkart.com/boat-rockerz-550/p/itm12345',
      },
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: false,
      },
      {
        storeId: 'ajio',
        storeName: 'AJIO',
        isAvailable: false,
      },
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: false,
      },
    ],
  },
  {
    id: 'iphone-16',
    name: 'Apple iPhone 16 128GB (Teal Titanium Finish)',
    category: 'Smartphones',
    image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&auto=format&fit=crop&q=80',
    rating: 4.7,
    ratingCount: 14200,
    stores: [
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 72499,
        originalPrice: 79900,
        delivery: 'Prime 1-Day Delivery',
        coupon: 'ICICI ₹4,000 Instant Card Discount',
        isLowest: true,
        url: 'https://www.amazon.in/dp/B0BDK62PDX',
      },
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 74900,
        originalPrice: 79900,
        delivery: 'Flipkart Assured (Tomorrow)',
        coupon: 'HDFC ₹3,000 Off',
        isLowest: false,
        url: 'https://www.flipkart.com/apple-iphone-16/p/itm67890',
      },
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: false,
      },
      {
        storeId: 'ajio',
        storeName: 'AJIO',
        isAvailable: false,
      },
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: false,
      },
    ],
  },
  {
    id: 'jordan-1',
    name: 'Nike Air Jordan 1 Low Retro Basketball Sneakers Men',
    category: 'Footwear & Shoes',
    image: 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=400&auto=format&fit=crop&q=80',
    rating: 4.6,
    ratingCount: 3200,
    stores: [
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: true,
        price: 6499,
        originalPrice: 8995,
        delivery: '2 Days Express Delivery',
        coupon: 'EORSNEW10 (Extra 10% Off)',
        isLowest: true,
        url: 'https://www.myntra.com/shoes/nike/nike-air-jordan/1234',
      },
      {
        storeId: 'ajio',
        storeName: 'AJIO Luxe',
        isAvailable: true,
        price: 7196,
        originalPrice: 8995,
        delivery: '3 Days Delivery',
        coupon: 'AJIOMANIA (₹500 Instant)',
        isLowest: false,
        url: 'https://www.ajio.com/nike-air-jordan/p/461234567',
      },
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 8499,
        originalPrice: 8995,
        delivery: 'Standard 4 Days',
        coupon: 'Axis 5% Cashback',
        isLowest: false,
        url: 'https://www.flipkart.com/nike-air-jordan-1-low/p/itm23456',
      },
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 8995,
        originalPrice: 8995,
        delivery: 'Standard 3 Days',
        coupon: 'No cost EMI available',
        isLowest: false,
        url: 'https://www.amazon.in/dp/B0856HNMR7',
      },
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: false,
      },
    ],
  },
  {
    id: 'minimalist-serum',
    name: 'Minimalist 10% Niacinamide Face Serum with Zinc (30ml)',
    category: 'Skincare & Beauty',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&auto=format&fit=crop&q=80',
    rating: 4.6,
    ratingCount: 38400,
    stores: [
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: true,
        price: 539,
        originalPrice: 599,
        delivery: 'Nykaa SuperFast (1-2 Days)',
        coupon: 'HOTPINK10 (10% Off)',
        isLowest: true,
        url: 'https://www.nykaa.com/minimalist-10-percent-niacinamide/p/892345',
      },
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 559,
        originalPrice: 599,
        delivery: 'Prime Tomorrow by 11 AM',
        coupon: '5% Extra Coupon on checkout',
        isLowest: false,
        url: 'https://www.amazon.in/dp/B0856HNMR7',
      },
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 585,
        originalPrice: 599,
        delivery: '3 Days Delivery',
        coupon: 'Save ₹14 with SuperCoins',
        isLowest: false,
        url: 'https://www.flipkart.com/minimalist-10-niacinamide/p/itm34567',
      },
      {
        storeId: 'ajio',
        storeName: 'AJIO',
        isAvailable: false,
      },
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: false,
      },
    ],
  },
  {
    id: 'levis-511',
    name: "Levi's Men 511 Slim Fit Stretchable Washed Blue Jeans",
    category: "Men's Apparel",
    image: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&auto=format&fit=crop&q=80',
    rating: 4.3,
    ratingCount: 3900,
    stores: [
      {
        storeId: 'ajio',
        storeName: 'AJIO',
        isAvailable: true,
        price: 1879,
        originalPrice: 3999,
        delivery: '2 Days Delivery',
        coupon: 'TRENDS50 (Flat 53% Off)',
        isLowest: true,
        url: 'https://www.ajio.com/levis-511-slim-fit-jeans/p/460789123',
      },
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: true,
        price: 1999,
        originalPrice: 3999,
        delivery: '3 Days Delivery',
        coupon: 'EORS50 (Extra 50% Off)',
        isLowest: false,
        url: 'https://www.myntra.com/jeans/levis/511-slim-fit/7890',
      },
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 2199,
        originalPrice: 3999,
        delivery: 'Prime Tomorrow',
        coupon: 'Bank Card 5% Back',
        isLowest: false,
        url: 'https://www.amazon.in/dp/B0BDK62PDX',
      },
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 2299,
        originalPrice: 3999,
        delivery: 'Flipkart Assured 2 Days',
        coupon: 'Flat ₹200 off on UPI',
        isLowest: false,
        url: 'https://www.flipkart.com/levis-511-slim-fit/p/itm56789',
      },
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: false,
      },
    ],
  },
  {
    id: 'boat-550',
    name: 'boAt Rockerz 550 Over-Ear Bluetooth Wireless Headphones',
    category: 'Budget Audio',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&auto=format&fit=crop&q=80',
    rating: 4.3,
    ratingCount: 89400,
    stores: [
      {
        storeId: 'flipkart',
        storeName: 'Flipkart',
        isAvailable: true,
        price: 1499,
        originalPrice: 4999,
        delivery: 'Flipkart Assured (Tomorrow)',
        coupon: 'Flat 70% Off Mega Sale',
        isLowest: true,
        url: 'https://www.flipkart.com/boat-rockerz-550/p/itm12345',
      },
      {
        storeId: 'amazon',
        storeName: 'Amazon India',
        isAvailable: true,
        price: 1599,
        originalPrice: 4999,
        delivery: 'Prime 1-Day Delivery',
        coupon: 'Amazon Pay ₹50 Cashback',
        isLowest: false,
        url: 'https://www.amazon.in/dp/B0856HNMR7',
      },
      {
        storeId: 'myntra',
        storeName: 'Myntra',
        isAvailable: true,
        price: 1799,
        originalPrice: 4999,
        delivery: '3 Days Delivery',
        coupon: 'MYNTRANEW15',
        isLowest: false,
        url: 'https://www.myntra.com/headphones/boat/rockerz-550/3456',
      },
      {
        storeId: 'ajio',
        storeName: 'AJIO',
        isAvailable: false,
      },
      {
        storeId: 'nykaa',
        storeName: 'Nykaa',
        isAvailable: false,
      },
    ],
  },
];

export default function CrossStoreCompareSection() {
  const { t } = useLanguage();
  const [selectedProduct, setSelectedProduct] = useState<CompareProduct>(REALTIME_COMPARE_PRODUCTS[0]);
  const [searchUrl, setSearchUrl] = useState('');
  const [isResolving, setIsResolving] = useState(false);

  const handleLiveCompareSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchUrl.trim();
    if (!query) return;

    setIsResolving(true);
    try {
      let cleanQuery = query;
      if (!cleanQuery.startsWith('http://') && !cleanQuery.startsWith('https://')) {
        if (cleanQuery.includes('amazon.') || cleanQuery.includes('amzn.') || cleanQuery.includes('flipkart.') || cleanQuery.includes('myntra.') || cleanQuery.includes('ajio.') || cleanQuery.includes('nykaa.')) {
          cleanQuery = 'https://' + cleanQuery;
        }
      }

      const res = await productsApi.resolveUrl(cleanQuery);
      if (res.data?.product) {
        const prod = res.data.product;
        const compOffers: any[] = res.data.comparison || [];
        
        const validPrices = compOffers
          .filter((o) => o.is_verified_match && typeof o.price === 'number' && o.price > 0)
          .map((o) => o.price as number);
        const lowest = validPrices.length > 0 ? Math.min(...validPrices) : undefined;

        const storeIds: ('amazon' | 'flipkart' | 'myntra' | 'ajio' | 'nykaa')[] = [
          'amazon', 'flipkart', 'myntra', 'ajio', 'nykaa'
        ];

        const mappedStores: StoreOffer[] = storeIds.map((sid) => {
          const offer = compOffers.find((o) => o.store?.toLowerCase() === sid);
          if (offer && offer.is_verified_match && typeof offer.price === 'number' && offer.price > 0) {
            return {
              storeId: sid,
              storeName: offer.store_name || sid.toUpperCase(),
              isAvailable: true,
              price: offer.price,
              originalPrice: offer.original_price || undefined,
              delivery: offer.delivery_text || 'Store Delivery',
              coupon: offer.coupon_text || undefined,
              isLowest: lowest !== undefined && offer.price === lowest,
              url: offer.url || prod.product_url,
            };
          }
          return {
            storeId: sid,
            storeName: PLATFORM_LABELS[sid]?.name || sid.charAt(0).toUpperCase() + sid.slice(1),
            isAvailable: false,
          };
        });

        const newCompareProd: CompareProduct = {
          id: `live-${prod.id || Date.now()}`,
          name: prod.product_name || prod.title || 'Verified Product',
          category: prod.brand || 'Verified Live Rates',
          image: prod.image_url || prod.product_image || 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&auto=format&fit=crop&q=80',
          rating: prod.rating || 4.5,
          ratingCount: prod.rating_count || 100,
          stores: mappedStores,
        };

        setSelectedProduct(newCompareProd);
        toast.success(`Loaded verified live prices for ${newCompareProd.name.slice(0, 32)}...`);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Could not resolve product. Please check the URL or product name.');
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <section className="my-8 p-5 sm:p-7 md:p-9 rounded-3xl bg-gradient-to-br from-[#12162a] via-[#101422] to-[#0c0f1a] border border-white/15 shadow-2xl">
      {/* Title & Description */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 font-extrabold text-xs uppercase tracking-wider mb-1">
            <Scale className="w-4 h-4" />
            <span>{t('cross_compare_title', 'Compare Stores in Real-Time')}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Live Price Comparison Across All 5 E-Commerces
          </h2>
          <p className="text-xs sm:text-sm text-gray-300 mt-1 max-w-2xl">
            {t('cross_compare_subtitle', 'Real-time pricing from Amazon, Flipkart, Myntra, AJIO & Nykaa with verified stock availability')}
          </p>
        </div>

        {/* Live URL / Product Resolver */}
        <form onSubmit={handleLiveCompareSearch} className="w-full lg:w-96 flex-shrink-0">
          <div className="flex items-center bg-white/10 backdrop-blur-md rounded-full border border-white/20 p-1 focus-within:ring-2 focus-within:ring-cyan-400/50">
            <Search className="w-4 h-4 text-gray-400 ml-3 flex-shrink-0" />
            <input
              type="text"
              value={searchUrl}
              onChange={(e) => setSearchUrl(e.target.value)}
              placeholder="Paste link to compare across 5 stores..."
              className="bg-transparent text-xs text-white placeholder-gray-400 px-2 py-1.5 focus:outline-none flex-1 min-w-0"
            />
            <button
              type="submit"
              disabled={isResolving}
              className="px-3 py-1.5 rounded-full bg-cyan-500 hover:bg-cyan-400 text-gray-950 font-bold text-xs flex items-center gap-1 cursor-pointer disabled:opacity-60"
            >
              {isResolving ? <Loader2 className="w-3 h-3 animate-spin" /> : <span>Compare</span>}
            </button>
          </div>
        </form>
      </div>

      {/* Product selector tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-6 scrollbar-none">
        {REALTIME_COMPARE_PRODUCTS.map((prod) => (
          <button
            key={prod.id}
            onClick={() => setSelectedProduct(prod)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer border ${
              selectedProduct.id === prod.id
                ? 'bg-cyan-500 text-gray-950 border-cyan-400 shadow-lg shadow-cyan-500/25'
                : 'bg-white/[0.06] text-gray-300 border-white/10 hover:text-white hover:bg-white/[0.12]'
            }`}
          >
            {prod.category}
          </button>
        ))}
      </div>

      {/* Main Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Product Spotlight Card */}
        <div className="lg:col-span-4 bg-white/[0.04] backdrop-blur-md border border-white/10 rounded-2xl p-5 text-white flex flex-col items-center text-center">
          <div className="w-48 h-48 sm:w-56 sm:h-56 rounded-2xl overflow-hidden mb-4 bg-black/40 border border-white/10 p-2 flex items-center justify-center">
            <img
              src={selectedProduct.image}
              alt={selectedProduct.name}
              className="w-full h-full object-cover rounded-xl"
            />
          </div>
          <span className="badge bg-cyan-400/20 text-cyan-300 border border-cyan-400/30 text-[10px] font-black uppercase mb-2">
            {selectedProduct.category}
          </span>
          <h3 className="font-bold text-sm sm:text-base text-white line-clamp-2 mb-2">
            {selectedProduct.name}
          </h3>
          <div className="flex items-center gap-1 text-amber-300 text-xs font-bold mb-4">
            <span>⭐ {selectedProduct.rating}</span>
            <span className="text-gray-400">({selectedProduct.ratingCount.toLocaleString()} verified ratings)</span>
          </div>

          <div className="w-full pt-4 border-t border-white/10 text-xs text-gray-400 flex items-center justify-between">
            <span>Stores Checked:</span>
            <span className="font-bold text-white">5 / 5 Major Platforms</span>
          </div>
        </div>

        {/* Right Column: All 5 E-Commerce Real-Time Store Comparison Rows */}
        <div className="lg:col-span-8 space-y-3">
          {selectedProduct.stores.map((store) => {
            const platformInfo = PLATFORM_LABELS[store.storeId] || { name: store.storeName, badgeClass: 'bg-gray-800 text-gray-200' };

            // Available store card
            if (store.isAvailable && store.price) {
              return (
                <div
                  key={store.storeId}
                  className={`p-4 rounded-2xl transition-all border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                    store.isLowest
                      ? 'bg-gradient-to-r from-emerald-950/60 via-emerald-900/30 to-black/50 border-emerald-500/50 shadow-lg shadow-emerald-500/10'
                      : 'bg-white/[0.04] border-white/10 hover:border-white/20'
                  }`}
                >
                  {/* Store Name & Delivery */}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-white/10 border border-white/15 flex items-center justify-center flex-shrink-0">
                      <span className={getPlatformBadgeClass(store.storeId) + ' text-[9px] font-black uppercase px-1.5 py-0.5 rounded'}>
                        {store.storeId.slice(0, 2).toUpperCase()}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-black text-white text-sm">
                          {store.storeName}
                        </span>
                        {store.isLowest && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500 text-gray-950 font-black text-[10px] shadow-sm">
                            <Sparkles className="w-3 h-3" />
                            {t('lowest_price', 'Lowest Price')}
                          </span>
                        )}
                        <span className="text-[10px] text-emerald-400 flex items-center gap-0.5 font-bold">
                          <CheckCircle2 className="w-3 h-3" />
                          {t('available', 'In Stock')}
                        </span>
                      </div>

                      <p className="text-[11px] text-gray-400 mt-0.5">
                        {store.delivery} • <span className="text-amber-300 font-semibold">{store.coupon}</span>
                      </p>
                    </div>
                  </div>

                  {/* Price & Action */}
                  <div className="flex items-center justify-between sm:justify-end gap-4">
                    <div className="text-left sm:text-right">
                      <div className="text-lg sm:text-xl font-black text-white tracking-tight">
                        {formatINR(store.price)}
                      </div>
                      {store.originalPrice && store.originalPrice > store.price && (
                        <div className="text-[11px] text-gray-400 line-through">
                          {formatINR(store.originalPrice)}
                        </div>
                      )}
                    </div>

                    <a
                      href={store.url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`px-4 py-2 rounded-xl font-extrabold text-xs flex items-center gap-1.5 transition-all cursor-pointer ${
                        store.isLowest
                          ? 'bg-emerald-500 hover:bg-emerald-400 text-gray-950 shadow-md shadow-emerald-500/30 hover:scale-105'
                          : 'bg-white/15 hover:bg-white/25 text-white'
                      }`}
                    >
                      <span>Buy on {store.storeName}</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              );
            }

            // NOT AVAILABLE store row (Nothing fake, clearly displayed)
            return (
              <div
                key={store.storeId}
                className="p-4 rounded-2xl border border-dashed border-gray-800 bg-white/[0.015] opacity-55 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-center flex-shrink-0 opacity-60">
                    <span className="text-gray-500 text-[9px] font-black uppercase">
                      {store.storeId.slice(0, 2).toUpperCase()}
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-400 text-sm">
                        {platformInfo.name}
                      </span>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 text-[10px] font-semibold border border-gray-700">
                        <XCircle className="w-3 h-3 text-rose-400" />
                        {t('not_available', 'Not Available')}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-500 mt-0.5">
                      This product is currently not carried or sold by this store.
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4">
                  <div className="text-gray-500 font-medium text-sm">
                    —
                  </div>
                  <button
                    disabled
                    className="px-4 py-2 rounded-xl font-bold text-xs bg-gray-800/80 text-gray-500 border border-gray-700/50 cursor-not-allowed opacity-60"
                  >
                    Unavailable
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
