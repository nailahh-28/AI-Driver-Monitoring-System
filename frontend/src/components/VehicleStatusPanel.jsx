import React from 'react';
import { Car, Gauge, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function VehicleStatusPanel({ systemState }) {
  const vehicleMode = systemState?.vehicle_mode || 'NORMAL';
  const speed = systemState?.vehicle_speed ?? 60.0;
  const vehicleId = systemState?.vehicle_id || 'CARLA-001';
  const isEmergency = systemState?.emergency_active || false;

  const getModeColor = (mode) => {
    switch (mode) {
      case 'NORMAL':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'EMERGENCY':
      case 'SLOWING_DOWN':
      case 'PULLING_OVER':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'STOPPED':
        return 'text-red-400 bg-red-500/10 border-red-500/30';
      case 'AUTONOMOUS_EMERGENCY':
      case 'NAVIGATING_TO_HOSPITAL':
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30 animate-pulse';
      case 'HOSPITAL_REACHED':
        return 'text-purple-400 bg-purple-500/10 border-purple-500/30';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Car className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">VEHICLE STATUS</h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
          ID: {vehicleId}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Mode */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">MODE</span>
          <div className={`text-xs font-bold px-2 py-1 rounded border inline-block ${getModeColor(vehicleMode)}`}>
            {vehicleMode}
          </div>
        </div>

        {/* Emergency Flag */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">EMERGENCY</span>
          <div className="flex items-center gap-1.5 mt-1">
            {isEmergency ? (
              <>
                <AlertTriangle className="w-4 h-4 text-red-400 animate-bounce" />
                <span className="text-xs font-bold text-red-400">ACTIVE</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">INACTIVE</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Speed Gauge summary */}
      <div className="mt-4 bg-slate-950/80 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-400">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-medium">VEHICLE SPEED</span>
        </div>
        <div className="text-xl font-extrabold font-mono text-cyan-400">
          {speed.toFixed(1)} <span className="text-xs text-slate-400 font-normal">km/h</span>
        </div>
      </div>
    </div>
  );
}
