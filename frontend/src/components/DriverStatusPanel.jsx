import React from 'react';
import { User, AlertOctagon, CheckCircle2, Clock, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function DriverStatusPanel({ systemState }) {
  const driverStatus = systemState?.driver_status || 'NORMAL';
  const driverResponsive = systemState?.driver_responsive || false;
  const isEmergency = systemState?.emergency_active || false;
  const emergencyStage = systemState?.emergency_stage || 'INACTIVE';
  const remaining = systemState?.response_time_remaining ?? 0;

  // Response window active check
  const isResponseWindowActive = isEmergency && (emergencyStage === 'WAITING_FOR_DRIVER' || emergencyStage === 'FAMILY_ALERT_SENT');

  const handleRespond = async () => {
    try {
      await api.driverRespond();
    } catch (err) {
      console.error('Error sending driver response:', err);
    }
  };

  const getDriverBadge = (status) => {
    switch (status) {
      case 'NORMAL':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'DROWSY':
      case 'FATIGUED':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'UNRESPONSIVE':
      case 'SERIOUS_EMERGENCY':
        return 'text-red-400 bg-red-500/10 border-red-500/30 animate-pulse';
      case 'DRIVER_RESPONDED':
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">DRIVER STATUS</h2>
        </div>
        <div className={`text-xs font-bold px-2.5 py-1 rounded border ${getDriverBadge(driverStatus)}`}>
          {driverStatus}
        </div>
      </div>

      {/* Emergency Warning Banner if unresponsive */}
      {driverStatus === 'UNRESPONSIVE' && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-3 flex items-center gap-2 text-red-400 text-xs font-bold">
          <AlertOctagon className="w-5 h-5 shrink-0 animate-bounce" />
          <span>⚠️ SERIOUS EMERGENCY — DRIVER UNRESPONSIVE</span>
        </div>
      )}

      {/* Response Countdown Area */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between mb-2 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-cyan-400" /> DRIVER RESPONSE WINDOW
          </span>
          <span className="font-mono text-slate-300">
            {driverResponsive ? (
              <span className="text-emerald-400 font-bold">CONFIRMED</span>
            ) : isResponseWindowActive ? (
              <span className="text-amber-400 font-bold">WAITING</span>
            ) : remaining === 0 && isEmergency ? (
              <span className="text-red-400 font-bold">NO RESPONSE</span>
            ) : (
              <span className="text-slate-500">IDLE</span>
            )}
          </span>
        </div>

        {/* Large Countdown Timer */}
        <div className="text-center py-2 bg-slate-900 rounded border border-slate-800">
          <span className={`text-4xl font-extrabold font-mono tracking-wider ${isResponseWindowActive ? 'text-amber-400 animate-pulse' : 'text-slate-600'}`}>
            {String(remaining).padStart(2, '0')}
          </span>
          <span className="text-xs text-slate-500 block mt-1 font-mono uppercase">seconds remaining</span>
        </div>
      </div>

      {/* Driver Responded Action Button */}
      <button
        onClick={handleRespond}
        disabled={!isResponseWindowActive}
        className={`w-full py-3 px-4 rounded-xl font-bold text-sm tracking-wide transition-all duration-200 flex items-center justify-center gap-2 shadow-lg ${
          isResponseWindowActive
            ? 'bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer ring-2 ring-emerald-400/50 shadow-emerald-900/40 animate-pulse'
            : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed opacity-60'
        }`}
      >
        <ShieldCheck className="w-5 h-5" />
        🟢 DRIVER RESPONDED
      </button>
    </div>
  );
}
