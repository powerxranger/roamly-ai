import React from 'react';
import { Plane, Hotel, CloudSun, Compass, CheckCircle2, Loader2 } from 'lucide-react';
import { PlannerTask } from '../types';

interface PlanningRadarProps {
  tasks: PlannerTask[];
  isProcessing: boolean;
}

export const PlanningRadar: React.FC<PlanningRadarProps> = ({
  tasks,
  isProcessing,
}) => {
  const getIcon = (type: PlannerTask['icon']) => {
    switch (type) {
      case 'flight':
        return <Plane className="h-4 w-4" />;
      case 'hotel':
        return <Hotel className="h-4 w-4" />;
      case 'weather':
        return <CloudSun className="h-4 w-4" />;
      case 'itinerary':
        return <Compass className="h-4 w-4" />;
    }
  };

  const completedCount = tasks.filter(t => t.status === 'completed').length;
  const progressPercent = Math.round((completedCount / tasks.length) * 100);

  return (
    <div className="w-full relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900/90 to-slate-950/95 border border-slate-800/80 p-5 sm:p-7 shadow-2xl backdrop-blur-xl">
      {/* Decorative ambient background glow */}
      <div className="absolute top-0 right-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Status Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-800/60 relative z-10">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="flex h-2.5 w-2.5 relative">
              {isProcessing && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
              )}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isProcessing ? 'bg-blue-500' : 'bg-emerald-500'}`} />
            </span>
            <h3 className="text-sm sm:text-base font-bold text-white tracking-tight">
              {isProcessing ? 'Planning Your Trip' : 'Trip Plan Ready'}
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {isProcessing
              ? 'Searching live flights, hotels, weather, and daily activities.'
              : 'All travel details gathered and organized into your plan.'}
          </p>
        </div>

        {/* Progress pill */}
        <div className="flex items-center gap-2 self-stretch sm:self-auto justify-end">
          <div className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800/80 text-blue-300 border border-slate-700/60">
            {progressPercent}% Complete
          </div>
        </div>
      </div>

      {/* Task Streams Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 relative z-10">
        {tasks.map((task) => {
          const isActive = task.status === 'in_progress';
          const isDone = task.status === 'completed';

          return (
            <div
              key={task.id}
              className={`p-3.5 sm:p-4 rounded-2xl border transition-all duration-300 relative ${
                isActive
                  ? 'bg-blue-950/20 border-blue-500/50 shadow-lg shadow-blue-500/10'
                  : isDone
                  ? 'bg-slate-900/60 border-emerald-500/30'
                  : 'bg-slate-900/30 border-slate-800/50 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  <div
                    className={`p-2.5 rounded-xl transition-colors ${
                      isActive
                        ? 'bg-blue-500 text-white shadow-md shadow-blue-500/30'
                        : isDone
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {getIcon(task.icon)}
                  </div>
                  <div className="min-w-0">
                    <h4 className="text-xs sm:text-sm font-semibold text-white truncate">
                      {task.label}
                    </h4>
                    <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2 leading-relaxed">
                      {task.sublabel}
                    </p>
                  </div>
                </div>

                {/* Status Icon */}
                <div className="flex-shrink-0 pt-1">
                  {isActive ? (
                    <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                  ) : isDone ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <div className="h-2 w-2 rounded-full bg-slate-700" />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
