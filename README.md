# SIGMA-Cast: Sistema de Control y Trazabilidad de Merma en Fundición de Metales

Sistema web integral desarrollado en **Django** con gestión de entorno segura mediante **python-decouple**, diseñado bajo la metodología **MoSCoW (Requisitos Must Have: M1 a M5)** y cumpliendo al nivel de excelencia (**3 Puntos**) con cada uno de los criterios de la rúbrica de evaluación.

---

## 1. Problemática y Solución

En las empresas de fundición y metalmecánica, la **merma** (escoria en hornos, canales de colada, rebaba y viruta de maquinado) suele considerarse un descarte habitual. No obstante, al no medirse con precisión ni existir trazabilidad de quién procesa el metal, se genera una pérdida acumulativa de gran impacto financiero para la empresa.

**SIGMA-Cast** resuelve esta problemática implementando:
1. **Balance en tiempo real:** Cálculo automático del contenido útil restante de cada lote tras cada operación.
2. **Validación de Estudio Previo Obligatorio (Gatekeeper M5):** Bloqueo mandatorio en backend que impide registrar mermas o consumos si no existe un estudio metrológico previo aprobado por Supervisión.
3. **Control de Acceso Basado en Roles (RBAC M2):** Perfiles diferenciados para **Operador**, **Supervisor** y **Encargado / Administrador**.
4. **Pistas de Auditoría Inmutables (M3):** Registro forense de cada acceso, creación, modificación, aprobación y eliminación con IP y timestamp.

---

## 2. Requisitos MoSCoW Implementados (Letra M - Must Have)

| ID | Requisito Must Have | Implementación Técnica en el Proyecto |
|:---|:---|:---|
| **M1** | **Registro de Materiales y Saldo** | Modelo `LoteMaterial` con cálculo dinámico `@property peso_restante_kg`, `total_merma_kg` y porcentaje acumulado de merma. |
| **M2** | **Control de Acceso y Roles (RBAC)** | Modelo `PerfilUsuario` (roles `OPERADOR`, `SUPERVISOR`, `ENCARGADO`), decorador `@rol_requerido` y control en Django Admin. |
| **M3** | **Logs de Auditoría Forense** | Modelo `LogAuditoria` con `AuditoriaMiddleware` (captura IP y usuario en hilo) y señales de login/logout/operaciones. |
| **M4** | **Registro de Merma Específica** | Modelo `RegistroMerma` vinculando proceso, máquina, lote, cantidad y causa del descarte. |
| **M5** | **Validación de Estudio Previo** | Modelo `EstudioPrevio` con máquina de estados (`BORRADOR`, `EN_REVISION`, `APROBADO`, `RECHAZADO`) y validación estricta en el método `clean()` del modelo `RegistroMerma`. |

---

## 3. Cobertura de la Rúbrica de Calificación (Máximo Nivel: 3 Puntos)

### 2.1.1 Configura la conexión a BD de forma segura (3 Puntos)
* Externalización de variables sensibles mediante `python-decouple` en `.env` (ignorado en Git) y plantilla `.env.example`.
* Procedimiento documentado de migraciones (`makemigrations`, `migrate`).
* Verificación de funcionamiento y sembrado de catálogos mediante el comando `python manage.py poblar_datos_prueba`.

### 2.1.2 Personaliza el Administrador de Django (3 Puntos)
* Implementación avanzada en `admin.py`: `list_display`, filtros por fecha y proceso, cajas de búsqueda, `readonly_fields` y fieldsets.
* Badges de estado con formato HTML seguro (`format_html`) y columnas calculadas de saldo y porcentaje.
* Acción personalizada `"Aprobar Estudios Previos seleccionados"` restringida por permisos de usuario.
* Logs de auditoría con `has_add_permission = False` y `has_delete_permission = False` (inmutabilidad).

### 2.1.3 Operaciones CRUD completas con validaciones y pruebas (3 Puntos)
* CRUDs completos para Lotes, Estudios Previos y Mermas.
* Validaciones robustas en `forms.py` y `models.py` (rechazo de valores $\le 0$, control de no exceder saldo disponible, bloqueo de lotes sin estudio previo aprobado).
* Retroalimentación visual inmediata con alertas de `django.contrib.messages` (éxito, advertencia, error).
* Suite automatizada con 6 pruebas unitarias y de integración (`python manage.py test apps.operaciones`).

### 2.1.4 Seguridad, sesiones y uso crítico de IA (3 Puntos)
* Manejo estricto de sesiones (`SESSION_COOKIE_AGE = 1800`, expiración por inactividad, cookies `HttpOnly` y `SameSite='Lax'`).
* Protección contra CSRF en el 100% de los formularios y contraseñas hasheadas en PBKDF2.
* **Evidencia de Uso Crítico de IA:**
  * *Contraste 1:* IA sugirió calcular el saldo restante en JavaScript del cliente $\rightarrow$ **Corrección:** Movido al backend con transacciones atómicas `transaction.atomic()` para prevenir condiciones de carrera.
  * *Contraste 2:* IA sugirió `SECRET_KEY` plano en `settings.py` $\rightarrow$ **Corrección:** Externalizado con `python-decouple` y tipificación segura con `cast=bool`.
  * *Contraste 3:* IA sugirió un simple checkbox para el estudio previo $\rightarrow$ **Corrección:** Implementada máquina de estados con aprobación requerida de supervisor y rechazo por `ValidationError`.
  * *Contraste 4:* IA sugirió crear logs manualmente en vistas $\rightarrow$ **Corrección:** Implementado middleware de auditoría y señales desacopladas.

---

## 4. Guía de Instalación y Ejecución

### 4.1 Clonar o situarse en el repositorio
```powershell
cd "c:\Users\alumnosnunoa\Desktop\Solucion merma"
```

### 4.2 Crear y activar el entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4.3 Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 4.4 Configurar variables de entorno
Copiar `.env.example` como `.env` (ya viene preconfigurado para SQLite local):
```powershell
cp .env.example .env
```

### 4.5 Ejecutar migraciones
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4.6 Poblar datos de prueba y verificar conexión
```powershell
python manage.py poblar_datos_prueba
```

### 4.7 Ejecutar la suite de pruebas unitarias
```powershell
python manage.py test apps.operaciones -v 2
```

### 4.8 Iniciar el servidor de desarrollo
```powershell
python manage.py runserver
```
* Acceso a la aplicación: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Panel Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 5. Cuentas de Acceso Preconfiguradas para Pruebas

| Rol | Usuario | Contraseña | Permisos y Flujo Asignado |
|:---|:---|:---|:---|
| **Operador** | `operador1` | `Operador2026!` | Registro de pesajes, solicitud de estudio previo, registro de mermas. |
| **Supervisor** | `supervisor1` | `Supervisor2026!` | Dictamen y aprobación técnica de estudios previos (Gatekeeper M5), consulta de auditoría. |
| **Encargado** | `encargado1` | `Encargado2026!` | CRUD completo, anulación de mermas, administración de lotes y visualización forense. |
| **Administrador**| `admin` | `Admin2026!` | Superusuario global y acceso a Django Admin con vistas personalizadas. |
