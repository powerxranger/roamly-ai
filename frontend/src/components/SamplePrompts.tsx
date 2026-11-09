import React from 'react';
import { Sparkles } from 'lucide-react';

interface SamplePromptsProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

const SAMPLE_PROMPTS = [
  {
    title: 'Tokyo & Kyoto Culture',
    query: 'Plan a 7-day trip to Tokyo and Kyoto in late October for two people, mid-range budget, interested in food, shrines, and scenic rail trips.',
    emoji: '⛩️',
    tag: 'Culture & Food',
  },
  {
    title: 'Amalfi Coast & Rome',
    query: 'Plan a 5-day romantic trip to Rome and the Amalfi Coast for a couple, focusing on coastal views, local pasta, and historic sights.',
    emoji: '🍋',
    tag: 'Romantic',
  },
  {
    title: 'Iceland Aurora & Springs',
    query: 'Plan a 6-day adventure around Iceland in November for 2 friends, seeking northern lights, geothermal springs, and waterfalls.',
    emoji: '🌌',
    tag: 'Adventure',
  },
  {
    title: 'Bali Villa Sanctuary',
    query: 'Plan a 4-day tropical vacation to Bali (Ubud and Seminyak) with private villa recommendations, beaches, and cafe culture.',
    emoji: '🌿',
    tag: 'Retreat',
  },
];

export const SamplePrompts: React.FC<SamplePromptsProps> = ({ onSelectPrompt, disabled }) => {
  return (
    <div className="w-full">
      <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 px-1">
        <Sparkles className="h-3.5 w-3.5 text-blue-400" />
        <span>Curated Journey Inspirations</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {SAMPLE_PROMPTS.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(sample.query)}
            className="flex flex-col text-left p-4 rounded-2xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-blue-500/40 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-xl hover:shadow-blue-500/5 hover:-translate-y-0.5"
          >
            <div className="flex items-center justify-between gap-1 w-full mb-2">
              <span className="text-xl group-hover:scale-110 transition-transform">
                {sample.emoji}
              </span>
              <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-950 text-slate-400 group-hover:text-blue-300 border border-slate-800">
                {sample.tag}
              </span>
            </div>
            <div className="text-xs sm:text-sm font-bold text-slate-200 group-hover:text-white mb-1 tracking-tight">
              {sample.title}
            </div>
            <div className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
              {sample.query}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
