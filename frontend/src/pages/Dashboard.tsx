import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Shield,
  Plus,
  Video,
  Moon,
  Flame,
  ChevronLeft,
  RefreshCw,
  Radio,
  Eye,
  EyeOff,
  Trash2,
  User,
} from "lucide-react";
import { CameraFeed } from "@/components/CameraFeed";
import { AlertPanel } from "@/components/AlertPanel";
import { AlertInspector } from "@/components/AlertInspector";
import { AIAssistantBar } from "@/components/AIAssistantBar";
import { PremiumCard } from "@/components/PremiumCard";
import { AddCameraModal } from "@/components/AddCameraModal";
import { ThreatGauge } from "@/components/ThreatGauge";
import { PremiumBackground } from "@/components/PremiumBackground";
import { StatusBar } from "@/components/StatusBar";
import { api } from "@/api/client";
import type { AlertItem, CameraRecord } from "@/types/surveillance";

export default function Dashboard() {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState<CameraRecord[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>("CAM-01");
  const [threatData, setThreatData] = useState<{ score: number; level: string }>({
    score: 0,
    level: "NORMAL",
  });
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [selectedAlertTime, setSelectedAlertTime] = useState<string | number | null>(null);
  const [showAddCamera, setShowAddCamera] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showGrid, setShowGrid] = useState(true);

  const fetchCameras = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.getCameras();
      if (res.cameras && res.cameras.length > 0) {
        setCameras(res.cameras);
        if (!res.cameras.some((c) => c.camera_id === selectedCameraId)) {
          setSelectedCameraId(res.cameras[0].camera_id);
        }
      } else {
        setCameras([
          {
            camera_id: "CAM-01",
            name: "Border Post Alpha",
            source_type: "video_file",
            modality: "STANDARD",
            is_running: true,
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch cameras:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedCameraId]);

  const fetchThreatLevel = useCallback(async () => {
    try {
      const res = await api.getThreatLevel(selectedCameraId);
      const rawLevel = String((res as any).threat_level || (res as any).level || "NORMAL").toUpperCase();
      let normLevel = "NORMAL";
      if (rawLevel === "DEFCON_RED" || rawLevel === "CRITICAL" || rawLevel === "RED") normLevel = "CRITICAL";
      else if (rawLevel === "DEFCON_ORANGE" || rawLevel === "HIGH" || rawLevel === "ORANGE") normLevel = "HIGH";
      else if (rawLevel === "DEFCON_YELLOW" || rawLevel === "ELEVATED" || rawLevel === "MODERATE" || rawLevel === "YELLOW") normLevel = "ELEVATED";
      else normLevel = "NORMAL";

      setThreatData({
        score: (res as any).threat_score ?? (res as any).score ?? 0,
        level: normLevel,
      });
    } catch (err) {
      console.error("Failed to fetch threat level:", err);
    }
  }, [selectedCameraId]);

  useEffect(() => {
    fetchCameras();
    fetchThreatLevel();
    const interval = setInterval(fetchThreatLevel, 10000);
    return () => clearInterval(interval);
  }, [fetchCameras, fetchThreatLevel]);

  const activeCamera = cameras.find((c) => c.camera_id === selectedCameraId) || cameras[0];

  const handleDeleteCamera = async (cameraId: string) => {
    try {
      await api.deleteCamera(cameraId);
      const updated = cameras.filter((c) => c.camera_id !== cameraId);
      setCameras(updated);
      if (selectedCameraId === cameraId && updated.length > 0) {
        setSelectedCameraId(updated[0].camera_id);
      }
    } catch (err) {
      console.error("Failed to remove camera:", err);
    }
  };

  const handleToggleRun = async () => {
    if (!activeCamera) return;
    try {
      if (activeCamera.is_running) {
        await api.stopCamera(activeCamera.camera_id);
      } else {
        await api.startCamera(activeCamera.camera_id);
      }
      await fetchCameras();
    } catch (err) {
      console.error("Failed to toggle camera analysis:", err);
    }
  };

  const handleSeekTime = (timestamp: string | number, cameraId?: string) => {
    if (cameraId && cameraId !== selectedCameraId) {
      setSelectedCameraId(cameraId);
    }
    setSelectedAlertTime(timestamp);
  };

  const handleExitSeek = () => setSelectedAlertTime(null);

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId);
      if (selectedAlert?.event_id === alertId || selectedAlert?.alert_id === alertId) {
        setSelectedAlert((prev) => (prev ? { ...prev, is_acknowledged: true } : null));
      }
    } catch (err) {
      console.error("Failed to acknowledge alert:", err);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/30 relative overflow-hidden">
      {/* Animated background */}
      {showGrid && <PremiumBackground />}

      {/* ═══ HEADER — Premium Glass ═══ */}
      <header className="sticky top-0 z-40 relative">
        {/* Gradient accent line at top */}
        <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-primary/60 to-transparent" />

        <div className="glass-panel border-b border-white/[0.06] px-5 py-3">
          <div className="max-w-[1920px] mx-auto flex items-center justify-between">
            {/* Left: Navigation + Brand */}
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/")}
                className="text-muted-foreground hover:text-foreground font-mono text-xs flex items-center gap-1 -ml-2 h-8"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>PORTAL</span>
              </Button>

              <div className="h-5 w-px bg-white/10" />

              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                    <Shield className="w-4.5 h-4.5 text-primary" />
                  </div>
                  {/* Pulsing ring around shield */}
                  <motion.div
                    className="absolute inset-[-3px] rounded-xl border border-primary/30"
                    animate={{ opacity: [0.3, 0.6, 0.3], scale: [1, 1.02, 1] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-sm font-bold tracking-wider font-mono text-foreground uppercase">
                      PERCEPTA DEFENSE C2
                    </h1>
                    <Badge variant="secondary" className="text-[9px] px-1.5 py-0 font-mono border-white/5">
                      SIH26187
                    </Badge>
                  </div>
                  <p className="text-[10px] font-mono text-muted-foreground/60">
                    Autonomous AI Border Surveillance Command
                  </p>
                </div>
              </div>
            </div>

            {/* Center: Threat Gauge */}
            <ThreatGauge score={threatData.score} level={threatData.level} />

            {/* Right: Actions */}
            <div className="flex items-center gap-2.5">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowGrid(!showGrid)}
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                title={showGrid ? "Hide background" : "Show background"}
              >
                {showGrid ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </Button>

              <div className="h-5 w-px bg-white/10" />

              <Button
                size="sm"
                onClick={() => setShowAddCamera(true)}
                className="h-9 bg-primary hover:bg-primary/90 text-primary-foreground font-mono text-xs flex items-center gap-1.5 shadow-lg shadow-primary/20 border-0"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>ADD CAMERA</span>
              </Button>

              <Button
                variant="outline"
                size="icon"
                onClick={() => {
                  fetchCameras();
                  fetchThreatLevel();
                }}
                className="h-8 w-8 text-muted-foreground hover:text-foreground border-white/10"
                title="Refresh"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              </Button>

              <div className="h-5 w-px bg-white/10 hidden sm:block" />

              {/* Active Operator Clearance */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/auth?redirect=/dashboard")}
                className="text-xs font-mono flex items-center gap-1.5 text-muted-foreground hover:text-primary h-8 px-2.5 bg-white/[0.03] border border-white/5"
                title="Active Operator Session (Click to switch / re-authenticate)"
              >
                <User className="w-3.5 h-3.5 text-primary" />
                <span className="hidden md:inline text-[11px]">OFFICER ALPHA</span>
                <Badge variant="outline" className="text-[8px] px-1 py-0 border-primary/40 text-primary font-mono ml-0.5">
                  DEFCON-2
                </Badge>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* ═══ MAIN WORKSPACE ═══ */}
      <main className="flex-1 p-4 grid grid-cols-1 xl:grid-cols-12 gap-4 max-w-[1920px] mx-auto w-full relative z-10">
        {/* LEFT: Camera + AI (8 cols) */}
        <div className="xl:col-span-8 flex flex-col gap-4">
          {/* Camera Selector Bar */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none px-1">
            {cameras.map((cam, idx) => {
              const isSelected = cam.camera_id === selectedCameraId;
              const mod = (cam.modality || "STANDARD").toUpperCase();
              return (
                <div key={cam.camera_id} className="relative flex items-center">
                  <PremiumCard
                    tilt={6}
                    lift={isSelected ? 1.04 : 1.01}
                    glare={isSelected}
                    glowColor="rgba(0, 229, 255, 0.15)"
                    depth={isSelected ? 3 : 1}
                  >
                    <div className="flex items-center">
                      <button
                        onClick={() => {
                          setSelectedCameraId(cam.camera_id);
                          setSelectedAlertTime(null);
                        }}
                        className={`px-4 py-2.5 rounded-xl text-xs font-mono border-0 flex items-center gap-2.5 transition-all duration-300 shrink-0 relative ${
                          isSelected
                            ? "bg-primary/15 text-foreground"
                            : "bg-transparent text-muted-foreground hover:text-foreground hover:bg-white/[0.04]"
                        }`}
                      >
                        <span
                          className={`w-2 h-2 rounded-full ${
                            cam.is_running ? "bg-emerald-500" : "bg-gray-500"
                          }`}
                          style={{
                            boxShadow: cam.is_running
                              ? "0 0 8px rgba(34,197,94,0.5)"
                              : "none",
                          }}
                        />
                        <div className="text-left">
                          <div className="font-bold flex items-center gap-1.5">
                            <span>{cam.camera_id}</span>
                            {mod === "IR_NIGHT" && <Moon className="w-3 h-3 text-emerald-400" />}
                            {mod === "THERMAL" && <Flame className="w-3 h-3 text-orange-400" />}
                            {mod === "STANDARD" && <Video className="w-3 h-3 text-cyan-400" />}
                          </div>
                          <div className="text-[10px] text-muted-foreground/70 truncate max-w-[140px]">
                            {cam.name}
                          </div>
                        </div>

                        {/* Active indicator bar */}
                        {isSelected && (
                          <motion.div
                            layoutId="cameraIndicator"
                            className="absolute bottom-0 left-2 right-2 h-[2px] bg-primary rounded-full"
                            style={{ boxShadow: "0 0 12px rgba(0,229,255,0.5)" }}
                            transition={{ type: "spring", stiffness: 400, damping: 30 }}
                          />
                        )}
                      </button>

                      {cameras.length > 1 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteCamera(cam.camera_id);
                          }}
                          className="mr-2 p-1 rounded-md text-muted-foreground hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title={`Remove ${cam.camera_id}`}
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </PremiumCard>
                </div>
              );
            })}
          </div>

          {/* Primary Camera Feed — Premium Frame */}
          <PremiumCard tilt={3} glare={false} depth={3}>
            <div className="h-[520px] w-full relative">
              {/* Corner brackets — premium frame effect */}
              <div className="absolute top-2 left-2 w-5 h-5 border-t-2 border-l-2 border-primary/40 rounded-tl-lg z-20 pointer-events-none" />
              <div className="absolute top-2 right-2 w-5 h-5 border-t-2 border-r-2 border-primary/40 rounded-tr-lg z-20 pointer-events-none" />
              <div className="absolute bottom-2 left-2 w-5 h-5 border-b-2 border-l-2 border-primary/40 rounded-bl-lg z-20 pointer-events-none" />
              <div className="absolute bottom-2 right-2 w-5 h-5 border-b-2 border-r-2 border-primary/40 rounded-br-lg z-20 pointer-events-none" />

              {activeCamera ? (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={selectedCameraId}
                    initial={{ opacity: 0.8, scale: 0.998 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0.8, scale: 0.998 }}
                    transition={{ duration: 0.3 }}
                    className="h-full"
                  >
                    <CameraFeed
                      cameraId={activeCamera.camera_id}
                      cameraName={activeCamera.name}
                      modality={activeCamera.modality || "STANDARD"}
                      selectedAlertTime={selectedAlertTime}
                      isRunning={activeCamera.is_running}
                      onToggleRun={handleToggleRun}
                      onExitSeek={handleExitSeek}
                      onZoneCreated={fetchCameras}
                    />
                  </motion.div>
                </AnimatePresence>
              ) : (
                <div className="h-full flex items-center justify-center bg-black/40 rounded-xl">
                  <div className="text-center">
                    <Radio className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
                    <p className="text-sm font-mono text-muted-foreground">No active camera stream</p>
                    <p className="text-[10px] font-mono text-muted-foreground/50 mt-1">
                      Add a camera feed to begin surveillance
                    </p>
                  </div>
                </div>
              )}
            </div>
          </PremiumCard>

          {/* AI Copilot — Premium Glass */}
          <PremiumCard tilt={2} glare={true} depth={2} glowColor="rgba(139, 92, 246, 0.12)">
            <AIAssistantBar selectedCameraId={selectedCameraId} />
          </PremiumCard>
        </div>

        {/* RIGHT: Alerts (4 cols) */}
        <div className="xl:col-span-4 h-[calc(100vh-100px)] sticky top-20 flex flex-col">
          <PremiumCard tilt={2} glare={true} depth={3} className="h-full flex flex-col">
            <AlertPanel
              onSelectAlert={(alert) => setSelectedAlert(alert)}
              selectedAlertId={selectedAlert?.event_id || selectedAlert?.alert_id}
              onSeekTime={handleSeekTime}
            />
          </PremiumCard>
        </div>
      </main>

      {/* ═══ STATUS BAR ═══ */}
      <StatusBar
        cameraCount={cameras.length}
        alertCount={0}
        threatLevel={threatData.level}
      />

      {/* ═══ MODALS ═══ */}
      {selectedAlert && (
        <AlertInspector
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onAcknowledge={handleAcknowledgeAlert}
          onSeekTime={handleSeekTime}
        />
      )}

      {showAddCamera && (
        <AddCameraModal
          onClose={() => setShowAddCamera(false)}
          onCameraAdded={() => {
            fetchCameras();
            setShowAddCamera(false);
          }}
        />
      )}
    </div>
  );
}
