window.ControlManager = {
    init: function() {
        initMap();
        connect();
    },

    toggleConnection: toggleConnection,
    sendMoo: sendMoo,
    sendBeep: sendBeep,
    startCommand: startCommand,
    stopCommand: stopCommand
};
let ws = null;
let isConnected = false;
let activeCommands = new Set();
let commandInterval = null;
let arenaSize = 11;

// Данные телеметрии
let telemetryData = {
    posX: 0,
    posY: 0,
    velX: 0,
    velY: 0,
    yaw: 0,
    battery: 0,
    speed: 0
};

// Инициализация карты
function initMap() {
    const mapContainer = document.getElementById('mapContainer');
    updateGrid();
}


function updateGrid() {
    const mapContainer = document.getElementById('mapContainer');

    // Очищаем старую сетку
    const oldLines = mapContainer.querySelectorAll('.grid-line');
    oldLines.forEach(line => line.remove());

    const size = arenaSize;
    const step = size / 10;
    const halfSize = arenaSize / 2;

    // Создаем сетку
    for (let i = -5; i <= 5; i++) {
    const position = i * step;
        // Вертикальные линии
        const vLine = document.createElement('div');
        vLine.className = 'grid-line vertical';
        vLine.style.left = `${50 + (position / halfSize) * 50}%`;
        mapContainer.appendChild(vLine);

        // Горизонтальные линии
        const hLine = document.createElement('div');
        hLine.className = 'grid-line horizontal';
        hLine.style.top = `${50 + (position / halfSize) * 50}%`;
        mapContainer.appendChild(hLine);
    }

    // Центральные оси (жирнее)
    const centerV = document.createElement('div');
    centerV.className = 'grid-line vertical';
    centerV.style.left = '50%';
    centerV.style.background = 'rgba(255, 126, 0, 0.3)';
    mapContainer.appendChild(centerV);

    const centerH = document.createElement('div');
    centerH.className = 'grid-line horizontal';
    centerH.style.top = '50%';
    centerH.style.background = 'rgba(255, 126, 0, 0.3)';
    mapContainer.appendChild(centerH);
}

// Обновление позиции на карте
function updateMapPosition() {
    const robotSprite = document.getElementById('robotSprite');
    const coordinates = document.getElementById('coordinates');

    const halfSize = arenaSize / 2;

    // Масштабируем координаты из [-halfSize, halfSize] в [0%, 100%]
    const xPercent = 50 + (telemetryData.posX / halfSize) * 50;
    const yPercent = 50 - (telemetryData.posY / halfSize) * 50;

    robotSprite.style.left = `${Math.max(0, Math.min(100, xPercent))}%`;
    robotSprite.style.top = `${Math.max(0, Math.min(100, yPercent))}%`;

    const yawDegrees = -telemetryData.yaw * (180 / Math.PI) + 90;
    robotSprite.style.transform = `translate(-50%, -50%) rotate(${yawDegrees}deg)`;

    if (telemetryData.speed > 0.1) {
        robotSprite.classList.add('moving');
    } else {
        robotSprite.classList.remove('moving');
    }

    // Обновляем координаты
    coordinates.textContent = `X: ${telemetryData.posX.toFixed(2)} Y: ${telemetryData.posY.toFixed(2)}`;
}

// Обновление батареи
function updateBatteryDisplay() {
    const batteryLevel = document.getElementById('batteryLevel');
    const batteryPercentage = document.getElementById('batteryPercentage');
    const batteryStatus = document.getElementById('batteryStatus');

    const batteryPercent = telemetryData.battery;
    batteryLevel.style.width = `${batteryPercent}%`;
    batteryPercentage.textContent = `${batteryPercent}%`;

    // Меняем цвет в зависимости от уровня заряда
    if (batteryPercent > 85) {
        batteryLevel.style.background = 'linear-gradient(90deg, #2ed573, #7bed9f)';
        batteryStatus.textContent = 'Отличное состояние';
    } else if (batteryPercent > 70) {
        batteryLevel.style.background = 'linear-gradient(90deg, #ffa502, #ffb142)';
        batteryStatus.textContent = 'Средний заряд';
    } else if (batteryPercent > 55) {
        batteryLevel.style.background = 'linear-gradient(90deg, #ff4757, #ff6b81)';
        batteryStatus.textContent = 'Низкий заряд';
    } else {
        batteryLevel.style.background = 'linear-gradient(90deg, #2f3542, #57606f)';
        batteryStatus.textContent = 'Требуется зарядка';
    }
}

function toggleConnection() {
    if (isConnected) {
        disconnect();
    } else {
        connect();
    }
}

function connect() {
    const address = "ws://localhost:8765";

    try {
        ws = new WebSocket(address);

        ws.onopen = () => {
            isConnected = true;
            console.log('WebSocket подключен');
        };

        ws.onclose = () => {
            isConnected = false;
            console.log('WebSocket отключен');
            stopSending();
        };

        ws.onerror = (error) => {
            console.error('WebSocket ошибка:', error);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === "telemetry") {
                    processTelemetryData(data);
                }
                if (data.type === "config") {
                    arenaSize = data.arena_size;
                    const roverIdElement = document.getElementById('rover-id');
                    roverIdElement.textContent = data.rover_id
                    updateGrid();
                }
            } catch (error) {
                console.error('Ошибка парсинга JSON:', error);
                console.log('Получено сообщение:', event.data);
            }
        };

    } catch (error) {
        alert('Ошибка подключения: ' + error.message);
    }
}

function processTelemetryData(data) {
    // Обрабатываем данные телеметрии
    if (data.posX !== undefined) telemetryData.posX = data.posX;
    if (data.posY !== undefined) telemetryData.posY = data.posY;
    if (data.velX !== undefined) telemetryData.velX = data.velX;
    if (data.velY !== undefined) telemetryData.velY = data.velY;
    if (data.yaw !== undefined) telemetryData.yaw = data.yaw;
    if (data.battery !== undefined) telemetryData.battery = data.battery;

    // Вычисляем общую скорость
    telemetryData.speed = Math.sqrt(
        telemetryData.velX * telemetryData.velX +
        telemetryData.velY * telemetryData.velY
    ).toFixed(2);

    updateTelemetryDisplay();
    updateMapPosition();
    updateBatteryDisplay();
}

function updateTelemetryDisplay() {
    document.getElementById('posX').textContent = telemetryData.posX.toFixed(2) + ' м';
    document.getElementById('posY').textContent = telemetryData.posY.toFixed(2) + ' м';
    document.getElementById('velX').textContent = telemetryData.velX.toFixed(2) + ' м/с';
    document.getElementById('velY').textContent = telemetryData.velY.toFixed(2) + ' м/с';
    document.getElementById('yaw').textContent = (telemetryData.yaw * (180 / Math.PI)).toFixed(2) + '°';
    document.getElementById('speed').textContent = telemetryData.speed + ' м/с';
}

function disconnect() {
    if (ws) {
        ws.close();
        ws = null;
    }
    isConnected = false;
    stopSending();
    activeCommands.clear();
    updateActiveCommandsDisplay();

    // Сбрасываем телеметрию
    telemetryData = { posX: 0, posY: 0, velX: 0, velY: 0, yaw: 0, battery: 0, speed: 0 };
    updateTelemetryDisplay();
    updateMapPosition();
    updateBatteryDisplay();
}

function startCommand(command) {
    if (!isConnected) {
        alert('Сначала подключитесь к серверу');
        return;
    }

    activeCommands.add(command);
    updateActiveCommandsDisplay();
    sendCombinedCommand();

    if (!commandInterval) {
        commandInterval = setInterval(() => {
            sendCombinedCommand();
        }, 100);
    }
}

function stopCommand(command) {
    activeCommands.delete(command);
    updateActiveCommandsDisplay();

    if (activeCommands.size === 0) {
        stopSending();
        sendStop();
    } else {
        sendCombinedCommand();
    }
}

function stopSending() {
    if (commandInterval) {
        clearInterval(commandInterval);
        commandInterval = null;
    }
}

function sendCombinedCommand() {
    if (!isConnected || !ws || activeCommands.size === 0) return;

    const channels = {
        channel1: 1500, // Steering
        channel2: 1500, // Moo command
        channel3: 1500, // Throttle
        channel4: 1500  // Beep command
    };

    activeCommands.forEach(cmd => {
        switch(cmd) {
            case 'forward':
                channels.channel3 = 1000; // Вперед
                break;
            case 'backward':
                channels.channel3 = 2000; // Назад
                break;
            case 'left':
                channels.channel1 = 2000; // Влево
                break;
            case 'right':
                channels.channel1 = 1000; // Вправо
                break;
        }
    });

    ws.send(JSON.stringify(channels));
    console.log('Отправлено:', channels, 'Активные команды:', Array.from(activeCommands));
}

function sendStop() {
    if (!isConnected || !ws) return;

    const channels = {
        channel1: 1500,
        channel2: 1500,
        channel3: 1500,
        channel4: 1500
    };

    ws.send(JSON.stringify(channels));
    console.log('Остановка');
}

function sendMoo() {
    if (!isConnected || !ws) return;

    const channels = {
        channel1: 1500,
        channel2: 1000, // Moo command
        channel3: 1500,
        channel4: 1500
    };

    ws.send(JSON.stringify(channels));
    console.log('Moo command sent');

    setTimeout(() => {
        channels.channel2 = 1500;
        if (isConnected && ws) {
            ws.send(JSON.stringify(channels));
        }
    }, 500);
}

function sendBeep() {
    if (!isConnected || !ws) return;

    const channels = {
        channel1: 1500,
        channel2: 1500,
        channel3: 1500,
        channel4: 1000  // Beep command
    };

    ws.send(JSON.stringify(channels));
    console.log('Beep command sent');

    setTimeout(() => {
        channels.channel4 = 1500;
        if (isConnected && ws) {
            ws.send(JSON.stringify(channels));
        }
    }, 500);
}

function updateActiveCommandsDisplay() {
    const activeCommandsElement = document.getElementById('activeCommands');
    const commandsListElement = document.getElementById('commandsList');

    if (activeCommands.size > 0) {
        const commandNames = Array.from(activeCommands).map(cmd => {
            switch(cmd) {
                case 'forward': return 'Вперед';
                case 'backward': return 'Назад';
                case 'left': return 'Влево';
                case 'right': return 'Вправо';
                default: return cmd;
            }
        });
        commandsListElement.innerHTML = commandNames.join(', ');
        activeCommandsElement.style.display = 'block';
    } else {
        activeCommandsElement.style.display = 'none';
    }
}

// Обработка клавиатуры
document.addEventListener('keydown', (e) => {
    if (!isConnected) return;

    const key = e.key.toLowerCase();
    let command = null;

    switch(key) {
        case 'w': command = 'forward'; break;
        case 's': command = 'backward'; break;
        case 'a': command = 'left'; break;
        case 'd': command = 'right'; break;
        case 'm':
            sendMoo();
            e.preventDefault();
            return;
        case 'b':
            sendBeep();
            e.preventDefault();
            return;
    }

    if (command && !activeCommands.has(command)) {
        startCommand(command);
        e.preventDefault();
    } else if (key === ' ') {
        sendStop();
        activeCommands.clear();
        updateActiveCommandsDisplay();
        e.preventDefault();
    }
});

document.addEventListener('keyup', (e) => {
    const key = e.key.toLowerCase();
    let command = null;

    switch(key) {
        case 'w': command = 'forward'; break;
        case 's': command = 'backward'; break;
        case 'a': command = 'left'; break;
        case 'd': command = 'right'; break;
    }

    if (command && activeCommands.has(command)) {
        stopCommand(command);
        e.preventDefault();
    }
});