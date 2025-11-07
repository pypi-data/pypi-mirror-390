var ws_server = `wss://arena.geoscan.aero/webrtc`;
var rtc_configuration = {iceServers: [ {urls: ["stun:10.1.100.6:30000", "stun:10.10.33.11:30000", "stun:arena.geoscan.aero:30000"]},
                                    {urls: ["turn:10.1.100.6:30000", "turn:10.10.33.11:30000", "turn:arena.geoscan.aero:30000"],
                                    username: "test",
                                    credential: "test"},]};

var peer_connection;
var ws_conn;
var offet_request_cd = null;

// Генерация ID для подключения WebRTC
const get_id = () => {
    return Math.floor(Math.random() * (9000 - 10) + 10).toString();
}

// Обработка ошибки, связанной с JSON, во время соединения
const handle_incoming_error = (error) => {
    console.log("Ошибка: " + error);
    ws_conn.close();
}
function showNoVideoSignal() {
    const noVideoElement = document.getElementById('noVideoSignal');
    if (noVideoElement) {
        noVideoElement.classList.add('active');
    }
}

function hideNoVideoSignal() {
    const noVideoElement = document.getElementById('noVideoSignal');
    if (noVideoElement) {
        noVideoElement.classList.remove('active');
    }
}

// Создание новго видеоэлемента на странице
const create_video_element = () => {
    var div = document.getElementById("videoControls");

    hideNoVideoSignal();

    const oldVideos = div.querySelectorAll('video');
    oldVideos.forEach(video => video.remove());

    var video_tag = document.createElement("video");
    video_tag.textContent = "Your browser doesn't support video";
    video_tag.muted = true;
    video_tag.autoplay = true;
    video_tag.playsinline = true;

    video_tag.onloadeddata = () => {
        console.log("Видео поток активирован");
        hideNoVideoSignal();
    };

    video_tag.onerror = () => {
        console.log("Ошибка видео потока");
        showNoVideoSignal();
    };

    div.appendChild(video_tag);
    return video_tag
}


// Сброс видео
const reset_video = () => {
    // Разрыв соединения, по которому передавалось видео
    if (peer_connection) {
        peer_connection.close();
        peer_connection = null;
    }

    // Удаление видеоэлемента со страницы
    document.getElementById("videoControls").innerHTML = "";
}

// Получение запроса SDP от объекта, создание удаленного SDP и ответа
const on_incoming_sdp = (sdp) => {
    peer_connection.setRemoteDescription(sdp).then(() => {
        console.log("Получен SDP объекта");
        peer_connection.createAnswer().then(on_local_description).catch(console.log);
    }).catch(console.log);
}

// Создание локального SDP и его отправка объекту
const on_local_description = (desc) => {
    console.log("Получен локальный SDP");
    peer_connection.setLocalDescription(desc).then(() => {
        console.log("Отправка локального SDP");
        sdp = {'sdp': peer_connection.localDescription}
        ws_conn.send(JSON.stringify(sdp));
    });
}

// Получение ICE от объекта и их добавление в соединение
const on_incoming_ice = (ice) => {
    var candidate = new RTCIceCandidate(ice);
    peer_connection.addIceCandidate(candidate).catch(console.log);
}

// Получение сообщения от WS сервера
const on_server_message = (event) => {
    clearTimeout(offet_request_cd);
    switch (event.data) {
        case "HELLO":
            console.log("Выполнена регистрация на сервере. Ожидание подключения...");
            return;
        case "SESSION_OK":
            console.log("Начато соединение с объектом");
            ws_conn.send("OFFER_REQUEST");
            console.log("Отправлен запрос. Ожидание ответа...");
            return;
        case "OFFER_REQUEST":
            offet_request_cd = setTimeout(() => { reconnect() }, 10000);
            return;
        default:
            if (event.data.startsWith("ERROR")) {
                handle_incoming_error(event.data);
                return;
            }
            try {
                msg = JSON.parse(event.data);
            } catch (e) {
                if (e instanceof SyntaxError) {
                    handle_incoming_error("Error parsing incoming JSON: " + event.data);
                } else {
                    handle_incoming_error("Unknown error parsing response: " + event.data);
                }
                return;
            }

            if (!peer_connection)
                create_сall(msg);

            if (msg.sdp != null) {
                on_incoming_sdp(msg.sdp);
            } else if (msg.ice != null) {
                on_incoming_ice(msg.ice);
            } else {
                handle_incoming_error("Получен неизвестный JSON: " + msg);
            }
    }
}

// Отключение от WS сервера
const on_server_close = (event) => {
    console.log("Отключен от WebSocket сервера для WebRTC");
    reconnect();
}

// Переподключение к WS серверу
const reconnect = () => {
    ws_conn.onmessage = null;
    ws_conn.onerror = null;
    ws_conn.onclose = null;
    delete ws_conn;
    setTimeout(websocket_server_connect, 1000);
}

// Получение ошибки от WS сервера
const on_server_error = (event) => {
    console.log("Ошибка подключения к WebSocket WebRTC")
    reconnect();
}

// Подключение к WS серверу
const websocket_server_connect = () => {
    var peer_id = get_id();

    var ws_url = ws_server
    console.log(`Попытка подключения к WebSocket WebRTC серверу ${ws_url}`);
    ws_conn = new WebSocket(ws_url);
    const roverIdElement = document.getElementById('rover-id');
    const rover_id = roverIdElement.textContent
    ws_conn.onopen = () => {
        console.log("Выполнено подключение к серверу");
        reset_video();
        ws_conn.send(`HELLO ${peer_id}`);
        ws_conn.send(`SESSION ${rover_id}`);
    };
    ws_conn.onerror = on_server_error;
    ws_conn.onmessage = on_server_message;
    ws_conn.onclose = on_server_close;
}

// Получение видео от объекта
const on_remote_track = (event) => {
    var videoElem = create_video_element();
    if (event.track.kind === 'audio')
        videoElem.style = 'display: none;';
    videoElem.srcObject = new MediaStream([event.track]);
}

// Создание соединения
const create_сall = (msg) => {
    console.log('Создание RTC соединения');

    peer_connection = new RTCPeerConnection(rtc_configuration);
    send_channel = peer_connection.createDataChannel('label', null);
    peer_connection.ontrack = on_remote_track;

    if (msg != null && !msg.sdp) {
        console.log("WARNING: First message wasn't an SDP message!?");
    }

    peer_connection.onicecandidate = (event) => {

        if (event.candidate == null) {
                console.log("Соединение завершено");
                return;
        }
        ws_conn.send(JSON.stringify({'ice': event.candidate}));
    };

    if (msg != null)
        console.log("Ожидание SDP пакетов...");
}

window.VideoManager = {
    init: function() {
        setTimeout(() => {
            websocket_server_connect();
        }, 1000);
    },

    reconnect: reconnect,
    resetVideo: reset_video
};