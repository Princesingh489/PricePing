import { useState } from 'react';
import {
  ShoppingCart, Plane, Smartphone, Shirt, Sparkles,
  Car, X
} from 'lucide-react';
import toast from 'react-hot-toast';

interface CategoryItem {
  id: string;
  title: string;
  subtitle: string;
  badge: string;
  icon: any;
  imgUrl: string;
  color: string;
  popularStores: string[];
  sampleDeal: string;
  samplePrice: string;
  sampleSavings: string;
}

const CATEGORIES: CategoryItem[] = [
  {
    id: 'grocery',
    title: 'Compare Grocery',
    subtitle: 'Blinkit • Zepto • Instamart',
    badge: '10 Min Delivery',
    icon: ShoppingCart,
    imgUrl: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&auto=format&fit=crop&q=80',
    color: 'text-emerald-600',
    popularStores: ['Blinkit', 'Zepto', 'Instamart', 'BigBasket'],
    sampleDeal: 'Amul Butter 500g + Aashirvaad Atta 10kg',
    samplePrice: '₹489',
    sampleSavings: 'Save ₹75 vs MRP',
  },
  {
    id: 'flights',
    title: 'Compare Flights',
    subtitle: 'MakeMyTrip • EaseMyTrip • Indigo',
    badge: 'Zero Convenience Fee',
    icon: Plane,
    imgUrl: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=300&auto=format&fit=crop&q=80',
    color: 'text-blue-600',
    popularStores: ['MakeMyTrip', 'EaseMyTrip', 'Indigo', 'Cleartrip'],
    sampleDeal: 'Delhi ✈️ Mumbai Direct Non-Stop',
    samplePrice: '₹3,899',
    sampleSavings: 'Cheapest on EaseMyTrip',
  },
  {
    id: 'electronics',
    title: 'Compare Electronics',
    subtitle: 'Amazon • Flipkart • Croma',
    badge: 'Lowest in 30 Days',
    icon: Smartphone,
    imgUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80',
    color: 'text-purple-600',
    popularStores: ['Amazon', 'Flipkart', 'Croma', 'Reliance Digital'],
    sampleDeal: 'Apple iPhone 16 (128GB Teal)',
    samplePrice: '₹72,499',
    sampleSavings: 'Save ₹7,401 + ₹4,000 Bank Offer',
  },
  {
    id: 'cabs',
    title: 'Compare Cabs',
    subtitle: 'Uber • Ola • Rapido',
    badge: 'Live Fare Radar',
    icon: Car,
    imgUrl: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=300&auto=format&fit=crop&q=80',
    color: 'text-amber-600',
    popularStores: ['Uber', 'Ola', 'Rapido', 'BluSmart'],
    sampleDeal: 'Airport Ride (Peak Hour Comparison)',
    samplePrice: '₹450',
    sampleSavings: 'Rapido Auto ₹180 cheaper',
  },
  {
    id: 'fashion',
    title: 'Compare Fashion',
    subtitle: 'Myntra • AJIO • Tata CliQ',
    badge: 'Extra 40% Coupon',
    icon: Shirt,
    imgUrl: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&auto=format&fit=crop&q=80',
    color: 'text-pink-600',
    popularStores: ['Myntra', 'AJIO', 'Tata CliQ', 'Nykaa Fashion'],
    sampleDeal: 'Nike Air Max Excee Sneakers',
    samplePrice: '₹4,495',
    sampleSavings: '50% OFF on Myntra EORS',
  },
  {
    id: 'beauty',
    title: 'Compare Beauty',
    subtitle: 'Nykaa • Purplle • Tira',
    badge: 'Buy 2 Get 1 Free',
    icon: Sparkles,
    imgUrl: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=300&auto=format&fit=crop&q=80',
    color: 'text-rose-600',
    popularStores: ['Nykaa', 'Purplle', 'Tira', 'Amazon Beauty'],
    sampleDeal: 'Minimalist 10% Niacinamide Serum',
    samplePrice: '₹559',
    sampleSavings: 'Extra 10% Off via Price Ping',
  },
];

interface Props {
  onSelectCategory?: (category: CategoryItem) => void;
}

export default function CategoryStrip({ onSelectCategory }: Props) {
  const [activeTab, setActiveTab] = useState<string>(CATEGORIES[0].id);
  const [selectedCat, setSelectedCat] = useState<CategoryItem | null>(null);

  const handleCardClick = (cat: CategoryItem) => {
    setSelectedCat(cat);
    if (onSelectCategory) onSelectCategory(cat);
  };

  return (
    <div className="my-6">
      {/* Sub-Header Soft Light Blue Pill (Exact match to screenshot) */}
      <div className="flex justify-center mb-6">
        <div className="px-6 py-2 rounded-full bg-[#edf2fe] border border-blue-100/80 text-center shadow-xs">
          <p className="text-[12px] sm:text-[13px] font-medium text-[#2d3a82]">
            Compare prices across flights, grocery, cabs & more. Choose the best option & save instantly.
          </p>
        </div>
      </div>

      {/* Main Dual-Column Section (Left Category Titles + Right Cards Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 items-center bg-white p-4 sm:p-6 lg:p-8 rounded-3xl border border-gray-150 shadow-sm">
        {/* Left Side: Category Text List (Horizontal swipe on phone, vertical column on laptop) */}
        <div className="lg:col-span-3 flex lg:flex-col overflow-x-auto lg:overflow-x-visible gap-2 lg:space-y-2 border-b lg:border-b-0 lg:border-r border-gray-100 pb-3 lg:pb-0 pr-0 lg:pr-4">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveTab(cat.id)}
              className={`whitespace-nowrap flex-shrink-0 lg:w-full text-left px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-xl font-bold text-xs sm:text-sm transition-all flex items-center justify-between gap-2 cursor-pointer ${
                activeTab === cat.id
                  ? 'text-[#24128c] bg-indigo-50/70 border-l-2 lg:border-l-4 border-[#24128c]'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <span>{cat.title}</span>
              {activeTab === cat.id && (
                <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-[#24128c]" />
              )}
            </button>
          ))}
        </div>

        {/* Right Side: Horizontal Row of Visual Cards */}
        <div className="lg:col-span-9 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
          {CATEGORIES.slice(0, 5).map((cat) => (
            <div
              key={cat.id}
              onClick={() => handleCardClick(cat)}
              className="group p-3 rounded-2xl border border-gray-100 bg-white hover:border-indigo-200 hover:shadow-md transition-all text-center flex flex-col items-center cursor-pointer"
            >
              <div className="w-14 h-14 rounded-2xl overflow-hidden mb-2.5 shadow-sm group-hover:scale-105 transition-transform">
                <img
                  src={cat.imgUrl}
                  alt={cat.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <h4 className="text-xs font-black text-navy-900 capitalize">
                {cat.id}
              </h4>
              <p className="text-[10px] text-gray-400 font-medium truncate w-full mt-0.5">
                {cat.subtitle}
              </p>
              <div className="mt-2 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[9px] font-bold">
                {cat.badge}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detail Modal if clicked */}
      {selectedCat && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4 border border-gray-150 animate-slide-in">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <img src={selectedCat.imgUrl} alt={selectedCat.title} className="w-10 h-10 rounded-xl object-cover" />
                <div>
                  <h3 className="text-base font-black text-navy-900">{selectedCat.title}</h3>
                  <p className="text-xs text-gray-500">{selectedCat.subtitle}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCat(null)}
                className="p-1 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-bold text-gray-500 uppercase">Popular Stores & Platforms</div>
              <div className="flex flex-wrap gap-2">
                {selectedCat.popularStores.map((st) => (
                  <span key={st} className="px-2.5 py-1 rounded-full bg-gray-100 text-gray-800 text-xs font-semibold">
                    {st}
                  </span>
                ))}
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-indigo-50/60 border border-indigo-100 text-xs space-y-1">
              <div className="font-bold text-indigo-900">Featured Deal</div>
              <div className="text-gray-700">{selectedCat.sampleDeal}</div>
              <div className="flex items-center gap-2 pt-1 font-black">
                <span className="text-indigo-600 text-sm">{selectedCat.samplePrice}</span>
                <span className="text-emerald-600 text-[11px] font-bold">{selectedCat.sampleSavings}</span>
              </div>
            </div>

            <button
              onClick={() => {
                toast.success(`Comparing best live prices for ${selectedCat.title}!`);
                setSelectedCat(null);
              }}
              className="btn-primary w-full py-2.5 rounded-xl text-xs font-bold"
            >
              Compare Live Offers
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
