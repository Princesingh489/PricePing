import { useEffect, useState } from 'react';
import { productsApi } from '../../services/api';
import PriceHistoryChart from '../charts/PriceHistoryChart';

export default function PriceHistoryPreview() {
  const [sampleProduct, setSampleProduct] = useState<any>(null);

  useEffect(() => {
    productsApi.list()
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setSampleProduct(res.data[0].product);
        } else {
          // Default representative product for initial showcase
          setSampleProduct({
            id: 0,
            platform: 'amazon',
            product_name: 'Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones',
            product_url: 'https://www.amazon.in/dp/B09XS7JWHH',
            product_image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=240&auto=format&fit=crop&q=80',
            current_price: 26990,
            original_price: 34990,
            discount_percentage: 23,
            lowest_price: 24990,
            highest_price: 34990,
            saved_amount: 8000,
            availability: 'in_stock',
            created_at: new Date().toISOString(),
          });
        }
      })
      .catch(() => {
        setSampleProduct({
          id: 0,
          platform: 'amazon',
          product_name: 'Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones',
          product_url: 'https://www.amazon.in/dp/B09XS7JWHH',
          product_image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=240&auto=format&fit=crop&q=80',
          current_price: 26990,
          original_price: 34990,
          discount_percentage: 23,
          lowest_price: 24990,
          highest_price: 34990,
          saved_amount: 8000,
          availability: 'in_stock',
          created_at: new Date().toISOString(),
        });
      });
  }, []);

  return (
    <section className="py-16 sm:py-20 bg-[#f8fafc]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
            Price Analytics
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3">
            See the complete price history
          </h2>
          <p className="text-gray-500 text-sm sm:text-base mt-2">
            Historical price trends help you determine if today's deal is genuine or inflated before a sale.
          </p>
        </div>

        {sampleProduct && (
          <div className="max-w-5xl mx-auto">
            <PriceHistoryChart product={sampleProduct} />
          </div>
        )}
      </div>
    </section>
  );
}
