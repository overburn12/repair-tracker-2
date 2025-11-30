import { useState, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { getIdFromKey } from '@utils/keyUtils';

/**
 * Custom hook to manage orders data from WebSocket
 * @returns {Object} - Orders data and methods
 */
export function useOrdersData() {
  const [orders, setOrders] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Subscribe to main:orders and main:status channels
  const { connected, messages, sendUpdate, sendDelete } = useWebSocket(['main:orders', 'main:status']);

  // Handle orders channel messages
  useEffect(() => {
    const ordersMessage = messages['main:orders'];
    if (!ordersMessage) return;

    try {
      if (ordersMessage.type === 'update') {
        // Upsert orders
        setOrders(prevOrders => {
          const newOrders = [...prevOrders];

          ordersMessage.data.forEach(orderData => {
            const index = newOrders.findIndex(o => o.id === orderData.id);
            if (index >= 0) {
              // Update existing
              newOrders[index] = orderData;
            } else {
              // Add new
              newOrders.push(orderData);
            }
          });

          return newOrders;
        });
        setLoading(false);
      } else if (ordersMessage.type === 'delete') {
        // Delete orders by key
        setOrders(prevOrders => {
          const keysToDelete = new Set(ordersMessage.data.map(key => getIdFromKey(key)));
          return prevOrders.filter(o => !keysToDelete.has(o.id));
        });
      }
    } catch (err) {
      console.error('Error processing orders message:', err);
      setError(err.message);
    }
  }, [messages]);

  // Handle statuses channel messages
  useEffect(() => {
    const statusesMessage = messages['main:status'];
    if (!statusesMessage) return;

    try {
      if (statusesMessage.type === 'update') {
        // Upsert statuses
        setStatuses(prevStatuses => {
          const newStatuses = [...prevStatuses];

          statusesMessage.data.forEach(statusData => {
            const index = newStatuses.findIndex(s => s.id === statusData.id);
            if (index >= 0) {
              // Update existing
              newStatuses[index] = statusData;
            } else {
              // Add new
              newStatuses.push(statusData);
            }
          });

          return newStatuses;
        });
      } else if (statusesMessage.type === 'delete') {
        // Delete statuses by key
        setStatuses(prevStatuses => {
          const keysToDelete = new Set(statusesMessage.data.map(key => getIdFromKey(key)));
          return prevStatuses.filter(s => !keysToDelete.has(s.id));
        });
      }
    } catch (err) {
      console.error('Error processing statuses message:', err);
      setError(err.message);
    }
  }, [messages]);

  // Add new order
  const addOrder = (name) => {
    sendUpdate('main:orders', [{ name }]);
  };

  return {
    orders,
    statuses,
    loading,
    error,
    connected,
    addOrder
  };
}
