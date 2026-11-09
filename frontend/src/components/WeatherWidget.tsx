import React, { useState } from 'react';
import {
  CloudSun,
  CheckSquare,
  Square,
  Compass,
  Briefcase,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ParsedWeatherInfo } from '../types';

interface WeatherWidgetProps {
  weather: ParsedWeatherInfo;
  destination: string;
}

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ weather, destination }) => {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});
  const [showRaw, setShowRaw] = useState(false);

  const toggleItem = (idx: number) => {
    setCheckedItems(prev => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const completedCount = Object.values(checkedItems).filter(Boolean).length;
  const totalCount = weather.packingList.length;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
            Climate & Preparation
          </span>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Weather Forecast & Packing Checklist
          </h3>
        </div>

        <button
          type="button"
          onClick={() => setShowRaw(!showRaw)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800"
        >
          <span>{showRaw ? 'Hide Raw Weather' : 'View Full Climate Data'}</span>
          {showRaw ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Main Grid: Climate Banner + Interactive Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Left: Climate Overview */}
        <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-6 border-b border-slate-800/80">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                  <CloudSun className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="text-lg font-bold text-white tracking-tight">
                    Seasonal Climate Outlook
                  </h4>
                  <p className="text-xs text-slate-400">
                    Live meteorological analysis for {destination}
                  </p>
                </div>
              </div>

              {weather.temperature && (
                <div className="px-3.5 py-1.5 rounded-2xl bg-slate-950 border border-slate-800 text-right">
                  <div className="text-[10px] uppercase font-bold text-slate-500">
                    Expected Temp
                  </div>
                  <div className="text-base font-bold text-amber-300">
                    {weather.temperature}
                  </div>
                </div>
              )}
            </div>

            {/* Current Conditions / Summary */}
            <div className="space-y-4 py-6">
              {weather.currentConditions && (
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80">
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                    Current Atmospheric Conditions
                  </div>
                  <p className="text-sm text-slate-200">
                    {weather.currentConditions}
                  </p>
                </div>
              )}

              {weather.forecastSummary && (
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80">
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                    Travel Window Guidance
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {weather.forecastSummary}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/60 text-xs text-slate-400 flex items-center gap-2">
            <Compass className="h-4 w-4 text-blue-400" />
            <span>FastMCP weather stream connected via Open-Meteo & Tavily</span>
          </div>
        </div>

        {/* Right: Interactive Packing Checklist */}
        <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-6 border-b border-slate-800/80">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                  <Briefcase className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="text-lg font-bold text-white tracking-tight">
                    Smart Packing Checklist
                  </h4>
                  <p className="text-xs text-slate-400">
                    Click items to track packed essentials
                  </p>
                </div>
              </div>

              <div className="text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-950 text-blue-300 border border-slate-800">
                {completedCount}/{totalCount} Packed
              </div>
            </div>

            {/* Checklist items */}
            <div className="space-y-2.5 py-6">
              {weather.packingList.map((item, idx) => {
                const isChecked = !!checkedItems[idx];
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => toggleItem(idx)}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 flex items-center justify-between gap-3 ${
                      isChecked
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200 line-through opacity-80'
                        : 'bg-slate-950/60 hover:bg-slate-950 border-slate-800/80 text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <span className="text-xs sm:text-sm font-medium">
                      {item}
                    </span>
                    <div className="flex-shrink-0 text-slate-400">
                      {isChecked ? (
                        <CheckSquare className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <Square className="h-4 w-4 text-slate-600" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/60 text-xs text-slate-400">
            Tailored dynamically to regional climate forecasts.
          </div>
        </div>

      </div>

      {/* Raw Weather Collapsible */}
      {showRaw && weather.rawText && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2 whitespace-pre-line leading-relaxed font-mono">
          {weather.rawText}
        </div>
      )}
    </div>
  );
};
