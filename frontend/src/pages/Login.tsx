import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back to PricePing! 👋');
      navigate('/dashboard');
    } catch (err: any) {
      if (err.response?.status === 401) {
        toast.error(err.response?.data?.detail || 'Invalid email or password');
      } else if (!err.response || err.response?.status >= 500) {
        toast.error(`Server connection issue (${err.response?.status || 'Network'}). Retrying...`);
      } else {
        toast.error(err.response?.data?.detail || 'Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-4 sm:p-6 relative overflow-hidden">
      {/* Background ambient accents */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md animate-fade-in relative z-10">
        {/* Brand Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <div className="w-12 h-12 bg-gradient-brand rounded-2xl flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-900 tracking-tight">Sign in to PricePing</h1>
          <p className="text-gray-500 mt-1 text-sm">Monitor e-commerce price drops & get instant alerts</p>
        </div>

        <div className="card p-7 sm:p-9 shadow-card-elevated border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email Address</label>
              <input
                type="email"
                className="input font-medium"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="label !mb-0">Password</label>
              </div>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  className="input pr-12 font-medium"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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
              className="btn-primary w-full py-3.5 text-sm font-extrabold shadow-md mt-2"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-500 mt-6 text-sm">
          Don't have an account yet?{' '}
          <Link to="/register" className="text-indigo-600 hover:text-indigo-800 font-bold hover:underline">
            Create an account for free
          </Link>
        </p>
      </div>
    </div>
  );
}
