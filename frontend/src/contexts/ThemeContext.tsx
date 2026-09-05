import React, { createContext, useContext, useState, useEffect } from 'react';

export type HeroTheme = 'festive' | 'cyber' | 'crimson' | 'emerald' | 'cosmic' | 'custom';

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

export const THEME_PRESETS: Record<HeroTheme, {
  name: string;
  description: string;
  badge: string;
  bannerUrl: string;
  gradient: string;
  accent: string;
}> = {
  festive: {
    name: 'Festive Royal Gold & Plum',
    description: 'Traditional Indian festive celebration with golden mandalas, diya lamps, and rich burgundy plum tones (Price Ping festive style)',
    badge: '🎆 Festive Theme',
    bannerUrl: '/hero-festive.jpg',
    gradient: 'linear-gradient(135deg, #4a044e 0%, #701a75 40%, #831843 70%, #3b0764 100%)',
    accent: '#f59e0b',
  },
  cyber: {
    name: 'Midnight Cyber Sapphire',
    description: 'Futuristic dark indigo mesh grid with neon cyan & sapphire floating credit card holograms',
    badge: '🌌 Cyber Dark',
    bannerUrl: '/hero-cyber.jpg',
    gradient: 'linear-gradient(135deg, #0b0f19 0%, #1e1b4b 40%, #0369a1 70%, #0f172a 100%)',
    accent: '#06b6d4',
  },
  crimson: {
    name: 'Imperial Velvet Crimson',
    description: 'Deep ruby crimson velvet backdrop with golden glitter and warm ambient glows',
    badge: '🌺 Velvet Crimson',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #881337 0%, #9f1239 40%, #be123c 70%, #4c0519 100%)',
    accent: '#fbbf24',
  },
  emerald: {
    name: 'Royal Emerald & Gold',
    description: 'Lush dark emerald jewel tones with sparkling champagne gold accents',
    badge: '🌿 Emerald Luxury',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #064e3b 0%, #065f46 40%, #047857 70%, #022c22 100%)',
    accent: '#34d399',
  },
  cosmic: {
    name: 'Deep Cosmic Violet',
    description: 'Rich galaxy purple with stardust particles and modern glassmorphic glow',
    badge: '🔮 Cosmic Violet',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #2e1065 0%, #3b0764 40%, #581c87 70%, #1e1b4b 100%)',
    accent: '#c084fc',
  },
  custom: {
    name: 'Custom Image / Wallpaper',
    description: 'Provide any custom background image URL or high-res wallpaper',
    badge: '🎨 Custom Wallpaper',
    bannerUrl: '',
    gradient: 'linear-gradient(135deg, #18181b 0%, #27272a 100%)',
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
