import { Activity, LineChart, Bell, Scale, TrendingDown, ShieldCheck } from 'lucide-react';

const FEATURES = [
  {
    icon: Activity,
    title: 'Track Prices',
    description: 'Monitor product prices automatically with scheduled background scrapers checking every drop.',
    gradient: 'from-indigo-500 to-indigo-700',
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
  },
  {
    icon: LineChart,
    title: 'Price History',
    description: 'See historical price movements, average retail trends, and best buying windows over time.',
    gradient: 'from-cyan-500 to-blue-600',
    color: 'text-cyan-600',
    bg: 'bg-cyan-50',
  },
  {
    icon: Bell,
    title: 'Smart Alerts',
    description: 'Get notified instantly via Email, Push, and SMS when your product reaches your exact target price.',
    gradient: 'from-amber-500 to-orange-600',
    color: 'text-amber-600',
    bg: 'bg-amber-50',
  },
  {
    icon: Scale,
    title: 'Compare Stores',
    description: 'Compare live product prices across Amazon, Flipkart, AJIO, Myntra & Nykaa in one place.',
    gradient: 'from-purple-500 to-fuchsia-600',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
  {
    icon: TrendingDown,
    title: 'Lowest Price',
    description: 'Identify the lowest recorded price ever so you never overpay or buy at artificial surge prices.',
    gradient: 'from-emerald-500 to-teal-600',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
  },
  {
    icon: ShieldCheck,
    title: 'Genuine Price Detection',
    description: 'Avoid misleading bank offers, fake discounts, and coupons to see the true verified product price.',
    gradient: 'from-rose-500 to-pink-600',
    color: 'text-rose-600',
    bg: 'bg-rose-50',
  },
];

export default function WhyPricePing() {
  return (
    <section className="py-16 sm:py-20 bg-[#f8fafc]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
            Why Choose PricePing
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3">
            Smarter shopping, real savings
          </h2>
          <p className="text-gray-500 text-sm sm:text-base mt-2">
            Powerful price tracking algorithms designed specifically for Indian e-commerce shoppers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((feat) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.title}
                className="card p-6 sm:p-7 hover:border-indigo-300 hover:shadow-card-hover transition-all duration-300 flex flex-col justify-between group"
              >
                <div>
                  <div className={`w-12 h-12 rounded-2xl ${feat.bg} ${feat.color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-xs`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-black text-navy-900 mb-2 tracking-tight group-hover:text-indigo-600 transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-gray-500 text-xs sm:text-sm leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
