import abc

class DIContainerInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get') and callable(subclass.get) and
                hasattr(subclass, 'has') and callable(subclass.has) and
                hasattr(subclass, 'set') and callable(subclass.set) and
                hasattr(subclass, 'merge') and callable(subclass.merge) or
                NotImplemented)

    @abc.abstractmethod
    def get(self, key: str) -> object | list:
        raise NotImplementedError

    @abc.abstractmethod
    def has(self, key: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, item):
        raise NotImplementedError

    @abc.abstractmethod
    def merge(self, dependencies: dict):
        raise NotImplementedError
