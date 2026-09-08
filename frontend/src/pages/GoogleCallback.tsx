import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export default function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const [status, setStatus] = useState<'loading' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const hasHandledRef = useRef(false);

  useEffect(() => {
    // Avoid double execution in React StrictMode
    if (hasHandledRef.current) return;
    hasHandledRef.current = true;

    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      const desc = searchParams.get('error_description') || 'Google authentication was cancelled or denied.';
      setStatus('error');
      setErrorMessage(desc);
      toast.error(desc);
      return;
    }

    if (!code) {
      const msg = 'No authorization code received from Google.';
      setStatus('error');
      setErrorMessage(msg);
      toast.error(msg);
      return;
    }

    const redirectUri = `${window.location.origin}/auth/google/callback`;

    loginWithGoogle(code, redirectUri)
      .then(() => {
        toast.success('Signed in with Google successfully! 👋');
        navigate('/', { replace: true });
      })
      .catch((err: any) => {
        const detail =
          err?.response?.data?.detail ||
          'Failed to sign in with Google. The authorization code may have expired.';
        setStatus('error');
        setErrorMessage(detail);
        toast.error(detail);
      });
  }, [searchParams, loginWithGoogle, navigate]);

  return (
    <div
      className="min-h-screen bg-[#F8F9FC] flex items-center justify-center px-4 py-12 relative overflow-hidden"
      style={{
        background: [
          'radial-gradient(ellipse 72% 58% at 50% 46%, rgba(124,58,237,0.08) 0%, rgba(124,58,237,0.04) 42%, transparent 68%)',
          'radial-gradient(ellipse 38% 34% at 92% 7%, rgba(99,102,241,0.055) 0%, transparent 58%)',
          '#F8F9FC',
        ].join(', '),
      }}
    >
      <div className="w-full max-w-md relative z-10 text-center">
        {/* Brand Header */}
        <Link to="/" className="inline-flex flex-col items-center gap-3 mb-6 group" aria-label="Price Ping home">
          <div className="w-16 h-16 bg-gradient-brand rounded-[22px] flex items-center justify-center text-white shadow-xl shadow-indigo-500/30 group-hover:shadow-indigo-500/50 transition-shadow">
            <svg
              className="w-8 h-8"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M12 2v20" />
              <path d="m17 5-5-3-5 3" />
              <path d="M4.5 9h15" />
              <path d="M6 16.5a6 6 0 0 0 12 0" />
            </svg>
          </div>
          <span className="font-black text-navy-900 text-2xl tracking-tight">
            Price<span className="text-indigo-600">Ping</span>
          </span>
        </Link>

        {/* Card */}
        <div
          className="bg-white rounded-[24px] p-8 sm:p-10 text-center"
          style={{
            border: '1px solid rgba(0,0,0,0.06)',
            boxShadow: '0 8px 30px rgba(0,0,0,0.06), 0 1px 6px rgba(0,0,0,0.04)',
          }}
        >
          {status === 'loading' ? (
            <div className="flex flex-col items-center justify-center py-4">
              <div className="relative mb-5">
                <div className="w-16 h-16 rounded-full border-4 border-indigo-100 border-t-indigo-600 animate-spin flex items-center justify-center" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg width="22" height="22" viewBox="0 0 48 48" aria-hidden="true">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                  </svg>
                </div>
              </div>
              <h2 className="text-xl font-black text-navy-900 mb-2">Authenticating with Google</h2>
              <p className="text-sm text-gray-500 max-w-xs leading-relaxed">
                Verifying your credentials and preparing your PricePing dashboard...
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-2">
              <div className="w-14 h-14 rounded-2xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-500 mb-4">
                <AlertCircle className="w-7 h-7" />
              </div>
              <h2 className="text-xl font-black text-navy-900 mb-2">Authentication Failed</h2>
              <p className="text-sm text-gray-500 mb-6 leading-relaxed">
                {errorMessage || 'Unable to authenticate with Google. Please try again.'}
              </p>
              <div className="flex flex-col sm:flex-row items-center gap-3 w-full">
                <Link
                  to="/login"
                  className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold shadow-md shadow-indigo-500/20 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Sign In
                </Link>
                <Link
                  to="/register"
                  className="w-full flex items-center justify-center px-5 py-3 rounded-xl border border-gray-200 hover:bg-gray-50 text-gray-700 text-sm font-semibold transition-colors"
                >
                  Create Account
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
