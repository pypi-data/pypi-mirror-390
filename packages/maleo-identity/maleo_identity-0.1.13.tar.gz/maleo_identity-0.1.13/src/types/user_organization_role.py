from typing import Tuple
from uuid import UUID
from maleo.enums.organization import OrganizationRole


CompositeIdentifier = Tuple[int, int, OrganizationRole]
IdentifierValueType = int | UUID | CompositeIdentifier
