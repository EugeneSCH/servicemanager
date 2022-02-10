from abc import ABC


class AbstractServiceManager(ABC):
    def stop(self):
        pass

    def start(self):
        pass

    def restart(self):
        pass

    def status(self):
        pass
