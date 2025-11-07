import asyncio
import json
import argparse
import sys
from pathlib import Path

try:
    import websockets
    from aiohttp import web
    ws_control = True
except ImportError:
    ws_control = False


from geodrive import AsyncRover
from geodrive.logging import get_logger

logger = get_logger("ws-control")

missing_depens_message = """
Не установлены зависимости для ws-control. Установите:

pip install 'geodrive[ws-control]'
или 
uv add geodrive[ws-control]
"""

async def create_http_app(video: bool):
    """
    Создает web приложение для обслуживания панели управления
    """
    app = web.Application()
    panel_file = 'control_panel.html'
    panel_dir = 'control_panel'
    if video:
        panel_file = 'video_control_panel.html'
        panel_dir = 'game'

    async def control_panel(request):
        script_dir = Path(__file__).parent
        html_file = script_dir / panel_dir / panel_file
        if html_file.exists():
            try:
                html_content = html_file.read_text(encoding='utf-8')
            except Exception as e:
                return web.Response(
                text=f"<h1>{e}</h1>",
                content_type='text/html',
                status=404
            )
            return web.Response(text=html_content, content_type='text/html')
        else:
            return web.Response(
                text=f"<h1>Файл {panel_file} не найден</h1>",
                content_type='text/html',
                status=404
            )

    async def serve_static(request):
        source = request.match_info['source']
        if source == 'css':
            return await serve_css(request)
        elif source == 'js':
            return await serve_js(request)
        return web.Response(status=404)


    async def serve_css(request):
        filename = request.match_info['filename']
        script_dir = Path(__file__).parent
        static_file = script_dir / panel_dir / 'css' / filename

        if static_file.exists() and static_file.suffix == '.css':
            content_type = 'text/css'
            content = static_file.read_text(encoding='utf-8')
            return web.Response(text=content, content_type=content_type)

        return web.Response(status=404)

    async def serve_js(request):
        filename = request.match_info['filename']
        script_dir = Path(__file__).parent
        static_file = script_dir / panel_dir / 'js' / filename

        if static_file.exists() and static_file.suffix == '.js':
            content_type = 'application/javascript'
            content = static_file.read_text(encoding='utf-8')
            return web.Response(text=content, content_type=content_type)

        return web.Response(status=404)

    async def serve_favicon(request):
        """Обслуживание favicon.ico"""
        script_dir = Path(__file__).parent
        favicon_file = script_dir / 'favicon.ico'

        if favicon_file.exists():
            return web.FileResponse(favicon_file)
        else:
            return web.Response(status=404)

    app.router.add_get('/', control_panel)
    app.router.add_get('/control', control_panel)
    app.router.add_get('/favicon.ico', serve_favicon)
    app.router.add_get('/static/{source}/{filename}', serve_static)

    return app


async def forward_websocket_to_rover(rover_number: int, local: bool, arena: int):

    if local:
        rover_ip = "localhost"
        logger.info("Подключение к локальному gRPC серверу")
    else:
        rover_ip = f"10.1.100.{rover_number}"

    rover = AsyncRover(rover_ip)

    if not await rover.connect():
        logger.info("Не удалось подключиться к роверу")
        return

    logger.info("Успешное подключение к роверу")

    async def handle_websocket(websocket):

        initial_data = {
            "type": "config",
            "rover_id": rover_number,
            "arena_size": arena
        }

        await websocket.send(json.dumps(initial_data))

        async with rover.rc_stream_context() as rc_control:

            async def send_robot_data():
                while True:
                    try:
                        async for telemetry in rover.stream_telemetry():
                            battery_data = await rover.get_battery_status()
                            robot_data = {
                                "type": "telemetry",
                                "posX": telemetry.position[0],
                                "posY": telemetry.position[1],
                                "velX": telemetry.velocity[0],
                                "velY": telemetry.velocity[1],
                                "yaw": telemetry.attitude[2],
                                "battery": battery_data.percentage
                            }

                            await websocket.send(json.dumps(robot_data))

                            await asyncio.sleep(0.02)

                    except Exception as e:
                        logger.error(f"Ошибка при отправке данных робота: {e}")
                        break

            send_task = asyncio.create_task(send_robot_data())

            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type", "rc_channels") == "navigate_to_point":
                            await asyncio.create_task(rover.goto(data.get("target_x"), data.get("target_y")))
                        else:
                            rc_control.channel1 = data.get('channel1', 1500)
                            rc_control.channel2 = data.get('channel2', 1500)
                            rc_control.channel3 = data.get('channel3', 1500)
                            rc_control.channel4 = data.get('channel4', 1500)
                            if rc_control.channel2 == 1000:
                                await rover.moo()
                            if rc_control.channel4 == 1000:
                                await rover.beep()

                            logger.debug(f"Каналы: {data}")

                    except json.JSONDecodeError:
                        logger.warning(f"Невалидный JSON: {message}")
                    except Exception as e:
                        logger.error(f"Ошибка: {e}")

            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket клиент отключился")
            finally:
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass

    async with websockets.serve(handle_websocket, "0.0.0.0", 8765):
        await asyncio.Future()

async def run(rover_num: int, local: bool, arena: int, video: bool):
    app = await create_http_app(video)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info(f"Панель управления доступна по адресу: http://localhost:8080")
    await forward_websocket_to_rover(rover_num, local, arena)

def main():
    parser = argparse.ArgumentParser(description="Websocket сервер для ручного управления роботом")
    parser.add_argument("num", type=int, nargs='?', default=160)
    parser.add_argument("-ip", type=str, default="10.1.100.160")
    parser.add_argument("-l", "--local", action="store_true",
                        help="Подключение к локальному серверу (localhost) вместо реального ровера")
    parser.add_argument("-v", "--video", action="store_true", help="Панель управления с видео")
    parser.add_argument("-a", "--arena", type=int, default=11, help="Размер арены (по умолчанию: 11)")

    args = parser.parse_args()

    if not (0 <= args.num <= 255):
        logger.error("Ошибка: номер ровера должен быть в диапазоне 0-255")
        sys.exit(1)

    if not ws_control:
        logger.error(missing_depens_message)
        sys.exit(1)

    try:
        asyncio.run(run(args.num, args.local, args.arena, args.video))
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")


if __name__ == "__main__":
    main()