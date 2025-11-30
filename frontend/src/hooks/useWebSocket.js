import { useEffect, useState, useCallback } from 'react';
import websocketService from '@services/websocketService';

/**
 * Custom hook for WebSocket functionality
 * @param {string|string[]} channels - Channel(s) to subscribe to
 * @returns {Object} - WebSocket state and methods
 */
export function useWebSocket(channels) {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState({});

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect()
      .then(() => {
        setConnected(true);
      })
      .catch((error) => {
        console.error('Failed to connect to WebSocket:', error);
        setConnected(false);
      });

    // Cleanup on unmount
    return () => {
      // Note: We don't close the websocket here because it's a singleton
      // and other components might be using it
    };
  }, []);

  useEffect(() => {
    if (!connected || !channels) return;

    const channelArray = Array.isArray(channels) ? channels : [channels];
    const unsubscribers = [];

    // Subscribe to each channel
    channelArray.forEach(channel => {
      const unsubscribe = websocketService.subscribe(channel, (message) => {
        setMessages(prev => ({
          ...prev,
          [channel]: message
        }));
      });

      unsubscribers.push(unsubscribe);
    });

    // Cleanup subscriptions on unmount or when channels change
    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [connected, channels]);

  const sendUpdate = useCallback((channel, data) => {
    websocketService.sendUpdate(channel, data);
  }, []);

  const sendDelete = useCallback((channel, keys) => {
    websocketService.sendDelete(channel, keys);
  }, []);

  return {
    connected,
    messages,
    sendUpdate,
    sendDelete
  };
}
