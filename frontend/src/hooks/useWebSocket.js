import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

export function useWebSocket() {
  const [systemState, setSystemState] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const connectWS = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname || 'localhost';
      const defaultWsUrl = `${protocol}//${host}:8000/ws`;
      const wsUrl = import.meta.env.VITE_WS_URL || defaultWsUrl;

      console.log('Connecting to WebSocket:', wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isMounted) setIsConnected(true);
        console.log('WebSocket connected.');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (isMounted) setSystemState(data);
        } catch (e) {
          console.error('Error parsing WS telemetry:', e);
        }
      };

      ws.onerror = (error) => {
        console.warn('WebSocket error, falling back to REST polling:', error);
        if (isMounted) setIsConnected(false);
      };

      ws.onclose = () => {
        if (isMounted) {
          setIsConnected(false);
          // Try reconnecting after 3 seconds
          setTimeout(() => {
            if (isMounted) connectWS();
          }, 3000);
        }
      };
    };

    connectWS();

    // Fallback REST polling interval (1s) if WS is not connected
    const pollingInterval = setInterval(async () => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        try {
          const res = await api.getStatus();
          if (isMounted) setSystemState(res.data);
        } catch (err) {
          console.error('Polling error:', err);
        }
      }
    }, 1000);

    return () => {
      isMounted = false;
      if (wsRef.current) wsRef.current.close();
      clearInterval(pollingInterval);
    };
  }, []);

  return { systemState, isConnected };
}
