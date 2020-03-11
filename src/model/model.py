from abc import ABCMeta, abstractmethod
from src.common.database import DB
from src.common.result import Result

class Model(metaclass=ABCMeta):
    collection: str

    def create(self) -> Result:
        return DB.create(self.collection, vars(self))

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    @classmethod
    def all(cls) -> list:
        return [cls(item) for item in DB.all(cls.collection)]

    def __repr__(self) -> str:
        return str(vars(self))