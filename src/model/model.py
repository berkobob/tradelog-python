from abc import ABCMeta, abstractmethod
from src.common.database import DB
from src.common.result import Result

class Model(metaclass=ABCMeta):
    collection: str
    _id: str

    def create(self) -> Result:
        return DB.create(self.collection, vars(self))

    @classmethod
    def read(cls, query):
        result = DB.read(cls.collection, query)
        if result.success: result.message = [cls(item) for item in result.message]
        # if result.success: result.message = [cls(result.message)]
        return result

    def update(self):
        pass

    def delete(self):
        return DB.delete(self.collection, {"_id": self._id})

    # @classmethod
    # def all(cls) -> list:
    #     return [cls(item) for item in DB.all(cls.collection)]

    def __repr__(self) -> str:
        return str(vars(self))