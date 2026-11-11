import React from 'react';
import { User } from 'lucide-react';

interface UserMessageCardProps {
  content: string;
  timestamp: Date;
}

export const UserMessageCard: React.FC<UserMessageCardProps> = ({
  content,
  timestamp,
}) => {
  const formattedTime = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="w-full rounded-2xl bg-slate-900/80 border border-slate-800 p-4 sm:p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800/60 mb-2.5">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <User className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-semibold text-white">You</span>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">{formattedTime}</span>
      </div>
      <p className="text-sm sm:text-base text-slate-100 leading-relaxed whitespace-pre-wrap">
        {content}
      </p>
    </div>
  );
};
