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

    def update(self, values):
        result = DB.update(self.collection, {"_id": self._id}, {"$set": values})
        
        if result.success:
            if result.message['n'] == 0:
                return Result(success=False, message=
                            "No records were found to update.",
                            severity="WARNING")
            if result.message['nModified'] == 0:
                return Result(success=False, message=
                            f"This record already reflectes this data: {values}",
                            severity="WARNING")
        return result

    def delete(self):
        result = DB.delete(self.collection, {"_id": self._id})
        if result.message.deleted_count < 1:
            return Result(success=False, message='Failed to delete', severity='ERROR')
        if result.message.deleted_count > 1:
            return Result(success=True, message='Multiple records deleted', severity='WARNING')
        return result


    def __repr__(self) -> str:
        return str(vars(self))