import React from 'react';
import { AlertCircle, CheckCircle2, Clock, Navigation, Hospital, Bell, Disc, Shield } from 'lucide-react';

export default function EmergencyStatusPanel({ systemState }) {
  const isEmergency = systemState?.emergency_active || false;
  const stage = systemState?.emergency_stage || 'INACTIVE';
  const mode = systemState?.vehicle_mode || 'NORMAL';
  const familyAlert = systemState?.family_alert_sent || false;

  const steps = [
    {
      id: 'EMERGENCY_DETECTED',
      label: 'Emergency Detected',
      isCompleted: isEmergency,
      isCurrent: stage === 'EMERGENCY_DETECTED',
      icon: AlertCircle
    },
    {
      id: 'SLOWING_DOWN',
      label: 'Vehicle Slowing Down',
      isCompleted: ['PULLING_OVER', 'VEHICLE_STOPPED', 'FAMILY_ALERT_SENT', 'WAITING_FOR_DRIVER', 'AUTONOMOUS_MODE_ACTIVATED'].includes(stage) || mode === 'NAVIGATING_TO_HOSPITAL' || mode === 'HOSPITAL_REACHED',
      isCurrent: stage === 'SLOWING_DOWN' || mode === 'SLOWING_DOWN',
      icon: Disc
    },
    {
      id: 'PULLING_OVER',
      label: 'Vehicle Pulling Over',
      isCompleted: ['VEHICLE_STOPPED', 'FAMILY_ALERT_SENT', 'WAITING_FOR_DRIVER', 'AUTONOMOUS_MODE_ACTIVATED'].includes(stage) || mode === 'NAVIGATING_TO_HOSPITAL' || mode === 'HOSPITAL_REACHED',
      isCurrent: stage === 'PULLING_OVER' || mode === 'PULLING_OVER',
      icon: Navigation
    },
    {
      id: 'VEHICLE_STOPPED',
      label: 'Vehicle Stopped',
      isCompleted: ['FAMILY_ALERT_SENT', 'WAITING_FOR_DRIVER', 'AUTONOMOUS_MODE_ACTIVATED'].includes(stage) || mode === 'NAVIGATING_TO_HOSPITAL' || mode === 'HOSPITAL_REACHED',
      isCurrent: stage === 'VEHICLE_STOPPED' || mode === 'STOPPED',
      icon: Shield
    },
    {
      id: 'FAMILY_ALERT',
      label: 'Family Emergency Alert Sent',
      isCompleted: familyAlert,
      isCurrent: stage === 'FAMILY_ALERT_SENT',
      icon: Bell
    },
    {
      id: 'WAITING_FOR_DRIVER',
      label: 'Waiting for Driver Response',
      isCompleted: stage === 'AUTONOMOUS_MODE_ACTIVATED' || mode === 'NAVIGATING_TO_HOSPITAL' || mode === 'HOSPITAL_REACHED',
      isCurrent: stage === 'WAITING_FOR_DRIVER' || mode === 'WAITING_FOR_DRIVER',
      icon: Clock
    },
    {
      id: 'AUTONOMOUS_MODE',
      label: 'Autonomous Emergency Mode',
      isCompleted: mode === 'NAVIGATING_TO_HOSPITAL' || mode === 'HOSPITAL_REACHED',
      isCurrent: stage === 'AUTONOMOUS_MODE_ACTIVATED' || mode === 'AUTONOMOUS_EMERGENCY',
      icon: Navigation
    },
    {
      id: 'HOSPITAL_REACHED',
      label: 'Hospital Reached',
      isCompleted: mode === 'HOSPITAL_REACHED',
      isCurrent: mode === 'NAVIGATING_TO_HOSPITAL',
      icon: Hospital
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-amber-400" /> EMERGENCY SEQUENCE TIMELINE
        </h2>
        <span className="text-xs font-mono text-slate-400">
          STAGE: {stage}
        </span>
      </div>

      <div className="space-y-2.5 overflow-y-auto max-h-[300px] pr-1">
        {steps.map((step, idx) => {
          const IconComp = step.icon;
          return (
            <div
              key={step.id}
              className={`flex items-center justify-between p-2.5 rounded-lg border text-xs font-medium transition-all ${
                step.isCompleted
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : step.isCurrent
                  ? 'bg-amber-500/10 border-amber-500/40 text-amber-300 animate-pulse font-bold'
                  : 'bg-slate-950/40 border-slate-800 text-slate-500 opacity-60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-[10px] text-slate-500">{idx + 1}.</span>
                <IconComp className={`w-4 h-4 ${step.isCompleted ? 'text-emerald-400' : step.isCurrent ? 'text-amber-400' : 'text-slate-600'}`} />
                <span>{step.label}</span>
              </div>
              <div>
                {step.isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : step.isCurrent ? (
                  <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/30">IN PROGRESS</span>
                ) : (
                  <span className="text-[10px] text-slate-600">PENDING</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
