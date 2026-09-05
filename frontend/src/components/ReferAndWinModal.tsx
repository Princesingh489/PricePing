import { useState } from 'react';
import { X, Gift, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function ReferAndWinModal({ isOpen, onClose }: Props) {
  const [copied, setCopied] = useState(false);
  const referralLink = 'https://priceping.in/join?ref=PRINCE_VIP_SAVER';

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    toast.success('Referral link copied to clipboard!');
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-[#121626] border border-white/15 rounded-3xl max-w-lg w-full p-6 sm:p-8 relative shadow-2xl shadow-emerald-500/20">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white flex items-center justify-center transition-all z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/30 mx-auto mb-4">
            <Gift className="w-8 h-8" />
          </div>
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-black uppercase tracking-wider">
            Refer & Win ₹500 Cashback
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-white mt-2">
            Invite Friends, Earn Rewards
          </h2>
          <p className="text-xs sm:text-sm text-gray-400 mt-1 max-w-sm mx-auto">
            Give your friends 1-minute price drop tracking. Earn ₹100 Amazon Pay balance for every friend who tracks 3 products!
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-3 mb-6">
          <div className="p-3.5 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center gap-3.5">
            <div className="w-8 h-8 rounded-xl bg-purple-500/20 text-purple-300 flex items-center justify-center font-black text-xs">
              1
            </div>
            <div className="text-xs text-gray-300">
              <strong className="text-white">Share your unique invite link</strong> via WhatsApp, Telegram, or Twitter
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center gap-3.5">
            <div className="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-300 flex items-center justify-center font-black text-xs">
              2
            </div>
            <div className="text-xs text-gray-300">
              <strong className="text-white">Friend signs up & tracks 1 product</strong> on Amazon/Flipkart
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3.5">
            <div className="w-8 h-8 rounded-xl bg-emerald-500 text-white flex items-center justify-center font-black text-xs">
              🎉
            </div>
            <div className="text-xs text-emerald-300">
              <strong className="text-white">Both of you get ₹100 instantly</strong> in Gift Voucher wallet!
            </div>
          </div>
        </div>

        {/* Share Link Box */}
        <div className="p-3 rounded-2xl bg-black/50 border border-white/15 flex items-center justify-between gap-2 mb-6">
          <div className="text-xs font-mono text-gray-300 truncate pl-2">
            {referralLink}
          </div>
          <button
            onClick={handleCopy}
            className="btn-primary text-xs py-2 px-4 flex-shrink-0"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-300" /> Copied!
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" /> Copy Link
              </>
            )}
          </button>
        </div>

        <button
          onClick={onClose}
          className="btn-secondary w-full py-2.5 text-xs font-bold cursor-pointer"
        >
          Close
        </button>
      </div>
    </div>
  );
}
