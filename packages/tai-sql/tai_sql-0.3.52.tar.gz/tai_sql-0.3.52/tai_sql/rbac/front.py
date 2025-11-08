from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Type, TYPE_CHECKING
from pydantic import BaseModel, Field, PrivateAttr

if TYPE_CHECKING:
    from ..orm import Table, AllTables, Permission

class ComponentType(Enum):
    """
    Tipos de componentes que pueden existir en una aplicación.
    Esto ayuda a categorizar los componentes y aplicar reglas específicas.
    """
    FORM = "form"
    TABLE = "table"
    BUTTON = "button"
    MENU = "menu"
    MODAL = "modal"
    CARD = "card"
    CHART = "chart"
    INPUT = "input"
    SELECT = "select"
    CUSTOM = "custom"

class AppElement(BaseModel):
    """
    Clase base para todos los elementos de la aplicación.
    Define el comportamiento común para App, Screen y Component.
    """
    id: str = Field(..., description="Identificador único del elemento")
    name: Optional[str] = Field(default=None, description="Nombre descriptivo del elemento")
    dependencies: List[str] = Field(default_factory=list, description="Dependencias de la base de datos") # type: ignore

class Component(AppElement):
    """
    Componente: elemento más básico de la aplicación.
    Representa cualquier elemento interactivo o visual.
    """
    type: ComponentType = Field(default=ComponentType.CUSTOM)
    screen: Optional[Screen] = Field(default=None, description="Pantalla padre")
    
    # Configuración específica del componente
    props: Dict[str, str] = Field(default_factory=dict, description="Propiedades del componente")

    def model_post_init(self, context):
        if self.screen is not None:
            self.screen.components.append(self)

    @property
    def path(self) -> str:
        return f"{self.screen.app.id}.{self.screen.id}.{self.id}"

class Screen(AppElement):
    """
    Pantalla: contiene múltiples componentes.
    Representa una vista o página de la aplicación.
    """
    app: Optional[App] = Field(default=None, description="Aplicación padre")
    components: List[Component] = Field(default_factory=list)

    def model_post_init(self, context):
        if self.app is not None:
            self.app.screens.append(self)

    @property
    def path(self) -> str:
        return f"{self.app.id}.{self.id}"
    
    def add_component(self, component: Component) -> Screen:
        """Añade un componente a la pantalla"""
        component.screen = self
        component.app = self.app
        self.components.append(component)

        return self
    
    def add_components(self, *components: List[Component]) -> Screen:
        """Añade múltiples componentes a la pantalla"""
        for component in components:
            self.add_component(component)

        return self
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Obtiene un componente por su ID"""
        return next((c for c in self.components if c.id == component_id), None)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[Component]:
        """Obtiene todos los componentes de un tipo específico"""
        return [c for c in self.components if c.type == component_type]

class Header(Screen):
    """
    Pantalla especial que actúa como encabezado global de la aplicación.
    Contiene componentes que se muestran en todas las pantallas.
    """
    pass

class Menu(Screen):
    """
    Pantalla especial que actúa como menú de navegación de la aplicación.
    Contiene componentes que permiten la navegación entre pantallas.
    """
    pass

class App(AppElement):
    """
    Aplicación: nivel superior que contiene pantallas.
    Representa toda la aplicación o un módulo principal.
    """
    screens: List[Screen] = Field(default_factory=list)
    _header: Header = PrivateAttr()
    _menu: Menu = PrivateAttr()
    
    @property
    def path(self) -> str:
        return self.id
    
    @property
    def header(self) -> Optional[Header]:
        if not self._header:
            self._header = Header(id="header", name="Header")
        return self._header
    @property
    def menu(self) -> Optional[Menu]:
        if not self._menu:
            self._menu = Menu(id="menu", name="Menu")
        return self._menu

    def add_screen(self, screen: Screen) -> App:
        """Añade una pantalla a la aplicación"""
        screen.app = self
        self.screens.append(screen)

        return self
    
    def add_screens(self, *screens: List[Screen]) -> App:
        """Añade múltiples pantallas a la aplicación"""
        for screen in screens:
            self.add_screen(screen)

        return self
    
    def get_screen(self, screen_id: str) -> Optional[Screen]:
        """Obtiene una pantalla por su ID"""
        return next((s for s in self.screens if s.id == screen_id), None)
    
    def get_component(self, screen_id: str, component_id: str) -> Optional[Component]:
        """Obtiene un componente específico de una pantalla"""
        screen = self.get_screen(screen_id)
        return screen.get_component(component_id) if screen else None
    
    def get_all_elements(self) -> List[AppElement]:
        """Retorna todos los elementos de la aplicación en una lista plana"""
        elements: List[AppElement] = [self]
        
        for screen in self.screens:
            elements.append(screen)
            elements.extend(screen.components)
            
        return elements


# Funciones helper para crear la estructura de forma más fluida
def app(id: str, name: Optional[str] = None, **kwargs) -> App:
    """Helper para crear una aplicación"""
    return App(id=id, name=name, **kwargs)

def screen(id: str, name: Optional[str] = None, dependencies: List[Permission] = [], **kwargs) -> Screen:
    """Helper para crear una pantalla"""
    unpacked_dependencies = set()
    for deps in dependencies:
        unpacked_dependencies.update(deps)
    return Screen(id=id, name=name, dependencies=unpacked_dependencies, **kwargs)

def component(id: str, name: Optional[str] = None, dependencies: List[Permission] = [], type: ComponentType = ComponentType.CUSTOM, **kwargs) -> Component:
    """Helper para crear un componente"""
    unpacked_dependencies = set()
    for deps in dependencies:
        unpacked_dependencies.update(deps)
    return Component(id=id, name=name, dependencies=unpacked_dependencies, type=type, **kwargs)

App.model_rebuild()