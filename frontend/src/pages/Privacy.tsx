import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';

export default function Privacy() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      <SEOHead
        title="Privacy Policy – Price Ping"
        description="Learn how Price Ping protects your personal information, price alert settings, and privacy."
        canonical="https://priceping.store/privacy"
      />

      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Privacy Policy</span>
      </nav>

      <div className="space-y-2">
        <h1 className="text-3xl font-black text-slate-900">Privacy Policy</h1>
        <p className="text-xs text-slate-500">Last updated: September 2026</p>
      </div>

      <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6 text-sm text-slate-700 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Information We Collect</h2>
          <p>
            Price Ping collects minimal information required to deliver your price alert preferences and user experience. This includes your email address, optional contact details, and the product links you choose to track. We do not collect credit card details or financial payment information.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. How Information is Used</h2>
          <p>
            Your information is solely used to deliver price drop notifications, service communications, and secure account access. We never sell, rent, or trade your personal email address or tracked preferences to third-party advertisers.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Data Security</h2>
          <p>
            All network communication is encrypted using industry-standard Transport Layer Security (TLS/HTTPS). User passwords are cryptographically hashed using salted Bcrypt before storage.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. Third-Party Links</h2>
          <p>
            Price Ping contains outbound links to third-party stores including Amazon, Flipkart, Myntra, Ajio, and Nykaa. When navigating to these external websites, their independent privacy terms and cookie practices apply.
          </p>
        </section>
      </div>
    </div>
  );
}
