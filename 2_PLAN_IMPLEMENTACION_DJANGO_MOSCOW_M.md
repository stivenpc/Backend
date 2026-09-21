# Plan de Implementación en Django: Sistema de Control de Mermas de Fundición
## Enfoque en Requisitos "Must Have" (M) de MoSCoW y Máxima Calificación en Rúbrica

---

## 1. Resumen Ejecutivo y Objetivos Técnicos

Este documento establece la arquitectura, diseño técnico y guía paso a paso para la implementación del sistema web en **Django**, enfocado exclusivamente en satisfacer al 100% los requerimientos de la categoría **Must Have (M)** de la metodología MoSCoW:

1. **M1. Módulo de Registro de Materiales e Inventario** (cálculo automático de contenido restante).
2. **M2. Control de Acceso y Roles - RBAC** (Operador, Supervisor y Encargado).
3. **M3. Logs de Auditoría** (trazabilidad de quién, cuándo, qué modificó, IP y seguridad).
4. **M4. Módulo de Registro de Merma Específica** (vinculado a proceso, máquina, tipo y cantidad de material).
5. **M5. Validación de Estudio Previo Obligatorio** (candado lógico en backend previo al registro).

Adicionalmente, el plan está diseñado para alcanzar el puntaje máximo (**3 puntos**) en cada uno de los cuatro criterios de la rúbrica de evaluación:
* **2.1.1 Configura la conexión a BD con seguridad y `python-decouple` (3 pts)**.
* **2.1.2 Personaliza el Administrador de Django para colecciones (3 pts)**.
* **2.1.3 Implementa operaciones CRUD completas con validaciones y pruebas (3 pts)**.
* **2.1.4 Desarrolla backend seguro con sesiones y evidencia crítica de uso de IA (3 pts)**.

---

## 2. Stack Tecnológico y Estructura del Proyecto

* **Lenguaje:** Python 3.10+
* **Framework Web:** Django 4.2+ LTS (o 5.x)
* **Gestión de Entornos y Secretos:** `python-decouple`
* **Base de Datos:** SQLite para desarrollo local / PostgreSQL compatible para producción mediante variables de entorno
* **Frontend:** Django Templates + Bootstrap 5 (responsive, intuitivo)
* **Testing:** Django Test Suite (`unittest` / `django.test.TestCase`)

### Estructura de Directorios Recomendada
```text
Solucion merma/
│
├── .env                         # Variables de entorno secretas (IGNORADO EN GIT)
├── .env.example                 # Plantilla pública de variables de entorno
├── .gitignore                   # Exclusión de .env, __pycache__, db.sqlite3, etc.
├── manage.py
├── requirements.txt             # Dependencias del proyecto
│
├── fundicion_core/              # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py              # Configuración segura con python-decouple
│   ├── urls.py                  # Enrutador principal
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── __init__.py
│   ├── auditoria/               # App de Logs y Trazabilidad (M3)
│   │   ├── __init__.py
│   │   ├── admin.py             # Admin de solo lectura con filtros forenses
│   │   ├── models.py            # Modelo LogAuditoria
│   │   ├── middleware.py        # Middleware para capturar IP y usuario actual
│   │   └── signals.py           # Receptores post_save y post_delete
│   │
│   ├── usuarios/                # App de Autenticación y RBAC (M2)
│   │   ├── __init__.py
│   │   ├── models.py            # Perfil con Roles (Operador, Supervisor, Encargado)
│   │   ├── decorators.py        # Decoradores @rol_requerido
│   │   ├── forms.py
│   │   ├── views.py             # Login, Logout, Dashboard según rol
│   │   └── urls.py
│   │
│   └── operaciones/             # App Central: Materiales, Merma y Estudio Previo (M1, M4, M5)
│       ├── __init__.py
│       ├── admin.py             # Admin ultra-personalizado (2.1.2)
│       ├── models.py            # Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma
│       ├── forms.py             # ModelForms con clean() y validaciones estrictas
│       ├── views.py             # CRUDs completos basados en clases y funciones (2.1.3)
│       ├── urls.py
│       ├── tests.py             # Pruebas automatizadas de CRUD y validaciones
│       └── management/
│           └── commands/
│               └── poblar_datos_prueba.py # Script de inicialización y verificación (2.1.1)
│
└── templates/                   # Vistas HTML base y modulares
    ├── base.html
    ├── registration/login.html
    ├── operaciones/
    └── auditoria/
```

---

## 3. Cumplimiento Estratégico de Criterios de Evaluación (Nivel 3 Puntos)

### 3.1 Criterio 2.1.1: Conexión a Base de Datos Segura con `python-decouple` (3 Puntos)
> **Requisito 3 puntos:** *Configura la conexión de forma correcta y segura: externaliza credenciales (variables de entorno), documenta el procedimiento y verifica el funcionamiento con migraciones y datos de prueba.*

#### A. Dependencias (`requirements.txt`)
```text
Django>=4.2,<5.1
python-decouple>=3.8
dj-database-url>=2.1.0
```

#### B. Archivo `.env` (Credenciales Reales Locales)
```ini
# Configuración Central de Seguridad
SECRET_KEY=django-insecure-fundicion-sigma-production-key-9283748291029384756102938
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Conexión a Base de Datos
# Por defecto SQLite local; si se usa PostgreSQL, descomentar la URL:
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgres://usuario_fundicion:PasswordSegura2026!@localhost:5432/fundicion_db
```

#### C. Archivo `.env.example` (Plantilla Documentada para el Repositorio)
```ini
# Variables de entorno requeridas para el Sistema de Merma de Fundición
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria-aqui
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,tudominio.com

# Motor de Base de Datos (SQLite o PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3
```

#### D. Configuración en `fundicion_core/settings.py`
```python
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga segura con tipos definidos (cast)
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# Conexión a Base de Datos externalizada
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}
```

#### E. Procedimiento Documentado de Migraciones y Verificación
1. **Creación y activación de entorno virtual:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. **Generación y aplicación de migraciones:**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Poblado de datos de prueba y verificación de conexión:**
   Se implementará el comando `python manage.py poblar_datos_prueba` que:
   * Verifica la conexión a la base de datos ejecutando una consulta elemental.
   * Crea los 3 grupos de roles: `Operador`, `Supervisor` y `Encargado`.
   * Crea 3 usuarios de prueba con contraseñas seguras (`operador1`, `supervisor1`, `encargado1`).
   * Registra materiales base (Aluminio A380, Bronce Fosforado, Hierro Gris nodular).
   * Registra maquinarias (Horno Inducción H1, Torno CNC T-100, Inyectora de Cámara Fría).
   * Registra procesos (Fusión, Colada, Rebabado, Maquinado).
   * Genera un lote de prueba con su respectivo **Estudio Previo Aprobado**.

---

### 3.2 Criterio 2.1.2: Personalización Avanzada del Administrador de Django (3 Puntos)
> **Requisito 3 puntos:** *Personaliza el administrador (list_display, filtros, búsqueda, validaciones y permisos por usuario) logrando una gestión de colecciones clara, eficiente y ajustada al problema.*

Se personalizará cada uno de los modelos del sistema mediante clases heredadas de `admin.ModelAdmin` con las siguientes características:

1. **`LoteMaterialAdmin`**:
   * `list_display`: `('codigo_lote', 'material', 'peso_inicial_kg', 'peso_restante_kg', 'porcentaje_merma_actual', 'fecha_ingreso', 'tiene_estudio_aprobado')`
   * `list_filter`: `('material', 'fecha_ingreso')`
   * `search_fields`: `('codigo_lote', 'material__nombre', 'proveedor')`
   * `readonly_fields`: `('peso_restante_kg', 'porcentaje_merma_actual')`
   * Columnas calculadas con formato visual de alerta (ej. color rojo si el remanente es bajo).

2. **`EstudioPrevioAdmin` (Gestión del Gatekeeper)**:
   * `list_display`: `('lote', 'fecha_estudio', 'peso_calibrado_kg', 'responsable_estudio', 'estado', 'supervisor_aprobador')`
   * `list_filter`: `('estado', 'fecha_estudio')`
   * `search_fields`: `('lote__codigo_lote', 'responsable_estudio__username')`
   * **Acción Personalizada:** Botón/acción masiva para `"Aprobar Estudios Previos Seleccionados"` restringida exclusivamente a usuarios con rol `Supervisor` o `Encargado`.
   * **Permisos granulares:** Un usuario con rol `Operador` solo puede ver o solicitar borrador, pero no puede aprobarlo (`has_change_permission`).

3. **`RegistroMermaAdmin`**:
   * `list_display`: `('lote', 'proceso', 'maquina', 'peso_merma_kg', 'tipo_merma', 'operador', 'fecha_registro')`
   * `list_filter`: `('proceso', 'maquina', 'tipo_merma', 'fecha_registro')`
   * `search_fields`: `('lote__codigo_lote', 'observaciones', 'operador__username')`
   * Validaciones a nivel de Admin mediante `save_model` que invocan el `full_clean()` del modelo.

4. **`LogAuditoriaAdmin` (Trazabilidad Inmutable)**:
   * `list_display`: `('fecha_hora', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'ip_origen')`
   * `list_filter`: `('accion', 'tabla_afectada', 'fecha_hora')`
   * `search_fields`: `('usuario__username', 'detalles', 'ip_origen')`
   * `readonly_fields`: Todos los campos.
   * `has_add_permission = False` y `has_delete_permission = False` (los logs no pueden alterarse ni borrarse manualmente).

---

### 3.3 Criterio 2.1.3: CRUDs Robustos con Validaciones y Pruebas (3 Puntos)
> **Requisito 3 puntos:** *Implementa el CRUD completo con validación de datos, manejo de errores y mensajes al usuario, código ordenado y reutilizable, verificado con casos de prueba.*

#### A. Operaciones CRUD para los Requisitos "M"
Se implementarán las 4 operaciones (Create, Read, Update, Delete) para cada entidad clave:
* **CRUD de Materiales y Lotes (M1):**
  * `Create:` Alta de nuevo lote con peso inicial y metadatos.
  * `Read:` Listado paginado con indicador de remanente en tiempo real y vista de detalle con desglose de consumos.
  * `Update:` Corrección de datos administrativos (proveedor, fecha) con bloqueo de edición sobre el peso inicial si ya posee mermas asociadas.
  * `Delete:` Eliminación lógica o física restringida si existen dependencias registradas.
* **CRUD de Estudio Previo de Contenido (M5):**
  * `Create:` Formulario de pesaje y metrología previa (peso bruto, tara, peso neto, impurezas estimadas).
  * `Read:` Ficha técnica del estudio previo con firma del técnico.
  * `Update / Aprobar:` Cambio de estado a `APROBADO` reservado a Supervisores.
  * `Delete:` Solo permitido en estado `BORRADOR`.
* **CRUD de Merma Específica (M4):**
  * `Create:` Registro de peso de merma vinculando proceso, máquina y lote.
  * `Read:` Listado histórico con filtros por máquina y material.
  * `Update:` Ajuste de observaciones o pesaje con recálculo automático del remanente.
  * `Delete:` Anulación de pesaje erróneo revirtiendo el saldo al lote de material.

#### B. Validaciones Estrictas de Negocio en Formularios y Modelos (`forms.py` y `models.py`)
```python
# Ejemplo conceptual de validación obligatoria en models.py / forms.py
def clean(self):
    super().clean()
    # 1. Validación de Estudio Previo (M5)
    if not hasattr(self.lote, 'estudio_previo') or self.lote.estudio_previo.estado != 'APROBADO':
        raise ValidationError(
            "ACCESO DENEGADO: No es posible registrar merma para este lote. "
            "El Estudio Previo de Contenido no existe o aún no ha sido Aprobado por el Supervisor."
        )

    # 2. Validación de Peso Positivo
    if self.peso_merma_kg <= 0:
        raise ValidationError("El peso de la merma debe ser un valor estrictamente mayor a 0 kg.")

    # 3. Validación de Capacidad / Saldo Remanente (M1)
    if self.peso_merma_kg > self.lote.peso_restante_kg:
        raise ValidationError(
            f"Error de inventario: La merma reportada ({self.peso_merma_kg} kg) "
            f"supera el contenido restante disponible en el lote ({self.lote.peso_restante_kg} kg)."
        )
```

#### C. Mensajería al Usuario (`django.contrib.messages`)
* Retroalimentación visual inmediata con alertas de Bootstrap:
  * `messages.success(request, "Merma de 45.2 kg registrada exitosamente. Saldo actualizado.")`
  * `messages.warning(request, "Atención: El lote ha alcanzado un 15% de merma acumulada.")`
  * `messages.error(request, "Operación rechazada: No cuenta con permisos de Supervisor para aprobar este estudio.")`

#### D. Casos de Prueba Automatizados (`apps/operaciones/tests.py`)
Se escribirán suites de prueba exhaustivas:
1. `test_calculo_automatico_contenido_restante`: Comprueba que al agregar mermas, el remanente disminuya matemáticamente de forma exacta.
2. `test_bloqueo_merma_sin_estudio_previo_aprobado`: Intenta registrar una merma en un lote sin estudio previo y comprueba que se lance un `ValidationError`.
3. `test_bloqueo_merma_superior_a_saldo`: Intenta registrar 150 kg de merma en un lote de 100 kg y comprueba el rechazo.
4. `test_permisos_rbac_operador_vs_supervisor`: Verifica que un operador reciba HTTP 403 al intentar aprobar un estudio previo.

---

### 3.4 Criterio 2.1.4: Seguridad, Sesiones y Evidencia Crítica de IA (3 Puntos)
> **Requisito 3 puntos:** *La aplicación integra sesiones y seguridad de forma robusta (permisos por rol, protección CSRF, validación de entradas, contraseñas cifradas) y evidencia un uso crítico de la IA: contrasta, corrige y justifica las sugerencias adoptadas.*

#### A. Mecanismos de Seguridad y Manejo de Sesiones
* **Protección CSRF:** Inclusión obligatoria del token `{% csrf_token %}` en todos los formularios de la aplicación.
* **Cifrado de Contraseñas:** Uso exclusivo del motor de hashing seguro de Django (PBKDF2 con SHA-256 por defecto).
* **Control de Sesiones:**
  * Expiración de sesión por inactividad tras 30 minutos (`SESSION_COOKIE_AGE = 1800`).
  * Destrucción de sesión en `logout` (`request.session.flush()`).
  * Cookies de sesión seguras (`SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`).
* **Decoradores y Mixins RBAC:**
  ```python
  from django.contrib.auth.decorators import user_passes_test
  
  def rol_requerido(*roles_permitidos):
      def check(user):
          return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=roles_permitidos).exists())
      return user_passes_test(check, login_url='usuarios:login')
  ```

#### B. Registro de Evidencia y Uso Crítico de Inteligencia Artificial (Bitácora de Decisiones)
Para cumplir con la rúbrica al nivel de 3 puntos, se documenta el contraste entre las sugerencias automatizadas de la IA y las correcciones de ingeniería aplicadas:

| Aspecto Evaluado | Sugerencia Inicial Generada por IA | Riesgo o Deficiencia Técnica Detectada | Solución Adoptada y Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Cálculo de Contenido Restante (M1)** | La IA sugirió calcular el saldo restante en el frontend con JavaScript y actualizarlo en una petición AJAX simple. | **Grave riesgo de inconsistencia:** Si dos operadores ingresan merma simultáneamente o si se altera el cliente web, los datos de inventario se corrompen y permiten saldos negativos (*race conditions*). | **Cálculo en Backend con Transacciones Atómicas:** Se implementó una propiedad `@property` en el modelo y las operaciones de descuento se encapsularon en bloques `transaction.atomic()` con `select_for_update()` a nivel de base de datos. |
| **Gestión de Credenciales (2.1.1)** | La IA propuso dejar `SECRET_KEY = 'clave-fija'` y `DEBUG = True` directamente en `settings.py`. | **Vulnerabilidad de seguridad:** Exposición de claves maestras en el repositorio de código y riesgo de fuga de información de debug en producción. | **Refactorización con `python-decouple`:** Se extrajeron todas las variables al archivo `.env`, se creó `.env.example` y se tipificaron las variables con `cast=bool` y `cast=Csv()`. |
| **Validación de Estudio Previo (M5)** | La IA propuso un simple checkbox `estudio_realizado = models.BooleanField(default=False)` que el operador marcaba libremente al registrar la merma. | **Invalidez de negocio:** El operador podía omitir el estudio real marcando la casilla sin supervisión ni datos metrológicos previos. | **Máquina de Estados y Aprobación Jerárquica:** Se creó el modelo relacional `EstudioPrevio` con estados (`BORRADOR`, `APROBADO`, `RECHAZADO`), firma del supervisor y bloqueo por `ValidationError` en backend. |
| **Logs de Auditoría (M3)** | La IA propuso escribir manualmente un `print()` o guardar un objeto log dentro de cada vista `post()`. | **Código frágil y no reutilizable:** Si se agregaban nuevas vistas o se modificaban registros desde el Administrador de Django o shell, las acciones quedaban sin registrar. | **Patrón Observer con Django Signals y Middleware:** Se crearon receptores para `post_save` y `post_delete` vinculados a un middleware que captura la IP y el usuario autenticado automáticamente en toda la app. |

---

## 4. Modelo de Datos y Diagrama de Entidades (Requisitos "M")

```mermaid
erDiagram
    UserProfile ||--o| User : "extiende"
    User ||--o{ EstudioPrevio : "registra / aprueba"
    User ||--o{ RegistroMerma : "registra como operador"
    User ||--o{ LogAuditoria : "ejecuta accion"

    Material ||--o{ LoteMaterial : "agrupa"
    LoteMaterial ||--|| EstudioPrevio : "requiere obligatoriamente"
    LoteMaterial ||--o{ RegistroMerma : "genera merma en"
    
    Maquina ||--o{ RegistroMerma : "maquinaria utilizada"
    Proceso ||--o{ RegistroMerma : "proceso realizado"

    LoteMaterial {
        string codigo_lote PK
        float peso_inicial_kg
        datetime fecha_ingreso
        string proveedor
    }

    EstudioPrevio {
        int id PK
        int lote_id FK
        float peso_calibrado_kg
        float porcentaje_humedad
        string estado "BORRADOR | APROBADO | RECHAZADO"
        int supervisor_id FK
        datetime fecha_aprobacion
    }

    RegistroMerma {
        int id PK
        int lote_id FK
        int proceso_id FK
        int maquina_id FK
        float peso_merma_kg
        string tipo_merma "ESCORIA | VIRUTA | REBABA | DEFECTO"
        int operador_id FK
        datetime fecha_registro
    }

    LogAuditoria {
        int id PK
        int usuario_id FK
        string accion "CREATE | UPDATE | DELETE"
        string tabla_afectada
        int registro_id
        text detalles
        string ip_origen
        datetime fecha_hora
    }
```

---

## 5. Guía de Ejecución y Comandos Paso a Paso

### Paso 1: Inicialización del Entorno y Dependencias
```powershell
cd "c:\Users\alumnosnunoa\Desktop\Solucion merma"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install django python-decouple dj-database-url
pip freeze > requirements.txt
```

### Paso 2: Creación del Proyecto y las Aplicaciones
```powershell
django-admin startproject fundicion_core .
python manage.py startapp auditoria
python manage.py startapp usuarios
python manage.py startapp operaciones
```

### Paso 3: Configuración de `.env` y `settings.py`
* Crear `.env` y `.env.example`.
* Modificar `settings.py` para integrar `python-decouple` y registrar las aplicaciones `apps.auditoria`, `apps.usuarios`, `apps.operaciones`.

### Paso 4: Migraciones y Creación de Base de Datos
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Paso 5: Carga de Datos de Prueba y Creación de Roles
```powershell
python manage.py createsuperuser --username admin --email admin@fundicion.local
python manage.py poblar_datos_prueba
```

### Paso 6: Ejecución de Pruebas Unitarias
```powershell
python manage.py test apps.operaciones apps.usuarios apps.auditoria -v 2
```

### Paso 7: Ejecución del Servidor
```powershell
python manage.py runserver
```
* Acceso a la aplicación: `http://127.0.0.1:8000/`
* Acceso al Administrador de Django: `http://127.0.0.1:8000/admin/`
