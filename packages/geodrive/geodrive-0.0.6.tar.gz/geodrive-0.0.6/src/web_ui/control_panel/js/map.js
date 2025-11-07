export class MapManager {
  constructor() {
    this.currentPosition = { x: 0, y: 0, yaw: 0 };
    this.currentVelocity = { vx: 0, vy: 0 };
    this.batteryData = 0;
    this.arenaSize = 11;
  }

  init() {
    this.createGrid();
    this.updatePosition(this.currentPosition);
  }

  createGrid() {
    const mapContainer = document.getElementById("mapContainer");

    // Очищаем старую сетку
    const oldGrid = mapContainer.querySelectorAll(".grid-line");
    oldGrid.forEach((el) => el.remove());

    const totalMeters = this.arenaSize;

    for (let meter = -5; meter <= 5; meter++) {
      const percent = 50 + (meter / 5.5) * 50;

      // Вертикальные линии (X)
      const vLine = document.createElement("div");
      vLine.className = "grid-line vertical";
      vLine.style.left = `${percent}%`;
      mapContainer.appendChild(vLine);

      // Горизонтальные линии (Y)
      const hLine = document.createElement("div");
      hLine.className = "grid-line horizontal";
      hLine.style.top = `${percent}%`;
      mapContainer.appendChild(hLine);
    }

    // Центральные оси
    const centerV = document.createElement("div");
    centerV.className = "grid-line vertical";
    centerV.style.left = "50%";
    centerV.style.background = "rgba(255, 126, 0, 0.3)";
    mapContainer.appendChild(centerV);

    const centerH = document.createElement("div");
    centerH.className = "grid-line horizontal";
    centerH.style.top = "50%";
    centerH.style.background = "rgba(255, 126, 0, 0.3)";
    mapContainer.appendChild(centerH);
  }

  updateBatteryDisplay() {
    const batteryLevel = document.getElementById("batteryLevel");

    const batteryPercent = this.batteryData;
    batteryLevel.style.width = `${batteryPercent}%`;

    if (batteryPercent > 85) {
      batteryLevel.style.background =
        "linear-gradient(90deg, #2ed573, #7bed9f)";
    } else if (batteryPercent > 70) {
      batteryLevel.style.background =
        "linear-gradient(90deg, #ffa502, #ffb142)";
    } else if (batteryPercent > 55) {
      batteryLevel.style.background =
        "linear-gradient(90deg, #ff4757, #ff6b81)";
    } else {
      batteryLevel.style.background =
        "linear-gradient(90deg, #2f3542, #57606f)";
    }
  }

  updatePosition(data) {
    if (data.posX !== undefined) this.currentPosition.x = data.posX;
    if (data.posY !== undefined) this.currentPosition.y = data.posY;
    if (data.yaw !== undefined) this.currentPosition.yaw = data.yaw;

    if (data.velX !== undefined) this.currentVelocity.vx = data.velX;
    if (data.velY !== undefined) this.currentVelocity.vy = data.velY;
    if (data.battery !== undefined) this.batteryData = data.battery;

    this.updateRobotMarker();
    this.updateCoordinatesDisplay();
    this.updateBatteryDisplay();
  }

  updateRobotMarker() {
    const robotSprite = document.getElementById("robotSprite");

    const halfSize = 11 / 2;

    // Масштабирование координат из [-5.5, 5.5] в [0%, 100%]
    const xPercent = 50 + (this.currentPosition.x / halfSize) * 50;
    const yPercent = 50 - (this.currentPosition.y / halfSize) * 50;

    robotSprite.style.left = `${Math.max(0, Math.min(100, xPercent))}%`;
    robotSprite.style.top = `${Math.max(0, Math.min(100, yPercent))}%`;

    // Конвертация радиан в градусы
    const yawDegrees = -this.currentPosition.yaw * (180 / Math.PI) + 90;
    robotSprite.style.transform = `translate(-50%, -50%) rotate(${yawDegrees}deg)`;

    const speed = Math.sqrt(
      this.currentVelocity.vx * this.currentVelocity.vx +
        this.currentVelocity.vy * this.currentVelocity.vy,
    ).toFixed(2);
    if (speed > 0.1) {
      robotSprite.classList.add("moving");
    } else {
      robotSprite.classList.remove("moving");
    }
  }

  updateCoordinatesDisplay() {
    const coordinates = document.getElementById("coordinates");
    coordinates.textContent = `X: ${this.currentPosition.x.toFixed(2)} Y: ${this.currentPosition.y.toFixed(2)} YAW: ${this.currentPosition.yaw.toFixed(2)}`;

    const velocities = document.getElementById("velocities");
    velocities.textContent = `VX: ${this.currentVelocity.vx.toFixed(2)} VY: ${this.currentVelocity.vy.toFixed(2)}`;
  }

  setArenaSize(size) {
    this.arenaSize = size;
    this.createGrid(); // Перерисовываем сетку под новый размер
  }
}
