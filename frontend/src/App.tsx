import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  RefreshCw,
  MapPin,
  ShieldAlert,
  Loader2,
  PlusCircle,
  ArrowLeft
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { ConciergeRadar } from './components/ConciergeRadar';
import { ResultsViewer } from './components/ResultsViewer';
import { SamplePrompts } from './components/SamplePrompts';
import { TechSpecsDrawer } from './components/TechSpecsDrawer';
import { UserQueryCard } from './components/UserQueryCard';
import { ConciergeTask, TravelSuccessResponse } from './types';
import { checkHealth, planTravel, ApiError } from './api';

const INITIAL_PLANNING_TASKS: ConciergeTask[] = [
  {
    id: 'flight_scout',
    label: 'Flights',
    sublabel: 'Searching routes, airports, and airfares',
    icon: 'flight',
    status: 'pending',
    technicalRole: 'Remote Tavily MCP',
  },
  {
    id: 'stays_curator',
    label: 'Hotels & Stays',
    sublabel: 'Finding hotels, boutique stays, and nightly rates',
    icon: 'hotel',
    status: 'pending',
    technicalRole: 'Remote Tavily MCP',
  },
  {
    id: 'climate_intel',
    label: 'Weather & Packing',
    sublabel: 'Checking weather forecast and packing essentials',
    icon: 'weather',
    status: 'pending',
    technicalRole: 'Local Stdio FastMCP',
  },
  {
    id: 'journey_architect',
    label: 'Itinerary Planner',
    sublabel: 'Building day-by-day schedules and activities',
    icon: 'itinerary',
    status: 'pending',
    technicalRole: 'LangGraph Barrier Fan-In',
  },
  {
    id: 'trip_summary',
    label: 'Trip Summary',
    sublabel: 'Organizing your travel plan and estimated budget',
    icon: 'synthesis',
    status: 'pending',
    technicalRole: 'Overview & State Reducer',
  },
];

export const App: React.FC = () => {
  const [query, setQuery] = useState('');
  const [initialQuery, setInitialQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [refinements, setRefinements] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [tasks, setTasks] = useState<ConciergeTask[]>(INITIAL_PLANNING_TASKS);
  const [results, setResults] = useState<TravelSuccessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isTechSpecsOpen, setIsTechSpecsOpen] = useState(false);

  const resultsRef = useRef<HTMLDivElement>(null);

  // When user has submitted a query or results exist, switch from centered landing to active dossier mode
  const hasStarted = isProcessing || !!results || !!error;

  // Poll backend health on initial load and every 60s
  useEffect(() => {
    let mounted = true;

    const verifyBackend = async () => {
      try {
        const health = await checkHealth();
        if (mounted) {
          setIsOnline(health.ready && health.status === 'ok');
        }
      } catch {
        if (mounted) {
          setIsOnline(false);
        }
      }
    };

    verifyBackend();
    const interval = setInterval(verifyBackend, 60000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleResetTrip = () => {
    setResults(null);
    setError(null);
    setQuery('');
    setInitialQuery('');
    setActiveQuery('');
    setRefinements([]);
    setThreadId(null);
    setTasks(INITIAL_PLANNING_TASKS);
  };

  const handlePlanTrip = async (customQuery?: string) => {
    const textToSubmit = (customQuery || query).trim();
    if (!textToSubmit || isProcessing) return;

    setError(null);
    setIsProcessing(true);
    setQuery(''); // Clear input for next prompt

    const isRefining = Boolean(initialQuery && results);

    if (!initialQuery) {
      setInitialQuery(textToSubmit);
      setActiveQuery(textToSubmit);
    } else {
      setRefinements(prev => [...prev, textToSubmit]);
      setActiveQuery(textToSubmit);
    }

    // Phase 1: Parallel scout tasks are activated concurrently
    setTasks([
      {
        ...INITIAL_PLANNING_TASKS[0],
        status: 'in_progress',
        sublabel: isRefining ? 'Evaluating flight adjustments...' : INITIAL_PLANNING_TASKS[0].sublabel
      },
      {
        ...INITIAL_PLANNING_TASKS[1],
        status: 'in_progress',
        sublabel: isRefining ? 'Checking accommodations alignment...' : INITIAL_PLANNING_TASKS[1].sublabel
      },
      {
        ...INITIAL_PLANNING_TASKS[2],
        status: 'in_progress',
        sublabel: isRefining ? 'Verifying regional climate...' : INITIAL_PLANNING_TASKS[2].sublabel
      },
      { ...INITIAL_PLANNING_TASKS[3], status: 'pending' },
      { ...INITIAL_PLANNING_TASKS[4], status: 'pending' },
    ]);

    // Timed realistic visual transitions reflecting the LangGraph fan-out / barrier fan-in
    const stageTimer1 = setTimeout(() => {
      setTasks(prev => prev.map(t =>
        ['flight_scout', 'stays_curator', 'climate_intel'].includes(t.id)
          ? { ...t, status: 'completed' }
          : t.id === 'journey_architect'
          ? {
              ...t,
              status: 'in_progress',
              sublabel: isRefining ? 'Updating day schedule with adjustments...' : t.sublabel
            }
          : t
      ));
    }, 4500);

    const stageTimer2 = setTimeout(() => {
      setTasks(prev => prev.map(t =>
        t.id === 'journey_architect'
          ? { ...t, status: 'completed' }
          : t.id === 'trip_summary'
          ? {
              ...t,
              status: 'in_progress',
              sublabel: isRefining ? 'Finalizing updated trip plan...' : t.sublabel
            }
          : t
      ));
    }, 8500);

    try {
      const response = await planTravel({
        message: textToSubmit,
        thread_id: threadId,
      });

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);

      // All concierge tasks complete
      setTasks(prev => prev.map(t => ({ ...t, status: 'completed' })));
      setResults(response);
      setThreadId(response.thread_id);

      // Smooth scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 150);

    } catch (err: unknown) {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);

      let message = 'An unexpected error occurred while creating your travel plan.';
      if (err instanceof ApiError) {
        message = err.message;
      } else if (err instanceof Error) {
        message = err.message;
      }

      setError(message);
      setTasks(prev => prev.map(t =>
        t.status === 'in_progress' ? { ...t, status: 'failed' } : t
      ));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handlePlanTrip();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-500 selection:text-white relative">

      {/* Ambient background glow accents */}
      <div className="fixed top-0 left-1/3 w-[600px] h-[400px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="fixed bottom-10 right-1/4 w-[500px] h-[400px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none" />

      {/* Navigation */}
      <Navbar
        isOnline={isOnline}
        llmCalls={results?.llm_calls}
        onOpenSpecs={() => setIsTechSpecsOpen(true)}
      />

      {/* Technical Architecture Drawer */}
      <TechSpecsDrawer
        isOpen={isTechSpecsOpen}
        onClose={() => setIsTechSpecsOpen(false)}
        llmCalls={results?.llm_calls || 5}
        threadId={threadId || undefined}
      />

      {/* Main Content Area */}
      <main className={`flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 transition-all duration-500 ${
        hasStarted ? 'py-6 sm:py-8 pb-36' : 'flex flex-col items-center justify-center min-h-[calc(100vh-5rem)] py-12'
      }`}>

        {/* ==================================================================== */}
        {/* SCENARIO A: INITIAL CENTERED HERO & INPUT (Clean, like ChatGPT/Perplexity) */}
        {/* ==================================================================== */}
        {!hasStarted ? (
          <div className="w-full max-w-3xl mx-auto space-y-8 text-center animate-in fade-in zoom-in-95 duration-500">

            {/* Hero Brand & Headline */}
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
                <Sparkles className="h-3.5 w-3.5 text-blue-400" />
                <span>AI Travel Planner</span>
              </div>

              <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
                Where will your curiosity <br className="hidden sm:inline" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-sky-400">
                  take you next?
                </span>
              </h1>

              <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                Describe where you want to go in plain English. We search real-time flights, hotels, weather, and create your complete travel plan.
              </p>
            </div>

            {/* Centered Input Box */}
            <div className="w-full">
              <form
                onSubmit={(e) => { e.preventDefault(); handlePlanTrip(); }}
                className="rounded-3xl p-3 sm:p-4 bg-slate-900/90 border border-slate-800 shadow-2xl relative focus-within:border-blue-500/60 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all backdrop-blur-xl text-left"
              >
                <div className="relative">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isProcessing}
                    rows={3}
                    placeholder="Where do you want to go? e.g., Plan a 7-day trip to Tokyo and Kyoto in late October for 2 people, mid-range budget, interested in food, shrines, and scenic rail trips..."
                    className="w-full bg-transparent text-sm sm:text-base text-slate-100 placeholder:text-slate-500 focus:outline-none resize-none pr-12 leading-relaxed"
                  />
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 mt-2">
                  <div className="flex items-center gap-2 text-xs text-slate-500 hidden sm:flex">
                    <MapPin className="h-3.5 w-3.5 text-slate-400" />
                    <span>Press <kbd className="px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400">Enter</kbd> to plan</span>
                  </div>

                  <button
                    type="submit"
                    disabled={!query.trim() || isProcessing}
                    className="ml-auto inline-flex items-center gap-2 px-6 py-2.5 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-bold shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Planning Trip...</span>
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        <span>Plan Trip</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Sample Prompts */}
              <div className="mt-6 text-left">
                <SamplePrompts
                  onSelectPrompt={(selected) => handlePlanTrip(selected)}
                  disabled={isProcessing}
                />
              </div>
            </div>

          </div>
        ) : (
          /* ==================================================================== */
          /* SCENARIO B: ACTIVE DOSSIER STATE (Results & Live Radar take center stage) */
          /* ==================================================================== */
          <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-300">

            {/* Top Toolbar: Plan Another Trip / New Search */}
            <div className="flex items-center justify-between gap-4 pb-1">
              <button
                type="button"
                onClick={handleResetTrip}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-900/90 hover:bg-slate-850 text-xs font-semibold text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 transition shadow-sm"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Plan Another Trip</span>
              </button>

              <button
                type="button"
                onClick={handleResetTrip}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-2xl bg-slate-900/90 hover:bg-slate-850 text-xs font-semibold text-blue-400 hover:text-blue-300 border border-slate-800 hover:border-slate-700 transition"
              >
                <PlusCircle className="h-3.5 w-3.5" />
                <span>New Search</span>
              </button>
            </div>

            {/* Prominent User Prompt & Refinement History Card */}
            <UserQueryCard
              initialQuery={initialQuery || activeQuery}
              refinements={refinements}
            />

            {/* Error Alert Card */}
            {error && (
              <div className="max-w-4xl mx-auto w-full p-5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3 shadow-lg">
                <ShieldAlert className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 text-xs sm:text-sm">
                  <div className="font-semibold text-rose-200 mb-0.5">Planning Request Interrupted</div>
                  <p className="text-rose-300/90 leading-relaxed">{error}</p>
                  <button
                    type="button"
                    onClick={() => handlePlanTrip(activeQuery)}
                    className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-xs font-semibold text-rose-200 border border-rose-500/30 transition"
                  >
                    <RefreshCw className="h-3 w-3" />
                    <span>Retry Request</span>
                  </button>
                </div>
              </div>
            )}

            {/* Live Concierge Radar */}
            <div className="max-w-5xl mx-auto w-full">
              <ConciergeRadar
                tasks={tasks}
                isProcessing={isProcessing}
                onOpenSpecs={() => setIsTechSpecsOpen(true)}
              />
            </div>

            {/* Results Section */}
            {results && (
              <div ref={resultsRef} className="max-w-5xl mx-auto w-full pt-2">
                <ResultsViewer
                  data={results}
                  query={activeQuery}
                  baseQuery={initialQuery}
                  onOpenSpecs={() => setIsTechSpecsOpen(true)}
                />
              </div>
            )}

          </div>
        )}

      </main>

      {/* ==================================================================== */}
      {/* FLOATING BOTTOM CHAT DOCK (Always available when results are active) */}
      {/* ==================================================================== */}
      {hasStarted && (
        <div className="fixed bottom-4 sm:bottom-6 left-1/2 -translate-x-1/2 w-full max-w-3xl px-4 z-40 animate-in slide-in-from-bottom-6 duration-300">
          <form
            onSubmit={(e) => { e.preventDefault(); handlePlanTrip(); }}
            className="flex items-center gap-2 p-2 sm:p-2.5 rounded-2xl bg-slate-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-2xl ring-1 ring-white/10"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isProcessing}
              placeholder={isProcessing ? "Searching live travel information..." : "Ask an update... e.g. 'Add a day trip to Hakone on Day 4' or 'Switch to boutique stays under ₹15,000'"}
              className="flex-1 bg-transparent px-3 py-1.5 text-xs sm:text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
            />

            <button
              type="submit"
              disabled={!query.trim() || isProcessing}
              className="flex-shrink-0 inline-flex items-center justify-center p-2.5 sm:px-4 sm:py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              {isProcessing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Send className="h-4 w-4 sm:mr-1.5" />
                  <span className="hidden sm:inline">Refine</span>
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* Footer */}
      {!hasStarted && (
        <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-1.5">
            <div className="flex items-center justify-center gap-4 text-xs font-medium text-slate-400">
              <span>Roamly AI</span>
              <span>•</span>
              <button
                type="button"
                onClick={() => setIsTechSpecsOpen(true)}
                className="text-blue-400 hover:text-blue-300 transition"
              >
                System Specs & Architecture
              </button>
              <span>•</span>
              <a
                href="/architecture.html"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition"
              >
                DAG Topology
              </a>
            </div>
            <p className="text-[11px] text-slate-600">
              LangGraph StateGraph • FastMCP • Groq LPU High-Speed Inference
            </p>
          </div>
        </footer>
      )}

    </div>
  );
};

export default App;
