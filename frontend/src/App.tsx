import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import Landing from "@/pages/Landing";
import Auth from "@/pages/Auth";
import Dashboard from "@/pages/Dashboard";
import { ProtectedRoute } from "@/features/routing/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. Public Landing Page */}
        <Route path="/" element={<Landing />} />
        <Route path="/landing" element={<Landing />} />

        {/* 2. Authentication Portal */}
        <Route path="/auth" element={<Auth />} />
        <Route path="/login" element={<Auth />} />

        {/* 3. Existing Old PERCEPTA C2 Dashboard (Protected by Operator Clearance) */}
        <Route
          path="/dashboard/*"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Fallback to Landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
