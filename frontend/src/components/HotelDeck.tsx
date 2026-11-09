import React, { useState } from 'react';
import { Hotel, MapPin, Sparkles, Star, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { ParsedHotelItem } from '../types';

interface HotelDeckProps {
  hotels: ParsedHotelItem[];
  rawText?: string;
}

export const HotelDeck: React.FC<HotelDeckProps> = ({ hotels, rawText }) => {
  const [showRaw, setShowRaw] = useState(false);

  const getTierBadge = (tier: ParsedHotelItem['tier']) => {
    switch (tier) {
      case 'Luxury':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-semibold text-amber-300">
            <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
            <span>Luxury</span>
          </span>
        );
      case 'Boutique':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-xs font-semibold text-purple-300">
            <Sparkles className="h-3 w-3 text-purple-400" />
            <span>Boutique</span>
          </span>
        );
      case 'Value':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-300">
            <CheckCircle className="h-3 w-3 text-emerald-400" />
            <span>Smart Value</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-300">
            <Hotel className="h-3 w-3 text-blue-400" />
            <span>Recommended</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
            Places to Stay
          </span>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Hotel Options
          </h3>
        </div>

        <button
          type="button"
          onClick={() => setShowRaw(!showRaw)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800"
        >
          <span>{showRaw ? 'Hide Details' : 'View Full Details'}</span>
          {showRaw ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Hotel Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {hotels.map((hotel, index) => (
          <div
            key={index}
            className="group relative rounded-3xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700/80 p-6 shadow-xl transition-all duration-300 flex flex-col justify-between"
          >
            {/* Top Row: Tier badge & Price */}
            <div>
              <div className="flex items-center justify-between gap-2 mb-4">
                {getTierBadge(hotel.tier)}
                {hotel.priceRange && (
                  <span className="text-xs font-bold text-emerald-400 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    {hotel.priceRange}
                  </span>
                )}
              </div>

              {/* Hotel Name */}
              <h4 className="text-lg font-bold text-white group-hover:text-blue-300 transition-colors tracking-tight">
                {hotel.name}
              </h4>

              {/* Location Tag */}
              {hotel.location && (
                <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-1 mb-3">
                  <MapPin className="h-3.5 w-3.5 text-slate-500 flex-shrink-0" />
                  <span className="truncate">{hotel.location}</span>
                </div>
              )}

              {/* Hotel Description */}
              <p className="text-xs text-slate-300 leading-relaxed line-clamp-4 mt-2">
                {hotel.description.replace(/^(\d+\.|\*\*|\#\#|Hotel:).*/gm, '').trim() || hotel.description}
              </p>
            </div>

            {/* Amenities Pills */}
            <div className="pt-4 mt-4 border-t border-slate-800/80">
              {hotel.amenities && hotel.amenities.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {hotel.amenities.map((amenity, i) => (
                    <span
                      key={i}
                      className="text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-950/80 text-slate-300 border border-slate-800"
                    >
                      {amenity}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="text-[11px] text-slate-500 italic">
                  Verified accommodation details
                </div>
              )}
            </div>

          </div>
        ))}
      </div>

      {/* Raw Notes Collapsible */}
      {showRaw && rawText && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2 whitespace-pre-line leading-relaxed font-mono">
          {rawText}
        </div>
      )}
    </div>
  );
};
