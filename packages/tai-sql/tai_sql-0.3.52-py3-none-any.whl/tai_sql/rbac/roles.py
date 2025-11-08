from __future__ import annotations
from pydantic import BaseModel, Field
from typing import (
    List, Union, Dict, TYPE_CHECKING
)

if TYPE_CHECKING:
    from ..orm import Permission
    
class Role(BaseModel):
    name: str
    description: str = Field(default="")
    permissions: List[Permission] = Field(default_factory=list)

    def info(self) -> Dict[str, Union[str, List[Dict]]]:
        """Información del rol"""
        return {
            'name': self.name,
            'description': self.description,
            'permissions': [perm.model_dump() for perm in self.permissions]
        }
    
    model_config = {
        'arbitrary_types_allowed': True
    }

def role(
    name: str,
    permissions: List[Permission],
    description: str = "") -> Role:
    """Helper para crear roles"""
            
    role = Role(
        name=name,
        description=description,
        permissions=permissions,
    )
    from tai_sql import pm
    pm.roles.register(role)

    return role