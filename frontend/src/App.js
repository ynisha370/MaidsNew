import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";

// Components
import Header from "./components/Header";
import Login from "./components/Login";
import Register from "./components/Register";
import AdminLogin from "./components/AdminLogin";
import AdminDashboard from "./components/AdminDashboard";
import CustomerDashboard from "./components/CustomerDashboard";
import CleanerLogin from "./components/CleanerLogin";
import CleanerSignup from "./components/CleanerSignup";
import CleanerDashboard from "./components/CleanerDashboard";
import BookingFlow from "./components/BookingFlow";
import BookingConfirmation from "./components/BookingConfirmation";
import RescheduleAppointment from "./components/RescheduleAppointment";
import EditCleaningSelection from "./components/EditCleaningSelection";
import PaymentInformation from "./components/PaymentInformation";
import StripePaymentInformation from "./components/StripePaymentInformation";
import PaymentPage from "./components/PaymentPage";
import Notes from "./components/Notes";
import PaymentHistory from "./components/PaymentHistory";
import UpcomingAppointments from "./components/UpcomingAppointments";
import CustomerSubscriptions from "./components/CustomerSubscriptions";
import GoogleCallback from "./components/GoogleCallback";
import { Toaster } from "./components/ui/sonner";

// Auth Context
import { AuthProvider, useAuth } from "./contexts/AuthContext";

const ProtectedRoute = ({ children, adminOnly = false, cleanerOnly = false }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/admin/login" />;
  }

  if (cleanerOnly && user.role !== 'cleaner') {
    return <Navigate to="/cleaner/login" />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { user } = useAuth();
  if (user && user.role === 'admin') {
    return <Navigate to="/admin" />;
  }
  if (user && user.role === 'customer') {
    return <Navigate to="/" />;
  }
  if (user && user.role === 'cleaner') {
    return <Navigate to="/cleaner" />;
  }
  return children;
};

const AdminPublicRoute = ({ children }) => {
  const { user } = useAuth();
  if (user && user.role === 'admin') {
    return <Navigate to="/admin" />;
  }
  // Allow access to admin login even if customer is logged in
  return children;
};

const CleanerPublicRoute = ({ children }) => {
  const { user } = useAuth();
  if (user && user.role === 'cleaner') {
    return <Navigate to="/cleaner" />;
  }
  // Allow access to cleaner login even if customer is logged in
  return children;
};

function AppContent() {
  const { user } = useAuth();

  return (
    <div className="App">
      {user?.role !== 'admin' && <Header />}
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />
        <Route path="/guest-booking" element={<BookingFlow isGuest={true} />} />
        <Route path="/auth/google/callback" element={<GoogleCallback />} />
        
        {/* Admin Routes */}
        <Route path="/admin/login" element={
          <AdminPublicRoute>
            <AdminLogin />
          </AdminPublicRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute adminOnly={true}>
            <AdminDashboard />
          </ProtectedRoute>
        } />

        {/* Cleaner Routes */}
        <Route path="/cleaner/login" element={
          <CleanerPublicRoute>
            <CleanerLogin />
          </CleanerPublicRoute>
        } />
        <Route path="/cleaner/signup" element={
          <CleanerPublicRoute>
            <CleanerSignup />
          </CleanerPublicRoute>
        } />
        <Route path="/cleaner" element={
          <ProtectedRoute cleanerOnly={true}>
            <CleanerDashboard />
          </ProtectedRoute>
        } />
        
        {/* Customer Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <CustomerDashboard />
          </ProtectedRoute>
        } />
        <Route path="/book" element={
          <ProtectedRoute>
            <BookingFlow />
          </ProtectedRoute>
        } />
        <Route path="/reschedule" element={
          <ProtectedRoute>
            <RescheduleAppointment />
          </ProtectedRoute>
        } />
        <Route path="/edit-cleaning" element={
          <ProtectedRoute>
            <EditCleaningSelection />
          </ProtectedRoute>
        } />
        <Route path="/payment" element={
          <ProtectedRoute>
            <StripePaymentInformation />
          </ProtectedRoute>
        } />
        <Route path="/payment/:bookingId" element={
          <ProtectedRoute>
            <PaymentPage />
          </ProtectedRoute>
        } />
        <Route path="/notes" element={
          <ProtectedRoute>
            <Notes />
          </ProtectedRoute>
        } />
        <Route path="/payment-history" element={
          <ProtectedRoute>
            <PaymentHistory />
          </ProtectedRoute>
        } />
        <Route path="/upcoming" element={
          <ProtectedRoute>
            <UpcomingAppointments />
          </ProtectedRoute>
        } />
        <Route path="/subscriptions" element={
          <ProtectedRoute>
            <CustomerSubscriptions />
          </ProtectedRoute>
        } />
        <Route path="/confirmation/:bookingId" element={
          <ProtectedRoute>
            <BookingConfirmation />
          </ProtectedRoute>
        } />
      </Routes>
      <Toaster />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;