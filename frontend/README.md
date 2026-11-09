# Roamly AI - React Frontend ✈️

A modern, high-performance React frontend for Roamly AI built with **Vite**, **TypeScript**, and **Tailwind CSS**.

---

## 🚀 Features

- **Parallel Agent Pipeline Visualizer**: Live graphical representation of the LangGraph state machine (concurrent fan-out for Flights, Hotels, and Weather, followed by the barrier fan-in Itinerary planner and Final synthesis).
- **Tabbed Travel Plan Viewer**:
  - 📋 Executive Overview & Budget Breakdown
  - 🗺️ Detailed Day-by-Day Itinerary
  - ✈️ Flight Routes & Estimated Fares
  - 🏨 Hotel & Accommodation Tiers
  - 🌤️ Weather Conditions & Smart Packing Advice
- **Actions**:
  - One-click copy of full Markdown itinerary
  - Direct `.md` file export
  - Curated 1-click sample prompts for testing
- **Resilient Error Handling**:
  - Automatic detection and user-friendly messaging for rate limits (Groq HTTP 429)
  - Connection health monitoring via `/health`

---

## 🛠️ Local Development

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```

The app will start at **http://localhost:5173**.

> **Note on API proxying**: In local development, requests to `/api/*` and `/health` are automatically proxied to `http://127.0.0.1:8000` via `vite.config.ts`, so you do not need to configure CORS or environment variables locally.

---

## 🚢 Production Deployment (Vercel)

1. Import this repository into [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. In the Vercel Project Settings under **Environment Variables**, add:
   ```env
   VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
   ```
4. Deploy! Vercel will run `npm run build` and serve the optimized static files from `dist/`.
