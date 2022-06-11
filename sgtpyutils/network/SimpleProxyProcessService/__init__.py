from concurrent.futures import ThreadPoolExecutor
import socket
import sys

from ...logger import logger
from typing import Dict, List, overload
from ..SimpleTcpService import SimpleTcpService, MessageEventArgs, NewConnectionEventArgs
from ...extensions import clazz
import subprocess


class ProcessSocketBind:
    def __init__(self, connection: socket.socket, process: subprocess.Popen):
        self.connection = connection
        self.process = process


class SimpleProxyProcessService(SimpleTcpService):
    def handle_message(self, event: MessageEventArgs):
        data = event.data
        name = event.host
        dic = self.process_dict
        try:
            if not name in dic:
                return
            p = dic[name]
            p.process.stdin.write(data)
        except Exception as e:
            result = f'Error: {e}\n'
            event.connection.send(result.encode())

    def handle_new_connection(self, event: NewConnectionEventArgs):
        if not self.validate:
            return False
        return self.start_new_process(
            name=event.host,
            connection=event.connection
        )

    def start_new_process(self, name: str, connection: socket.socket = None):
        if not self.validate:
            return False
        dic = self.process_dict
        if name in dic:
            try:
                dic[name].process.kill()
            except:
                pass
        try:
            p = subprocess.Popen(
                args=self.command,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True
            )
            logger.info(f'process {p.pid} is created.({self.command})')
            if connection == None:
                p.kill()
                return False

            # seems useless
            p.stdout = connection.makefile('rb',buffering=None)
            p.stderr = connection.makefile('rb',buffering=None)
            p.stdin = connection.makefile('wb',buffering=None)
        except Exception as e:
            logger.error(f'exception on create process:{e}')
            self.validate = False
            return False
        bind = ProcessSocketBind(
            connection=connection,
            process=p
        )

        # self.ThreadPoolExecutor.submit(self.handle_process_stdout, p=bind)
        # self.ThreadPoolExecutor.submit(self.handle_process_stderr, p=bind)
        dic[name] = bind
        return True

    def handle_process_stdout(self, p: ProcessSocketBind):
        try:
            while True:
                subprocess.call
                r = p.process.stdout.read(1024)
                p.connection.send(r)
        except Exception as e:
            try:
                p.connection.close()
            except:
                pass

    def handle_process_stderr(self, p: ProcessSocketBind):
        try:
            while True:
                r = p.process.stderr.read(1024)
                p.connection.send(r)
        except:
            try:
                p.connection.close()
            except:
                pass

    def start_process(self):
        self.ThreadPoolExecutor = ThreadPoolExecutor()
        self.process_dict: Dict[str, ProcessSocketBind] = {}
        return self.start_new_process('default', None)

    @overload
    def __init__(self, command: List, host: str = '127.0.0.1', port: int = None):
        ...

    @overload
    def __init__(self, command: str, host: str = '127.0.0.1', port: int = None):
        ...

    def __init__(self, command, host: str = '127.0.0.1', port: int = None):
        if isinstance(command, str):
            self.command = [command]
        else:
            self.command = command
        self.validate: bool = True
        init = super().__init__(
            on_message=self.handle_message,
            on_new_connection=self.handle_new_connection,
            host=host,
            port=port
        )
        self.start_process()
        return init
