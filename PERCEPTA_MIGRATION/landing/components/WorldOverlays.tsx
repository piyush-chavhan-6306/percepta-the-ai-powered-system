import React from "react";
import "../styles/WorldOverlays.css";

export interface OverlayTransform {
  opacity: number;
  scale: number;
  translateY: number;
}

export interface WorldOverlaysProps {
  opacities: Record<string, OverlayTransform>;
}

export const WorldOverlays: React.FC<WorldOverlaysProps> = ({ opacities }) => {
  const getStyle = (id: string) => {
    const item = opacities[id] || { opacity: 0, scale: 0.94, translateY: 0 };
    return {
      opacity: item.opacity,
      transform: `scale(${item.scale}) translateY(${item.translateY}px)`,
      pointerEvents: item.opacity > 0.35 ? ("auto" as const) : ("none" as const),
      display: item.opacity > 0 ? "block" : "none",
    };
  };

  return (
    <div
      className="world-overlays"
      aria-live="polite"
      data-testid="world-story-overlays"
    >
      {/* ── 01. Observe ──────────────────────────────────────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("observe")}
        data-testid="world-observe-overlay"
      >
        <div className="orbit-label orbit-cam cam-a">
          <span className="signal-dot" />
          CAM-01 <small>OPTICAL</small>
        </div>
        <div className="orbit-label orbit-cam cam-b active-anchor">
          <span className="signal-dot active-dot" />
          CAM-02 <small>IR · ACTIVE</small>
        </div>
        <div className="orbit-label orbit-cam cam-c">
          <span className="signal-dot" />
          CAM-03 <small>RGB</small>
        </div>
        {/* Subtle sensor network connection lines */}
        <svg className="camera-network-svg" aria-hidden="true">
          <line x1="58%" y1="28%" x2="74%" y2="44%" stroke="rgba(158,231,223,0.35)" strokeDasharray="3 3" />
          <line x1="74%" y1="44%" x2="64%" y2="70%" stroke="rgba(158,231,223,0.35)" strokeDasharray="3 3" />
        </svg>
        <span className="orbit-ring ring-one" />
        <span className="orbit-ring ring-two" />
      </div>

      {/* ── 02. Detect (Direct Anchor to CAM-02 Active Sensor) ─────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("detect")}
        data-testid="world-detect-overlay"
      >
        <div className="detection-field">
          {/* Active Locked Entity: PERSON-042 at CAM-02 */}
          <div className="tactical-box box-person tactical-box-corners ring-1 ring-[#9ee7df]/50 shadow-[0_0_24px_rgba(158,231,223,0.2)]">
            <div className="box-tag">
              <b className="text-[#9ee7df]">PERSON</b>
              <span className="box-conf">[0.94]</span>
            </div>
            <div className="box-reticle" />
            <div className="text-[7px] text-[#e8ebe6] font-mono font-medium mt-1">PERSON-042</div>
            <div className="text-[6.5px] text-[#9ee7df]/90 font-mono tracking-wider">LOCKED · CAM-02 [IR]</div>
          </div>

          {/* Vehicle Box */}
          <div className="tactical-box box-vehicle tactical-box-corners opacity-75">
            <div className="box-tag">
              <b>VEHICLE</b>
              <span className="box-conf">[0.89]</span>
            </div>
            <div className="box-reticle" />
            <div className="text-[6.5px] text-[#d6c19b]/80 font-mono">SUV · 24 KM/H</div>
          </div>

          {/* Plate Box */}
          <div className="tactical-box box-plate tactical-box-corners opacity-75">
            <div className="box-tag">
              <b>PLATE</b>
              <span className="box-conf">[0.92]</span>
            </div>
            <div className="text-[7px] text-[#e8ebe6] font-mono tracking-widest text-center mt-1">
              DL-04-AB-1982
            </div>
          </div>

          {/* Face Box */}
          <div className="tactical-box box-face tactical-box-corners opacity-75">
            <div className="box-tag">
              <b>FACE</b>
              <span className="box-conf">[0.95]</span>
            </div>
            <div className="box-reticle" />
            <div className="text-[6.5px] text-[#8fb8b5] font-mono">VERIFIED</div>
          </div>
        </div>
      </div>

      {/* ── 03. Track (Continuous Entity Handoff) ────────────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("track")}
        data-testid="world-track-overlay"
      >
        <div className="track-journey-centered">
          <div className="track-id">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#9ee7df] shadow-[0_0_8px_#9ee7df]" />
              TRACK-017
            </span>
            <b>PERSON-042</b>
          </div>
          <div className="track-route">
            <span className="text-[#9ee7df] border-[#9ee7df]/40 font-medium">CAM-02 (ORIGIN)</span>
            <i />
            <span>CAM-01</span>
            <i />
            <span>CAM-03</span>
          </div>
          <small>CROSS-CAMERA CONTINUITY / SPATIAL-TEMPORAL HANDOFF</small>
        </div>
      </div>

      {/* ── 04. Understand (Entity Enters Zone Context) ──────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("understand")}
        data-testid="world-understand-overlay"
      >
        <div className="context-radar-centered">
          <div className="radar-core">
            <span className="text-[7.5px] tracking-widest text-[#9ee7df] uppercase">
              RADAR CONTEXT · 14:32:18 UTC
            </span>
            <b>TRACK-017 [PERSON-042]</b>
          </div>
          <span className="context-tag zone">RESTRICTED ZONE</span>
          <span className="context-tag movement">PERIMETER INTRUSION</span>
          <span className="context-tag time">DWELL: 42s</span>
          <span className="context-tag direction">HEADING: 114° SE</span>
        </div>
      </div>

      {/* ── 05. Assess (Observable Risk Weighting) ───────────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("assess")}
        data-testid="world-assess-overlay"
      >
        <div className="risk-reading-centered">
          <p>THREAT ASSESSMENT</p>
          <strong>
            72 <small>/ 100</small>
          </strong>
          <span>HIGH / CONTEXTUAL</span>
          <div>
            <i /> RESTRICTED-ZONE PERSISTENCE
          </div>
          <div>
            <i /> VECTOR: PERIMETER GATE 2
          </div>
          <div className="text-[7px] text-[#8fa09d] pt-2 font-mono">
            OBSERVABLE EVIDENCE WEIGHTING · NOT RAW CONFIDENCE
          </div>
        </div>
      </div>

      {/* ── 06. Evidence (Tamper-Evident Forensic Source) ────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("evidence")}
        data-testid="world-evidence-overlay"
      >
        <div className="evidence-frame-centered">
          <div className="evidence-image">
            <span>FRAME 14:32:10 UTC</span>
          </div>
          <div>
            <p>EVIDENCE / TARGET CROP</p>
            <strong>PERSON-042</strong>
            <small>
              CAM-02 · SOURCE FRAME
              <br />
              REASON: RESTRICTED-ZONE ENTRY
              <br />
              SHA-256: 7f3a9e...c410 [VERIFIED]
            </small>
          </div>
        </div>
      </div>

      {/* ── 07. Incidents (Multi-Signal Convergence) ─────────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("incidents")}
        data-testid="world-incidents-overlay"
      >
        <div className="incident-convergence-centered">
          <div className="incident-signals">
            <span>DWELL 42s</span>
            <span>ZONE BREACH</span>
            <span>TRACK ENTITY</span>
          </div>
          <div className="convergence-line">
            <i />
            <i />
            <i />
          </div>
          <div className="incident-result">
            <p>ONE MEANINGFUL INCIDENT</p>
            <strong>RESTRICTED-ZONE ENTRY</strong>
            <small>MULTIPLE SENSOR SIGNALS → CONVERGED INCIDENT</small>
          </div>
        </div>
      </div>

      {/* ── 08. Command (Clear Operating Picture) ───────────────────────────── */}
      <div
        className="overlay-stage-container"
        style={getStyle("command")}
        data-testid="world-command-overlay"
      >
        <div className="command-transition-right">
          <span className="text-[9px] tracking-widest text-[#9ee7df] uppercase font-bold">
            WORLD → OPERATING PICTURE
          </span>
          <div className="command-mini">
            <b>COMMAND CENTER</b>
            <em>
              <i /> CAM-01 · LIVE STREAMING
            </em>
            <span>OPERATING STATE: ACTIVE C2</span>
            <small>ACTIVE INCIDENTS · PERSISTENT TRACKS · EVIDENCE READY</small>
          </div>
        </div>
      </div>
    </div>
  );
};
