import React from 'react';
import { Gauge, MapPin, Clock, Compass } from 'lucide-react';

export default function LiveMetrics({ systemState }) {
  const speed = systemState?.vehicle_speed ?? 60.0;
  const distance = systemState?.hospital_distance;
  const eta = systemState?.route_eta;
  const lat = systemState?.gps_latitude || 12.971820;
  const lng = systemState?.gps_longitude || 77.594003;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Speed Card */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
        <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-xl">
          <Gauge className="w-6 h-6" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">VEHICLE SPEED</span>
          <div className="text-2xl font-extrabold font-mono text-cyan-400">
            {speed.toFixed(1)} <span className="text-xs font-normal text-slate-400">km/h</span>
          </div>
        </div>
      </div>

      {/* Hospital Distance Card */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl">
          <MapPin className="w-6 h-6" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">HOSPITAL DISTANCE</span>
          <div className="text-2xl font-extrabold font-mono text-emerald-400">
            {distance !== null && distance !== undefined ? `${distance.toFixed(2)}` : '0.00'}{' '}
            <span className="text-xs font-normal text-slate-400">km</span>
          </div>
        </div>
      </div>

      {/* ETA Card */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl">
          <Clock className="w-6 h-6" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">ESTIMATED ETA</span>
          <div className="text-2xl font-extrabold font-mono text-amber-400">
            {eta !== null && eta !== undefined ? `${eta.toFixed(1)}` : '0.0'}{' '}
            <span className="text-xs font-normal text-slate-400">min</span>
          </div>
        </div>
      </div>

      {/* GPS Position Card */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
        <div className="p-3 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl">
          <Compass className="w-6 h-6" />
        </div>
        <div className="overflow-hidden">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">GPS COORDINATES</span>
          <div className="text-xs font-bold font-mono text-purple-300 truncate">
            {lat.toFixed(6)}, {lng.toFixed(6)}
          </div>
        </div>
      </div>
    </div>
  );
}
