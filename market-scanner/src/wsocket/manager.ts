type ListenerCallback = (payload: any) => void;

class WebSocketManager {
  private url: string;
  private socket: WebSocket | null;
  private listeners: Map<string, ListenerCallback[]>;
  private reconnectInterval: number = 5000;

  constructor(url: string) {
    this.url = url;
    this.socket = null;
    this.listeners = new Map<string, ListenerCallback[]>();
  }

  private handleReconnect(): void {
    console.log("Attempting to reconnect...");
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  connect(): void {
    if (this.socket) {
      console.warn("WebSocket is already connected.");
      return;
    }

    console.log("Attempting to connect to WebSocket...");
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("WebSocket connection established.");
    };

    this.socket.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      console.log(data)
      this.notifyListeners(data.event, data.payload);
    };

    this.socket.onclose = () => {
      console.log("WebSocket connection closed.");
      this.socket = null;
      this.handleReconnect();
    };

    this.socket.onerror = (error: Event) => {
      console.error("WebSocket error:", error);
    };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    } else {
      console.warn("WebSocket is not connected.");
    }
  }

  sendMessage(event: string, payload: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ event, payload }));
    } else {
      console.error("WebSocket is not connected or not ready.");
    }
  }

  addListener(event: string, callback: ListenerCallback): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  removeListener(event: string, callback: ListenerCallback): void {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)?.filter((cb) => cb !== callback) || [];
      this.listeners.set(event, callbacks);
    }
  }

  private notifyListeners(event: string, payload: any): void {
    if (this.listeners.has(event)) {
      this.listeners.get(event)?.forEach((callback) => callback(payload));
    }
  }
}

export default WebSocketManager;