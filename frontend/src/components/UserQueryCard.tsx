import React from 'react';
import { User, MessageSquare, CornerDownRight, CheckCircle2 } from 'lucide-react';

interface UserQueryCardProps {
  initialQuery: string;
  refinements: string[];
}

export const UserQueryCard: React.FC<UserQueryCardProps> = ({
  initialQuery,
  refinements,
}) => {
  return (
    <div className="w-full rounded-3xl bg-gradient-to-b from-slate-900/90 to-slate-950/95 border border-slate-800/80 p-5 sm:p-7 shadow-2xl backdrop-blur-xl relative overflow-hidden">
      {/* Subtle ambient corner light */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <User className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-bold text-white tracking-tight">
              Your Travel Request
            </span>
            <span className="text-[11px] text-slate-400 block">
              Autonomous Concierge Session
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {refinements.length > 0 && (
            <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20">
              {refinements.length} {refinements.length === 1 ? 'Refinement' : 'Refinements'} Applied
            </span>
          )}
          <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            <CheckCircle2 className="h-3 w-3 text-emerald-400" />
            <span>Curated</span>
          </span>
        </div>
      </div>

      {/* Primary User Prompt */}
      <div className="relative pl-3 sm:pl-4 border-l-2 border-blue-500/50 my-1">
        <p className="text-sm sm:text-base text-slate-100 font-medium leading-relaxed italic">
          "{initialQuery}"
        </p>
      </div>

      {/* Follow-up Refinements Stream (if any) */}
      {refinements.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/60 space-y-2.5">
          <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-400">
            <MessageSquare className="h-3.5 w-3.5 text-indigo-400" />
            <span>Follow-up Adjustments & Conversation</span>
          </div>

          <div className="space-y-2">
            {refinements.map((refinement, index) => (
              <div
                key={index}
                className="flex items-start gap-2.5 p-3 rounded-2xl bg-slate-950/70 border border-slate-800/80 text-xs sm:text-sm text-slate-200"
              >
                <CornerDownRight className="h-4 w-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400 block mb-0.5">
                    Refinement #{index + 1}
                  </span>
                  <span className="text-slate-300 italic">"{refinement}"</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
