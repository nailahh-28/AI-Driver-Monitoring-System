import React, { useState } from 'react';
import { Play, AlertTriangle, ShieldCheck, RotateCcw, Octagon, Cpu, Info, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function ControlPanel({ systemState }) {
  const [loadingAction, setLoadingAction] = useState(null);
  const [actionFeedback, setActionFeedback] = useState({ type: 'info', message: 'System Ready. Click "Start Offline Simulation" to begin normal driving simulation.' });

  const isEmergency = systemState?.emergency_active;
  const emergencyStage = systemState?.emergency_stage;
  const isResponseWindowActive = isEmergency && (emergencyStage === 'WAITING_FOR_DRIVER' || emergencyStage === 'FAMILY_ALERT_SENT');

  const handleAction = async (actionName, apiCall) => {
    try {
      setLoadingAction(actionName);
      const res = await apiCall();
      if (res.data?.message) {
        setActionFeedback({
          type: res.data.status === 'SUCCESS' ? 'success' : 'info',
          message: res.data.message
        });
      }
    } catch (err) {
      console.error(`Error performing ${actionName}:`, err);
      setActionFeedback({
        type: 'error',
        message: err.response?.data?.message || `Failed to perform ${actionName}. Ensure backend is running.`
      });
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <Cpu className="w-5 h-5 text-purple-400" /> SYSTEM CONTROLS & DEMO SUITE
        </h2>
        <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/30 font-semibold">
          ⚡ NO CARLA REQUIRED (OFFLINE SIMULATION READY)
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {/* Start Offline Simulation */}
        <button
          onClick={() => handleAction('start', () => api.startSimulation(false))}
          disabled={loadingAction === 'start'}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold py-3 px-3 rounded-xl text-xs flex flex-col items-center justify-center gap-1.5 transition-all shadow cursor-pointer ring-1 ring-emerald-400/40"
        >
          <Play className="w-4 h-4 text-white" />
          <span>Start Offline Sim</span>
        </button>

        {/* Simulate Emergency */}
        <button
          onClick={() => handleAction('emergency', () => api.startEmergency(true))}
          disabled={isEmergency || loadingAction === 'emergency'}
          className={`font-bold py-3 px-3 rounded-xl text-xs flex flex-col items-center justify-center gap-1.5 transition-all shadow ${
            !isEmergency
              ? 'bg-red-600/90 hover:bg-red-500 text-white border border-red-400 cursor-pointer shadow-red-900/30'
              : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed opacity-50'
          }`}
        >
          <AlertTriangle className="w-4 h-4 text-white" />
          <span>Simulate Emergency</span>
        </button>

        {/* Driver Responded */}
        <button
          onClick={() => handleAction('respond', api.driverRespond)}
          disabled={!isResponseWindowActive || loadingAction === 'respond'}
          className={`font-bold py-3 px-3 rounded-xl text-xs flex flex-col items-center justify-center gap-1.5 transition-all shadow ${
            isResponseWindowActive
              ? 'bg-cyan-600 hover:bg-cyan-500 text-white border border-cyan-400 cursor-pointer ring-2 ring-cyan-400/40 animate-pulse'
              : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed opacity-50'
          }`}
        >
          <ShieldCheck className="w-4 h-4 text-cyan-200" />
          <span>Driver Responded</span>
        </button>

        {/* Stop Vehicle */}
        <button
          onClick={() => handleAction('stop', api.stopVehicle)}
          disabled={loadingAction === 'stop'}
          className="bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 font-bold py-3 px-3 rounded-xl text-xs flex flex-col items-center justify-center gap-1.5 transition-all cursor-pointer"
        >
          <Octagon className="w-4 h-4 text-amber-400" />
          <span>Stop Vehicle</span>
        </button>

        {/* Reset Simulation */}
        <button
          onClick={() => handleAction('reset', api.resetSimulation)}
          disabled={loadingAction === 'reset'}
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-bold py-3 px-3 rounded-xl text-xs flex flex-col items-center justify-center gap-1.5 transition-all cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 text-cyan-400" />
          <span>Reset System</span>
        </button>
      </div>

      {/* Real-time Status Feedback Banner */}
      {actionFeedback.message && (
        <div className={`p-3 rounded-lg border text-xs flex items-center gap-2 font-medium ${
          actionFeedback.type === 'success'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : actionFeedback.type === 'error'
            ? 'bg-red-500/10 border-red-500/30 text-red-300'
            : 'bg-slate-950 border-slate-800 text-slate-400'
        }`}>
          {actionFeedback.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <Info className="w-4 h-4 text-cyan-400 shrink-0" />
          )}
          <span>{actionFeedback.message}</span>
        </div>
      )}
    </div>
  );
}
