# Documento de Especificación del Proyecto: Control y Trazabilidad de Merma en Fundición de Metales

---

## 1. Planteamiento de la Problemática

### 1.1 Contexto Industrial
En la industria de la fundición y metalmecánica, los procesos de transformación térmica y mecánica implican someter materias primas metálicas (lingotes, chatarra seleccionada, aleaciones como aluminio, bronce, acero y hierro gris) a distintas etapas operativas:
1. **Fusión y escoriado en hornos** (inducción, crisol o cubilote).
2. **Vaciado y colada** en moldes de arena o coquillas metálicas.
3. **Solidificación y desmolde**.
4. **Corte de mazarotas, canales de alimentación y rebabado**.
5. **Mecanizado, torneado, fresado y acabado superficial**.

### 1.2 La "Merma Silenciosa" y su Impacto Financiero
Durante cada una de estas fases se genera un porcentaje inevitable de **merma** (desperdicio o pérdida de material), atribuible a:
* Oxidación y volatilización de componentes metálicos en horno.
* Generación de escoria y restos en cucharas de colada.
* Desprendimiento de virutas, rebabas y partes no conformes en el maquinado.
* Piezas defectuosas por porosidad o contracción que deben descartarse.

A corto plazo, la merma suele percibirse en la planta como un costo inherente y tolerable. Sin embargo, al no existir un sistema formal y centralizado de medición:
* **Erosión de márgenes a largo plazo:** El material perdido acumula toneladas de metal de alto costo que se adquirió a precio de materia prima virgen y que termina devaluado o extraviado sin registro.
* **Falta de imputabilidad del costo:** La empresa desconoce con exactitud qué aleación, qué lote de producción o qué línea de negocio está absorbiendo el costo del desperdicio.
* **Descontrol de inventario real vs. teórico:** Los sistemas contables asumen un rendimiento teórico que no coincide con las existencias físicas en bodega, provocando desfases en las compras y paradas de planta.

### 1.3 Factores de Variabilidad No Controlados
El volumen de merma no es constante, sino que depende directamente de:
1. **Tipo y composición del material:** Cada metal posee diferente tasa de oxidación, fluidez y punto de fusión (ej. el magnesio o aluminio se oxidan mucho más rápido que el hierro).
2. **Maquinaria y tecnología utilizada:** Hornos descalibrados, crisoles desgastados o tornos con desgaste de herramienta aumentan drásticamente el desperdicio.
3. **Secuencia de exposición y tiempos de permanencia:** El número de horas de exposición térmica en el horno o la velocidad de mecanizado modifican la cantidad de merma producida.
4. **Falta de Trazabilidad Humana y Operativa:** No se registra de manera fidedigna qué operador estuvo al mando, qué supervisor aprobó la tirada ni quién autorizó el pesaje de salida.
5. **Carencia de un Estudio Previo Estandarizado:** Con frecuencia se inicia la fundición sin un pesaje metrológico y análisis de pureza previo del contenido, imposibilitando auditar cuánto material ingresó realmente al sistema antes de reportar la merma.

---

## 2. Propuesta de Solución Integral

Se plantea el diseño e implementación de una **Plataforma Web Especializada para el Control y Gestión de Mermas de Fundición**, construida bajo una arquitectura sólida que centralice el registro, automatice los balances de materia y garantice la seguridad y trazabilidad en toda la línea productiva.

### 2.1 Ejes Fundamentales de la Solución
1. **Balance Automático de Materia:** A partir del material bruto ingresado a producción y de la merma reportada en cada etapa, el sistema calcula de forma instantánea el **contenido restante útil** y las desviaciones respecto al estándar.
2. **Puerta de Control (Gatekeeper) por Estudio Previo:** Se implementa una validación obligatoria a nivel de sistema. **Ningún operador o supervisor puede registrar consumo o merma de un lote sin haber registrado y aprobado previamente los parámetros del estudio de contenido** (peso bruto calibrado, humedad superficial, pureza y porcentaje teórico admisible).
3. **Seguridad y Control de Acceso Basado en Roles (RBAC):**
   * **Operador:** Acceso restringido al ingreso de pesajes y reportes de producción de su turno.
   * **Supervisor:** Revisión, validación técnica, aprobación de estudios previos y control de tolerancias.
   * **Encargado (Administrador / Jefe de Planta):** Parametrización del sistema (maquinarias, materiales, procesos), auditoría de logs, análisis global y gestión de usuarios.
4. **Pistas de Auditoría Inmutables (Audit Trail):** Registro automático de metadatos (usuario que ejecutó la acción, marca temporal exacta `timestamp`, dirección IP, tipo de operación `CREATE/UPDATE/DELETE`, y estado previo vs. posterior de los datos).

---

## 3. Matriz de Priorización de Requisitos: Metodología MoSCoW

Para garantizar un desarrollo ágil, enfocado y alineado estrictamente con los objetivos del negocio y los criterios de evaluación, los requisitos se clasifican según el estándar **MoSCoW**:

```
+----------------------------------------------------------------------------------------------------+
|                                    METODOLOGÍA MoSCoW                                              |
+-------------------+--------------------------------------------------------------------------------+
| M - Must Have     | Indispensables y críticos. Si falta uno, la app no cumple su objetivo.        |
| S - Should Have   | Importantes de alto valor, a incorporar inmediatamente tras el núcleo base.    |
| C - Could Have    | Deseables y mejoras funcionales si existe disponibilidad de tiempo y recursos. |
| W - Won't Have    | Descartados explícitamente para el alcance de la versión inicial (MVP).        |
+-------------------+--------------------------------------------------------------------------------+
```

### 3.1 M - Must Have (Debe Tener - Crítico para el Éxito)
*Son los requisitos indispensables sin los cuales la aplicación no cumple su propósito principal.*

1. **M1. Módulo de Registro de Materiales e Inventario:**
   * Ingreso digitalizado de lotes de material (tipo de aleación, peso inicial ingresado en kg, proveedor, fecha).
   * Cálculo automático del contenido restante en tiempo real:
     $$\text{Contenido Restante} = \text{Peso Inicial Ingresado} - \sum(\text{Material Utilizado en Procesos}) - \sum(\text{Merma Directa Registrada})$$
   * Bloqueo lógico contra saldos negativos o consumos superiores a la disponibilidad real.

2. **M2. Control de Acceso y Roles (RBAC):**
   * Autenticación segura mediante usuario y contraseña cifrada.
   * Tres perfiles con permisos claramente delimitados:
     * **Operador:** Creación de registros operativos de uso y merma asociados a su persona; visualización limitada a su turno.
     * **Supervisor:** Aprobación de estudios previos, validación de desvíos, visualización de todo el historial de su área.
     * **Encargado:** Control total (CRUD completo sobre catálogos de máquinas, procesos, materiales, usuarios y reportes).

3. **M3. Logs de Auditoría (Trazabilidad y Seguridad):**
   * Registro histórico detallado para cada transacción crítica:
     * Quién realizó la acción (ID de usuario y rol).
     * Cuándo se realizó (fecha y hora exacta en zona horaria local).
     * Qué se modificó (acción: Creación, Modificación, Eliminación, valores anteriores y nuevos).
     * Origen de la conexión (dirección IP y agente de usuario).
   * Visualización no editable reservada exclusivamente para el rol de Encargado/Administrador.

4. **M4. Módulo de Registro de Merma Específica:**
   * Formulario estructurado para asentar la merma generada, vinculando obligatoriamente cuatro variables:
     * **El proceso realizado:** Fusión, Colada, Rebabado, Maquinado, etc.
     * **La máquina utilizada:** Horno 1, Crisol B, Torno CNC 3, Fresadora 2, etc.
     * **El tipo y cantidad de material:** Aleación específica y peso de la merma en kilogramos/gramos.
     * **Causa/Tipo de merma:** Escoria, rebaba, viruta metálica, pieza defectuosa.

5. **M5. Validación de Estudio Previo Obligatorio:**
   * Flujo de negocio mandatorio que impide el registro de operaciones de merma o consumo si no existe un **Estudio Previo de Contenido** formalmente registrado y en estado "Aprobado" para el lote en cuestión.
   * El estudio previo debe certificar: peso neto real inicial verificado en báscula, lote de material, fecha de calibración y firma/usuario del responsable del estudio.

---

### 3.2 S - Should Have (Debería Tener - Importante pero no bloqueante)
*Aportan un valor significativo y se incorporarán en cuanto la base de los requisitos "Must Have" esté consolidada.*

1. **S1. Secuencia de Exposición:**
   * Registro del historial secuencial de etapas a las que fue sometido el material (ej. Paso 1: Fusión a 750°C durante 120 min $\rightarrow$ Paso 2: Colada $\rightarrow$ Paso 3: Mecanizado).
2. **S2. Reportes de Acumulación Financiera:**
   * Módulo que multiplica los kilogramos de merma acumulada por el costo unitario de adquisición/fusión del material, reportando la pérdida monetaria total por período y por línea de fundición.
3. **S3. Historial de Variaciones y Patrones:**
   * Vista analítica con filtros avanzados para comparar la merma entre diferentes tipos de aleaciones e identificar qué material sufre mayor degradación.

---

### 3.3 C - Could Have (Podría Tener - Deseable si hay margen)
*Mejoras para optimizar la experiencia de usuario y la proactividad del sistema.*

1. **C1. Dashboard Visual Interactivo:**
   * Gráficos estadísticos en tiempo real (barras y gráficos de torta) que muestren las máquinas o procesos con mayores tasas de desperdicio.
2. **C2. Alertas Tempranas de Umbrales:**
   * Notificaciones en pantalla o correos automáticos dirigidos a los supervisores cuando una colada supere el umbral máximo de merma permitida (ej. > 8% del peso total).

---

### 3.4 W - Won't Have (No Tendrá - Fuera del Alcance Inicial)
*Exclusiones deliberadas para mantener el foco en la estabilidad del MVP.*

1. **W1. Integración IoT Automática:**
   * Conexión por telemetría directa con PLC, sensores de pesaje en tolva o básculas industriales mediante protocolos MQTT/Modbus. El pesaje en esta versión se efectuará mediante ingreso asistido validado.
2. **W2. Gestión Comercial de Desperdicios:**
   * Módulo para venta, cotización externa, reciclaje con terceros o subasta automatizada del material de merma acumulado.

---

## 4. Matriz de Alineación: Requisitos "Must Have" vs. Criterios de Calificación

| Requisito MoSCoW (M) | Criterio 2.1.1 (Base de Datos & Decouple) | Criterio 2.1.2 (Admin de Django Personalizado) | Criterio 2.1.3 (CRUDs Robustos con Validaciones) | Criterio 2.1.4 (Seguridad, Sesiones y Uso Crítico de IA) |
| :--- | :--- | :--- | :--- | :--- |
| **M1: Materiales y Saldo** | Parámetros DB en `.env`, migraciones limpias y seed data. | Admin con columnas calculadas, filtros por tipo y búsqueda. | CRUD completo de Lotes y Materiales con cálculo automático de remanente. | Vistas protegidas; transacciones atómicas para consistencia de saldo. |
| **M2: Roles y Acceso (RBAC)** | Modelo de usuarios y grupos persistidos correctamente. | Permisos granulares en Admin (`has_add_permission`, etc.). | Formularios condicionales según el rol autenticado. | Decoradores `@rol_requerido`, control estricto de sesiones y contraseñas cifradas. |
| **M3: Logs de Auditoría** | Modelo `AuditLog` persistido con integridad referencial. | Admin de solo lectura (`readonly_fields`), filtros por fecha/usuario. | Creación automática de logs ante operaciones C-U-D. | Trazabilidad forense con IP, sesión, timestamp y datos antiguos vs. nuevos. |
| **M4: Merma Específica** | Tablas relacionales normalizadas para Procesos, Máquinas y Mermas. | Admin con filtros cruzados por máquina, proceso y material. | CRUD completo de Merma con validación de peso y cálculo de balance. | Protección CSRF, sanitización de inputs y validación en backend. |
| **M5: Estudio Previo** | Restricciones de clave foránea y campos de estado (`APROBADO`, etc.). | Acciones personalizadas en Admin para aprobar/rechazar estudios. | Flujo de negocio obligatorio: bloqueo de merma si no existe estudio aprobado. | Arquitectura justificada contra sugerencias iniciales de IA (evaluación crítica). |
