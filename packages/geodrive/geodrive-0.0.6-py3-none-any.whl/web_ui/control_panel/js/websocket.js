import { logger } from "./logger.js";

export class WebSocketManager {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.messageHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(address = "ws://localhost:8765") {
    try {
      this.ws = new WebSocket(address);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyStatus("connected", "Подключено к серверу");
        logger.success("WebSocket подключен");
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyStatus("disconnected", "Соединение разорвано");
        this.handleReconnect();
      };

      this.ws.onerror = (error) => {
        logger.error(`WebSocket ошибка: ${error.message}`);
        this.notifyStatus("error", "Ошибка подключения");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyMessageHandlers(data);
        } catch (error) {
          console.log("Невалидный JSON:", event.data);
        }
      };
    } catch (error) {
      logger.error(`Ошибка создания WebSocket: ${error.message}`);
      this.notifyStatus("error", `Ошибка: ${error.message}`);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.notifyStatus("disconnected", "Отключено вручную");
  }

  sendCommand(command) {
    if (!this.isConnected || !this.ws) {
      console.warn("WebSocket не подключен");
      return;
    }

    this.ws.send(JSON.stringify(command));
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  notifyMessageHandlers(data) {
    this.messageHandlers.forEach((handler) => handler(data));
  }

  notifyStatus(status, message) {
    const event = new CustomEvent("websocket-status", {
      detail: { status, message },
    });
    document.dispatchEvent(event);
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Попытка переподключения ${this.reconnectAttempts}`);
        this.connect();
      }, 2000 * this.reconnectAttempts);
    }
  }
}
