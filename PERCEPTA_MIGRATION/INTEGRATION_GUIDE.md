# PERCEPTA — LANDING & AUTHENTICATION MIGRATION PACKAGE
## Comprehensive Integration & Deployment Guide

This package contains the complete, self-contained **PERCEPTA Landing Page**, **Tactical Authentication Portal**, **3D Earth Scene**, **Sound Effects**, **Design Tokens**, **Animations**, and **Isolated Auth Service Adapter**. It is designed to be copied directly into the older PERCEPTA codebase without disturbing the existing backend, YOLO AI pipeline, ByteTrack, camera ingestion, database, or C2 dashboard.

---

### Table of Contents
1. [File Inventory & Structure](#1-file-inventory--structure)
2. [Folder Mapping in Destination Project](#2-folder-mapping-in-destination-project)
3. [Required NPM Packages](#3-required-npm-packages)
4. [Required Google Fonts](#4-required-google-fonts)
5. [Environment Variables](#5-environment-variables)
6. [Routing Configuration](#6-routing-configuration)
7. [Connecting Authentication (Adapter Guide)](#7-connecting-authentication-adapter-guide)
8. [Untouched Old Components Guarantee](#8-untouched-old-components-guarantee)
9. [Import Path Customization](#9-import-path-customization)
10. [Landing Page Verification](#10-landing-page-verification)
11. [Authentication Page Verification](#11-authentication-page-verification)
12. [End-to-End Navigation Verification](#12-end-to-end-navigation-verification)

---

### 1. File Inventory & Structure

The migration package is organized in a self-contained hierarchy with clean relative imports:

```
PERCEPTA_MIGRATION/
├── landing/
│   ├── LandingPage.tsx              # Complete 8-stage 3D Earth landing page
│   ├── components/
│   │   ├── EarthGlobe.tsx           # Photorealistic Three.js 3D earth scene + camera choreography
│   │   ├── WorldOverlays.tsx        # 8-stage HUD reticles, labels, radars & metrics
│   │   ├── TacticalCursor.tsx       # Custom tactical mouse cursor with crosshairs
│   │   └── C2Loader.tsx             # Military-grade enclave boot loader
│   ├── assets/
│   │   ├── c2-loader.mp3            # Audio effect for C2Loader
│   │   └── earth_atmos_2048.jpg     # Offline high-resolution 2K Earth texture
│   └── styles/
│       ├── WorldOverlays.css        # HUD reticle styling, bounding boxes & radar sweep
│       └── WorldMotion.css          # Kinetic keyframes, entrance transitions & responsive rules
│
├── auth/
│   ├── AuthPage.tsx                 # Tactical operator authentication portal
│   ├── authService.adapter.ts       # Decoupled auth interface & offline/edge adapter
│   └── styles/
│       └── Auth.css                 # Terminal card, corner brackets, inputs & SSO buttons
│
├── shared/
│   ├── components/
│   │   ├── PerceptaLogo.tsx         # Vector tactical aperture emblem + typography
│   │   └── StarsBackground.tsx      # Multi-layer deep space Three.js starfield & nebula
│   ├── styles/
│   │   ├── designTokens.css         # Overridable CSS custom properties (--percepta-*)
│   │   └── tokens.ts                # TypeScript design tokens export (for Tailwind)
│   └── assets/
│       └── favicon.svg              # Percepta SVG icon
│
├── routing/
│   └── routes.tsx                   # Route definitions, ProtectedRoute clearance guard & router
│
└── INTEGRATION_GUIDE.md             # This document
```

---

### 2. Folder Mapping in Destination Project

Copy the `PERCEPTA_MIGRATION` directory directly into your older PERCEPTA project's `frontend/src/` (or your existing frontend root):

| Source Folder | Destination in Older Project | Purpose |
| :--- | :--- | :--- |
| `PERCEPTA_MIGRATION/landing/` | `src/pages/Landing/` or `src/features/landing/` | Landing page, 3D Earth globe, and chapter overlays |
| `PERCEPTA_MIGRATION/auth/` | `src/pages/Auth/` or `src/features/auth/` | Auth page and isolated `authService.adapter.ts` |
| `PERCEPTA_MIGRATION/shared/` | `src/shared/` or `src/components/percepta-shared/` | Logo, starfield, and theme design tokens |
| `PERCEPTA_MIGRATION/routing/` | `src/routes/` or directly inside `src/App.tsx` | Route definitions & clearance guard |
| `landing/assets/c2-loader.mp3` | `public/c2-loader.mp3` *(optional public fallback)* | Bundled automatically via Vite/Webpack import |

*Note: You can keep the folder intact as `src/PERCEPTA_MIGRATION/` if you prefer zero path adjustments.*

---

### 3. Required NPM Packages

Ensure the following packages are present in your destination project's `package.json`:

```bash
# Core 3D & UI Icons
npm install three lucide-react

# TypeScript definitions
npm install --save-dev @types/three

# Routing (if not already installed)
npm install react-router
```

> **Compatible Versions:**
> - `three`: `^0.160.0` or later (tested on `0.185.1`)
> - `lucide-react`: `^0.300.0` or later (tested on `1.33.0`)
> - `react`: `^18.0.0` or `^19.0.0`
> - `react-router`: `^6.0.0` or `^7.0.0` (or `react-router-dom`)

---

### 4. Required Google Fonts

Add the following Google Fonts link to your destination project's `index.html` within the `<head>` section:

```html
<!-- Percepta Defense Typography Stacks -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,700&family=Chakra+Petch:wght@500;600;700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&family=Teko:wght@500;600;700&display=swap" rel="stylesheet">
```

| Font Name | Role in Design |
| :--- | :--- |
| **Barlow Condensed** | Massive editorial hero title (`"See the whole picture."`), chapter titles, stats |
| **Teko** | Auth portal bold title (`"COMMAND PORTAL"`) |
| **Chakra Petch** | Tactical buttons (`"ENTER COMMAND CENTER"`) & modal titles |
| **JetBrains Mono** | Field inputs, telemetry metadata, status banners, credentials |
| **DM Mono** | Chapter metrics & telemetry lines |
| **DM Serif Display** | C2 Loader central progress percentage |
| **Space Grotesk** | Clean readable descriptions & body paragraphs |

---

### 5. Environment Variables

The package is **100% functional without any environment variables**.

If you wish to configure a custom backend URL for authentication:
```env
# Optional: Set your existing older PERCEPTA backend API endpoint
VITE_PERCEPTA_API_URL=http://localhost:8000/api
```

You can pass this variable into the adapter during initialization:
```ts
import { configureAuthService } from "./auth/authService.adapter";

configureAuthService({
  apiBaseUrl: import.meta.env.VITE_PERCEPTA_API_URL || "/api/auth",
});
```

---

### 6. Routing Configuration

In your destination project's `App.tsx` (or your root router file):

```tsx
import React from "react";
import { Routes, Route, Navigate } from "react-router";
import LandingPage from "./PERCEPTA_MIGRATION/landing/LandingPage";
import AuthPage from "./PERCEPTA_MIGRATION/auth/AuthPage";
import { ProtectedRoute } from "./PERCEPTA_MIGRATION/routing/routes";

// Import your existing OLD PERCEPTA Dashboard
import OldCommandDashboard from "./views/Dashboard"; 

export default function App() {
  return (
    <Routes>
      {/* 1. Public Landing Page */}
      <Route path="/" element={<LandingPage />} />

      {/* 2. Authentication Portal */}
      <Route path="/auth" element={<AuthPage />} />

      {/* 3. Existing Old PERCEPTA Dashboard (Clearance Guarded) */}
      <Route
        path="/dashboard/*"
        element={
          <ProtectedRoute>
            <OldCommandDashboard />
          </ProtectedRoute>
        }
      />

      {/* Fallback to Landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

---

### 7. Connecting Authentication (Adapter Guide)

The authentication portal calls `authService.adapter.ts`. It does not rely on any current backend code, YOLO, SQLite, or FastAPI routes.

#### Option A: Standalone / Offline Testing (Ready Immediately)
Out of the box, `authService.adapter.ts` operates in standalone mode. Any user can test the login immediately with default operator clearances:
- **Callsign / Email:** `operator` (or `callsign@defense.percepta.ai` or `admin`)
- **Passphrase:** `operator123`

#### Option B: Connecting to Existing Older PERCEPTA Backend
If your older project has an authentication endpoint (e.g. `/api/login` or `/api/token`), configure it in your application bootstrap (`index.tsx` or `main.tsx`):

```ts
import { configureAuthService } from "./PERCEPTA_MIGRATION/auth/authService.adapter";

configureAuthService({
  apiBaseUrl: "http://localhost:8000/api/auth",
});
```

#### Option C: Providing a Custom Adapter
If your older project uses Firebase, Supabase, JWT cookies, or a custom session store, implement `IAuthAdapter`:

```ts
import { setAuthAdapter, IAuthAdapter, AuthResult } from "./PERCEPTA_MIGRATION/auth/authService.adapter";
import { oldAuthSystem } from "./services/oldAuth";

const customOlderBackendAdapter: IAuthAdapter = {
  async login({ emailOrCallsign, password }) {
    const response = await oldAuthSystem.authenticate(emailOrCallsign, password);
    return {
      success: response.ok,
      session: { user: response.user, access_token: response.token },
      error: response.errorMsg,
    };
  },
  async register(credentials) {
    return oldAuthSystem.createAccount(credentials);
  },
  async loginOAuth(provider) {
    return oldAuthSystem.sso(provider);
  },
  async resetPassword(email) {
    return oldAuthSystem.sendReset(email);
  },
  async logout() {
    return oldAuthSystem.clearSession();
  },
  async getCurrentSession() {
    return oldAuthSystem.checkSession();
  },
  async isAuthenticated() {
    const s = await oldAuthSystem.checkSession();
    return Boolean(s);
  },
};

// Activate custom adapter
setAuthAdapter(customOlderBackendAdapter);
```

---

### 8. Untouched Old Components Guarantee

The following components and subsystems in the older PERCEPTA project **must remain completely untouched**:

1. **AI Perception & YOLO Model**: `yolov8n.pt`, inference threads, and detection models.
2. **ByteTrack & Multi-Camera Re-ID**: Object tracking, entity ID assignment, trajectory buffers.
3. **Camera Stream Ingestion**: RTSP streams, MJPEG feeds, WebSocket frame pipelines.
4. **Database & Storage**: SQLite `percepta.db`, tables (`incidents`, `evidence`, `tracks`, `detections`).
5. **C2 Command Center Dashboard**: Real-time camera matrix, incident timeline, telemetry panels, zones manager, radar map.
6. **Backend Server**: FastAPI / ASGI application, router endpoints, WebSocket broadcasters.

The migration package interacts **only** by rendering at `/` and `/auth`, and conditionally routing authorized operators to `/dashboard`.

---

### 9. Import Path Customization

All imports inside `PERCEPTA_MIGRATION/` use clean relative paths (`./components/...`, `../shared/...`). If you relocate the folders to fit an existing directory convention (such as `src/pages/` and `src/components/`), simply update the following relative imports:

```tsx
// Example if moving files:
// In LandingPage.tsx:
import { EarthGlobe } from "./components/EarthGlobe";
import { PerceptaLogo } from "@/shared/components/PerceptaLogo";
import "./styles/WorldOverlays.css";

// In AuthPage.tsx:
import { authService } from "./authService.adapter";
import { StarsBackground } from "@/shared/components/StarsBackground";
import "./styles/Auth.css";
```

---

### 10. Landing Page Verification

Verify that the landing page renders all components:

- [ ] **Hero Section**: Eyebrow (`INTELLIGENCE, GROUNDED`), title (`See the whole picture.`), description, and action buttons (`ENTER COMMAND CONSOLE`, `OPERATOR AUTH // ACCESS`).
- [ ] **Choreographed 3D Earth Globe**: The Three.js globe smoothly pans and rotates on scroll through all 11 choreography milestones (`earthChoreography`).
- [ ] **8 Interactive Chapters**:
  - `01. Observe`: Optical & IR camera markers (`CAM-01`, `CAM-02`, `CAM-03`) with active blinking sensor nodes.
  - `02. Detect`: Bounding reticles for `PERSON`, `VEHICLE`, `PLATE`, and `FACE` with confidence tags.
  - `03. Track`: Multi-camera route progression (`CAM-02 → CAM-01 → CAM-03`).
  - `04. Understand`: Rotating radar sweep and zone breach indicators.
  - `05. Assess`: Large threat score (`72 / 100 HIGH / CONTEXTUAL`).
  - `06. Evidence`: Tamper-evident frame with SHA-256 validation tag.
  - `07. Incidents`: Convergence lines consolidating multiple signals into a single incident.
  - `08. Command`: Command Center mini status panel.
- [ ] **Tactical Cursor**: Inner reticle dot with damped trailing outer ring and crosshairs on hover.
- [ ] **C2 Boot Loader**: Initial circular SVG load gauge with audio cue and `SKIP INTRO →` button.
- [ ] **Footer**: Grounded Defense AI section with `ENTER COMMAND CONSOLE` and `INCIDENTS DOSSIER` buttons.

---

### 11. Authentication Page Verification

Navigate to `http://localhost:5173/auth` and verify:

- [ ] **Deep Space Starfield**: Background renders twinkling stars and atmospheric nebula without errors.
- [ ] **Tactical Terminal Card**: Glassmorphism container with corner brackets (`#33f0b4`).
- [ ] **Tabs Switcher**: Clean switching between `SIGN IN` and `REQUEST ACCESS`.
- [ ] **Visibility Toggles**: Clicking `[ SHOW ]` / `[ HIDE ]` reveals or masks the passphrase.
- [ ] **Validation States**: Error banner renders red (`#ef4444`) with shield alert icon when invalid credentials are submitted.
- [ ] **Success States**: Success banner renders mint (`#33f0b4`) with check icon upon valid submission.
- [ ] **SSO Providers**: Buttons for `GOOGLE`, `GITHUB`, and `MICROSOFT` are displayed.

---

### 12. End-to-End Navigation Verification

Test the complete navigation lifecycle:

1. **Initial Visit (`/`)**:
   - Open root URL `http://localhost:5173/`.
   - The Landing Page appears with the 3D Earth globe.
   - Click `ENTER COMMAND CONSOLE` or `ENTER C2` in the navbar.
2. **Clearance Check (`/dashboard` → `/auth`)**:
   - Because no session is present, `ProtectedRoute` intercepts the request and redirects to `/auth?redirect=/dashboard`.
3. **Authentication (`/auth`)**:
   - On the Auth page, enter `operator` and `operator123`.
   - Click `ENTER COMMAND CENTER`.
   - The button shows `AUTHENTICATING ENCLAVE...` and stores the clearance token.
4. **Arrival at Old Dashboard (`/dashboard`)**:
   - The user is seamlessly redirected to `/dashboard`.
   - The older PERCEPTA Command Dashboard renders in its original, untouched state with all camera feeds, YOLO detections, and telemetry functioning as expected.
