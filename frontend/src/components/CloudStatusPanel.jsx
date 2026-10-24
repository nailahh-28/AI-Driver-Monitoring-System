import React from 'react';
import { Server, Cpu, Zap, Radio, CheckCircle2, XCircle, RefreshCw, Layers } from 'lucide-react';
import { api } from '../services/api';

export default function CloudStatusPanel({ systemState, isConnected }) {
  const mode = systemState?.execution_mode?.toUpperCase() || 'LOCAL';
  const carlaConnected = systemState?.carla_connected || false;
  const cudaAvailable = systemState?.cuda_available || false;
  const gpuName = systemState?.gpu_name || 'None';
  const vramUsage = systemState?.vram_usage || 'N/A';
  const aiWorkerStatus = systemState?.ai_worker_status || 'OFFLINE';
  const carlaFps = systemState?.carla_fps || 0.0;
  const cameraFps = systemState?.camera_fps || 0.0;
  const aiFps = systemState?.ai_fps || 0.0;

  const handleSwitchLocal = async () => {
    try {
      await api.startSimulation(false);
    } catch (err) {
      console.error('Error switching to local mode:', err);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-purple-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">CLOUD & HARDWARE SYSTEM STATUS</h2>
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded border ${mode === 'CLOUD' ? 'bg-purple-500/10 border-purple-500/30 text-purple-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
          {mode} MODE
        </span>
      </div>

      {/* Hardware Telemetry Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {/* Backend Status */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">FASTAPI BACKEND</span>
          <div className="flex items-center gap-1.5">
            {isConnected ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">ONLINE</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-red-400 animate-pulse" />
                <span className="text-xs font-bold text-red-400">DISCONNECTED</span>
              </>
            )}
          </div>
        </div>

        {/* CARLA Status */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">CARLA SIMULATOR</span>
          <div className="flex items-center gap-1.5">
            {carlaConnected ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">CONNECTED ({carlaFps} FPS)</span>
              </>
            ) : (
              <>
                <Radio className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-bold text-slate-400">STANDBY (OFFLINE SIM)</span>
              </>
            )}
          </div>
        </div>

        {/* GPU Hardware Status */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">GPU HARDWARE</span>
          <div className="flex items-center gap-1.5">
            {cudaAvailable ? (
              <>
                <Zap className="w-4 h-4 text-emerald-400 animate-pulse" />
                <span className="text-xs font-bold text-emerald-300 truncate" title={gpuName}>{gpuName}</span>
              </>
            ) : (
              <>
                <Cpu className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-amber-300">CPU SIMULATION</span>
              </>
            )}
          </div>
        </div>

        {/* AI Worker Status */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">AI GPU WORKER</span>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-bold text-purple-300">{aiWorkerStatus} ({aiFps} FPS)</span>
          </div>
        </div>

        {/* VRAM Memory */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">GPU VRAM MEMORY</span>
          <div className="text-xs font-mono font-bold text-slate-200">
            {vramUsage}
          </div>
        </div>

        {/* Camera Stream FPS */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">CAMERA STREAM</span>
          <div className="text-xs font-mono font-bold text-cyan-400">
            {cameraFps > 0 ? `${cameraFps} FPS` : '15.0 FPS (MJPEG)'}
          </div>
        </div>
      </div>

      {/* Disconnection Warning & Fallback Action Bar */}
      {!isConnected && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-red-300 font-semibold">
            <XCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>CLOUD DISCONNECTED — Laptop running in offline standby mode.</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleSwitchLocal}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold transition-all cursor-pointer flex items-center gap-1"
            >
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400" /> Reconnect Local
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
