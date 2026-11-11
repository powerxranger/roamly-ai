import React from 'react';
import { Sparkles, GitFork } from 'lucide-react';
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
}

export const AssistantMessageCard: React.FC<AssistantMessageCardProps> = ({
  content,
  data,
  query,
  baseQuery,
  timestamp,
  onOpenSpecs,
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
                ? 'Fast Advisor (1-Hop)'
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
        />
      ) : (
        <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-7 shadow-2xl">
          <MarkdownRenderer content={content} />
        </div>
      )}
    </div>
  );
};
