import React from 'react';
import { Plane, CheckCircle2, AlertTriangle, ExternalLink, GitFork } from 'lucide-react';

interface NavbarProps {
  isOnline: boolean | null;
  llmCalls?: number | null;
  onOpenSpecs?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ isOnline, llmCalls, onOpenSpecs }) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">

        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/25">
            <Plane className="h-5 w-5 text-white transform -rotate-45" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight text-white font-sans">
                Roamly<span className="text-blue-500">.ai</span>
              </span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Concierge
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Autonomous Travel Intelligence
            </p>
          </div>
        </div>

        {/* Right Navigation & Status Actions */}
        <div className="flex items-center gap-3">
          {/* Tech Specs Slide-Over Trigger */}
          {onOpenSpecs && (
            <button
              type="button"
              onClick={onOpenSpecs}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/25 text-xs font-semibold text-indigo-300 hover:text-white transition shadow-sm"
              title="Open System Architecture & Multi-Agent Telemetry Drawer"
            >
              <GitFork className="h-3.5 w-3.5 text-indigo-400" />
              <span>System Specs</span>
              {typeof llmCalls === 'number' && llmCalls > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-indigo-500/30 text-[10px] text-indigo-200">
                  {llmCalls}
                </span>
              )}
            </button>
          )}

          {/* Backend Health Badge */}
          <div
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors ${
              isOnline === true
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                : isOnline === false
                ? 'bg-rose-500/10 border-rose-500/20 text-rose-300'
                : 'bg-amber-500/10 border-amber-500/20 text-amber-300'
            }`}
          >
            {isOnline === true ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span className="hidden xs:inline">Concierge</span> Online
              </>
            ) : isOnline === false ? (
              <>
                <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                <span className="hidden xs:inline">Service</span> Offline
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
                <span>Connecting...</span>
              </>
            )}
          </div>

          {/* Interactive DAG Diagram Page Link */}
          <a
            href="/architecture.html"
            target="_blank"
            rel="noopener noreferrer"
            title="Inspect Interactive Architecture Diagram"
            className="hidden sm:flex items-center gap-1 text-xs text-slate-400 hover:text-white px-2.5 py-1.5 rounded-xl hover:bg-slate-900 border border-transparent hover:border-slate-800 transition"
          >
            <span>Topology</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>

      </div>
    </header>
  );
};
