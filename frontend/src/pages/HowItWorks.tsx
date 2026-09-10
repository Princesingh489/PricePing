import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { Link2, Search, Scale, BookmarkPlus, Eye, BellRing, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      icon: <Link2 className="w-6 h-6 text-indigo-600" />,
      title: 'Search or Paste Any Store URL',
      description:
        'Copy a product link from Amazon India, Flipkart, Myntra, Ajio, or Nykaa, or simply type the product name into the Price Ping search bar.',
    },
    {
      num: '02',
      icon: <Search className="w-6 h-6 text-indigo-600" />,
      title: 'Instant Product Identification',
      description:
        'Price Ping parses the canonical product identity, identifying the brand, model, storage, color variant, and unique store identifiers (ASIN, PID, or SKU).',
    },
    {
      num: '03',
      icon: <Scale className="w-6 h-6 text-indigo-600" />,
      title: 'Multi-Store Price Comparison',
      description:
        'Price Ping scans across all 5 supported Indian stores to compare live prices, delivery estimates, seller ratings, and stock status in one unified view.',
    },
    {
      num: '04',
      icon: <BookmarkPlus className="w-6 h-6 text-indigo-600" />,
      title: 'Set Target Price Threshold',
      description:
        'Add the product to your personal tracking dashboard and specify your preferred buying price or desired percentage drop.',
    },
    {
      num: '05',
      icon: <Eye className="w-6 h-6 text-indigo-600" />,
      title: '24/7 Automated Price Monitoring',
      description:
        'Our background workers continuously monitor price adjustments and flash sales directly from the retail platforms.',
    },
    {
      num: '06',
      icon: <BellRing className="w-6 h-6 text-indigo-600" />,
      title: 'Instant Price Drop Notification',
      description:
        'As soon as any store drops its price to or below your target threshold, you receive an immediate alert so you can complete your purchase at the lowest rate.',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      <SEOHead
        title="How Price Ping Works – 6-Step Price Tracking & Comparison Guide"
        description="Discover how Price Ping compares prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa, tracks price drops 24/7, and notifies you when target prices are reached."
        canonical="https://priceping.store/how-it-works"
        keywords="how Price Ping works, price tracker guide, compare Amazon and Flipkart prices, Price Ping price alerts"
      />

      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">How It Works</span>
      </nav>

      {/* Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          How Price Ping Works
        </h1>
        <p className="text-slate-600 text-base sm:text-lg leading-relaxed">
          Follow these 6 simple steps to track prices, compare e-commerce deals, and never overpay on your online purchases.
        </p>
      </div>

      {/* Step Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {steps.map((step) => (
          <div
            key={step.num}
            className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm relative overflow-hidden flex flex-col justify-between space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center">
                {step.icon}
              </div>
              <span className="text-3xl font-black text-slate-200">{step.num}</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-2">{step.title}</h2>
              <p className="text-sm text-slate-600 leading-relaxed">{step.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Stores Grid */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-3xl p-8 text-white text-center space-y-6">
        <h2 className="text-2xl font-black">Supported Retail Stores in India</h2>
        <p className="text-sm text-slate-300 max-w-2xl mx-auto">
          Price Ping supports full-featured real-time price comparison and tracking across the 5 premier e-commerce destinations:
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-bold">
          <span className="px-4 py-2 rounded-full bg-amber-400/10 border border-amber-400/30 text-amber-300">Amazon India</span>
          <span className="px-4 py-2 rounded-full bg-blue-400/10 border border-blue-400/30 text-blue-300">Flipkart</span>
          <span className="px-4 py-2 rounded-full bg-rose-400/10 border border-rose-400/30 text-rose-300">Myntra</span>
          <span className="px-4 py-2 rounded-full bg-teal-400/10 border border-teal-400/30 text-teal-300">AJIO</span>
          <span className="px-4 py-2 rounded-full bg-pink-400/10 border border-pink-400/30 text-pink-300">Nykaa</span>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center py-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-indigo-600 text-white text-sm font-bold shadow-lg shadow-indigo-600/30 hover:bg-indigo-700 transition-all hover:scale-105"
        >
          <span>Try Price Ping Now</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
