import React, { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../services/api";
import { Mail, ArrowLeft, Loader2, CheckCircle2, ShieldCheck } from "lucide-react";

function isValidEmail(v: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [emailTouched, setEmailTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const emailError =
    emailTouched && email.length > 0 && !isValidEmail(email)
      ? "Please enter a valid email address."
      : "";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailTouched(true);
    if (!isValidEmail(email)) return;

    setLoading(true);
    try {
      await authApi.forgotPassword(email.trim().toLowerCase());
      setSent(true);
    } catch {
      // Always show success — never reveal whether the email exists
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/40 to-purple-50/30 flex items-center justify-center p-4 sm:p-6 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/8 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-[420px] relative z-10">

        {/* Back link */}
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-500 hover:text-indigo-600 transition-colors mb-6 group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Back to Sign In
        </Link>

        {/* Brand */}
        <div className="text-center mb-8">
          <Link to="/" aria-label="Price Ping home" className="inline-flex flex-col items-center gap-3 group">
            <div className="w-14 h-14 bg-gradient-brand rounded-[20px] flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 group-hover:shadow-indigo-500/50 transition-shadow">
              <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 2v20" />
                <path d="m17 5-5-3-5 3" />
                <path d="M4.5 9h15" />
                <path d="M6 16.5a6 6 0 0 0 12 0" />
              </svg>
            </div>
          </Link>
          <h1 className="text-[24px] font-black text-navy-900 tracking-tight mt-4">
            {sent ? "Check your inbox" : "Reset your password"}
          </h1>
          <p className="text-gray-400 mt-1.5 text-[13px] font-medium">
            {sent
              ? "We sent a reset link to your email. It expires in 30 minutes."
              : "Enter your email and we will send you a reset link."}
          </p>
        </div>

        <div className="bg-white rounded-3xl border border-gray-200/80 shadow-xl shadow-gray-900/8 p-7 sm:p-8">
          {sent ? (
            /* ── Success state ── */
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto border border-emerald-100">
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              </div>
              <p className="text-sm text-gray-600 font-medium leading-relaxed">
                If <strong className="text-navy-900">{email}</strong> is registered with Price Ping,
                you will receive a password reset link shortly.
              </p>
              <p className="text-xs text-gray-400">
                Didn&apos;t get an email? Check your spam folder, or{" "}
                <button
                  type="button"
                  onClick={() => { setSent(false); }}
                  className="text-indigo-600 font-bold hover:underline cursor-pointer"
                >
                  try again
                </button>
                .
              </p>
              <div className="pt-2">
                <Link to="/login" className="btn-primary w-full block text-center py-3 text-sm font-extrabold">
                  Return to Sign In
                </Link>
              </div>
              <div className="flex items-center justify-center gap-1.5 text-[11px] font-semibold text-gray-400 mt-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                Reset links expire after 30 minutes
              </div>
            </div>
          ) : (
            /* ── Email form ── */
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <div>
                <label htmlFor="forgot-email" className="label">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    id="forgot-email"
                    type="email"
                    autoComplete="email"
                    autoFocus
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onBlur={() => setEmailTouched(true)}
                    placeholder="you@example.com"
                    className={`input pl-10 font-medium transition-all ${emailError ? "border-rose-400 ring-2 ring-rose-200" : ""}`}
                    aria-describedby={emailError ? "forgot-email-error" : undefined}
                    aria-invalid={!!emailError}
                  />
                </div>
                {emailError && (
                  <p id="forgot-email-error" role="alert" className="text-rose-600 text-[11px] font-semibold mt-1.5 ml-0.5">
                    {emailError}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-3.5 text-sm font-extrabold shadow-md shadow-indigo-500/25 hover:shadow-indigo-500/40 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Sending reset link...
                  </span>
                ) : (
                  "Send Reset Link"
                )}
              </button>

              <p className="text-center text-[11px] text-gray-400 font-medium pt-1">
                For security, we never reveal whether an email is registered.
              </p>
            </form>
          )}
        </div>

        <p className="text-center text-gray-500 mt-6 text-sm">
          Remembered your password?{" "}
          <Link to="/login" className="text-indigo-600 hover:text-indigo-800 font-bold hover:underline transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
