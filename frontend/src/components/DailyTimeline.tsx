import React, { useState } from 'react';
import {
  Sun,
  Sunrise,
  Moon,
  Calendar,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ParsedItineraryDay } from '../types';

interface DailyTimelineProps {
  days: ParsedItineraryDay[];
  rawText?: string;
}

export const DailyTimeline: React.FC<DailyTimelineProps> = ({ days, rawText }) => {
  const [selectedDay, setSelectedDay] = useState<number>(days[0]?.dayNumber || 1);
  const [showRaw, setShowRaw] = useState(false);

  const activeDayData = days.find(d => d.dayNumber === selectedDay) || days[0];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
            Day-by-Day Journey
          </span>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Daily Itinerary
          </h3>
        </div>

        <button
          type="button"
          onClick={() => setShowRaw(!showRaw)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800"
        >
          <span>{showRaw ? 'Hide Raw Schedule' : 'View Full Schedule'}</span>
          {showRaw ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Day Selector Pills */}
      {days.length > 1 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {days.map((day) => {
            const isSelected = day.dayNumber === selectedDay;
            return (
              <button
                key={day.dayNumber}
                type="button"
                onClick={() => setSelectedDay(day.dayNumber)}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-200 ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 border border-blue-500'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Calendar className="h-3.5 w-3.5" />
                <span>Day {day.dayNumber}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Active Day Detail Card */}
      {activeDayData && (
        <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          {/* Subtle glow */}
          <div className="absolute top-0 right-1/4 w-72 h-72 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

          {/* Day Title & Highlights */}
          <div className="pb-6 border-b border-slate-800/80">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
              <span>Day {activeDayData.dayNumber} Schedule</span>
            </div>
            <h4 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              {activeDayData.title}
            </h4>

            {activeDayData.highlights && activeDayData.highlights.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {activeDayData.highlights.map((h, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 font-medium"
                  >
                    <Sparkles className="h-3 w-3 text-blue-400" />
                    <span>{h}</span>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Time Block Cards: Morning, Afternoon, Evening */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">

            {/* Morning */}
            {activeDayData.morning && (
              <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <Sunrise className="h-4 w-4" />
                    <span>Morning</span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {activeDayData.morning}
                  </p>
                </div>
              </div>
            )}

            {/* Afternoon */}
            {activeDayData.afternoon && (
              <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-sky-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <Sun className="h-4 w-4" />
                    <span>Afternoon</span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {activeDayData.afternoon}
                  </p>
                </div>
              </div>
            )}

            {/* Evening */}
            {activeDayData.evening && (
              <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <Moon className="h-4 w-4" />
                    <span>Evening & Dinner</span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {activeDayData.evening}
                  </p>
                </div>
              </div>
            )}

          </div>

          {/* Day Text fallback if morning/afternoon split was brief */}
          {(!activeDayData.morning && !activeDayData.afternoon) && (
            <div className="mt-6 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 leading-relaxed whitespace-pre-line font-sans">
              {activeDayData.rawText}
            </div>
          )}
        </div>
      )}

      {/* Raw Itinerary Collapsible */}
      {showRaw && rawText && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2 whitespace-pre-line leading-relaxed font-mono">
          {rawText}
        </div>
      )}
    </div>
  );
};
