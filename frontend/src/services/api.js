import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export const api = {
  getStatus: () => axios.get(`${API_BASE}/status`),
  getVehicle: () => axios.get(`${API_BASE}/vehicle`),
  getDriver: () => axios.get(`${API_BASE}/driver`),
  getGps: () => axios.get(`${API_BASE}/gps`),
  getHospital: () => axios.get(`${API_BASE}/hospital`),
  getRoute: () => axios.get(`${API_BASE}/route`),
  getNavigation: () => axios.get(`${API_BASE}/navigation`),
  
  startEmergency: (demoMode = true, responseTime = null) =>
    axios.post(`${API_BASE}/emergency/start`, { demo_mode: demoMode, response_time: responseTime }),
  
  driverRespond: () =>
    axios.post(`${API_BASE}/driver/respond`),
  
  startSimulation: (useCarla = false) =>
    axios.post(`${API_BASE}/simulation/start`, { use_carla: useCarla }),
  
  resetSimulation: () =>
    axios.post(`${API_BASE}/simulation/reset`),
  
  stopVehicle: () =>
    axios.post(`${API_BASE}/vehicle/stop`),
};
