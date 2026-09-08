import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import MyProducts from './pages/MyProducts';
import AddProduct from './pages/AddProduct';
import Alerts from './pages/Alerts';
import Notifications from './pages/Notifications';
import ComparePrices from './pages/ComparePrices';
import PriceHistoryPage from './pages/PriceHistoryPage';
import Settings from './pages/Settings';
import AdminPanel from './pages/AdminPanel';
import ProductDetailPage from './pages/ProductDetailPage';
import GoogleCallback from './pages/GoogleCallback';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500 font-bold">Loading PricePing...</p>
        </div>
      </div>
    );
  }
  return user ? <>{children}</> : <Navigate to="/login" replace />;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  return user?.is_admin ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/auth/google/callback" element={<GoogleCallback />} />

      {/* Main Home / Landing Route */}
      <Route
        path="/"
        element={
          <Layout>
            <Home />
          </Layout>
        }
      />

      {/* Consumer Dashboard Route */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Compare Prices Route */}
      <Route
        path="/compare"
        element={
          <Layout>
            <ComparePrices />
          </Layout>
        }
      />

      {/* Price History Analytics Route */}
      <Route
        path="/history"
        element={
          <Layout>
            <PriceHistoryPage />
          </Layout>
        }
      />

      {/* My Tracked Products */}
      <Route
        path="/products"
        element={
          <ProtectedRoute>
            <Layout>
              <MyProducts />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Add Product Tracking */}
      <Route
        path="/add-product"
        element={
          <ProtectedRoute>
            <Layout>
              <AddProduct />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Price Alerts */}
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <Layout>
              <Alerts />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Notifications */}
      <Route
        path="/notifications"
        element={
          <ProtectedRoute>
            <Layout>
              <Notifications />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Account Settings */}
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout>
              <Settings />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Admin Panel */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminRoute>
              <Layout>
                <AdminPanel />
              </Layout>
            </AdminRoute>
          </ProtectedRoute>
        }
      />

      {/* Product Detail Page */}
      <Route
        path="/product/:trackerId"
        element={
          <ProtectedRoute>
            <Layout>
              <ProductDetailPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ThemeProvider>
          <LanguageProvider>
            <AppRoutes />
            <Toaster
              position="top-right"
              toastOptions={{
                style: {
                  background: '#0f172a',
                  color: '#ffffff',
                  borderRadius: '16px',
                  fontSize: '13px',
                  fontWeight: 600,
                  padding: '12px 16px',
                },
                success: { iconTheme: { primary: '#10b981', secondary: '#0f172a' } },
                error: { iconTheme: { primary: '#ef4444', secondary: '#0f172a' } },
              }}
            />
          </LanguageProvider>
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
