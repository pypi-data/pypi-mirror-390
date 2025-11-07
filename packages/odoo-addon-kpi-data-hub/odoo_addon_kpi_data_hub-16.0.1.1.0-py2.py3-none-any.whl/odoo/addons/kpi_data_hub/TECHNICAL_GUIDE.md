# Guía Técnica del Módulo KPI Data Hub

**Versión:** 1.0
**Fecha:** 2025-10-20

## 1. Introducción

El módulo **KPI Data Hub** ha sido diseñado como un repositorio centralizado para almacenar, gestionar y versionar datos de Indicadores Clave de Rendimiento (KPIs). Su principal objetivo es desacoplar la captura de datos de su presentación, permitiendo una integración fluida con herramientas de reporting como **MIS Builder**.

Este documento detalla la arquitectura técnica, el flujo de datos y la lógica de negocio implementada.

## 2. Arquitectura y Modelos de Datos

El módulo se articula en torno a un núcleo de modelos de datos que separan la estructura (plantillas) de los datos concretos (registros).

### 2.1. Modelos Principales

-   `kpi_hub.template`: **Plantilla de KPI**
    -   **Propósito:** Define la estructura de un conjunto de KPIs (ej. un Estado de Resultados). Contiene los `item.template`.
    -   **Campos Clave:**
        -   `name`: Nombre de la plantilla (ej. "P&L Statement").
        -   `item_template_ids`: One2many a `kpi_hub.item.template`.
        -   **Campos de Versionado:** `version`, `version_date`, `version_changes`, `previous_version_id`.

-   `kpi_hub.item.template`: **Ítem de Plantilla de KPI**
    -   **Propósito:** Define una línea individual dentro de una plantilla (ej. "Ingresos", "COGS", "Margen Bruto").
    -   **Campos Clave:**
        -   `name`: Nombre del ítem.
        -   `code`: Identificador único usado en fórmulas (ej. `REVENUE`).
        -   `calculation_type`: Define si el valor es `'data'` (entrada manual), `'formula'` (calculado) o `'group'` (agrupador).
        -   `formula`: Expresión Python para ítems calculados (ej. `REVENUE - COGS`).
        -   `parent_id`: Para crear jerarquías.

-   `kpi_hub.record`: **Registro de Datos KPI**
    -   **Propósito:** Almacena los valores concretos para una plantilla, una entidad y un período de tiempo específicos.
    -   **Campos Clave:**
        -   `template_id`: Many2one a `kpi_hub.template`.
        -   `entity_id`: Many2one a `kpi_hub.entity`.
        -   `date_from`, `date_to`: Período del registro.
        -   `value_ids`: One2many a `kpi_hub.item.value`.
        -   **Campos de Versionado:** `template_version`, `is_outdated`, `outdated_message`.

-   `kpi_hub.item.value`: **Valor de Ítem KPI**
    -   **Propósito:** Almacena el valor numérico para un `item.template` dentro de un `record`.
    -   **Campos Clave:**
        -   `record_id`: Many2one a `kpi_hub.record`.
        -   `item_template_id`: Many2one a `kpi_hub.item.template`.
        -   `value`: El valor numérico del KPI.

### 2.2. Modelos de Integración (MIS Builder)

-   `kpi_hub.mis.report`: **Integración de Reporte MIS**
    -   **Propósito:** Vincula una `kpi_hub.template` con un `mis.report`.
    -   **Lógica:** Actúa como puente para la configuración de mapeos.

-   `kpi_hub.mis.item.mapping`: **Mapeo de Ítems**
    -   **Propósito:** Mapea un `kpi_hub.item.template` con un `mis.report.kpi`. Esto le dice a MIS Builder qué KPI de KPI Hub debe usar.

-   `kpi_hub.aep.source`: **Fuente de Datos AEP**
    -   **Propósito:** Expone los datos de KPI Hub a MIS Builder a través del motor AEP (Accounting Expression Processor).
    -   **Lógica:** Permite usar expresiones como `kpi('REVENUE')` en los KPIs de MIS Builder para obtener datos directamente desde los registros de KPI Hub.

## 3. Lógica de Negocio y Flujos de Trabajo

### 3.1. Sistema de Versionado

El versionado es una característica central para garantizar la integridad de los datos históricos cuando una plantilla cambia.

-   **Disparador:** El versionado se activa al modificar campos críticos de una `kpi_hub.template` (como `name` o `item_template_ids`) a través de la sobrescritura del método `write`.
-   **Proceso (`_increment_version`):**
    1.  Se crea una copia de la plantilla actual, que se convierte en la "versión anterior".
    2.  La plantilla actual incrementa su campo `version`.
    3.  Se actualizan los campos `version_date` y `version_changes`.
    4.  La nueva versión anterior (`previous_version_id`) apunta a la copia creada.
-   **Detección de Desactualización (`_compute_is_outdated`):**
    -   Un campo computado en `kpi_hub.record` compara `record.template_version` con `record.template_id.version`.
    -   Si la versión del registro es menor que la de su plantilla, `is_outdated` se establece en `True`.
    -   Esto dispara alertas visuales en la interfaz (ribbon y banner).

### 3.2. Sincronización de Plantillas

-   **Sincronización Individual (`action_sync_with_template`):**
    -   Actualiza `template_version` en el `kpi_hub.record`.
    -   Compara los ítems de la nueva versión de la plantilla con los `value_ids` existentes.
    -   Añade nuevos `item.value` para los ítems que no existían.
    -   Elimina los `item.value` de ítems que ya no están en la plantilla.
    -   Recalcula todas las fórmulas.

-   **Wizard de Actualización Masiva (`kpi_template_version_update_wizard`):**
    -   Permite a los usuarios actualizar múltiples registros desactualizados de una sola vez.
    -   Ofrece opciones para actualizar registros seleccionados, todos los de una plantilla o todos los de una entidad.

### 3.3. Cálculo de Fórmulas (`action_calculate_formulas`)

-   **Motor:** Utiliza `safe_eval` para ejecutar de forma segura las expresiones Python definidas en `kpi_hub.item.template`.
-   **Contexto de Evaluación:**
    -   Se construye un diccionario donde las claves son los `code` de los ítems y los valores son sus `value`.
    -   `safe_eval` ejecuta la fórmula usando este diccionario como `globals`.
-   **Orden de Cálculo:**
    1.  Primero se evalúan las fórmulas que no dependen de otros ítems calculados.
    2.  Se itera hasta que todas las fórmulas se hayan resuelto o se detecte una dependencia circular.

### 3.4. Post-Install Hook (`post_install_versioning_system`)

-   **Propósito:** Inicializa el sistema de versionado para datos preexistentes cuando el módulo se instala o actualiza.
-   **Lógica:**
    1.  Recorre todas las `kpi_hub.template` y les asigna `version = 1` y una fecha de versión.
    2.  Recorre todos los `kpi_hub.record` y establece su `template_version` a `1`.

## 4. Estructura del Módulo

```
kpi_data_hub/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── kpi_data_template.py  # Modelo de plantillas y versionado
│   ├── kpi_data_record.py    # Modelo de registros y cálculo de fórmulas
│   └── mis_kpi_data_integration.py # Modelos para la integración con MIS
├── wizards/
│   ├── kpi_record_create_wizard.py     # Lógica del wizard de creación
│   └── kpi_template_version_update_wizard.py # Lógica del wizard de actualización
├── views/
│   ├── kpi_data_template_views.xml
│   ├── kpi_data_record_views.xml
│   ├── mis_integration_views.xml
│   └── kpi_menus.xml
├── security/
│   └── ir.model.access.csv
└── demo/
    ├── comprehensive_demo.xml # Datos de ejemplo principales
    └── mis_reports_demo.xml   # Datos para la integración con MIS
```

## 5. Puntos de Extensión y Futuras Mejoras

-   **Nuevos Tipos de Cálculo:** Se podría extender `calculation_type` para soportar lógicas más complejas (ej. promedios, valores de períodos anteriores).
-   **Importación/Exportación:** Crear asistentes para importar/exportar plantillas y registros desde/hacia CSV o Excel.
-   **Integración con Presupuestos:** Añadir dependencias de `mis_builder_budget` para permitir la comparación de datos reales vs. presupuestados directamente en KPI Hub.
-   **Dashboards:** Crear vistas de tablero (dashboard) nativas para visualizar los KPIs sin depender de MIS Builder.
