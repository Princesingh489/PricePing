import { useState } from 'react';
import { useTheme, THEME_PRESETS } from '../contexts/ThemeContext';
import { useLanguage } from '../contexts/LanguageContext';
import toast from 'react-hot-toast';
import {
  Search, Sparkles, Mic, X
} from 'lucide-react';
import QuickTrackModal from './QuickTrackModal';

interface Props {
  onProductTracked?: () => void;
}

export default function HeroTrackerSection({ onProductTracked }: Props) {
  const { settings } = useTheme();
  const currentPreset = THEME_PRESETS[settings.heroTheme] || THEME_PRESETS.cyber;
  const bannerImage = settings.customImageUrl || currentPreset.bannerUrl;
  const { t } = useLanguage();
  const [urlInput, setUrlInput] = useState('');
  const [modalSearchedUrl, setModalSearchedUrl] = useState<string>('');
  const [activeModalProduct, setActiveModalProduct] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const executeTrack = (queryToTrack: string) => {
    const raw = queryToTrack.trim();
    if (!raw) return;

    let cleanQuery = raw;
    if (!cleanQuery.startsWith('http://') && !cleanQuery.startsWith('https://')) {
      if (cleanQuery.includes('amazon.') || cleanQuery.includes('amzn.') || cleanQuery.includes('flipkart.') || cleanQuery.includes('myntra.') || cleanQuery.includes('ajio.') || cleanQuery.includes('nykaa.')) {
        cleanQuery = 'https://' + cleanQuery;
      }
    }

    // Instant modal opening (BuyHatke-style 0ms feedback)
    setActiveModalProduct(null);
    setModalSearchedUrl(cleanQuery);
    setModalOpen(true);
  };

  const handleSearchOrTrack = (e: React.FormEvent) => {
    e.preventDefault();
    const query = urlInput.trim();
    if (!query) {
      toast.error('Please paste a product URL or search term');
      return;
    }
    executeTrack(query);
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pasted = e.clipboardData.getData('text').trim();
    if (pasted && (
      pasted.includes('amazon.') || pasted.includes('amzn.') ||
      pasted.includes('flipkart.') || pasted.includes('fkrt.it') ||
      pasted.includes('myntra.') ||
      pasted.includes('ajio.') ||
      pasted.includes('nykaa.')
    )) {
      setUrlInput(pasted);
      executeTrack(pasted);
    }
  };

  return (
    <>
      <section
        className="relative w-full overflow-hidden text-white transition-all duration-500"
        style={{ backgroundColor: currentPreset.bgBase || '#121626' }}
      >
        {/* Rich Wallpaper Image or Theme Gradient Layer */}
        <div
          className="absolute inset-0 bg-cover bg-center transition-all duration-500"
          style={
            bannerImage
              ? {
                  backgroundImage: `url("${bannerImage}")`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  filter: `brightness(${settings.bannerBrightness}%)`,
                }
              : {
                  background: currentPreset.gradient,
                  filter: `brightness(${settings.bannerBrightness}%)`,
                }
          }
        />

        {/* Ambient Overlay dynamically matched to active theme preset */}
        <div
          className="absolute inset-0 pointer-events-none transition-all duration-500"
          style={{
            background: currentPreset.overlayGradient || 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(15,23,42,0.5) 50%, rgba(10,13,24,0.95) 100%)',
          }}
        />

        {/* Hero Content Container */}
        <div className="relative z-10 px-4 py-12 sm:py-16 lg:py-20 max-w-5xl mx-auto text-center flex flex-col items-center">
          {/* Top Pill Badge */}
          <div className="inline-flex items-center gap-1.5 px-4 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-amber-300 text-xs font-semibold shadow-sm mb-5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            <span>Price History & Tracker</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-[54px] font-black text-white tracking-tight leading-[1.15] max-w-4xl drop-shadow-md">
            {t('hero_title', 'Never Overpay. Let PricePing Find the Right Price.')}
          </h1>

          {/* Subtitle */}
          <p className="mt-3 text-base sm:text-lg text-gray-200 font-normal drop-shadow">
            {t('hero_subtitle', 'Compare prices, watch price history, and get alerted when it’s finally worth buying.')}
          </p>

          {/* Main Search & URL Tracker Input Bar */}
          <form
            onSubmit={handleSearchOrTrack}
            className="w-full max-w-3xl mt-7 relative"
          >
            <div className="relative flex items-center bg-white rounded-full p-1 sm:p-2 shadow-2xl shadow-black/70 border border-white/40 focus-within:ring-4 focus-within:ring-indigo-500/30 transition-all">
              {/* Search Icon */}
              <div className="pl-3 sm:pl-4 text-gray-400 flex-shrink-0">
                <Search className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>

              {/* Input Field */}
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                onPaste={handlePaste}
                placeholder={t('hero_placeholder', 'Search or paste any Amazon, Flipkart, Myntra, AJIO, Nykaa link...')}
                className="w-full min-w-0 flex-1 bg-transparent px-2.5 sm:px-3 py-2 sm:py-3 text-xs sm:text-sm md:text-[15px] text-gray-900 placeholder-gray-400 font-medium focus:outline-none"
              />

              {/* Clear button if text */}
              {urlInput && (
                <button
                  type="button"
                  onClick={() => setUrlInput('')}
                  className="p-1 rounded-full text-gray-400 hover:text-gray-600 mr-1 flex-shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              )}

              {/* Voice / Mic Icon */}
              <button
                type="button"
                onClick={() => toast('Voice search: Say a product name...')}
                className="p-1.5 sm:p-2 rounded-full text-gray-400 hover:text-indigo-600 transition-colors mr-0.5 sm:mr-1 flex-shrink-0"
                title="Voice Search"
              >
                <Mic className="w-4 h-4" />
              </button>

              {/* Submit CTA Button */}
              <button
                type="submit"
                className="px-3.5 sm:px-6 py-2 sm:py-3 rounded-full bg-[#4139d4] hover:bg-[#342cb8] text-white font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center gap-1.5 sm:gap-2 flex-shrink-0 cursor-pointer whitespace-nowrap"
              >
                <span>{t('find_best_price', 'Find Best Price')}</span>
              </button>
            </div>
          </form>

          {/* Supported Platforms Pill */}
          <div className="mt-4 px-3 sm:px-4 py-1.5 rounded-full bg-black/40 backdrop-blur-md border border-white/15 text-[11px] sm:text-xs text-gray-200 font-medium flex items-center justify-center gap-1.5 flex-wrap shadow-sm text-center">
            <span>•</span>
            <span>Works with <strong className="text-amber-300">Amazon, Flipkart, AJIO, Myntra &amp; Nykaa</strong></span>
          </div>

        </div>
      </section>

      {/* Quick Track Modal */}
      <QuickTrackModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setModalSearchedUrl('');
          setActiveModalProduct(null);
        }}
        initialProduct={activeModalProduct}
        searchedUrl={modalSearchedUrl}
        onSuccessTrack={onProductTracked}
      />
    </>
  );
}
