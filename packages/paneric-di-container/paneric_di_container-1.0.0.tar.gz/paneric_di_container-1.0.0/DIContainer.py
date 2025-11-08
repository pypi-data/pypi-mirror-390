from DIContainerInterface import DIContainerInterface

class DIContainer(DIContainerInterface):

    __mapper: dict
    __container: dict

    def __init__(self, mapper: dict = None, container: dict = None):
        self.__mapper = {} if mapper is None else mapper
        self.__container = {} if container is None else container

    def get(self, key: str) -> object | list | None:

        if key in self.__mapper:
            return self.get_instance(key)

        return None

    def has(self, key: str) -> bool:

        return key in self.__mapper

    def set(self, key: str, item):

        if key in self.__container:
            return

        self.__container[key] = item

        self.__mapper[key] = lambda di: (
            di.container[key]
        )

    def merge(self, dependencies: dict):

        self.__mapper.update(dependencies)

    def get_instance(self, key: str):

        if key in self.__container:
            return self.__container[key]

        if not callable(self.__mapper[key]):
            self.__container[key] = self.__mapper[key]
            return self.__container[key]

        self.__container[key] = self.__mapper[key](self)

        return self.__container[key]
