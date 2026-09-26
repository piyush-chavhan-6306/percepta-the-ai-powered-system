import React, { useState, useEffect } from "react";
import { Route, Routes, Navigate } from "react-router";
import LandingPage from "../landing/LandingPage";
import AuthPage from "../auth/AuthPage";
import { authService } from "../auth/authService.adapter";
import { Loader2 } from "lucide-react";

/**
 * Standard Canonical Route Constants
 */
export const PERCEPTA_ROUTES = {
  LANDING: "/",
  AUTH: "/auth",
  DASHBOARD: "/dashboard",
} as const;

/**
 * Operator Clearance Guard (Protected Route)
 * Enforces authenticated operator clearance before allowing access to the Command Dashboard.
 */
export function ProtectedRoute({
  children,
  redirectPath = "/auth?redirect=/dashboard",
}: {
  children: React.ReactNode;
  redirectPath?: string;
}) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    authService.getCurrentSession().then((session) => {
      if (mounted) {
        setIsAuthenticated(Boolean(session && session.access_token));
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#05070a] text-gray-400 font-mono text-xs select-none">
        <Loader2 className="w-5 h-5 animate-spin mr-2 text-[#00e5ff]" />
        VERIFYING OPERATOR CLEARANCE...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
}

/**
 * Complete Plug-and-Play Router Example
 * Pass your existing OLD PERCEPTA Dashboard component as a child to connect the entire flow!
 * 
 * Example usage in your App.tsx:
 * ```tsx
 * import { PerceptaRouter } from "./PERCEPTA_MIGRATION/routing/routes";
 * import OldDashboard from "./components/OldDashboard";
 * 
 * export default function App() {
 *   return (
 *     <PerceptaRouter>
 *       <OldDashboard />
 *     </PerceptaRouter>
 *   );
 * }
 * ```
 */
export function PerceptaRouter({
  children,
}: {
  children?: React.ReactNode;
}) {
  return (
    <Routes>
      {/* 1. Public Landing Page */}
      <Route path={PERCEPTA_ROUTES.LANDING} element={<LandingPage />} />

      {/* 2. Authentication Portal */}
      <Route path={PERCEPTA_ROUTES.AUTH} element={<AuthPage />} />

      {/* 3. Existing Old PERCEPTA Command Dashboard (Clearance Guarded) */}
      <Route
        path={`${PERCEPTA_ROUTES.DASHBOARD}/*`}
        element={
          <ProtectedRoute>
            {children || (
              <div className="flex flex-col items-center justify-center min-h-screen bg-[#050709] text-gray-300 font-mono p-8 text-center">
                <span className="text-xl font-bold text-[#9ee7df] mb-2">OPERATOR CLEARANCE VERIFIED</span>
                <p className="text-sm text-gray-400 max-w-md">
                  Mount your existing OLD PERCEPTA Dashboard component here inside <code>&lt;PerceptaRouter&gt;</code>.
                </p>
              </div>
            )}
          </ProtectedRoute>
        }
      />

      {/* Fallback to Landing */}
      <Route path="*" element={<Navigate to={PERCEPTA_ROUTES.LANDING} replace />} />
    </Routes>
  );
}

export default PerceptaRouter;
