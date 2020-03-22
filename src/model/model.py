from abc import ABCMeta, abstractmethod
from src.common.database import DB
from src.common.result import Result
from bson.objectid import ObjectId

class Model(metaclass=ABCMeta):
    collection: str
    _id: str

    def create(self) -> Result:
        """ Save a copy of the class in the DB, add the _id and return the object """
        result = DB.create(self.collection, vars(self))
        if not result.success: return result
        self._id = ObjectId(result.message)
        return Result(success=True, message=self, severity='SUCCESS')

    @classmethod
    def read(cls, query, many=False):
        if many: 
            result = DB.read_many(cls.collection, query)
            if result.success: 
                result.message = [cls(item) for item in result.message]
        else: 
            result = DB.read_one(cls.collection, query)
            if result.success and result.message:
                    result.message = cls(result.message)
        return result

    @classmethod
    def get(cls, _id):
        return cls.read({'_id': ObjectId(_id)})
        
    def update(self, values):
        result = DB.update(self.collection, 
                            {"_id": ObjectId(self._id)}, {"$set": values})
        
        if result.success:
            if result.message['n'] == 0:
                return Result(success=False, message=
                            "No records were found to update.",
                            severity="WARNING")
            if result.message['nModified'] == 0:
                return Result(success=False, message=
                            f"This record already reflectes this data: {values}",
                            severity="WARNING")
            result.message = self
        return result

    def delete(self):
        result = DB.delete(self.collection, {"_id": ObjectId(self._id)})
        if result.message.deleted_count < 1:
            return Result(success=False, message='Failed to delete', severity='ERROR')
        if result.message.deleted_count > 1:
            return Result(success=True, message='Multiple records deleted', severity='WARNING')
        return result

    def __repr__(self) -> str:
        return str(vars(self))