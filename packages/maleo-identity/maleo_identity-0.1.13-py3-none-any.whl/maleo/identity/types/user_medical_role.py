from typing import Tuple
from uuid import UUID
from maleo.enums.medical import MedicalRole


CompositeIdentifier = Tuple[int, int, MedicalRole]
IdentifierValueType = int | UUID | CompositeIdentifier
