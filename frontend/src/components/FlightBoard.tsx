import React, { useState } from 'react';
import {
  Plane,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Car,
  Train,
  Route,
  Compass
} from 'lucide-react';
import { ParsedFlightInfo } from '../types';

interface FlightBoardProps {
  flights: ParsedFlightInfo;
  destination: string;
}

export const FlightBoard: React.FC<FlightBoardProps> = ({ flights, destination }) => {
  const [showRaw, setShowRaw] = useState(false);
  const isMultiModal = Boolean(flights.originToAirportTransit || flights.airportToDestinationTransit);
  const hasAlternatives = Boolean(flights.trainOption || flights.roadOption);

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
              {flights.primaryMode === 'Train' ? (
                <Train className="h-6 w-6" />
              ) : flights.primaryMode === 'Road / Drive' || flights.primaryMode === 'Road' ? (
                <Car className="h-6 w-6" />
              ) : (
                <Plane className="h-6 w-6" />
              )}
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
                {flights.routeType || 'Transit Details'}
              </span>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Recommended Transit Path & Options
              </h3>
            </div>
          </div>

          {(flights.fareRange || flights.trainOption?.fareRange) && (
            <div className="px-4 py-2 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-right">
              <div className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold">
                {flights.primaryMode === 'Train' ? 'Est. Train Fare' : (flights.primaryMode === 'Road / Drive' ? 'Est. Road Cost' : 'Est. Roundtrip Airfare')}
              </div>
              <div className="text-lg font-bold text-emerald-300">
                {flights.primaryMode === 'Train'
                  ? (flights.trainOption?.fareRange || flights.fareRange)
                  : (flights.fareRange || flights.roadOption?.fareRange)}
              </div>
            </div>
          )}
        </div>

        {/* Recommended Travel Mode Callout (when advice is present) */}
        {(flights.primaryMode || flights.modeRecommendation) && (
          <div className="mt-6 p-5 rounded-2xl bg-gradient-to-r from-blue-950/60 via-indigo-950/40 to-slate-900 border border-blue-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2.5 rounded-xl bg-blue-500/20 text-blue-300 mt-0.5">
                <Compass className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    Recommended Travel Medium
                  </span>
                  {flights.primaryMode && (
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
                      {flights.primaryMode}
                    </span>
                  )}
                </div>
                {flights.modeRecommendation && (
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed max-w-2xl">
                    {flights.modeRecommendation}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Multi-Medium Comparison: Flight vs Train vs Road (when alternatives exist) */}
        {hasAlternatives && (
          <div className="mt-6 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Route className="h-4 w-4 text-blue-400" />
              <span>Available Transit Mediums</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Flight Option */}
              {(flights.duration || flights.fareRange || (flights.airlines && flights.airlines.length > 0)) && (
                <div className={`p-4 rounded-xl border transition-all ${
                  flights.primaryMode === 'Flight'
                    ? 'bg-blue-950/40 border-blue-500/50 shadow-md shadow-blue-500/10'
                    : 'bg-slate-950/60 border-slate-800'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wider">
                      <Plane className="h-4 w-4" />
                      <span>Flight</span>
                    </div>
                    {flights.primaryMode === 'Flight' && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-300 border border-emerald-500/30">
                        Recommended
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-bold text-white tracking-tight">
                    {flights.duration || 'Direct / Connecting'}
                  </div>
                  {flights.fareRange && (
                    <div className="text-xs font-semibold text-emerald-300 mt-1">
                      {flights.fareRange}
                    </div>
                  )}
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {flights.airlines && flights.airlines.length > 0 ? `Carriers: ${flights.airlines.slice(0, 3).join(', ')}` : 'Air travel route'}
                  </p>
                </div>
              )}

              {/* Train Option */}
              {flights.trainOption && (
                <div className={`p-4 rounded-xl border transition-all ${
                  flights.primaryMode === 'Train'
                    ? 'bg-blue-950/40 border-blue-500/50 shadow-md shadow-blue-500/10'
                    : 'bg-slate-950/60 border-slate-800'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
                      <Train className="h-4 w-4" />
                      <span>Train / Rail</span>
                    </div>
                    {flights.primaryMode === 'Train' && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-300 border border-emerald-500/30">
                        Recommended
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-bold text-white tracking-tight">
                    {flights.trainOption.duration || 'Express Rail'}
                  </div>
                  {flights.trainOption.fareRange && (
                    <div className="text-xs font-semibold text-emerald-300 mt-1">
                      {flights.trainOption.fareRange}
                    </div>
                  )}
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {flights.trainOption.operators && flights.trainOption.operators.length > 0
                      ? flights.trainOption.operators.join(', ')
                      : (flights.trainOption.details || 'Express rail connection')}
                  </p>
                  {flights.trainOption.terminals && flights.trainOption.terminals.length > 0 && (
                    <div className="text-[11px] text-slate-500 mt-1 font-mono">
                      {flights.trainOption.terminals.join(' to ')}
                    </div>
                  )}
                </div>
              )}

              {/* Road Option */}
              {flights.roadOption && (
                <div className={`p-4 rounded-xl border transition-all ${
                  (flights.primaryMode === 'Road / Drive' || flights.primaryMode === 'Road')
                    ? 'bg-blue-950/40 border-blue-500/50 shadow-md shadow-blue-500/10'
                    : 'bg-slate-950/60 border-slate-800'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                      <Car className="h-4 w-4" />
                      <span>Road / Drive / Cab</span>
                    </div>
                    {(flights.primaryMode === 'Road / Drive' || flights.primaryMode === 'Road') && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-300 border border-emerald-500/30">
                        Recommended
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-bold text-white tracking-tight">
                    {flights.roadOption.duration || 'Highway Route'}
                  </div>
                  {flights.roadOption.fareRange && (
                    <div className="text-xs font-semibold text-emerald-300 mt-1">
                      {flights.roadOption.fareRange}
                    </div>
                  )}
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {flights.roadOption.operators && flights.roadOption.operators.length > 0
                      ? flights.roadOption.operators.join(', ')
                      : (flights.roadOption.details || 'Expressway and road corridor')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Multi-modal Door-to-Door Journey Breakdown (when ground transfers are needed) */}
        {isMultiModal && (
          <div className="mt-6 p-5 rounded-2xl bg-slate-950/70 border border-slate-800/90 space-y-4">
            <div className="flex items-center gap-2">
              <Route className="h-4 w-4 text-blue-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-blue-300">
                Door-to-Door Transit Breakdown
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Leg 1: Origin to Departure Airport */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                  <Car className="h-4 w-4 text-sky-400" />
                  <span>Leg 1: Ground Transfer</span>
                </div>
                <div className="text-sm font-bold text-white">
                  {flights.origin || 'Origin'} <span className="text-slate-500">to</span> {flights.departureAirport || 'Departure Airport'}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {flights.originToAirportTransit || 'Direct access to departure airport'}
                </p>
              </div>

              {/* Leg 2: Flight Route */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                  <Plane className="h-4 w-4 text-blue-400" />
                  <span>Leg 2: Flight Route</span>
                </div>
                <div className="text-sm font-bold text-white">
                  {flights.departureAirport || 'Departure Airport'} <span className="text-slate-500">to</span> {flights.arrivalAirport || 'Arrival Airport'}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {flights.duration ? `${flights.duration} flight` : 'Scheduled flight'}
                  {flights.airlines && flights.airlines.length > 0 ? ` via ${flights.airlines.slice(0, 2).join(', ')}` : ''}
                </p>
              </div>

              {/* Leg 3: Arrival Airport to Destination */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                  <Train className="h-4 w-4 text-emerald-400" />
                  <span>Leg 3: Ground Transfer</span>
                </div>
                <div className="text-sm font-bold text-white">
                  {flights.arrivalAirport || 'Arrival Airport'} <span className="text-slate-500">to</span> {destination}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {flights.airportToDestinationTransit || 'Direct access to destination'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Route Visual Banner */}
        <div className="py-6 my-4 flex flex-col md:flex-row items-center justify-between gap-6 bg-slate-950/60 rounded-2xl p-6 border border-slate-800/80">
          {/* Origin */}
          <div className="text-center md:text-left">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
              Origin
            </div>
            <div className="text-2xl font-black text-white tracking-tight mt-0.5">
              {flights.origin || 'Departure Hub'}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              {flights.departureAirport ? `Via ${flights.departureAirport}` : (flights.origin ? 'Departure Gateway' : 'Origin Location')}
            </div>
          </div>

          {/* Path Graphic */}
          <div className="flex-1 flex flex-col items-center px-4 w-full md:w-auto">
            {(flights.duration || flights.trainOption?.duration || flights.roadOption?.duration) && (
              <div className="flex items-center justify-center gap-2 text-xs font-medium text-slate-400 mb-2">
                <Clock className="h-3.5 w-3.5 text-blue-400" />
                <span>
                  {flights.primaryMode === 'Train'
                    ? (flights.trainOption?.duration || flights.duration)
                    : (flights.primaryMode === 'Road / Drive'
                      ? (flights.roadOption?.duration || flights.duration)
                      : (flights.duration || flights.trainOption?.duration || flights.roadOption?.duration))}
                </span>
              </div>
            )}

            <div className="w-full flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-blue-500" />
              <div className="flex-1 relative flex items-center">
                <div className="w-full border-t-2 border-dashed border-slate-700" />
                {flights.primaryMode === 'Train' ? (
                  <Train className="absolute left-1/2 -translate-x-1/2 h-4 w-4 text-amber-400" />
                ) : flights.primaryMode === 'Road / Drive' || flights.primaryMode === 'Road' ? (
                  <Car className="absolute left-1/2 -translate-x-1/2 h-4 w-4 text-emerald-400" />
                ) : (
                  <Plane className="absolute left-1/2 -translate-x-1/2 h-4 w-4 text-blue-400 transform rotate-90" />
                )}
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
              {flights.arrivalAirport ? `Via ${flights.arrivalAirport}` : 'Arrival Gateway'}
            </div>
          </div>
        </div>

        {/* Airports & Carriers Chips */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
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
            <span>{showRaw ? 'Hide Raw Transit Notes' : 'View Full Scout Notes'}</span>
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
