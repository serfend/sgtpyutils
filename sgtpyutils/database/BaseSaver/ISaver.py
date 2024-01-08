import abc


class ISaver:
    @abc.abstractmethod
    def save(self):
        ...
