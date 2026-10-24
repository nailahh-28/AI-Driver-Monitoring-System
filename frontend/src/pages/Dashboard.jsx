import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

import Header from '../components/Header';
import LiveMetrics from '../components/LiveMetrics';
import CloudStatusPanel from '../components/CloudStatusPanel';
import VehicleStatusPanel from '../components/VehicleStatusPanel';
import DriverStatusPanel from '../components/DriverStatusPanel';
import EmergencyStatusPanel from '../components/EmergencyStatusPanel';
import HospitalPanel from '../components/HospitalPanel';
import GpsMapPanel from '../components/GpsMapPanel';
import SpeedGraph from '../components/SpeedGraph';
import CameraPanel from '../components/CameraPanel';
import ControlPanel from '../components/ControlPanel';

export default function Dashboard() {
  const { systemState, isConnected } = useWebSocket();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header */}
      <Header systemState={systemState} isConnected={isConnected} />

      {/* Main Dashboard Workspace */}
      <main className="flex-1 p-6 space-y-6 max-w-[1800px] mx-auto w-full">
        {/* Prominent Live Telemetry KPI Cards */}
        <LiveMetrics systemState={systemState} />

        {/* Cloud & Hardware System Telemetry Panel */}
        <CloudStatusPanel systemState={systemState} isConnected={isConnected} />

        {/* Action Controls Bar */}
        <ControlPanel systemState={systemState} />

        {/* Row 1: Camera & Leaflet GPS Navigation Map */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CameraPanel systemState={systemState} />
          <GpsMapPanel systemState={systemState} />
        </div>

        {/* Row 2: Status Panels Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <VehicleStatusPanel systemState={systemState} />
          <DriverStatusPanel systemState={systemState} />
          <HospitalPanel systemState={systemState} />
          <EmergencyStatusPanel systemState={systemState} />
        </div>

        {/* Row 3: Real-Time Speed Telemetry Graph */}
        <div className="grid grid-cols-1 gap-6">
          <SpeedGraph systemState={systemState} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500 font-mono">
        AI-Based Driver Monitoring & Automated Emergency Response System • Built with FastAPI, CARLA 0.9.16 & Cloud GPU PyTorch
      </footer>
    </div>
  );
}
