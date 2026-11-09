import React, { useState } from 'react';
import {
  Sparkles,
  Calendar,
  Plane,
  Hotel,
  CloudSun,
  FileText,
  ArrowRight
} from 'lucide-react';
import { ActiveTab, TravelSuccessResponse } from '../types';
import { parseTripResponse } from '../utils/parser';
import { TripHeader } from './TripHeader';
import { FlightBoard } from './FlightBoard';
import { HotelDeck } from './HotelDeck';
import { DailyTimeline } from './DailyTimeline';
import { WeatherWidget } from './WeatherWidget';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ResultsViewerProps {
  data: TravelSuccessResponse;
  query: string;
  onOpenSpecs: () => void;
}

export const ResultsViewer: React.FC<ResultsViewerProps> = ({ data, query, onOpenSpecs }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');

  // Parse structured data from raw LLM responses
  const parsedPlan = React.useMemo(() => parseTripResponse(query, data), [query, data]);

  const tabs: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'overview',
      label: 'Trip Overview',
      icon: <Sparkles className="h-4 w-4" />,
    },
    {
      id: 'itinerary',
      label: 'Day-by-Day',
      icon: <Calendar className="h-4 w-4" />,
    },
    {
      id: 'flights',
      label: 'Flights',
      icon: <Plane className="h-4 w-4" />,
    },
    {
      id: 'hotels',
      label: 'Stays',
      icon: <Hotel className="h-4 w-4" />,
    },
    {
      id: 'weather',
      label: 'Climate & Packing',
      icon: <CloudSun className="h-4 w-4" />,
    },
    {
      id: 'dossier',
      label: 'Full Dossier',
      icon: <FileText className="h-4 w-4" />,
    },
  ];

  return (
    <div className="w-full space-y-6">
      {/* 1. Magazine-Style Trip Header */}
      <TripHeader
        plan={parsedPlan}
        rawResponse={data}
        onOpenSpecs={onOpenSpecs}
      />

      {/* 2. Visual Navigation Tabs */}
      <div className="bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800/80 backdrop-blur-xl overflow-x-auto scrollbar-none">
        <nav className="flex space-x-1.5 min-w-max">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 border border-blue-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* 3. Visual Content Panels */}
      <div className="transition-all duration-300">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Quick Glimpse Cards: Itinerary highlight + Flight highlight + Stays highlight */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

              {/* Daily Schedule Preview */}
              <div
                onClick={() => setActiveTab('itinerary')}
                className="cursor-pointer group p-5 rounded-3xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-blue-400 font-bold uppercase tracking-wider mb-2">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>Itinerary</span>
                    </span>
                    <span className="text-slate-500 font-normal">{parsedPlan.durationLabel}</span>
                  </div>
                  <h4 className="text-base font-bold text-white group-hover:text-blue-300 transition-colors">
                    {parsedPlan.itineraryDays[0]?.title || 'Daily Schedule'}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                    {parsedPlan.itineraryDays[0]?.morning || parsedPlan.itineraryDays[0]?.rawText.slice(0, 120) || 'Custom day-by-day exploration.'}
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-blue-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                  <span>Explore All Days</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>

              {/* Flights Preview */}
              <div
                onClick={() => setActiveTab('flights')}
                className="cursor-pointer group p-5 rounded-3xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-blue-400 font-bold uppercase tracking-wider mb-2">
                    <span className="flex items-center gap-1.5">
                      <Plane className="h-3.5 w-3.5" />
                      <span>Flights</span>
                    </span>
                    {parsedPlan.flights.fareRange && (
                      <span className="text-emerald-400 font-semibold">{parsedPlan.flights.fareRange}</span>
                    )}
                  </div>
                  <h4 className="text-base font-bold text-white group-hover:text-blue-300 transition-colors">
                    {parsedPlan.flights.duration || 'Optimal Flight Routes'}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                    {parsedPlan.flights.airlines?.join(', ') || parsedPlan.flights.seasonTips || 'Scouted route intelligence.'}
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-blue-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                  <span>View Boarding Pass</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>

              {/* Accommodations Preview */}
              <div
                onClick={() => setActiveTab('hotels')}
                className="cursor-pointer group p-5 rounded-3xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-purple-400 font-bold uppercase tracking-wider mb-2">
                    <span className="flex items-center gap-1.5">
                      <Hotel className="h-3.5 w-3.5" />
                      <span>Stays</span>
                    </span>
                    <span className="text-slate-500 font-normal">{parsedPlan.hotels.length} Curated</span>
                  </div>
                  <h4 className="text-base font-bold text-white group-hover:text-purple-300 transition-colors">
                    {parsedPlan.hotels[0]?.name || 'Luxury & Boutique Stays'}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                    {parsedPlan.hotels[0]?.location || parsedPlan.hotels[0]?.description.slice(0, 120) || 'Handpicked sanctuaries.'}
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-purple-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                  <span>Browse Accommodations</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>

            </div>

            {/* Recommendations & Tips */}
            {parsedPlan.recommendations && parsedPlan.recommendations.length > 0 && (
              <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-400">
                  <Sparkles className="h-4 w-4" />
                  <span>Concierge Insider Recommendations</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {parsedPlan.recommendations.map((rec, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed flex items-start gap-2.5"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'itinerary' && (
          <DailyTimeline
            days={parsedPlan.itineraryDays}
            rawText={data.itinerary}
          />
        )}

        {activeTab === 'flights' && (
          <FlightBoard
            flights={parsedPlan.flights}
            destination={parsedPlan.destinationTitle}
          />
        )}

        {activeTab === 'hotels' && (
          <HotelDeck
            hotels={parsedPlan.hotels}
            rawText={data.hotel_results}
          />
        )}

        {activeTab === 'weather' && (
          <WeatherWidget
            weather={parsedPlan.weather}
            destination={parsedPlan.destinationTitle}
          />
        )}

        {activeTab === 'dossier' && (
          <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl">
            <div className="pb-4 mb-4 border-b border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Complete Synthesized Markdown Dossier
              </span>
              <button
                type="button"
                onClick={onOpenSpecs}
                className="text-xs text-blue-400 hover:text-blue-300 font-medium"
              >
                Inspect Execution DAG
              </button>
            </div>
            <MarkdownRenderer content={data.answer} />
          </div>
        )}
      </div>
    </div>
  );
};
