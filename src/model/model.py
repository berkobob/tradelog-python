from src.common.database import DB
from bson.objectid import ObjectId

class Model:
    collection: str
    _id: str

    def create(self):
        """ Save a copy of the class in the DB, add the _id and return the object """
        DB.create(self.collection, vars(self))
        return self

    @classmethod
    def read(cls, query, many=False):
        if many: 
            return [cls(record) for record in DB.read_many(cls.collection, query)]
        else: 
            record = (DB.read_one(cls.collection, query))
            if record: return cls(record)
        return None

    @classmethod
    def get(cls, _id):
        return cls(DB.read_one(cls.collection, {'_id': ObjectId(_id)}))
        
    def update(self, values=None):
        if not values: values = vars(self)
        return DB.update(self.collection, 
                            {"_id": ObjectId(self._id)}, {"$set": values})
        
    def delete(self):
        return DB.delete(self.collection, {"_id": ObjectId(self._id)})

    def __repr__(self) -> str:
        return str(vars(self))