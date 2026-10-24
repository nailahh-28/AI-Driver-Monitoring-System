import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Navigation, Compass } from 'lucide-react';
import { api } from '../services/api';

// Fix default Leaflet icon assets
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom Car SVG Icon
const carIcon = new L.DivIcon({
  className: 'custom-car-icon',
  html: `<div style="background-color:#06b6d4;width:24px;height:24px;border-radius:50%;border:2px solid white;box-shadow:0 0 10px #06b6d4;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;">🚗</div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

// Custom Hospital SVG Icon
const hospitalIcon = new L.DivIcon({
  className: 'custom-hospital-icon',
  html: `<div style="background-color:#ef4444;width:26px;height:26px;border-radius:50%;border:2px solid white;box-shadow:0 0 10px #ef4444;display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">🏥</div>`,
  iconSize: [26, 26],
  iconAnchor: [13, 13]
});

// Auto-recenter helper
function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, map.getZoom(), { animate: true });
    }
  }, [center, map]);
  return null;
}

export default function GpsMapPanel({ systemState }) {
  const vehicleLat = systemState?.gps_latitude || 12.971820;
  const vehicleLng = systemState?.gps_longitude || 77.594003;
  
  const hospitalLat = systemState?.hospital_latitude;
  const hospitalLng = systemState?.hospital_longitude;
  const hospitalName = systemState?.hospital_name;

  const [routePolyline, setRoutePolyline] = useState([]);

  useEffect(() => {
    let isMounted = true;
    const fetchRoute = async () => {
      try {
        const res = await api.getRoute();
        if (res.data?.waypoints && isMounted) {
          const pts = res.data.waypoints.map(w => [w.lat, w.lng]);
          setRoutePolyline(pts);
        }
      } catch (err) {
        console.error('Error fetching map route:', err);
      }
    };

    if (hospitalLat && hospitalLng) {
      fetchRoute();
    } else {
      setRoutePolyline([]);
    }

    return () => { isMounted = false; };
  }, [hospitalLat, hospitalLng, vehicleLat, vehicleLng]);

  const vehiclePos = [vehicleLat, vehicleLng];
  const hospitalPos = hospitalLat && hospitalLng ? [hospitalLat, hospitalLng] : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col h-full min-h-[380px]">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold tracking-wider text-slate-200 uppercase">📍 CURRENT LOCATION & NAVIGATION MAP</h2>
        </div>
        <div className="text-xs font-mono text-cyan-400 font-bold bg-slate-950 px-2.5 py-1 rounded border border-slate-800 flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-purple-400" />
          {vehicleLat.toFixed(6)}, {vehicleLng.toFixed(6)}
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 rounded-lg overflow-hidden border border-slate-800 relative z-0 min-h-[280px]">
        <MapContainer
          center={vehiclePos}
          zoom={14}
          scrollWheelZoom={false}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapRecenter center={vehiclePos} />

          {/* Vehicle Marker */}
          <Marker position={vehiclePos} icon={carIcon}>
            <Popup>
              <strong>Tesla Model 3 (Simulated Vehicle)</strong><br />
              Speed: {systemState?.vehicle_speed || 0} km/h
            </Popup>
          </Marker>

          {/* Hospital Marker */}
          {hospitalPos && (
            <Marker position={hospitalPos} icon={hospitalIcon}>
              <Popup>
                <strong>🏥 {hospitalName}</strong><br />
                Distance: {systemState?.hospital_distance || 0} km
              </Popup>
            </Marker>
          )}

          {/* OSRM Route Polyline */}
          {routePolyline.length > 0 && (
            <Polyline
              positions={routePolyline}
              color="#06b6d4"
              weight={5}
              opacity={0.8}
              dashArray="1, 8"
            />
          )}
        </MapContainer>
      </div>

      <div className="flex items-center justify-around mt-3 text-xs text-slate-400 bg-slate-950/60 p-2 rounded-lg border border-slate-800">
        <span className="flex items-center gap-1.5 font-medium"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" /> 🚗 Vehicle Position</span>
        {hospitalPos && (
          <span className="flex items-center gap-1.5 font-medium"><span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> 🏥 Target Hospital</span>
        )}
        {routePolyline.length > 0 && (
          <span className="flex items-center gap-1.5 font-medium"><span className="w-4 h-1 bg-cyan-400 inline-block rounded" /> 🛣️ OSRM Route ({routePolyline.length} pts)</span>
        )}
      </div>
    </div>
  );
}
