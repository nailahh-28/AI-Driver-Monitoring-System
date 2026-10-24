import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Cpu, Clock, Server, Zap, WifiOff } from 'lucide-react';

export default function Header({ systemState, isConnected }) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const isEmergency = systemState?.emergency_active;
  const executionMode = systemState?.execution_mode?.toUpperCase() || 'LOCAL';
  const carlaConnected = systemState?.carla_connected || false;
  const cudaAvailable = systemState?.cuda_available || false;
  const gpuName = systemState?.gpu_name || 'CPU';
  const vramUsage = systemState?.vram_usage || 'N/A';

  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-xl ${isEmergency ? 'bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'}`}>
          {isEmergency ? <ShieldAlert className="w-8 h-8" /> : <Activity className="w-8 h-8" />}
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            AI DRIVER MONITORING & AUTOMATED EMERGENCY RESPONSE SYSTEM
          </h1>
          <p className="text-xs text-slate-400 font-medium tracking-wide">
            COLLEGE MAJOR PROJECT PROTOTYPE • CLOUD GPU & REAL CARLA SIMULATION CONTROLLER
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 text-xs font-semibold flex-wrap">
        {/* Execution Mode Badge */}
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border ${executionMode === 'CLOUD' ? 'bg-purple-500/10 border-purple-500/30 text-purple-300' : 'bg-slate-800 border-slate-700 text-slate-300'}`}>
          <Server className="w-4 h-4 text-purple-400" />
          <span>MODE: <strong className="text-purple-300">{executionMode} ARCHITECTURE</strong></span>
        </div>

        {/* GPU Status Badge */}
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border ${cudaAvailable ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
          <Zap className={`w-4 h-4 ${cudaAvailable ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
          <span>GPU: <strong className={cudaAvailable ? 'text-emerald-300' : 'text-slate-400'}>{cudaAvailable ? gpuName : 'CPU SIMULATION'}</strong></span>
        </div>

        {/* System Online Status */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${isConnected ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'}`}>
          <span className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`} />
          <span>{isConnected ? 'ONLINE' : 'DISCONNECTED'}</span>
        </div>

        {/* Time */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-400">
          <Clock className="w-4 h-4 text-slate-400" />
          <span>{timeStr}</span>
        </div>
      </div>
    </header>
  );
}
