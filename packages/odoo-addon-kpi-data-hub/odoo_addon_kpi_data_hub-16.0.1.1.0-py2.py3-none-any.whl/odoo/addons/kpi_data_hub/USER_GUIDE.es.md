# Guía de Usuario del Módulo KPI Data Hub

**Versión:** 1.0
**Fecha:** 2025-10-20

## 1. ¿Qué es el KPI Data Hub?

¡Bienvenido al **KPI Data Hub**! Esta herramienta te permite centralizar, organizar y analizar los indicadores clave (KPIs) de tu negocio de una manera estructurada y sencilla.

Con este módulo podrás:
-   **Crear plantillas reutilizables** para informes como Estados de Resultados (P&L), Balances, etc.
-   **Registrar datos** para diferentes empresas o departamentos (Entidades) y períodos de tiempo.
-   **Calcular automáticamente** KPIs complejos basados en fórmulas.
-   **Mantener un historial de versiones** de tus plantillas y saber qué registros están desactualizados.
-   **Integrar los datos** con los informes de MIS Builder.

## 2. Configuración Inicial

Antes de registrar datos, necesitas configurar las plantillas y las entidades.

### 2.1. Crear Entidades

Una "Entidad" representa una empresa, departamento, o cualquier unidad de negocio para la que quieras registrar KPIs.

1.  Ve a `KPI Hub > Configuración > Entidades`.
2.  Haz clic en **Crear**.
3.  Asigna un nombre (ej. "Filial España", "Departamento de Marketing") y guarda.

### 2.2. Crear una Plantilla de KPIs

La plantilla es la estructura de tu informe. Aquí definirás todas las líneas (ítems) que contendrá.

1.  Ve a `KPI Hub > Configuración > Plantillas`.
2.  Haz clic en **Crear**.
3.  Dale un nombre descriptivo, como "Estado de Resultados Mensual".
4.  En la pestaña **Items de la Plantilla**, haz clic en **Añadir una línea** para empezar a definir tus KPIs.

#### **Definir los Ítems de la Plantilla**

Cada línea de tu informe es un "Ítem". Puede ser un dato de entrada, una fórmula o un título.

-   **Nombre:** El texto que se mostrará en la línea (ej. "Ingresos por Ventas").
-   **Código:** Un identificador corto y único **SIN ESPACIOS** que usarás en las fórmulas (ej. `INGRESOS_VENTAS`).
-   **Tipo de Cálculo:**
    -   `Data Input`: Para valores que introducirás manualmente.
    -   `Formula`: Para valores que se calculan automáticamente.
    -   `Group Total`: Para ítems que funcionan como títulos o agrupadores.
-   **Fórmula:** Si el tipo es `Formula`, escribe aquí la operación matemática usando los **Códigos** de otros ítems.
    -   *Ejemplo:* Para un ítem "Margen Bruto" (código `MARGEN_BRUTO`), la fórmula podría ser `INGRESOS_TOTALES - COGS`.
-   **Padre:** Para crear jerarquías y agrupar ítems. Por ejemplo, "Salarios" y "Alquileres" pueden tener como padre a "Gastos Operativos".

**¡Guarda la plantilla cuando hayas añadido todos los ítems!**

## 3. Uso Diario: Registrar y Analizar Datos

Una vez configuradas las plantillas, ya puedes empezar a registrar los datos de tus KPIs.

### 3.1. Crear un Nuevo Registro de Datos

Hemos simplificado la creación de registros con un asistente.

1.  Ve a `KPI Hub > Data > Crear Registro`.
2.  Se abrirá un asistente. Rellena los siguientes campos:
    -   **Plantilla:** Elige la estructura que quieres usar (ej. "Estado de Resultados Mensual").
    -   **Entidad:** Selecciona para qué empresa o departamento son los datos.
    -   **Rango de Fechas:** Elige un período predefinido (ej. "Q1 2025") o introduce las fechas manualmente.
3.  Haz clic en **Crear Registro**.

Serás redirigido al formulario del nuevo registro, con todas las líneas de la plantilla listas para ser rellenadas.

### 3.2. Introducir Datos y Calcular Fórmulas

1.  Dentro del registro, ve a la pestaña **Valores de Items**.
2.  Rellena los campos de la columna **Valor** para todos los ítems que sean de entrada manual.
3.  Una vez introducidos los datos, haz clic en el botón **Calcular Fórmulas**.
4.  ¡Listo! El sistema calculará automáticamente todos los ítems definidos con fórmulas.

## 4. Gestión de Versiones de Plantillas

Si modificas una plantilla (ej. añades un nuevo tipo de gasto), el sistema creará una nueva versión. Los registros antiguos que usaban la versión anterior serán marcados como "desactualizados".

### 4.1. Identificar Registros Desactualizados

Un registro desactualizado mostrará:
-   Una cinta roja que dice **"Template Outdated"**.
-   Un banner de advertencia en la parte superior del formulario.

### 4.2. Actualizar un Registro a la Última Versión

Dentro del banner de advertencia, encontrarás el botón **"Actualizar a la Última Versión"**.
1.  Haz clic en el botón.
2.  El sistema actualizará el registro a la nueva estructura.
    -   Se añadirán las nuevas líneas (con valor 0).
    -   Se eliminarán las líneas que ya no existan.
3.  Recuerda rellenar los nuevos campos y volver a **Calcular Fórmulas**.

### 4.3. Actualizar Varios Registros a la Vez

Si tienes muchos registros desactualizados, puedes usar el asistente de actualización masiva.

1.  Ve a `KPI Hub > Configuración > Plantillas` y abre la plantilla que has modificado.
2.  En la parte superior, verás un botón inteligente que dice **"Registros Desactualizados"**. Haz clic en él.
3.  Se abrirá una vista con todos los registros afectados.
4.  Desde el menú `Acción`, selecciona **"Actualizar Versión de Plantilla"**.
5.  Se abrirá un asistente que te permitirá actualizar todos esos registros de una sola vez.

## 5. Integración con MIS Builder

Puedes usar los datos de KPI Hub directamente en tus informes de MIS Builder.

1.  Ve a `KPI Hub > Configuración > MIS Integration > MIS Report Integration`.
2.  Crea un nuevo registro de integración:
    -   **Nombre:** Un nombre descriptivo.
    -   **KPI Hub Template:** La plantilla de KPI Hub que quieres usar como fuente de datos.
    -   **MIS Report:** El informe de MIS Builder donde quieres mostrar los datos.
3.  En la pestaña **Item Mappings**, mapea cada "KPI Hub Item" con su correspondiente "MIS KPI".
4.  ¡Listo! Ahora, cuando ejecutes tu informe de MIS Builder, las expresiones `kpi(...)` obtendrán los datos directamente desde KPI Hub.
