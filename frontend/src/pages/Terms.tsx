import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';

export default function Terms() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      <SEOHead
        title="Terms and Conditions – Price Ping"
        description="Review the terms of service and conditions for using Price Ping's price comparison and tracking tools."
        canonical="https://priceping.store/terms"
      />

      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Terms &amp; Conditions</span>
      </nav>

      <div className="space-y-2">
        <h1 className="text-3xl font-black text-slate-900">Terms and Conditions</h1>
        <p className="text-xs text-slate-500">Last updated: September 2026</p>
      </div>

      <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6 text-sm text-slate-700 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Nature of the Service</h2>
          <p>
            Price Ping operates as an independent price comparison and tracking aggregation tool for online shoppers in India. Price Ping is not an e-commerce store, retailer, or vendor. When you click an external link to Amazon, Flipkart, Myntra, Ajio, or Nykaa, you are redirected to the respective store website to complete your transaction.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Price Accuracy and Store Policies</h2>
          <p>
            Online prices, shipping charges, delivery times, and inventory levels are controlled exclusively by the respective retail merchants and change dynamically. While Price Ping utilizes advanced automated observation engines to reflect current pricing, final charges and terms are governed by the merchant platform at the time of purchase.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Intellectual Property</h2>
          <p>
            All brand names, trademarks, product images, and service marks mentioned on Price Ping belong to their respective copyright holders. Reference to third-party stores does not imply endorsement or direct affiliation.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. User Accounts and Fair Usage</h2>
          <p>
            Users agree not to exploit automated bots, scrapers, or denial-of-service attacks against Price Ping services. We reserve the right to suspend accounts that abuse notification systems or violate system integrity.
          </p>
        </section>
      </div>
    </div>
  );
}
