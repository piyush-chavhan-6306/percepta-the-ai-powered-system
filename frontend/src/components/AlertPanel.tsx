import { useEffect, useState } from "react";
import { AlertItem } from "@/types/surveillance";
import { api } from "@/api/client";
import { useWebSocket, WsMessage } from "@/hooks/useWebSocket";
import {
  AlertTriangle,
  ShieldAlert,
  Check,
  Filter,
  RefreshCw,
  ChevronRight,
  Clock,
  Compass,
  PlayCircle,
  Camera,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface AlertPanelProps {
  onSelectAlert?: (alert: AlertItem) => void;
  selectedAlertId?: string;
  onSeekTime?: (timestamp: string | number, cameraId?: string) => void;
}

function formatAlertTime(ts: string | number): string {
  try {
    const d = typeof ts === "number" ? new Date(ts) : new Date(ts);
    if (isNaN(d.getTime())) return String(ts);
    return d.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return String(ts);
  }
}

export function AlertPanel({ onSelectAlert, selectedAlertId, onSeekTime }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.getAlerts({ limit: 50 });
      setAlerts(res.alerts || []);
    } catch (err) {
      console.error("Failed to load alert history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  // Listen to live WebSocket events
  useWebSocket((msg: WsMessage) => {
    if (msg.event_type === "ALERT" || msg.event_type === "alert") {
      const newAlert: AlertItem = {
        event_id: msg.event_id || `alert-${Date.now()}`,
        alert_id: msg.alert_id || msg.event_id,
        timestamp: msg.timestamp || new Date().toISOString(),
        camera_id: msg.camera_id || "CAM-01",
        track_id: msg.track_id,
        incident_id: msg.incident_id,
        severity: (msg.severity || "CRITICAL").toUpperCase(),
        message: msg.message || "Security violation detected",
        confidence: msg.confidence,
        is_acknowledged: false,
        threat_score: (msg as any).threat_score || 85,
        threat_level: (msg as any).threat_level || "CRITICAL",
        threat_reasons: (msg as any).threat_reasons,
        causal_chain: (msg as any).causal_chain,
        evidence_snapshot_uri: (msg as any).evidence_snapshot_uri,
        face_snapshot_uri: (msg as any).face_snapshot_uri,
        anpr_snapshot_uri: (msg as any).anpr_snapshot_uri,
      };

      setAlerts((prev) => {
        if (prev.some((a) => a.event_id === newAlert.event_id)) return prev;
        return [newAlert, ...prev];
      });
    }
  });

  const handleAcknowledge = async (e: React.MouseEvent, alertId: string) => {
    e.stopPropagation();
    try {
      await api.acknowledgeAlert(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.event_id === alertId || a.alert_id === alertId ? { ...a, is_acknowledged: true } : a))
      );
    } catch (err) {
      console.error("Failed to acknowledge alert:", err);
    }
  };

  const handleTimelineSeek = (e: React.MouseEvent, alert: AlertItem) => {
    e.stopPropagation();
    if (onSeekTime) {
      onSeekTime(alert.timestamp, alert.camera_id);
    }
    if (onSelectAlert) {
      onSelectAlert(alert);
    }
  };

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity === "ALL") return true;
    return a.severity?.toUpperCase() === filterSeverity;
  });

  const unacknowledgedCount = alerts.filter((a) => !a.is_acknowledged).length;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-3.5 border-b border-white/10 flex items-center justify-between bg-black/40">
        <div className="flex items-center gap-2">
          <div className="relative">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            {unacknowledgedCount > 0 && (
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500 animate-ping" />
            )}
          </div>
          <h2 className="text-xs font-bold text-foreground font-mono uppercase tracking-wider">
            TACTICAL INCIDENT FEED
          </h2>
          <span className="px-1.5 py-0.5 text-[10px] font-mono bg-red-500/20 text-red-400 border border-red-500/30 rounded-md">
            {unacknowledgedCount} ACTIVE
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-black/60 border border-white/10 rounded-md px-2 py-1 text-[10px] font-mono text-muted-foreground focus:outline-none"
          >
            <option value="ALL">ALL SEVERITY</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="RESTRICTED">RESTRICTED</option>
            <option value="NORMAL">NORMAL</option>
          </select>
          <Button
            variant="ghost"
            size="icon"
            onClick={fetchAlerts}
            className="h-7 w-7 text-muted-foreground hover:text-foreground"
            title="Refresh feed"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto divide-y divide-white/5 scrollbar-thin scrollbar-thumb-white/10">
        {filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center p-4">
            <ShieldAlert className="w-8 h-8 text-muted-foreground/40 mb-2" />
            <p className="text-xs text-muted-foreground font-mono">NO ACTIVE INCIDENTS IN SECTOR</p>
            <p className="text-[10px] text-muted-foreground/60 mt-1">Perimeter status normal</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isSelected = selectedAlertId === alert.event_id || selectedAlertId === alert.alert_id;
            const sevUpper = (alert.severity || "NORMAL").toUpperCase();
            const isCrit = sevUpper === "CRITICAL";
            const isRestricted = sevUpper === "RESTRICTED";
            const threatScore = alert.threat_score ?? (isCrit ? 85 : isRestricted ? 50 : 15);

            return (
              <div
                key={alert.event_id || alert.alert_id}
                onClick={() => onSelectAlert?.(alert)}
                className={`p-3 transition-all cursor-pointer relative group ${
                  isSelected
                    ? "bg-primary/10 border-l-4 border-l-primary"
                    : alert.is_acknowledged
                    ? "opacity-60 hover:opacity-100 hover:bg-white/[0.03]"
                    : "hover:bg-white/[0.04] border-l-2 border-l-transparent"
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span
                      className={`text-[9px] font-mono px-2 py-0.5 uppercase rounded-full border font-bold ${
                        isCrit
                          ? "bg-red-500/20 text-red-400 border-red-500/40"
                          : isRestricted
                          ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                      }`}
                    >
                      {sevUpper}
                    </span>

                    {/* Threat Score Badge */}
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded border font-semibold ${
                        threatScore >= 75
                          ? "bg-red-950/80 text-red-300 border-red-700/60"
                          : threatScore >= 50
                          ? "bg-orange-950/80 text-orange-300 border-orange-700/60"
                          : "bg-amber-950/80 text-amber-300 border-amber-700/60"
                      }`}
                    >
                      THREAT {threatScore}/100
                    </span>

                    <span className="text-[10px] font-mono text-cyan-400 flex items-center gap-1">
                      <Camera className="w-2.5 h-2.5" />
                      {alert.camera_id}
                    </span>

                    {alert.track_id && (
                      <span className="text-[10px] font-mono text-muted-foreground">
                        TRACK #{alert.track_id}
                      </span>
                    )}
                  </div>

                  {/* Clickable Timestamp with Timeline Seek Action */}
                  <button
                    onClick={(e) => handleTimelineSeek(e, alert)}
                    className="flex items-center gap-1 text-[10px] font-mono text-cyan-300 hover:text-cyan-100 bg-cyan-950/50 hover:bg-cyan-900/70 border border-cyan-800/50 px-1.5 py-0.5 rounded transition-colors group/btn"
                    title="Click to seek video timeline to event moment"
                  >
                    <PlayCircle className="w-3 h-3 text-cyan-400 group-hover/btn:scale-110 transition-transform" />
                    <span>{formatAlertTime(alert.timestamp)}</span>
                  </button>
                </div>

                <p className="text-xs text-foreground font-medium line-clamp-2 leading-tight">
                  {alert.message || alert.reason || "Perimeter anomaly detected"}
                </p>

                {/* Footer telemetry */}
                <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-muted-foreground">
                  <div className="flex items-center gap-2">
                    {alert.heading && (
                      <span className="flex items-center gap-0.5 text-blue-400">
                        <Compass className="w-2.5 h-2.5" />
                        {alert.heading}
                      </span>
                    )}
                    {alert.speed_description && (
                      <span className="text-muted-foreground/80">{alert.speed_description}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {!alert.is_acknowledged ? (
                      <button
                        onClick={(e) => handleAcknowledge(e, alert.event_id || alert.alert_id || "")}
                        className="text-[9px] text-emerald-400 hover:text-emerald-300 flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20"
                      >
                        <Check className="w-2.5 h-2.5" /> ACK
                      </button>
                    ) : (
                      <span className="text-[9px] text-muted-foreground flex items-center gap-0.5">
                        <Check className="w-2.5 h-2.5" /> ACKED
                      </span>
                    )}
                    <ChevronRight className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
