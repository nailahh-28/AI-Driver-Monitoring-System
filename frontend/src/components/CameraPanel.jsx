import React, { useState } from 'react';
import { Camera, Radio, AlertTriangle } from 'lucide-react';

export default function CameraPanel({ systemState }) {
  const [streamError, setStreamError] = useState(false);
  const isEmergency = systemState?.emergency_active;
  const streamUrl = '/api/camera/stream';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Camera className="w-5 h-5 text-purple-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">🎥 LIVE VEHICLE CAMERA FEED</h2>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-300">
            <Radio className="w-3.5 h-3.5 text-red-500 animate-pulse" /> 1280x720 • 90° FOV
          </span>
        </div>
      </div>

      {/* Video Container */}
      <div className="relative flex-1 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center min-h-[300px]">
        {!streamError ? (
          <img
            src={streamUrl}
            alt="Live Vehicle Camera Feed"
            className="w-full h-full object-cover"
            onError={() => setStreamError(true)}
          />
        ) : (
          <div className="text-center p-6">
            <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-2" />
            <p className="text-sm text-slate-300 font-semibold mb-1">Camera Stream Standby</p>
            <p className="text-xs text-slate-500">Ensure backend service is running on port 8000.</p>
            <button
              onClick={() => setStreamError(false)}
              className="mt-3 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded border border-slate-700"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Live Banner Overlay */}
        {isEmergency && (
          <div className="absolute top-3 left-3 bg-red-600/90 backdrop-blur text-white text-xs font-extrabold px-3 py-1.5 rounded-lg border border-red-400 shadow-lg flex items-center gap-2 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-white animate-ping" />
            <span>🚨 EMERGENCY MODE ACTIVE</span>
          </div>
        )}
      </div>
    </div>
  );
}
