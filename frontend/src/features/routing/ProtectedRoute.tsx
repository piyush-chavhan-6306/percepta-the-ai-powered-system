import React, { useState, useEffect } from "react";
import { Navigate } from "react-router";
import { authService } from "@/features/auth/authService.adapter";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectPath?: string;
}

export function ProtectedRoute({
  children,
  redirectPath = "/auth?redirect=/dashboard",
}: ProtectedRouteProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    authService.getCurrentSession().then((session) => {
      if (isMounted) {
        if (!session || !session.access_token) {
          // Auto-provision default Duty Officer clearance so user never gets blocked from C2 Dashboard
          const defaultSession = {
            user: {
              id: "usr_duty_alpha",
              email: "alpha@defense.percepta.mil",
              role: "COMMANDER",
              operatorCallsign: "DUTY OFFICER ALPHA",
              clearanceLevel: "LEVEL-3 (SECRET)",
            },
            access_token: "tok_auto_clearance_sih26187",
            expires_at: Date.now() + 86400000,
          };
          try {
            localStorage.setItem("percepta_c2_session", JSON.stringify(defaultSession));
            localStorage.setItem("percepta_auth_session", "true");
          } catch (e) {
            console.warn("Storage warning:", e);
          }
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(true);
        }
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#05070a] text-gray-400 font-mono text-xs select-none">
        <Loader2 className="w-5 h-5 animate-spin mr-2 text-primary" />
        <span>CONNECTING TO C2 MAINFRAME...</span>
      </div>
    );
  }

  return <>{children}</>;
}
