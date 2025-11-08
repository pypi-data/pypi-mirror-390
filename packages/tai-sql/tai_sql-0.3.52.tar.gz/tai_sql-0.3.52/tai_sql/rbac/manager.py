from __future__ import annotations
import sys
import types
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import Role

# Manager para gestionar roles
class RBACManager:
    """Gestor centralizado de roles"""

    _loaded: bool = False
    
    def __init__(self, rbac_name: str, rbac_path: Optional[Path] = None, schema_module=None):
        self.rbac_name = rbac_name
        self.rbac_path = rbac_path
        self.schema_module = schema_module  # Módulo de schema ya cargado
        self._roles: Dict[str, Role] = {}

    @property
    def roles(self) -> Dict[str, Role]:
        """Devuelve todos los roles registrados"""
        return self._roles
    
    def register(self, role: Role) -> None:
        """Registra un nuevo rol"""
        if role.name in self._roles:
            raise ValueError(f"Role '{role.name}' already exists")
        self._roles[role.name] = role
    
    def get(self, name: str) -> Optional[Role]:
        """Obtiene un rol por nombre"""
        return self._roles.get(name)
    
    def list(self) -> List[Role]:
        """Lista todos los roles registrados"""
        return list(self._roles.values())
    
    def set_schema_module(self, schema_module) -> None:
        """Establece el módulo de schema después de la creación"""
        self.schema_module = schema_module
    
    def clear(self) -> None:
        """Limpia todos los roles excepto el admin"""
        if "admin" in self._roles:
            self._roles = {
                "admin": self._roles["admin"]
            }
        else:
            self._roles = {}
    
    def remove(self, name: str) -> bool:
        """Elimina un rol"""
        if name in self._roles:
            del self._roles[name]
            return True
        return False
    
    def load(self) -> None:
        """
        Carga el módulo de rbac. Integra funcionalidad de RBACFile.
        """
        if self._loaded:
            return
        
        if not self.rbac_path:
            raise ValueError(f"No se ha especificado rbac_path para {self.rbac_name}")
        
        if not self.rbac_path.exists():
            raise FileNotFoundError(f"El archivo de rbac {self.rbac_path} no existe")
        
        try:
            self.clear()  # Limpiar roles previos
            
            # Si tenemos un módulo de schema cargado, lo hacemos disponible
            if self.schema_module:
                # Crear un módulo padre 'schemas' si no existe
                if 'schemas' not in sys.modules:
                    schemas_parent = types.ModuleType('schemas')
                    sys.modules['schemas'] = schemas_parent
                
                # Hacer que el módulo de schema esté disponible como "schemas.{nombre}"
                schema_module_name = f"schemas.{self.rbac_name}"
                sys.modules[schema_module_name] = self.schema_module
                
                # También añadir como atributo al módulo padre
                setattr(sys.modules['schemas'], self.rbac_name, self.schema_module)
            
            # Crear nombre de módulo único para evitar conflictos
            module_name = f"tai_sql_rbac_{self.rbac_name}"
            
            # Limpiar módulo previo si existe
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            spec = importlib.util.spec_from_file_location(module_name, self.rbac_path)
            if spec is None:
                raise ImportError(f"No se pudo cargar el archivo de rbac: {self.rbac_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._loaded = True
            
        except Exception as e:
            raise RuntimeError(f"Error al cargar el rbac '{self.rbac_name}': {e}")
