import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TrendingUp } from 'lucide-react';

export default function SpeedGraph({ systemState }) {
  const speedHistory = systemState?.speed_history || [];

  // Format data points for Recharts
  const chartData = speedHistory.map((point, index) => ({
    time: index,
    speed: point.speed_kmh,
  }));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">REAL-TIME SPEED TELEMETRY GRAPH</h2>
        </div>
        <span className="text-xs font-mono text-slate-400">
          CURRENT: <strong className="text-cyan-400">{(systemState?.vehicle_speed || 0).toFixed(1)} km/h</strong>
        </span>
      </div>

      <div className="flex-1 w-full min-h-[200px]">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#f8fafc' }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Line
                type="monotone"
                dataKey="speed"
                stroke="#06b6d4"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#38bdf8' }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-xs text-slate-500 font-mono">
            Awaiting speed telemetry stream...
          </div>
        )}
      </div>
    </div>
  );
}
