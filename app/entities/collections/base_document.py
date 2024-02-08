import dataclasses

from bson import ObjectId


@dataclasses.dataclass(kw_only=True)
class BaseDocument:
    _id: ObjectId

    @property
    def id(self) -> ObjectId:
        return self._id
