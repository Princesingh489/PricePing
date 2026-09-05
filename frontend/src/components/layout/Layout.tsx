import React from 'react';
import AnnouncementBar from './AnnouncementBar';
import Header from './Header';
import Footer from './Footer';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f8fafc] text-navy-900 flex flex-col antialiased selection:bg-indigo-500/25 selection:text-indigo-900">
      {/* 1. Top Announcement Bar */}
      <AnnouncementBar />

      {/* 2. Main Navigation Header */}
      <Header />

      {/* 3. Main Page Content */}
      <main className="flex-1 w-full animate-fade-in">
        {children}
      </main>

      {/* 4. Rich Footer */}
      <Footer />
    </div>
  );
}
