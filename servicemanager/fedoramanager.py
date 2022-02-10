from .basemanager import AbstractServiceManager
from pystemd.systemd1 import Unit
import asyncio
import time
import logging


class FedoraServiceManager(AbstractServiceManager):
    def __init__(self, unitname: str) -> None:
        super().__init__()
        self.unitname: str = unitname
        self._unit = Unit(self.unitname.encode())
        self._unit.load()
        self.__running = True

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, value):
        self.__running = value

    async def setup(self):
        logging.debug('setup')
        self._queue = asyncio.Queue()

        asyncio.create_task(self.worker())

    async def worker(self):
        while self.__running:
            try:
                task = await self._queue.get()
                logging.debug('Get task {}, run it'.format(task))

                if task == 'START':
                    self._unit.Unit.Start(b'replace')
                elif task == 'STOP':
                    self._unit.Unit.Stop(b'replace')
                elif task == 'RESTART':
                    self._unit.Unit.Stop(b'replace')
                    self._unit.Unit.Start(b'replace')

                self._queue.task_done()
            except Exception as e:
                logging.error(e)

    async def stop(self):
        self._queue.put_nowait('STOP')

    async def start(self):
        self._queue.put_nowait('START')

    async def restart(self):
        self._queue.put_nowait('RESTART')

    def status(self):
        unit_status = self._unit.Unit.ActiveState.decode()
        unit_name = self._unit.Unit.Names[0].decode()
        return unit_name, unit_status
