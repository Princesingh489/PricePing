import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { Eye, EyeOff, Bell, ShieldCheck, TrendingDown } from 'lucide-react';
import { authApi } from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ name: '', email: '', password: '', phone_number: '' });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setLoading(true);
    try {
      await authApi.register(form);
      await login(form.email, form.password);
      toast.success('Welcome to PricePing! 🎉');
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex">
      {/* Left Feature Column */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-hero flex-col justify-center p-16 relative overflow-hidden text-white">
        <div className="relative z-10 max-w-lg">
          <div className="flex items-center gap-2.5 mb-10">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20 shadow-md">
              <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
            <span className="text-2xl font-black text-white tracking-tight">Price<span className="text-indigo-300">Ping</span></span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-black text-white leading-tight mb-5 tracking-tight">
            Never pay <br /><span className="text-amber-300 underline decoration-amber-400">full price</span> online again.
          </h1>

          <p className="text-indigo-100 text-base mb-10 leading-relaxed font-normal">
            Automated 24/7 price tracking on Amazon, Flipkart, AJIO, Myntra & Nykaa. Get instant drops directly via Email & Push.
          </p>

          <div className="space-y-4">
            {[
              { icon: Bell, text: 'Instant price drop alerts via Email & SMS' },
              { icon: TrendingDown, text: 'Track historical price trends with interactive charts' },
              { icon: ShieldCheck, text: 'Genuine price detection with zero spam alerts' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3.5">
                <div className="w-9 h-9 bg-white/15 backdrop-blur-md rounded-xl flex items-center justify-center flex-shrink-0 border border-white/15">
                  <Icon className="w-4.5 h-4.5 text-white" />
                </div>
                <span className="text-white font-semibold text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Form Column */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 relative">
        <div className="w-full max-w-md animate-fade-in">
          <div className="lg:hidden flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-gradient-brand rounded-xl flex items-center justify-center text-white shadow-md">
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
            <span className="font-black text-navy-900 text-2xl">PricePing</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-navy-900 mb-1.5 tracking-tight">Create Free Account</h2>
          <p className="text-gray-500 mb-8 text-sm">Join smart shoppers and track prices across top Indian stores</p>

          <div className="card p-7 sm:p-8 shadow-card-elevated border-gray-200">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Full Name</label>
                <input
                  className="input font-medium"
                  placeholder="Priya Sharma"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Email Address</label>
                <input
                  type="email"
                  className="input font-medium"
                  placeholder="priya@example.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="label">Phone Number (optional for SMS)</label>
                <input
                  className="input font-medium"
                  placeholder="+91 98765 43210"
                  value={form.phone_number}
                  onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
                />
              </div>

              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    className="input pr-12 font-medium"
                    placeholder="Min. 8 characters"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-navy-900 transition-colors"
                  >
                    {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-3.5 text-sm font-extrabold shadow-md mt-4"
              >
                {loading ? 'Creating Account...' : 'Create Free Account'}
              </button>
            </form>
          </div>

          <p className="text-center text-gray-500 mt-6 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-600 hover:text-indigo-800 font-bold hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
