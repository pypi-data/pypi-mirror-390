from typing import Tuple
from uuid import UUID
from maleo.types.integer import OptInt


CompositeIdentifier = Tuple[int, OptInt]
IdentifierValueType = int | UUID | str | CompositeIdentifier
