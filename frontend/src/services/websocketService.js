/**
 * WebSocket Service
 * Handles WebSocket connection, subscriptions, and message handling
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.websocketId = null;
    this.connected = false;
    this.subscribers = new Map(); // channel -> Set of callbacks
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    return new Promise((resolve, reject) => {
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.connected = false;
        this.websocketId = null;
        this.attemptReconnect();
      };
    });
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect()
        .then(() => {
          // Re-subscribe to all channels after reconnect
          const channels = Array.from(this.subscribers.keys());
          if (channels.length > 0) {
            this.subscribeToChannels(channels);
          }
        })
        .catch((error) => {
          console.error('Reconnection failed:', error);
        });
    }, delay);
  }

  /**
   * Handle incoming WebSocket message
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data);

      // Handle connection confirmation
      if (message.type === 'connected') {
        this.websocketId = message.websocket_id;
        console.log('WebSocket ID:', this.websocketId);
        return;
      }

      // Handle channel messages
      if (message.channel) {
        const callbacks = this.subscribers.get(message.channel);
        if (callbacks) {
          callbacks.forEach(callback => callback(message));
        }
      }

      // Handle __messages__ channel (errors)
      if (message.channel === '__messages__') {
        console.error('WebSocket error message:', message);
      }

    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Subscribe to one or more channels
   * @param {string|string[]} channels - Channel name(s) to subscribe to
   */
  subscribeToChannels(channels) {
    const channelArray = Array.isArray(channels) ? channels : [channels];

    const message = {
      type: 'subscribe',
      channels: channelArray
    };

    this.send(message);
  }

  /**
   * Subscribe to a channel with a callback
   * @param {string} channel - Channel name
   * @param {Function} callback - Callback function to handle messages
   */
  subscribe(channel, callback) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
      // Subscribe to the channel on the server
      this.subscribeToChannels(channel);
    }

    this.subscribers.get(channel).add(callback);

    // Return unsubscribe function
    return () => {
      this.unsubscribe(channel, callback);
    };
  }

  /**
   * Unsubscribe from a channel
   * @param {string} channel - Channel name
   * @param {Function} callback - Callback function to remove
   */
  unsubscribe(channel, callback) {
    const callbacks = this.subscribers.get(channel);
    if (callbacks) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.subscribers.delete(channel);
      }
    }
  }

  /**
   * Send an update message to the server
   * @param {string} channel - Channel name
   * @param {object[]} data - Array of data objects to update
   */
  sendUpdate(channel, data) {
    const message = {
      type: 'update',
      channel,
      data
    };

    this.send(message);
  }

  /**
   * Send a delete message to the server
   * @param {string} channel - Channel name
   * @param {string[]} keys - Array of keys to delete
   */
  sendDelete(channel, keys) {
    const message = {
      type: 'delete',
      channel,
      data: keys
    };

    this.send(message);
  }

  /**
   * Send a message to the WebSocket server
   * @param {object} message - Message object to send
   */
  send(message) {
    if (this.ws && this.connected) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
    }
  }

  /**
   * Close the WebSocket connection
   */
  close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
      this.websocketId = null;
      this.subscribers.clear();
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
