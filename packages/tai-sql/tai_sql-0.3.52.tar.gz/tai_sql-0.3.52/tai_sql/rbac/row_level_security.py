from __future__ import annotations
from pydantic import BaseModel
from typing import (
    List, Type,
    Union, Dict,
    TYPE_CHECKING
)
if TYPE_CHECKING:
    from ..orm import Table

class RLS(BaseModel):
    resource: Type[Table]
    condition: Dict[str, Union[str | int, List[str | int]]]


def rls(resource: Type[Table], condition: Dict[str, str | int]) -> RLS:
    """
    Define una política de seguridad a nivel de fila (RLS) para una tabla específica.
    Args:
        resource: Clase de tabla específica
        condition: Condición SQL para la política RLS. Puede ser una string SQL o una expresión SQLAlchemy
    """
    if not issubclass(resource, Table):
        raise ValueError("El resource debe ser una subclase de Table")
    
    if not isinstance(condition, dict):
        raise ValueError("La condición debe ser un diccionario de pares columna: valor")
    
    for column_name in condition.keys():
        if not hasattr(resource, column_name):
            raise ValueError(f"La columna '{column_name}' no existe en la tabla '{resource.tablename}'")
        
    return RLS(
        resource=resource,
        condition=condition
    )