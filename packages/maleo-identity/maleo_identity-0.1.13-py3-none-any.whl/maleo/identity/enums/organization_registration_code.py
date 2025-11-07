from enum import StrEnum
from maleo.types.string import ListOfStrs


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    ORGANIZATION_ID = "organization_id"
    CODE = "code"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]
