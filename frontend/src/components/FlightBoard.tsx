import React, { useState } from 'react';
import { Plane, Clock, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { ParsedFlightInfo } from '../types';

interface FlightBoardProps {
  flights: ParsedFlightInfo;
  destination: string;
}

export const FlightBoard: React.FC<FlightBoardProps> = ({ flights, destination }) => {
  const [showRaw, setShowRaw] = useState(false);

  return (
    <div className="space-y-6">
      {/* Boarding-Pass Styled Card */}
      <div className="relative rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 p-6 sm:p-8 shadow-2xl overflow-hidden">
        {/* Decorative corner glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Plane className="h-6 w-6" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
                Flight Details
              </span>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Recommended Flight Path & Options
              </h3>
            </div>
          </div>

          {flights.fareRange && (
            <div className="px-4 py-2 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-right">
              <div className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold">
                Est. Roundtrip Airfare
              </div>
              <div className="text-lg font-bold text-emerald-300">
                {flights.fareRange}
              </div>
            </div>
          )}
        </div>

        {/* Flight Route Visual Banner */}
        <div className="py-6 my-2 flex flex-col md:flex-row items-center justify-between gap-6 bg-slate-950/60 rounded-2xl p-6 border border-slate-800/80">
          {/* Origin */}
          <div className="text-center md:text-left">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
              Origin
            </div>
            <div className="text-2xl font-black text-white tracking-tight mt-0.5">
              {flights.origin || 'Departure Hub'}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              {flights.origin ? 'Departure Gateway' : 'Origin Location'}
            </div>
          </div>

          {/* Flight Path Graphic */}
          <div className="flex-1 flex flex-col items-center px-4 w-full md:w-auto">
            {flights.duration && (
              <div className="flex items-center justify-center gap-2 text-xs font-medium text-slate-400 mb-2">
                <Clock className="h-3.5 w-3.5 text-blue-400" />
                <span>{flights.duration}</span>
              </div>
            )}

            <div className="w-full flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-blue-500" />
              <div className="flex-1 relative flex items-center">
                <div className="w-full border-t-2 border-dashed border-slate-700" />
                <Plane className="absolute left-1/2 -translate-x-1/2 h-4 w-4 text-blue-400 transform rotate-90" />
              </div>
              <div className="h-2 w-2 rounded-full bg-emerald-400" />
            </div>
          </div>

          {/* Destination */}
          <div className="text-center md:text-right">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
              Destination
            </div>
            <div className="text-2xl font-black text-white tracking-tight mt-0.5">
              {destination}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Arrival Gateways
            </div>
          </div>
        </div>

        {/* Airports & Carriers Chips */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
          {flights.airlines && flights.airlines.length > 0 && (
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Recommended Carriers
              </div>
              <div className="flex flex-wrap gap-2">
                {flights.airlines.map((airline, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-700/60 text-xs font-medium text-slate-200"
                  >
                    {airline}
                  </span>
                ))}
              </div>
            </div>
          )}

          {flights.airports && flights.airports.length > 0 && (
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Key Airports & Gateways
              </div>
              <div className="flex flex-wrap gap-2">
                {flights.airports.map((airport, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-700/60 text-xs font-medium text-slate-200"
                  >
                    {airport}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Season & Booking Advisory */}
        {flights.seasonTips && (
          <div className="mt-4 p-4 rounded-2xl bg-blue-500/5 border border-blue-500/20 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300 leading-relaxed">
              <strong className="text-blue-300 font-semibold">Booking Advisory: </strong>
              {flights.seasonTips}
            </div>
          </div>
        )}

        {/* Boarding Pass Barcode Simulation */}
        <div className="mt-6 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-xs font-mono">
          <div className="flex items-center gap-1 tracking-widest text-[10px] opacity-70">
            ||||| | |||| || |||||| | ||||| ||| ||||||| | || ||||
          </div>
          <button
            type="button"
            onClick={() => setShowRaw(!showRaw)}
            className="flex items-center gap-1 text-slate-400 hover:text-white transition font-sans text-xs"
          >
            <span>{showRaw ? 'Hide Raw Flight Notes' : 'View Full Scout Notes'}</span>
            {showRaw ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
        </div>

      </div>

      {/* Raw Notes Drawer/Collapsible */}
      {showRaw && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2 whitespace-pre-line leading-relaxed font-mono">
          {flights.rawText}
        </div>
      )}
    </div>
  );
};
