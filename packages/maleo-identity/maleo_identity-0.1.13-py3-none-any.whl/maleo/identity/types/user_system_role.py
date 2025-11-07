from typing import Tuple
from uuid import UUID
from maleo.enums.system import SystemRole


CompositeIdentifier = Tuple[int, SystemRole]
IdentifierValueType = int | UUID | CompositeIdentifier
