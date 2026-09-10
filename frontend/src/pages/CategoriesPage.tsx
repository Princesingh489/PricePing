import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { Smartphone, Laptop, Tv, Watch, Headphones, Shirt, Sparkles, ArrowRight } from 'lucide-react';

export const CATEGORIES_DATA = [
  {
    slug: 'mobiles',
    name: 'Mobiles & Smartphones',
    icon: <Smartphone className="w-6 h-6 text-indigo-600" />,
    description: 'Compare prices on Apple iPhone, Samsung Galaxy, OnePlus, Xiaomi, and Google Pixel.',
    popularItems: ['Apple iPhone 15', 'Samsung Galaxy S24', 'OnePlus 12', 'Redmi Note 13'],
  },
  {
    slug: 'laptops',
    name: 'Laptops & Computers',
    icon: <Laptop className="w-6 h-6 text-indigo-600" />,
    description: 'Track price drops on MacBooks, gaming laptops, ultrabooks from HP, Dell, Lenovo, and ASUS.',
    popularItems: ['Apple MacBook Air M3', 'Dell XPS 13', 'HP Pavilion', 'ASUS TUF Gaming'],
  },
  {
    slug: 'electronics',
    name: 'Consumer Electronics',
    icon: <Tv className="w-6 h-6 text-indigo-600" />,
    description: 'Smart TVs, tablets, home appliances, and smart devices across major online retailers.',
    popularItems: ['Sony Bravia 4K TV', 'Apple iPad 10th Gen', 'Samsung 55-inch QLED'],
  },
  {
    slug: 'wearables',
    name: 'Smartwatches & Wearables',
    icon: <Watch className="w-6 h-6 text-indigo-600" />,
    description: 'Smart fitness bands, luxury watches, and calling smartwatches from Fire-Boltt, Noise, boAt, and Apple.',
    popularItems: ['Fire-Boltt Ninja Call Pro Plus', 'Noise ColorFit Pulse', 'Apple Watch Series 9'],
  },
  {
    slug: 'audio',
    name: 'Headphones & Audio',
    icon: <Headphones className="w-6 h-6 text-indigo-600" />,
    description: 'Noise-cancelling headphones, wireless Bluetooth earbuds, and speakers from Sony, JBL, and boAt.',
    popularItems: ['Sony WH-1000XM5', 'boAt Airdopes 141', 'JBL Flip 6', 'AirPods Pro'],
  },
  {
    slug: 'fashion',
    name: 'Fashion & Apparel',
    icon: <Shirt className="w-6 h-6 text-indigo-600" />,
    description: 'Casual wear, jeans, sneakers, and ethnic fashion across Myntra, Ajio, Amazon, and Flipkart.',
    popularItems: ['Levi’s 511 Slim Jeans', 'Red Tape Clogs', 'Puma Smash Sneakers', 'Nike Air Max'],
  },
  {
    slug: 'beauty',
    name: 'Beauty & Personal Care',
    icon: <Sparkles className="w-6 h-6 text-indigo-600" />,
    description: 'Skincare, makeup, hair care, and fragrances verified on Nykaa and major beauty portals.',
    popularItems: ['Maybelline Superstay Lipstick', 'L’Oreal Paris Serum', 'Nykaa Cosmetics'],
  },
];

export default function CategoriesPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      <SEOHead
        title="Product Categories – Compare Prices by Category on Price Ping"
        description="Browse all product categories on Price Ping. Compare prices and track price drops across Mobiles, Laptops, Electronics, Wearables, Audio, Fashion, and Beauty."
        canonical="https://priceping.store/categories"
        keywords="Price Ping categories, compare mobile prices, compare laptop prices, online shopping categories India"
      />

      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Categories</span>
      </nav>

      <div className="space-y-3 text-center max-w-3xl mx-auto">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          Browse Price Comparisons by Category
        </h1>
        <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
          Select a category to compare verified offers, monitor price history, and spot active discounts across Amazon, Flipkart, Myntra, Ajio, and Nykaa.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CATEGORIES_DATA.map((cat) => (
          <Link
            key={cat.slug}
            to={`/category/${cat.slug}`}
            className="group bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center group-hover:scale-110 transition-transform">
                {cat.icon}
              </div>
              <h2 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                {cat.name}
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                {cat.description}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-indigo-600">
              <span>View Deals &amp; Products</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
