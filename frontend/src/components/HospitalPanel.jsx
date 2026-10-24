import React from 'react';
import { Hospital, MapPin, Clock, Compass } from 'lucide-react';

export default function HospitalPanel({ systemState }) {
  const hospitalName = systemState?.hospital_name;
  const hospitalDistance = systemState?.hospital_distance;
  const eta = systemState?.route_eta;
  const lat = systemState?.hospital_latitude;
  const lng = systemState?.hospital_longitude;
  const navStatus = systemState?.navigation_status;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Hospital className="w-5 h-5 text-red-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">NEAREST HOSPITAL</h2>
        </div>
        {hospitalName && (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 uppercase">
            TARGET MATCHED
          </span>
        )}
      </div>

      {hospitalName ? (
        <div className="space-y-3">
          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">FACILITY NAME</span>
            <div className="text-sm font-extrabold text-cyan-300 truncate">
              {hospitalName}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block font-semibold">DISTANCE</span>
                <span className="text-xs font-mono font-bold text-slate-200">
                  {hospitalDistance !== null ? `${hospitalDistance.toFixed(2)} km` : 'N/A'}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block font-semibold">ESTIMATED ETA</span>
                <span className="text-xs font-mono font-bold text-slate-200">
                  {eta !== null ? `${eta.toFixed(1)} min` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-2.5 flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1"><Compass className="w-3.5 h-3.5 text-purple-400" /> GPS</span>
            <span>{lat?.toFixed(6)}, {lng?.toFixed(6)}</span>
          </div>
        </div>
      ) : (
        <div className="bg-slate-950/60 border border-slate-800 border-dashed rounded-lg p-6 text-center">
          <Hospital className="w-8 h-8 text-slate-600 mx-auto mb-2 animate-pulse" />
          <p className="text-xs text-slate-400 font-medium">
            {navStatus === 'SEARCHING_HOSPITAL' ? 'Searching for nearest hospital...' : 'Hospital routing idle. Triggers upon emergency.'}
          </p>
        </div>
      )}
    </div>
  );
}
