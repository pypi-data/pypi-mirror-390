# Sistema RBAC Declarativo - Definición Lógica de Aplicaciones

Este sistema permite definir aplicaciones de forma declarativa usando una estructura en árbol **App → Screen → Component**, donde cada elemento implementa acciones nativas de aplicación como "PUEDE ENTRAR", "PUEDE ESCRIBIR", "PUEDE ELIMINAR".

## 🎯 Filosofía del Sistema

En lugar de gestionar únicamente permisos a nivel de base de datos (tablas y operaciones SQL), este sistema permite:

1. **Declarar la estructura** de la aplicación de forma clara y jerárquica
2. **Definir roles** basándose en esta declaración de la aplicación
3. **Integrar** con el sistema de permisos de base de datos existente
4. **Generar permisos** para el frontend de forma automática

## 🏗️ Estructura de la Aplicación

### Jerarquía de Elementos

```
App (Aplicación)
├── Screen (Pantalla/Vista)
│   ├── Component (Componente)
│   ├── Component (Componente)
│   └── ...
├── Screen (Pantalla/Vista)
│   └── ...
└── ...
```

### Acciones Nativas

Cada elemento soporta estas acciones básicas:

- **`PUEDE_ENTRAR`**: Puede acceder/ver el elemento
- **`PUEDE_ESCRIBIR`**: Puede modificar/editar el elemento  
- **`PUEDE_ELIMINAR`**: Puede eliminar/borrar el elemento

Y acciones compuestas:
- **`LECTURA`**: Solo puede entrar/ver
- **`ESCRITURA`**: Puede entrar + escribir
- **`ADMIN`**: Todas las acciones

## 🚀 Uso Básico

### 1. Definir la Aplicación

```python
from tai_sql.orm.mappers.rbac import app, screen, component, ComponentType

# Crear la aplicación
mi_app = app("crm", "Sistema CRM", "Gestión de relaciones con clientes")

# Crear pantalla
dashboard = screen("dashboard", "Dashboard Principal", route="/dashboard")

# Crear componentes
metrics = component("metrics", "Métricas", ComponentType.CARD)
chart = component("sales_chart", "Gráfico Ventas", ComponentType.CHART)

# Ensamblar
dashboard.add_component(metrics)
dashboard.add_component(chart)
mi_app.add_screen(dashboard)
```

### 2. Definir Roles

```python
from tai_sql.orm.mappers.rbac import create_role, AppAction

# Rol con acceso completo al dashboard
admin = (create_role("admin", "Administrador")
         .allow_screen(dashboard, AppAction.ADMIN)
         .build())

# Rol de solo lectura
viewer = (create_role("viewer", "Solo lectura")
          .allow_screen(dashboard, AppAction.PUEDE_ENTRAR)
          .build())

# Rol específico para componente
analyst = (create_role("analyst", "Analista")
           .allow_component(chart, AppAction.ESCRITURA)
           .build())
```

### 3. Configurar el Sistema

```python
from tai_sql.orm.mappers.rbac import quick_setup

# Configurar integración
integration = quick_setup(mi_app, [admin, viewer, analyst])

# Verificar permisos en runtime
user_roles = ["viewer"]
puede_acceder = integration.can_user_access_element(
    user_roles, dashboard, AppAction.PUEDE_ENTRAR
)

# Generar permisos para frontend
permisos_frontend = integration.generate_frontend_permissions(user_roles)
```

## 📋 Ejemplos Completos

Ver `app_examples.py` para ejemplos detallados incluyendo:

- **Sistema CRM completo** con múltiples pantallas y componentes
- **Definición de roles** específicos (vendedor, supervisor, admin)
- **Verificación de permisos** en tiempo de ejecución
- **Migración** desde sistemas existentes basados solo en BD

## 🔄 Integración con Sistema Existente

El nuevo sistema es **compatible** con el sistema RBAC existente:

```python
from tai_sql.orm.mappers.rbac import migrate_from_db_only

# Migrar roles existentes de BD
integration = migrate_from_db_only(mi_app, existing_db_roles)

# Crear roles híbridos que combinan permisos de app y BD  
hybrid_role = integration.create_hybrid_role(
    "admin_hybrid", app_role, db_role
)
```

## 🎨 Patrones de Uso Comunes

### Rol de Administrador Global
```python
admin = admin_role(mi_app, "global_admin")
```

### Rol de Solo Lectura
```python
readonly = reader_role(mi_app, "readonly_user")  
```

### Rol para Pantallas Específicas
```python
screen_user = screen_user_role([dashboard, reports], "dashboard_user")
```

### Rol con Permisos Granulares
```python
custom_role = (create_role("custom", "Rol personalizado")
               .allow_app(mi_app, AppAction.PUEDE_ENTRAR)
               .allow_screen(sensitive_screen, AppAction.ESCRITURA)
               .allow_component(delete_button, AppAction.PUEDE_ELIMINAR)
               .build())
```

## 🏷️ Tipos de Componentes

El sistema incluye tipos predefinidos que automáticamente determinan qué acciones están disponibles:

- **`FORM`**: Formularios (permite escritura)
- **`TABLE`**: Tablas (permite eliminación)  
- **`BUTTON`**: Botones (permite escritura)
- **`CHART`**: Gráficos (solo lectura por defecto)
- **`CARD`**: Tarjetas (permite eliminación)
- **`MENU`**: Menús (solo entrada)
- Y más...

## 🔍 Validación y Debugging

```python
# Validar definición de aplicación
warnings = integration.validate_application_definition()
for warning in warnings:
    print(f"⚠️  {warning}")

# Obtener resumen de rol
role_summary = hybrid_role.get_summary()
print(role_summary)

# Listar elementos accesibles
accessible = integration.get_user_accessible_elements(
    ["user_role"], AppAction.PUEDE_ENTRAR
)
```

## 📁 Archivos del Sistema

- **`app_structure.py`**: Clases base (App, Screen, Component)
- **`app_permissions.py`**: Sistema de permisos y roles de aplicación
- **`integration.py`**: Integración con sistema existente
- **`app_examples.py`**: Ejemplos completos de uso
- **`app.py`**: Archivo original (ahora deprecado con compatibilidad)

## 🚀 Ventajas del Nuevo Sistema

1. **Declarativo**: Define la aplicación de forma clara y estructurada
2. **Jerárquico**: Los permisos se heredan de elementos superiores  
3. **Granular**: Control fino hasta el nivel de componente
4. **Integrado**: Compatible con permisos de base de datos existentes
5. **Frontend-ready**: Genera permisos listos para usar en UI
6. **Validado**: Incluye validaciones automáticas de la definición
7. **Extensible**: Fácil de extender con nuevos tipos y acciones

## 🛠️ Migración

Para migrar código existente:

1. **Reemplazar** imports del `app.py` antiguo por `app_structure.py`
2. **Definir** la estructura de aplicación usando las nuevas clases
3. **Crear** roles usando el nuevo sistema de permisos
4. **Configurar** la integración con `quick_setup()` o `migrate_from_db_only()`
5. **Actualizar** el frontend para usar los nuevos permisos generados

El sistema mantiene **compatibilidad hacia atrás** durante la transición.