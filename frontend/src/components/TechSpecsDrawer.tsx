import React from 'react';
import { X, Cpu, GitFork, Server, Zap, CheckCircle2, Copy, Check, ExternalLink } from 'lucide-react';

interface TechSpecsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  llmCalls?: number;
  threadId?: string;
}

export const TechSpecsDrawer: React.FC<TechSpecsDrawerProps> = ({
  isOpen,
  onClose,
  llmCalls = 5,
  threadId,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const handleCopySpecs = async () => {
    const specs = `Roamly AI System Architecture:
• Orchestration: LangGraph StateGraph (DAG with Parallel Fan-Out / Fan-In Barrier)
• Concurrency: Concurrent async tasks for FlightAgent, HotelAgent, WeatherAgent
• State Reducers: Annotated[int, operator.add] for collision-free call counting
• MCP Architecture: Hybrid (Remote Streamable HTTP MCP via Tavily + Local Stdio FastMCP subprocess for Weather)
• Inference: Groq LPU high-speed inference (openai/gpt-oss-120b)
• Backend: FastAPI with nest_asyncio & CORS
• Frontend: React 18, TypeScript, Tailwind CSS, Vite (Decoupled Vercel + Render)`;

    try {
      await navigator.clipboard.writeText(specs);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over panel */}
      <div className="relative z-10 w-full max-w-lg bg-slate-900/95 border-l border-slate-800 p-6 sm:p-8 overflow-y-auto shadow-2xl flex flex-col justify-between">
        <div className="space-y-6">

          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <GitFork className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  System Architecture & Specs
                </h3>
                <p className="text-xs text-slate-400">
                  Engineering Blueprint & Multi-Agent Telemetry
                  {threadId && <span className="block font-mono text-[10px] text-slate-500 mt-0.5">Thread: {threadId.slice(0, 18)}</span>}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                <Cpu className="h-3.5 w-3.5 text-indigo-400" />
                <span>LLM Operations</span>
              </div>
              <div className="text-lg font-bold text-white">
                {llmCalls} <span className="text-xs text-indigo-400 font-normal">nodes executed</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                <Zap className="h-3.5 w-3.5 text-amber-400" />
                <span>Inference Engine</span>
              </div>
              <div className="text-sm font-bold text-white truncate">
                Groq GPT-OSS-120B
              </div>
            </div>
          </div>

          {/* Orchestration Topology */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              LangGraph State Topology
            </h4>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-3 font-mono text-xs">
              <div className="flex items-center gap-2 text-blue-400 font-semibold">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>START ➔ Semantic Router (router_agent)</span>
              </div>
              <div className="pl-5 text-[11px] text-slate-400 font-sans">
                Evaluates user intent & trip state into Pydantic <code className="text-blue-300 font-mono">TravelIntent</code> (Zero keyword checks)
              </div>

              <div className="flex items-center gap-2 text-emerald-400 font-semibold pt-1">
                <GitFork className="h-3.5 w-3.5" />
                <span>Parallel Research Fan-Out (Gated by Intent)</span>
              </div>

              <div className="pl-5 space-y-1.5 text-slate-300">
                <div className="flex items-center justify-between text-[11px] bg-slate-900/60 p-2 rounded border border-slate-800">
                  <span>• flight_agent</span>
                  <span className="text-blue-400 font-sans">Remote HTTP MCP (Tavily)</span>
                </div>
                <div className="flex items-center justify-between text-[11px] bg-slate-900/60 p-2 rounded border border-slate-800">
                  <span>• hotel_agent</span>
                  <span className="text-blue-400 font-sans">Remote HTTP MCP (Tavily)</span>
                </div>
                <div className="flex items-center justify-between text-[11px] bg-slate-900/60 p-2 rounded border border-slate-800">
                  <span>• weather_agent</span>
                  <span className="text-amber-400 font-sans">Local FastMCP Stdio Subprocess</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-indigo-400 font-semibold pt-1">
                <GitFork className="h-3.5 w-3.5 rotate-180" />
                <span>Fan-In Barrier: itinerary_agent</span>
              </div>

              <div className="flex items-center gap-2 text-sky-400 font-semibold">
                <Server className="h-3.5 w-3.5" />
                <span>Synthesis Node: final_agent (Structured TripPlan) ➔ END</span>
              </div>
            </div>
          </div>

          {/* Technical Highlights for Recruiters */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Senior Engineering Talking Points
            </h4>

            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                <span className="h-1.5 w-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                <span><strong>Semantic Supervisor (Zero Keyword Hacks):</strong> Replaces brittle substring matching with a Pydantic <code className="text-blue-300 font-mono">TravelIntent</code> router that classifies conversational turns and emits typed JSON directly to the UI.</span>
              </li>
              <li className="flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <span><strong>Parallel Async Fan-Out:</strong> Cuts query response latency by ~60% compared to sequential agent chains.</span>
              </li>
              <li className="flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0" />
                <span><strong>Thread-Safe Reducers:</strong> Uses <code className="text-indigo-300 font-mono">Annotated[int, operator.add]</code> in LangGraph TravelState to prevent race conditions during concurrent node execution.</span>
              </li>
              <li className="flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                <span><strong>Hybrid MCP Architecture:</strong> Demonstrates production Model Context Protocol by pairing remote cloud servers with an internal stdio FastMCP server.</span>
              </li>
              <li className="flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <span><strong>Token Truncation & 429 Handling:</strong> Pre-summarizes 8k+ search snippets to 2k tokens to respect strict Groq TPM thresholds.</span>
              </li>
            </ul>
          </div>

        </div>

        {/* Footer actions */}
        <div className="pt-6 border-t border-slate-800 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleCopySpecs}
            className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span>Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-400" />
                <span>Copy Architecture Summary</span>
              </>
            )}
          </button>

          <a
            href="/architecture.html"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 px-4 py-2.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 text-xs font-semibold text-blue-300 border border-blue-500/30 transition"
          >
            <span>Full Map</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>

      </div>
    </div>
  );
};
