import { logger } from "./logger.js";

export class RoutePlanner {
  constructor() {
    this.arenaSize = 11;
    this.targetPosition = null;
    this.contextMenuHandlers = [];

    this.waypoints = [];
    this.isRouteActive = false;
    this.currentWaypointIndex = 0;
    this.routeLines = [];
  }

  init() {
    this.setupContextMenu();
    this.setupRoutePanel();
  }

  setupContextMenu() {
    const mapContainer = document.getElementById("mapContainer");
    const contextMenu = document.getElementById("mapContextMenu");
    const targetMarker = document.getElementById("targetMarker");
    const sendToPointBtn = document.getElementById("sendToPoint");

    // Открытие контекстного меню по правой кнопке
    mapContainer.addEventListener("contextmenu", (e) => {
      e.preventDefault();

      // Получаем координаты клика относительно карты
      const rect = mapContainer.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickY = e.clientY - rect.top;

      // Конвертируем в проценты
      const xPercent = (clickX / rect.width) * 100;
      const yPercent = (clickY / rect.height) * 100;

      // Конвертируем в координаты ровера
      const halfSize = this.arenaSize / 2;
      const targetX = ((xPercent - 50) / 50) * halfSize;
      const targetY = -((yPercent - 50) / 50) * halfSize;

      // Сохраняем целевую позицию
      this.targetPosition = { x: targetX, y: targetY };

      // Показываем маркер цели
      targetMarker.style.left = `${xPercent}%`;
      targetMarker.style.top = `${yPercent}%`;
      targetMarker.style.display = "block";

      // Показываем контекстное меню
      contextMenu.style.left = `${e.clientX}px`;
      contextMenu.style.top = `${e.clientY}px`;
      contextMenu.style.display = "block";
    });

    // Закрытие контекстного меню
    document.addEventListener("click", (e) => {
      if (!contextMenu.contains(e.target)) {
        contextMenu.style.display = "none";
      }
    });

    // Обработка выбора "Отправить ровер в точку"
    sendToPointBtn.addEventListener("click", () => {
      if (this.targetPosition) {
        this.sendToPoint(this.targetPosition);
        contextMenu.style.display = "none";
      }
    });

    document.getElementById("addWaypoint").addEventListener("click", () => {
      if (this.targetPosition) {
        this.addWaypoint(this.targetPosition);
        contextMenu.style.display = "none";
      }
    });

    document.getElementById("clearRoute").addEventListener("click", () => {
      this.clearRoute();
      contextMenu.style.display = "none";
    });

    document.getElementById("startRoute").addEventListener("click", () => {
      this.startRoute();
      contextMenu.style.display = "none";
    });

    // Закрытие по ESC
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        contextMenu.style.display = "none";
        targetMarker.style.display = "none";
      }
    });
  }

  setupRoutePanel() {
    document.getElementById("routeClear").addEventListener("click", () => {
      this.clearRoute();
    });

    document.getElementById("routeStart").addEventListener("click", () => {
      this.startRoute();
    });

    document.getElementById("routeStop").addEventListener("click", () => {
      this.stopRoute();
    });

    document.getElementById("routeSave").addEventListener("click", () => {
      this.saveRoute();
    });

    document.getElementById("routeLoad").addEventListener("click", () => {
      this.loadRoute();
    });
  }

  getCoordinatesFromClick(e) {
    const mapContainer = document.getElementById("mapContainer");
    const rect = mapContainer.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    // Конвертируем в проценты
    const xPercent = (clickX / rect.width) * 100;
    const yPercent = (clickY / rect.height) * 100;

    // Конвертируем в координаты ровера
    const halfSize = this.arenaSize / 2;
    const targetX = ((xPercent - 50) / 50) * halfSize;
    const targetY = -((yPercent - 50) / 50) * halfSize;

    return { targetX, targetY, xPercent, yPercent };
  }

  // Сохранение маршрута
  saveRoute() {
    const routeData = {
      waypoints: this.waypoints,
      timestamp: new Date().toISOString(),
      name: `geodrive_route_${new Date().toLocaleDateString()}`,
    };

    const dataStr = JSON.stringify(routeData);
    const dataBlob = new Blob([dataStr], { type: "application/json" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(dataBlob);
    link.download = `route_${Date.now()}.json`;
    link.click();

    this.notifyContextMenuHandlers({
      type: "route_saved",
      route: routeData,
    });
  }

  // Загрузка маршрута
  loadRoute() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";

    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const routeData = JSON.parse(event.target.result);
          this.waypoints = routeData.waypoints || [];
          this.updateRouteDisplay();
          this.drawRouteLines();

          this.notifyContextMenuHandlers({
            type: "route_loaded",
            route: routeData,
          });
        } catch (error) {
          logger.error(`Ошибка загрузки маршрута: ${error}`);
        }
      };
      reader.readAsText(file);
    };

    input.click();
  }

  showTargetMarker(xPercent, yPercent) {
    const targetMarker = document.getElementById("targetMarker");
    targetMarker.style.left = `${xPercent}%`;
    targetMarker.style.top = `${yPercent}%`;
    targetMarker.style.display = "block";
  }

  hideTargetMarker() {
    document.getElementById("targetMarker").style.display = "none";
  }

  addWaypoint(position) {
    const waypoint = {
      id: Date.now() + Math.random(),
      x: position.x,
      y: position.y,
      order: this.waypoints.length + 1,
    };

    this.waypoints.push(waypoint);
    this.updateRouteDisplay();
    this.drawRouteLines();

    this.notifyContextMenuHandlers({
      type: "waypoint_added",
      waypoint: waypoint,
    });
  }

  removeWaypoint(waypointId) {
    this.waypoints = this.waypoints.filter((wp) => wp.id !== waypointId);
    this.updateRouteDisplay();
    this.drawRouteLines();
  }

  clearRoute() {
    this.waypoints = [];
    this.isRouteActive = false;
    this.currentWaypointIndex = 0;
    this.updateRouteDisplay();
    this.clearRouteLines();
    this.hideTargetMarker();

    this.notifyContextMenuHandlers({
      type: "route_cleared",
    });
  }

  startRoute() {
    if (this.waypoints.length === 0) {
      logger.warning("Нет точек маршрута");
      return;
    }
    const routeStatusElement = document.getElementById("routeStatus");
    routeStatusElement.textContent = "В движении";

    this.isRouteActive = true;
    this.currentWaypointIndex = 0;
    this.navigateToWaypoint(this.currentWaypointIndex);

    this.notifyContextMenuHandlers({
      type: "route_started",
      waypoints: this.waypoints,
    });
  }

  stopRoute() {
    this.isRouteActive = false;
    const routeStatusElement = document.getElementById("routeStatus");
    routeStatusElement.textContent = "Остановлен";
    this.notifyContextMenuHandlers({
      type: "route_stopped",
    });
  }

  navigateToWaypoint(index) {
    if (index >= this.waypoints.length) {
      this.stopRoute();
      return;
    }

    const waypoint = this.waypoints[index];
    this.sendToPoint(waypoint);
    this.highlightCurrentWaypoint(index);
  }

  highlightCurrentWaypoint(index) {
    const waypointElements = document.querySelectorAll(".waypoint-marker");
    waypointElements.forEach((el, i) => {
      if (i === index) {
        el.classList.add("current");
      } else {
        el.classList.remove("current");
      }
    });
  }

  updateRouteDisplay() {
    const waypointsList = document.getElementById("waypointsList");
    const routeOverlay = document.getElementById("routeOverlay");
    const waypointsCount = document.getElementById("waypointsCount");

    // Очищаем списки
    waypointsList.innerHTML = "";
    routeOverlay.innerHTML = "";

    // Обновляем стату
    waypointsCount.textContent = this.waypoints.length;
    // Добавляем точки маршрута
    this.waypoints.forEach((waypoint, index) => {
      // Добавляем в список
      const waypointElement = document.createElement("div");
      waypointElement.className = "waypoint-item";
      waypointElement.innerHTML = `
                <span class="waypoint-order">${index + 1}</span>
                <span class="waypoint-coords">X: ${waypoint.x.toFixed(2)} Y: ${waypoint.y.toFixed(2)}</span>
                <button class="waypoint-remove" data-id="${waypoint.id}">×</button>
            `;
      waypointsList.appendChild(waypointElement);

      // Добавляем на карту
      const waypointMarker = document.createElement("div");
      waypointMarker.className = "waypoint-marker";
      waypointMarker.setAttribute("data-id", waypoint.id);

      const xPercent = 50 + (waypoint.x / (this.arenaSize / 2)) * 50;
      const yPercent = 50 - (waypoint.y / (this.arenaSize / 2)) * 50;

      waypointMarker.style.left = `${xPercent}%`;
      waypointMarker.style.top = `${yPercent}%`;
      waypointMarker.innerHTML = `
                <div class="waypoint-number">${index + 1}</div>
            `;
      routeOverlay.appendChild(waypointMarker);

      // Обработчик удаления
      waypointElement
        .querySelector(".waypoint-remove")
        .addEventListener("click", (e) => {
          e.stopPropagation();
          this.removeWaypoint(waypoint.id);
        });
    });
  }

  drawRouteLines() {
    this.clearRouteLines();

    if (this.waypoints.length < 2) return;

    const routeOverlay = document.getElementById("routeOverlay");

    for (let i = 0; i < this.waypoints.length - 1; i++) {
      const start = this.waypoints[i];
      const end = this.waypoints[i + 1];

      const startX = 50 + (start.x / (this.arenaSize / 2)) * 50;
      const startY = 50 - (start.y / (this.arenaSize / 2)) * 50;
      const endX = 50 + (end.x / (this.arenaSize / 2)) * 50;
      const endY = 50 - (end.y / (this.arenaSize / 2)) * 50;

      const line = document.createElement("div");
      line.className = "route-line";

      // Вычисляем длину и угол линии
      const dx = endX - startX;
      const dy = endY - startY;
      const length = Math.sqrt(dx * dx + dy * dy);
      const angle = Math.atan2(dy, dx) * (180 / Math.PI);

      line.style.width = `${length}%`;
      line.style.left = `${startX}%`;
      line.style.top = `${startY}%`;
      line.style.transform = `rotate(${angle}deg)`;
      line.style.transformOrigin = "0 0";

      routeOverlay.appendChild(line);
      this.routeLines.push(line);
    }
  }

  clearRouteLines() {
    this.routeLines.forEach((line) => line.remove());
    this.routeLines = [];
  }

  sendToPoint(targetPos) {
    // Уведомляем обработчики о команде перемещения
    this.notifyContextMenuHandlers({
      type: "navigate_to_point",
      target: targetPos,
    });

    console.log(
      `Отправка ровера в точку: X=${targetPos.x.toFixed(2)}, Y=${targetPos.y.toFixed(2)}`,
    );
  }

  onContextMenu(handler) {
    this.contextMenuHandlers.push(handler);
  }

  notifyContextMenuHandlers(data) {
    this.contextMenuHandlers.forEach((handler) => handler(data));
  }
}
