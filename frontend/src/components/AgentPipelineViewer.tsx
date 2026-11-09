import React from 'react';
import { Plane, Hotel, CloudSun, Calendar, Sparkles, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { AgentProgress } from '../types';

interface AgentPipelineViewerProps {
  agents: AgentProgress[];
  isProcessing: boolean;
}

export const AgentPipelineViewer: React.FC<AgentPipelineViewerProps> = ({ agents, isProcessing }) => {
  const parallelAgents = agents.filter(a => a.category === 'parallel');
  const sequentialAgents = agents.filter(a => a.category === 'sequential');

  const getIcon = (id: string) => {
    switch (id) {
      case 'flight_agent':
        return <Plane className="h-4 w-4" />;
      case 'hotel_agent':
        return <Hotel className="h-4 w-4" />;
      case 'weather_agent':
        return <CloudSun className="h-4 w-4" />;
      case 'itinerary_agent':
        return <Calendar className="h-4 w-4" />;
      case 'final_agent':
        return <Sparkles className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: AgentProgress['status']) => {
    switch (status) {
      case 'running':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full border border-blue-500/30">
            <Loader2 className="h-3 w-3 animate-spin" />
            Active
          </span>
        );
      case 'completed':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
            <CheckCircle2 className="h-3 w-3" />
            Done
          </span>
        );
      case 'failed':
        return (
          <span className="text-[11px] font-medium text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/30">
            Failed
          </span>
        );
      default:
        return (
          <span className="text-[11px] font-medium text-slate-500 bg-slate-800/40 px-2 py-0.5 rounded-full border border-slate-700/50">
            Queued
          </span>
        );
    }
  };

  return (
    <div className="w-full glass-card rounded-2xl p-4 sm:p-5 border border-slate-800/90 shadow-xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              LangGraph Multi-Agent Orchestration
            </h3>
            {isProcessing && (
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Concurrent Fan-Out (Flights, Hotels, Weather) → Barrier Fan-In (Itinerary) → Synthesis (Final)
          </p>
        </div>

        <div className="text-xs text-slate-400 flex items-center gap-2">
          <span className="inline-block px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px]">
            Hybrid MCP: HTTP + FastMCP
          </span>
        </div>
      </div>

      {/* Grid Layout representing the LangGraph topology */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">

        {/* Step 1: Parallel Fan-Out (3 concurrent agents) */}
        <div className="lg:col-span-6 flex flex-col gap-2">
          <div className="flex items-center justify-between text-[11px] font-semibold text-blue-400 uppercase tracking-wider px-1">
            <span>Phase 1 • Parallel Fan-Out</span>
            <span className="text-slate-500">Async / Concurrent</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-2">
            {parallelAgents.map((agent) => {
              const isRunning = agent.status === 'running';
              const isDone = agent.status === 'completed';

              return (
                <div
                  key={agent.id}
                  className={`flex items-center justify-between p-3 rounded-xl border transition-all duration-300 ${
                    isRunning
                      ? 'bg-blue-950/30 border-blue-500/50 shadow-lg shadow-blue-500/10'
                      : isDone
                      ? 'bg-slate-900/60 border-emerald-500/30'
                      : 'bg-slate-900/40 border-slate-800/60 opacity-60'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div
                      className={`p-2 rounded-lg ${
                        isRunning
                          ? 'bg-blue-600/20 text-blue-400'
                          : isDone
                          ? 'bg-emerald-600/20 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {getIcon(agent.id)}
                    </div>
                    <div className="truncate">
                      <div className="text-xs font-semibold text-slate-200 truncate">
                        {agent.label}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">
                        {agent.role}
                      </div>
                    </div>
                  </div>

                  <div className="ml-2 flex-shrink-0">
                    {getStatusBadge(agent.status)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Arrow connector */}
        <div className="hidden lg:flex lg:col-span-1 justify-center text-slate-600">
          <ArrowRight className="h-5 w-5" />
        </div>

        {/* Step 2: Sequential Pipeline (Barrier Fan-In & Final Synthesis) */}
        <div className="lg:col-span-5 flex flex-col gap-2">
          <div className="flex items-center justify-between text-[11px] font-semibold text-indigo-400 uppercase tracking-wider px-1">
            <span>Phase 2 • Barrier Fan-In & Synthesis</span>
            <span className="text-slate-500">Synchronized</span>
          </div>

          <div className="flex flex-col gap-2">
            {sequentialAgents.map((agent) => {
              const isRunning = agent.status === 'running';
              const isDone = agent.status === 'completed';

              return (
                <div
                  key={agent.id}
                  className={`flex items-center justify-between p-3 rounded-xl border transition-all duration-300 ${
                    isRunning
                      ? 'bg-indigo-950/30 border-indigo-500/50 shadow-lg shadow-indigo-500/10'
                      : isDone
                      ? 'bg-slate-900/60 border-emerald-500/30'
                      : 'bg-slate-900/40 border-slate-800/60 opacity-60'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div
                      className={`p-2 rounded-lg ${
                        isRunning
                          ? 'bg-indigo-600/20 text-indigo-400'
                          : isDone
                          ? 'bg-emerald-600/20 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {getIcon(agent.id)}
                    </div>
                    <div className="truncate">
                      <div className="text-xs font-semibold text-slate-200 truncate">
                        {agent.label}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">
                        {agent.role}
                      </div>
                    </div>
                  </div>

                  <div className="ml-2 flex-shrink-0">
                    {getStatusBadge(agent.status)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
};
