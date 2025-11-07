from typing import Tuple
from uuid import UUID
from maleo.enums.organization import OrganizationRelation


CompositeIdentifier = Tuple[int, int, OrganizationRelation]
IdentifierValueType = int | UUID | CompositeIdentifier
