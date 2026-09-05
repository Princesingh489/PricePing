import { useState } from 'react';
import { Gift, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';

interface GiftCard {
  id: string;
  brand: string;
  category: string;
  discount: string;
  code: string;
  description: string;
  color: string;
  bgGradient: string;
}

const GIFT_CARDS: GiftCard[] = [
  {
    id: 'gc-1',
    brand: 'Amazon Pay',
    category: 'Shopping & Bills',
    discount: 'Flat 5% Cashback',
    code: 'AMZPING5',
    description: 'Instant credit on Amazon India orders & utility bill payments',
    color: 'text-amber-500',
    bgGradient: 'from-amber-500/20 via-orange-500/10 to-transparent',
  },
  {
    id: 'gc-2',
    brand: 'Flipkart Gift Card',
    category: 'Electronics & Fashion',
    discount: 'Extra ₹250 Off',
    code: 'FKPING250',
    description: 'Valid on Big Billion Days & all electronics above ₹2,000',
    color: 'text-blue-500',
    bgGradient: 'from-blue-500/20 via-indigo-500/10 to-transparent',
  },
  {
    id: 'gc-3',
    brand: 'Myntra Voucher',
    category: 'Fashion & Footwear',
    discount: 'Flat 12% Off',
    code: 'MYNPING12',
    description: 'Applicable across 1,000+ top fashion brands on Myntra',
    color: 'text-pink-500',
    bgGradient: 'from-pink-500/20 via-rose-500/10 to-transparent',
  },
  {
    id: 'gc-4',
    brand: 'Swiggy & Instamart',
    category: 'Food & Quick Grocery',
    discount: 'Up to ₹120 Off',
    code: 'SWIGPING120',
    description: 'Valid on restaurant orders and 10-minute grocery delivery',
    color: 'text-orange-500',
    bgGradient: 'from-orange-500/20 via-amber-500/10 to-transparent',
  },
  {
    id: 'gc-5',
    brand: 'Zomato Gold & Dining',
    category: 'Dining & Delivery',
    discount: 'Flat 15% Off',
    code: 'ZOMPING15',
    description: 'Instant discount at 10,000+ partner restaurants in India',
    color: 'text-red-500',
    bgGradient: 'from-red-500/20 via-rose-500/10 to-transparent',
  },
  {
    id: 'gc-6',
    brand: 'Uber Rides & Cabs',
    category: 'Commute & Travel',
    discount: 'Flat 20% Off',
    code: 'UBERPING20',
    description: 'Valid on Uber Premier, Go, Auto & Intercity rides',
    color: 'text-cyan-500',
    bgGradient: 'from-cyan-500/20 via-blue-500/10 to-transparent',
  },
];

export default function GiftCardsSection() {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (gc: GiftCard) => {
    navigator.clipboard.writeText(gc.code);
    setCopiedId(gc.id);
    toast.success(`Coupon code ${gc.code} copied!`);
    setTimeout(() => setCopiedId(null), 2500);
  };

  return (
    <section id="gift-cards" className="my-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-amber-400 font-extrabold text-xs uppercase tracking-wider mb-1">
            <Gift className="w-4 h-4" />
            Price Ping Gift Cards & Instant Cashback
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Exclusive Coupons & Gift Vouchers
          </h2>
          <p className="text-sm text-gray-400 mt-1">Stack extra cashback and discount codes on top of live price drops</p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-amber-300 bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 rounded-full">
            🎁 Guaranteed 100% Working
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {GIFT_CARDS.map((gc) => {
          const isCopied = copiedId === gc.id;
          return (
            <div
              key={gc.id}
              className={`p-5 rounded-2xl bg-gradient-to-br ${gc.bgGradient} bg-surface-card border border-white/10 hover:border-white/20 transition-all duration-300 flex flex-col justify-between group hover:-translate-y-1 hover:shadow-xl`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                    {gc.category}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-black">
                    {gc.discount}
                  </span>
                </div>

                <h3 className="text-lg font-black text-white mb-1 group-hover:text-amber-300 transition-colors">
                  {gc.brand}
                </h3>
                <p className="text-xs text-gray-400 mb-4">{gc.description}</p>
              </div>

              <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between gap-3">
                <div className="px-3 py-1.5 rounded-xl bg-black/50 border border-white/15 font-mono text-xs font-black text-amber-300 tracking-wider">
                  {gc.code}
                </div>

                <button
                  onClick={() => handleCopy(gc)}
                  className="btn-primary text-xs py-2 px-3.5"
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-300" /> Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" /> Copy Code
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
