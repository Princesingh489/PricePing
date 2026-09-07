import { useState } from 'react';
import { useTheme, THEME_PRESETS } from '../contexts/ThemeContext';
import type { HeroTheme } from '../contexts/ThemeContext';
import { X, Palette, Sparkles, Image as ImageIcon, Sliders, Check, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function ThemeCustomizerModal({ isOpen, onClose }: Props) {
  const { settings, setHeroTheme, setCustomImageUrl, setBannerBrightness, setShowOrnaments, resetTheme } = useTheme();
  const [customUrlInput, setCustomUrlInput] = useState(settings.customImageUrl || '');

  if (!isOpen) return null;

  const handleApplyCustomUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUrlInput.trim()) {
      toast.error('Please enter an image URL');
      return;
    }
    setCustomImageUrl(customUrlInput.trim());
    toast.success('Custom background applied!');
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-[#121624] border border-white/15 rounded-3xl max-w-3xl w-full p-6 lg:p-8 relative shadow-2xl shadow-purple-500/20 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white flex items-center justify-center transition-all z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-purple-500/30">
            <Palette className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-white flex items-center gap-2">
              Background Theme & Wallpaper
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Customizer
              </span>
            </h2>
            <p className="text-sm text-gray-400">Personalize the Price Ping hero backdrop and festive ambiance</p>
          </div>
        </div>

        {/* Theme Presets Grid */}
        <div className="space-y-4 mb-6">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            Select Backdrop Theme
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {(Object.keys(THEME_PRESETS) as HeroTheme[]).map((themeKey) => {
              const preset = THEME_PRESETS[themeKey];
              const isSelected = settings.heroTheme === themeKey;

              return (
                <button
                  key={themeKey}
                  type="button"
                  onClick={() => {
                    setHeroTheme(themeKey);
                    toast.success(`Switched to ${preset.name}`);
                  }}
                  className={`p-4 rounded-2xl border text-left transition-all relative overflow-hidden group ${
                    isSelected
                      ? 'border-purple-400 ring-2 ring-purple-500/50 bg-white/[0.08] shadow-lg shadow-purple-500/20'
                      : 'border-white/10 hover:border-white/20 bg-white/[0.03] hover:bg-white/[0.06]'
                  }`}
                >
                  <div
                    className="h-16 rounded-xl mb-3 flex items-center justify-center relative overflow-hidden border border-white/10"
                    style={{ background: preset.gradient }}
                  >
                    {preset.bannerUrl && (
                      <img
                        src={preset.bannerUrl}
                        alt=""
                        className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-300"
                      />
                    )}
                    <span className="relative z-10 text-xs font-extrabold text-white px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm border border-white/20">
                      {preset.badge}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="font-bold text-sm text-white group-hover:text-purple-300 transition-colors">
                      {preset.name}
                    </div>
                    {isSelected && (
                      <div className="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center text-white">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{preset.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Image URL Input */}
        <div className="p-4 rounded-2xl bg-white/[0.04] border border-white/10 mb-6">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2 mb-2">
            <ImageIcon className="w-4 h-4 text-cyan-400" />
            Use Custom Background Image URL
          </label>
          <form onSubmit={handleApplyCustomUrl} className="flex gap-2">
            <input
              type="url"
              placeholder="https://images.unsplash.com/photo-..."
              value={customUrlInput}
              onChange={(e) => setCustomUrlInput(e.target.value)}
              className="flex-1 bg-black/40 border border-white/15 rounded-xl px-3.5 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
            <button type="submit" className="btn-primary text-xs px-4 py-2">
              Apply
            </button>
          </form>
        </div>

        {/* Controls: Brightness & Ornaments */}
        <div className="p-4 rounded-2xl bg-white/[0.04] border border-white/10 space-y-4 mb-6">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-pink-400" />
            Visual Fine-Tuning
          </label>

          <div className="flex items-center justify-between gap-4">
            <span className="text-sm text-gray-300">Banner Brightness ({settings.bannerBrightness}%)</span>
            <input
              type="range"
              min="40"
              max="100"
              value={settings.bannerBrightness}
              onChange={(e) => setBannerBrightness(Number(e.target.value))}
              className="w-48 accent-purple-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-300">Show Festive Golden Sparkles & Badges</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.showOrnaments}
                onChange={(e) => setShowOrnaments(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => {
              resetTheme();
              setCustomUrlInput('');
              toast.success('Reset to default festive theme');
            }}
            className="flex items-center gap-2 text-xs text-gray-400 hover:text-white transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset to Default
          </button>

          <button onClick={onClose} className="btn-primary">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
