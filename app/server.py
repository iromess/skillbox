"""
Серверное приложение для соединений
Выполнил Фофонов Роман
fofonovrv@gmail.com
"""
import asyncio
from asyncio import transports
from typing import Optional


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        print(decoded)

        if self.login is None:

            if decoded.startswith("login:"):
                login = decoded.replace("login:", "").replace("\r\n", "")
                for client in process.clients:
                    if client.login == login:
                        self.transport.write(
                            f"Логин {login} уже занят, попробуйте другой!".encode()
                        )
                        self.transport.close()
                        break
                else:
                    self.login = login
                    self.transport.write(
                        f"Привет, {self.login}!".encode())
                    self.send_history()

        else:
            self.send_message(decoded)

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()
        process.write_history(format_string)

        for client in self.server.clients:
            if (client.login != self.login) & (client.login is not None):
                client.transport.write(encoded)

    def send_history(self):
        self.transport.writelines(process.message_history)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено ...")

    def connection_lost(self, exc):
        self.server.clients.remove(self)
        print("Соединение разорвано ...")


class Server:
    clients: list
    message_history: list

    def __init__(self):
        self.clients = []
        self.message_history = [b'', b'', b'', b'', b'', b'', b'', b'', b'', b'']

    def write_history(self,last_message):
        self.message_history = self.message_history[1:] + self.message_history[:1]
        self.message_history[-1] = (last_message + "\r\n").encode()

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную ...")