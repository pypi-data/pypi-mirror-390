import { WebSocketManager } from "./websocket.js";
import { ControlsManager } from "./control.js";
import { MapManager } from "./map.js";
import { Configurator } from "./configurator.js";
import { RoutePlanner } from "./route_planner.js";

class GeodriveControlPanel {
  constructor() {
    this.modules = {};
    this.roverApiBase = "http://localhost:8000";
    this.roverAddress = "localhost";
    this.arenaSize = 11;
  }

  async init() {
    this.modules.websocket = new WebSocketManager();
    this.modules.controls = new ControlsManager();
    this.modules.map = new MapManager();
    this.modules.configurator = new Configurator();
    this.modules.route_planner = new RoutePlanner();

    this.setupModuleConnections();

    this.initTabs();

    await this.initModules();

    console.log("GEODRIVE Control Panel инициализирована");
  }

  initTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");

    tabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const tabId = button.getAttribute("data-tab");

        // Убираем активный класс у всех кнопок и контента
        tabButtons.forEach((btn) => btn.classList.remove("active"));
        document
          .querySelectorAll(".tab-content")
          .forEach((content) => content.classList.remove("active"));

        // Добавляем активный класс текущей кнопке и соответствующему контенту
        button.classList.add("active");
        document.getElementById(`${tabId}-tab`).classList.add("active");
      });
    });
  }

  setupModuleConnections() {
    this.modules.route_planner.onContextMenu((data) => {
      if (data.type === "navigate_to_point") {
        // Отправляем команду через WebSocket
        this.modules.websocket.sendCommand({
          type: "navigate_to_point",
          target_x: data.target.x,
          target_y: data.target.y,
        });

        this.modules.configurator.log(
          `Навигация к точке: X=${data.target.x.toFixed(2)}, Y=${data.target.y.toFixed(2)}`,
          "info",
        );
      }
    });
    this.modules.websocket.onMessage((data) => {
      if (data.type === "config") {
        if (data.rover_address) {
          this.roverAddress = data.rover_address;
          this.roverApiBase = `http://${data.rover_address}:8000`;
          this.modules.configurator.setApiBase(this.roverApiBase);
        }
      }

      if (data.type === "telemetry") {
        this.modules.map.updatePosition(data);
      }
      if (data.type === "log") {
        this.modules.configurator.log(data.message, data.msg_type);
      }
    });

    //        this.modules.controls.onCommand((command) => {
    //            this.modules.websocket.sendCommand(command);
    //        });

    this.modules.configurator.onConfigApply((config) => {
      this.applyConfiguration(config);
    });
  }

  async initModules() {
    this.modules.map.init();
    this.modules.controls.init();
    this.modules.route_planner.init();
    await this.modules.configurator.init();
    this.modules.websocket.connect();
  }

  async applyConfiguration(config) {
    try {
      const response = await fetch(`${this.roverApiBase}/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        this.modules.configurator.log("Конфигурация применена");
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      this.modules.configurator.log(`Ошибка: ${error.message}`, "error");
    }
  }
}

const app = new GeodriveControlPanel();
app.init().catch(console.error);

window.GeodriveControlPanel = GeodriveControlPanel;
window.app = app;
