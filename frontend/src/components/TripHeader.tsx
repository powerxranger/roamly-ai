import React, { useState } from 'react';
import {
  Clock,
  IndianRupee,
  CloudSun,
  Copy,
  Check,
  Download,
  Sparkles,
  GitFork
} from 'lucide-react';
import { ParsedTripPlan, TravelSuccessResponse } from '../types';

interface TripHeaderProps {
  plan: ParsedTripPlan;
  rawResponse: TravelSuccessResponse;
  onOpenSpecs: () => void;
}

export const TripHeader: React.FC<TripHeaderProps> = ({
  plan,
  rawResponse,
  onOpenSpecs,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const fullText = `# Travel Plan: ${plan.destinationTitle}\n\n` +
      `**Duration**: ${plan.durationLabel}\n` +
      (plan.estimatedBudget ? `**Estimated Budget**: ${plan.estimatedBudget}\n\n` : '\n') +
      `## Overview\n${rawResponse.answer}\n\n` +
      `## Day-by-Day Itinerary\n${rawResponse.itinerary}\n\n` +
      `## Flights\n${rawResponse.flight_results}\n\n` +
      `## Accommodations\n${rawResponse.hotel_results}\n\n` +
      `## Weather & Advice\n${rawResponse.weather_results}\n\n` +
      `---\nCurated by Roamly AI`;

    try {
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  const handleDownload = () => {
    const fullText = `# Travel Plan: ${plan.destinationTitle}\n\n` +
      `**Duration**: ${plan.durationLabel}\n` +
      (plan.estimatedBudget ? `**Estimated Budget**: ${plan.estimatedBudget}\n\n` : '\n') +
      `## Overview\n${rawResponse.answer}\n\n` +
      `## Day-by-Day Itinerary\n${rawResponse.itinerary}\n\n` +
      `## Flights\n${rawResponse.flight_results}\n\n` +
      `## Accommodations\n${rawResponse.hotel_results}\n\n` +
      `## Weather & Advice\n${rawResponse.weather_results}\n\n` +
      `---\nCurated by Roamly AI`;

    const blob = new Blob([fullText], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `roamly-${plan.destinationTitle.toLowerCase().replace(/[^a-z0-9]/g, '-')}-plan.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900/90 via-slate-900/80 to-slate-950/90 border border-slate-800 p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
      {/* Subtle ambient gradient */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">

        {/* Left: Destination Info & Summary */}
        <div className="space-y-3 max-w-2xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Curated Travel Blueprint</span>
            </span>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs text-slate-400 font-mono">
              Thread {rawResponse.thread_id.slice(0, 10)}
            </span>
          </div>

          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white font-sans">
            {plan.destinationTitle}
          </h2>

          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            {plan.overviewSummary}
          </p>

          {/* Key Stat Pills */}
          <div className="flex flex-wrap items-center gap-2.5 pt-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200">
              <Clock className="h-3.5 w-3.5 text-blue-400" />
              <span>{plan.durationLabel}</span>
            </div>

            {plan.estimatedBudget && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-emerald-300">
                <IndianRupee className="h-3.5 w-3.5 text-emerald-400" />
                <span>{plan.estimatedBudget}</span>
              </div>
            )}

            {plan.weather.temperature && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-amber-300">
                <CloudSun className="h-3.5 w-3.5 text-amber-400" />
                <span>{plan.weather.temperature}</span>
              </div>
            )}

            <button
              type="button"
              onClick={onOpenSpecs}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-xs font-medium text-indigo-300 transition"
              title="Inspect multi-agent LangGraph execution"
            >
              <GitFork className="h-3.5 w-3.5 text-indigo-400" />
              <span>System Specs ({rawResponse.llm_calls} nodes)</span>
            </button>
          </div>
        </div>

        {/* Right: Quick Actions */}
        <div className="flex flex-row lg:flex-col items-center lg:items-end gap-2.5 self-start">
          <button
            type="button"
            onClick={handleCopy}
            className="flex-1 lg:flex-none flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition border border-slate-700 shadow-md"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-300">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-400" />
                <span>Copy Dossier</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleDownload}
            className="flex-1 lg:flex-none flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-950 hover:bg-slate-900 text-xs font-semibold text-slate-300 hover:text-white transition border border-slate-800"
          >
            <Download className="h-3.5 w-3.5 text-slate-400" />
            <span>Export .md</span>
          </button>
        </div>

      </div>
    </div>
  );
};
