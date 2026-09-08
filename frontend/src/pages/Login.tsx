import React, { useState, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import toast from "react-hot-toast";
import { Eye, EyeOff, Loader2, ShieldCheck, TrendingDown, Bell } from "lucide-react";

function isValidEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
      <path fill="none" d="M0 0h48v48H0z"/>
    </svg>
  );
}

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [emailTouched, setEmailTouched] = useState(false);
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const emailRef = useRef<HTMLInputElement>(null);
  const from = (location.state as any)?.from?.pathname || "/dashboard";

  const emailError =
    emailTouched && email.length > 0 && !isValidEmail(email)
      ? "Please enter a valid email address."
      : "";

  function mapError(err: any): string {
    const status = err?.response?.status;
    const detail: string = err?.response?.data?.detail || "";
    if (status === 401) return "Incorrect email or password.";
    if (status === 429) return "Too many login attempts. Please try again later.";
    if (status === 400 && detail.toLowerCase().includes("inactive"))
      return "Your account is inactive. Please contact support.";
    if (!err.response || status >= 500)
      return "Unable to sign in right now. Please try again.";
    return "Unable to sign in. Please check your details and try again.";
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidEmail(email)) {
      setEmailTouched(true);
      emailRef.current?.focus();
      return;
    }
    setLoading(true);
    setErrorMsg("");
    try {
      await login(email, password);
      toast.success("Welcome back to Price Ping! 👋");
      navigate(from, { replace: true });
    } catch (err: any) {
      const msg = mapError(err);
      setErrorMsg(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const googleClientId = (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID;
    if (!googleClientId) {
      toast("Google Sign-In is not configured yet. Please use email & password.", {
        icon: "ℹ️",
        duration: 4000,
      });
      return;
    }
    const redirectUri = `${window.location.origin}/auth/google/callback`;
    const params = new URLSearchParams({
      client_id: googleClientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      access_type: "offline",
      prompt: "select_account",
    });
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  };


  return (
    <div
      className="min-h-screen bg-[#F8F9FC] flex items-center justify-center px-4 py-10 sm:py-12 relative overflow-hidden"
      style={{
        background: [
          'radial-gradient(ellipse 72% 58% at 50% 46%, rgba(124,58,237,0.08) 0%, rgba(124,58,237,0.04) 42%, transparent 68%)',
          'radial-gradient(ellipse 38% 34% at 92% 7%, rgba(99,102,241,0.055) 0%, transparent 58%)',
          'radial-gradient(ellipse 34% 28% at 7% 93%, rgba(139,92,246,0.045) 0%, transparent 58%)',
          '#F8F9FC',
        ].join(', '),
      }}
    >
      {/* Primary centered purple glow — animates very slowly */}
      <div
        aria-hidden="true"
        className="login-glow-primary absolute left-1/2 top-[44%] -translate-x-1/2 -translate-y-1/2 w-[640px] h-[480px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at center, rgba(124,58,237,0.11) 0%, rgba(124,58,237,0.05) 35%, transparent 70%)',
          filter: 'blur(72px)',
        }}
      />
      {/* Top-right secondary lavender glow */}
      <div
        aria-hidden="true"
        className="absolute -top-16 -right-16 w-80 h-80 rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle at 60% 40%, rgba(99,102,241,0.07) 0%, transparent 65%)',
          filter: 'blur(96px)',
        }}
      />
      {/* Bottom-left tertiary blob */}
      <div
        aria-hidden="true"
        className="absolute -bottom-10 -left-10 w-72 h-72 rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle at 40% 60%, rgba(139,92,246,0.06) 0%, transparent 65%)',
          filter: 'blur(96px)',
        }}
      />
      {/* Keyframe styles injected inline — no extra lib needed */}
      <style>{`
        .login-glow-primary { animation: glow-drift 14s ease-in-out infinite alternate; }
        @keyframes glow-drift {
          0%   { transform: translate(-50%, -50%) scale(1);    opacity: 1; }
          50%  { transform: translate(-50%, -52%) scale(1.06); opacity: 0.85; }
          100% { transform: translate(-50%, -50%) scale(1);    opacity: 1; }
        }
        @media (prefers-reduced-motion: reduce) {
          .login-glow-primary { animation: none !important; }
        }
      `}</style>

      <div className="w-full max-w-[420px] relative z-10">

        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex flex-col items-center gap-3 mb-2 group" aria-label="Price Ping home">
            <div className="w-14 h-14 bg-gradient-brand rounded-[20px] flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 group-hover:shadow-indigo-500/50 transition-shadow">
              <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
          </Link>
          <h1 className="text-[26px] sm:text-[28px] font-black text-navy-900 tracking-tight leading-tight mt-3">
            Sign in to Price Ping
          </h1>
          <p className="text-gray-500 mt-1.5 text-[13px] font-medium">
            Monitor e-commerce price drops &amp; get instant alerts
          </p>
        </div>

        {/* Auth Card */}
        <div
          className="bg-white rounded-[20px] p-6 sm:p-7"
          style={{
            border: '1px solid rgba(0,0,0,0.06)',
            boxShadow: '0 4px 24px rgba(0,0,0,0.06), 0 1px 6px rgba(0,0,0,0.04)',
          }}
        >

          {/* Google Sign-In */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 text-sm font-bold text-gray-700 transition-all shadow-sm hover:shadow-md cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label="Continue with Google"
          >
            <GoogleIcon />
            Continue with Google
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-gray-100" />
            <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest whitespace-nowrap">
              or continue with email
            </span>
            <div className="flex-1 h-px bg-gray-100" />
          </div>

          {/* Error Banner */}
          {errorMsg && (
            <div
              role="alert"
              className="flex items-start gap-2.5 p-3.5 mb-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-700 font-semibold"
            >
              <ShieldCheck className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-500" />
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
            {/* Email */}
            <div>
              <label htmlFor="login-email" className="label">
                Email Address
              </label>
              <input
                id="login-email"
                ref={emailRef}
                type="email"
                autoComplete="email"
                autoFocus
                required
                value={email}
                onChange={(e) => { setEmail(e.target.value); setErrorMsg(""); }}
                onBlur={() => setEmailTouched(true)}
                placeholder="you@example.com"
                className={`input font-medium transition-all ${emailError ? "border-rose-400 ring-2 ring-rose-200 focus:border-rose-500" : ""}`}
                aria-describedby={emailError ? "email-error" : undefined}
                aria-invalid={!!emailError}
              />
              {emailError && (
                <p id="email-error" role="alert" className="text-rose-600 text-[11px] font-semibold mt-1.5 ml-0.5">
                  {emailError}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="login-password" className="label !mb-0">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-[12px] font-semibold text-indigo-600 hover:text-indigo-800 hover:underline transition-colors"
                  tabIndex={0}
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPass ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrorMsg(""); }}
                  placeholder="Enter your password"
                  className="input pr-12 font-medium"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  aria-label={showPass ? "Hide password" : "Show password"}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-navy-900 transition-colors p-1 rounded-lg hover:bg-gray-100 cursor-pointer"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Sign In */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3.5 text-sm font-extrabold shadow-md shadow-indigo-500/25 hover:shadow-lg hover:shadow-indigo-500/30 mt-2 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 transition-all"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
            </button>
          </form>


        </div>

        <p className="text-center text-gray-500 mt-5 text-sm">
          Don&apos;t have an account yet?{" "}
          <Link
            to="/register"
            className="text-indigo-600 hover:text-indigo-800 font-bold hover:underline transition-colors"
          >
            Create an account for free
          </Link>
        </p>

        {/* Trust row */}
        <div className="flex items-center justify-center gap-4 mt-4 text-gray-400 flex-wrap">
          <div className="flex items-center gap-1 text-[10px] font-medium">
            <ShieldCheck className="w-3 h-3 text-emerald-500" />
            Secure &amp; Encrypted
          </div>
          <div className="w-px h-2.5 bg-gray-200 hidden sm:block" />
          <div className="flex items-center gap-1 text-[10px] font-medium">
            <Bell className="w-3 h-3 text-indigo-400" />
            Instant Alerts
          </div>
          <div className="w-px h-2.5 bg-gray-200 hidden sm:block" />
          <div className="flex items-center gap-1 text-[10px] font-medium">
            <TrendingDown className="w-3 h-3 text-purple-400" />
            Price Tracking
          </div>
        </div>
      </div>
    </div>
  );
}
