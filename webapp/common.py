import abc


class Reactor(abc.ABC):
    @abc.abstractmethod
    def process(self, args):
        pass
