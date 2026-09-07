import React, { createContext, useContext, useState, useEffect } from 'react';

export type HeroTheme =
  | 'festive'
  | 'cyber'
  | 'crimson'
  | 'emerald'
  | 'cosmic'
  | 'neon_tokyo'
  | 'nordic_aurora'
  | 'sunset_miami'
  | 'obsidian_gold'
  | 'solar_flare'
  | 'custom';

export interface ThemeSettings {
  heroTheme: HeroTheme;
  customImageUrl?: string;
  bannerBrightness: number; // 50 to 100
  showOrnaments: boolean;
  accentColor: string;
}

interface ThemeContextType {
  settings: ThemeSettings;
  setHeroTheme: (theme: HeroTheme) => void;
  setCustomImageUrl: (url: string) => void;
  setBannerBrightness: (val: number) => void;
  setShowOrnaments: (show: boolean) => void;
  setAccentColor: (color: string) => void;
  resetTheme: () => void;
}

const defaultSettings: ThemeSettings = {
  heroTheme: 'festive',
  customImageUrl: '',
  bannerBrightness: 85,
  showOrnaments: true,
  accentColor: '#6366f1',
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export interface ThemePresetDetails {
  name: string;
  description: string;
  badge: string;
  bannerUrl: string;
  gradient: string;
  overlayGradient: string;
  bgBase: string;
  accent: string;
}

export const THEME_PRESETS: Record<HeroTheme, ThemePresetDetails> = {
  festive: {
    name: 'Festive Royal Gold & Plum',
    description: 'Traditional Indian festive celebration with golden mandalas, diya lamps, and rich burgundy plum tones',
    badge: '🎆 Festive Theme',
    bannerUrl: '/hero-festive.jpg',
    gradient: 'linear-gradient(135deg, #4a044e 0%, #701a75 40%, #831843 70%, #3b0764 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(59,7,100,0.5) 50%, rgba(36,0,29,0.95) 100%)',
    bgBase: '#24001d',
    accent: '#f59e0b',
  },
  cyber: {
    name: 'Midnight Cyber Sapphire',
    description: 'Futuristic dark indigo mesh grid with neon cyan & sapphire floating holograms',
    badge: '🌌 Cyber Dark',
    bannerUrl: '/hero-cyber.jpg',
    gradient: 'linear-gradient(135deg, #0b0f19 0%, #1e1b4b 40%, #0369a1 70%, #0f172a 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(15,23,42,0.6) 50%, rgba(11,15,25,0.95) 100%)',
    bgBase: '#0b0f19',
    accent: '#06b6d4',
  },
  crimson: {
    name: 'Imperial Velvet Crimson',
    description: 'Deep ruby crimson velvet backdrop with golden glitter and warm ambient glows',
    badge: '🌺 Velvet Crimson',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #881337 0%, #9f1239 40%, #be123c 70%, #4c0519 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(136,19,55,0.55) 50%, rgba(76,5,25,0.95) 100%)',
    bgBase: '#4c0519',
    accent: '#fbbf24',
  },
  emerald: {
    name: 'Royal Emerald & Gold',
    description: 'Lush dark emerald jewel tones with sparkling champagne gold accents',
    badge: '🌿 Emerald Luxury',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #064e3b 0%, #065f46 40%, #047857 70%, #022c22 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(6,78,59,0.55) 50%, rgba(2,44,34,0.95) 100%)',
    bgBase: '#022c22',
    accent: '#34d399',
  },
  cosmic: {
    name: 'Deep Cosmic Violet',
    description: 'Rich galaxy purple with stardust particles and modern glassmorphic glow',
    badge: '🔮 Cosmic Violet',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #2e1065 0%, #3b0764 40%, #581c87 70%, #1e1b4b 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(46,16,101,0.55) 50%, rgba(30,27,75,0.95) 100%)',
    bgBase: '#1e1b4b',
    accent: '#c084fc',
  },
  neon_tokyo: {
    name: 'Neon Tokyo Night',
    description: 'Electric neon violet, cyberpunk cyan lasers, and vibrant Japanese metropolis night aura',
    badge: '⚡ Neon Tokyo',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #09090b 0%, #3b0764 35%, #0891b2 75%, #0284c7 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(9,9,11,0.3) 0%, rgba(59,7,100,0.5) 50%, rgba(9,9,11,0.96) 100%)',
    bgBase: '#09090b',
    accent: '#22d3ee',
  },
  nordic_aurora: {
    name: 'Nordic Aurora Borealis',
    description: 'Polar night sky illuminated by dancing northern lights in luminous arctic teal & emerald',
    badge: '🌌 Nordic Aurora',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #022c22 0%, #064e3b 30%, #0369a1 65%, #0f172a 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(2,44,34,0.3) 0%, rgba(6,78,59,0.5) 50%, rgba(15,23,42,0.95) 100%)',
    bgBase: '#0f172a',
    accent: '#10b981',
  },
  sunset_miami: {
    name: 'Miami Sunset Vaporwave',
    description: 'Vibrant tropical sunset with warm coral pink, golden apricot and deep ocean magenta',
    badge: '🌅 Miami Sunset',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #831843 0%, #be185d 30%, #ea580c 70%, #7c2d12 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(131,24,67,0.5) 50%, rgba(67,20,7,0.95) 100%)',
    bgBase: '#431407',
    accent: '#f97316',
  },
  obsidian_gold: {
    name: 'Obsidian Stealth & 24K Gold',
    description: 'Ultra-exclusive matte obsidian black with radiant champagne 24K gold metallic shimmer',
    badge: '👑 Obsidian Gold',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #000000 0%, #18181b 40%, #713f12 75%, #422006 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(24,24,27,0.6) 50%, rgba(0,0,0,0.97) 100%)',
    bgBase: '#09090b',
    accent: '#eab308',
  },
  solar_flare: {
    name: 'Solar Flare & Sunset Amber',
    description: 'Radiant solar plasma energy with deep blazing amber, molten tangerine, and warm embers',
    badge: '🔥 Solar Flare',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #451a03 0%, #7c2d12 35%, #c2410c 70%, #9a3412 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(124,45,18,0.55) 50%, rgba(69,26,3,0.95) 100%)',
    bgBase: '#451a03',
    accent: '#fb923c',
  },
  custom: {
    name: 'Custom Image / Wallpaper',
    description: 'Provide any custom background image URL or high-res wallpaper',
    badge: '🎨 Custom Wallpaper',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #18181b 0%, #27272a 100%)',
    overlayGradient: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(24,24,27,0.6) 50%, rgba(15,19,34,0.95) 100%)',
    bgBase: '#121626',
    accent: '#6366f1',
  },
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<ThemeSettings>(() => {
    try {
      const saved = localStorage.getItem('priceping_theme_settings');
      return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    } catch {
      return defaultSettings;
    }
  });

  useEffect(() => {
    localStorage.setItem('priceping_theme_settings', JSON.stringify(settings));
  }, [settings]);

  const setHeroTheme = (theme: HeroTheme) => {
    setSettings((prev) => ({ ...prev, heroTheme: theme }));
  };

  const setCustomImageUrl = (url: string) => {
    setSettings((prev) => ({ ...prev, customImageUrl: url, heroTheme: 'custom' }));
  };

  const setBannerBrightness = (val: number) => {
    setSettings((prev) => ({ ...prev, bannerBrightness: val }));
  };

  const setShowOrnaments = (show: boolean) => {
    setSettings((prev) => ({ ...prev, showOrnaments: show }));
  };

  const setAccentColor = (color: string) => {
    setSettings((prev) => ({ ...prev, accentColor: color }));
  };

  const resetTheme = () => {
    setSettings(defaultSettings);
  };

  return (
    <ThemeContext.Provider
      value={{
        settings,
        setHeroTheme,
        setCustomImageUrl,
        setBannerBrightness,
        setShowOrnaments,
        setAccentColor,
        resetTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
