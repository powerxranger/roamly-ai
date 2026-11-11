import React from 'react';
import { Sparkles, GitFork, ArrowRight } from 'lucide-react';
import { TravelSuccessResponse } from '../types';
import { ResultsViewer } from './ResultsViewer';
import { MarkdownRenderer } from './MarkdownRenderer';

interface AssistantMessageCardProps {
  content: string;
  data?: TravelSuccessResponse;
  query: string;
  baseQuery: string;
  timestamp: Date;
  onOpenSpecs: () => void;
  onSelectPrompt?: (prompt: string) => void;
}

export const AssistantMessageCard: React.FC<AssistantMessageCardProps> = ({
  content,
  data,
  query,
  baseQuery,
  timestamp,
  onOpenSpecs,
  onSelectPrompt,
}) => {
  const formattedTime = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="w-full space-y-4">
      {/* Assistant Header Badge */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-sm">
            <Sparkles className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-bold text-white">Roamly AI</span>
          <span className="text-xs text-slate-600">•</span>
          <span className="text-[11px] text-slate-500 font-mono">{formattedTime}</span>
        </div>

        {data && (
          <button
            type="button"
            onClick={onOpenSpecs}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-300 hover:text-white transition"
            title="Inspect Execution DAG and System Specs"
          >
            <GitFork className="h-3 w-3 text-indigo-400" />
            <span>
              {data.response_type === 'conversation'
                ? data.llm_calls <= 1
                  ? 'Guardrail Filter (Direct)'
                  : 'Fast Advisor (1-Hop)'
                : `${data.llm_calls} nodes executed`}
            </span>
          </button>
        )}
      </div>

      {/* Structured Results or Conversational Markdown Response */}
      {data && data.response_type !== 'conversation' && data.plan ? (
        <ResultsViewer
          data={data}
          query={query}
          baseQuery={baseQuery}
          onSelectPrompt={onSelectPrompt}
        />
      ) : (
        <div className="space-y-3">
          <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-7 shadow-2xl">
            <MarkdownRenderer content={content} />
          </div>

          {data?.followup_suggestions && data.followup_suggestions.length > 0 && (
            <div className="p-4 sm:p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-lg space-y-2.5">
              <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-blue-400">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Suggested Follow-ups</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-0.5">
                {data.followup_suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onSelectPrompt?.(suggestion)}
                    className="text-left px-3.5 py-2 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 hover:border-blue-500/40 text-xs font-medium text-blue-200 hover:text-white transition-all flex items-center gap-2 group cursor-pointer"
                  >
                    <span>{suggestion}</span>
                    <ArrowRight className="h-3 w-3 text-blue-400 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
