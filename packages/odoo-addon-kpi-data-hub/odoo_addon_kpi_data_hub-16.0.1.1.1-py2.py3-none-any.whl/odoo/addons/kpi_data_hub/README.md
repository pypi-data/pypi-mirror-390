# 📊 KPI Data Hub - Manual de Usuario Completo

## 🎯 **Descripción General**

**KPI Data Hub** es un módulo de Odoo que permite crear, gestionar y analizar Indicadores Clave de Rendimiento (KPIs) de forma dinámica y flexible. Se integra perfectamente con **MIS Builder** para generar reportes ejecutivos y dashboards interactivos.

### ✨ **Características Principales**

- **Gestión de KPIs**: Crear y mantener KPIs con fórmulas dinámicas
- **Integración MIS Builder**: Generar reportes ejecutivos automáticamente
- **Cálculos Pro-rata**: Ajuste automático de valores por períodos
- **Multi-compañía**: Soporte completo para entornos multi-empresa
- **Jerarquías**: Organización de KPIs en grupos y subgrupos
- **Fórmulas Avanzadas**: Expresiones matemáticas complejas entre KPIs

---

## 🚀 **Instalación y Configuración**

### **Requisitos Previos**

- Odoo 16.0+
- Módulo `mis_builder` instalado
- Módulo `date_range` (OCA/server-ux)

### **Instalación**

1. **Instalar el módulo** desde la interfaz de Odoo
2. **Reiniciar Odoo** para cargar todos los modelos
3. **Verificar dependencias** en Aplicaciones > KPI Data Hub

---

## 📋 **Estructura del Módulo**

### **Modelos Principales**

#### 1. **Plantillas de KPI** (`kpi_hub.template`)
- Define la estructura base de KPIs
- Contiene items y configuraciones generales
- Base para crear registros de datos

#### 2. **Items de KPI** (`kpi_hub.item.template`)
- KPIs individuales dentro de una plantilla
- Tipos: datos, fórmulas, grupos
- Configuración de cálculos y validaciones

#### 3. **Entidades** (`kpi_hub.entity`)
- Organizaciones o unidades de negocio
- Pueden ser empresas, departamentos, proyectos
- Base para segmentación de datos

#### 4. **Registros de KPI** (`kpi_hub.record`)
- Instancias de datos para períodos específicos
- Vincula plantilla, entidad y rango de fechas
- Contiene valores reales de los KPIs

#### 5. **Valores de Items** (`kpi_hub.item.value`)
- Valores numéricos de cada KPI
- Cálculos automáticos para fórmulas
- Validaciones de datos y restricciones

---

## 🔧 **Configuración Inicial**

### **Paso 1: Crear Plantilla de KPI**

1. **Ir a**: KPI Data Hub > Configuración > Plantillas de KPI
2. **Crear nueva plantilla**:
   - **Nombre**: "Indicadores Financieros 2024"
   - **Descripción**: "KPIs principales del negocio"

### **Paso 2: Definir Items de KPI**

#### **Item de Datos (REVENUE)**
```
Nombre: REVENUE
Código: REVENUE
Tipo de Cálculo: Data Input
Tipo de Dato: Currency
Prefijo: €
Decimales: 2
Secuencia: 10
```

#### **Item de Fórmula (PROFIT)**
```
Nombre: PROFIT
Código: PROFIT
Tipo de Cálculo: Formula
Fórmula: REVENUE - COSTS
Tipo de Dato: Currency
Prefijo: €
Decimales: 2
Secuencia: 30
```

#### **Item de Fórmula (MARGIN)**
```
Nombre: MARGIN
Código: MARGIN
Tipo de Cálculo: Formula
Fórmula: PROFIT / REVENUE * 100
Tipo de Dato: Percentage
Sufijo: %
Decimales: 2
Secuencia: 40
```

### **Paso 3: Crear Entidad**

1. **Ir a**: KPI Data Hub > Configuración > Entidades
2. **Crear nueva entidad**:
   - **Nombre**: "Empresa Principal"
   - **Compañía**: Seleccionar compañía
   - **Partner**: Opcional

### **Paso 4: Configurar Rango de Fechas**

1. **Ir a**: Configuración > Técnico > Rangos de Fecha > Tipos de Rango
2. **Crear tipo**: "Períodos Mensuales"
3. **Ir a**: Rangos de Fecha
4. **Crear rango**: "Enero 2024" (01/01/2024 - 31/01/2024)

---

## 📊 **Creación de Datos**

### **Paso 1: Crear Registro de KPI**

1. **Ir a**: KPI Data Hub > Datos > Registros de KPI
2. **Crear nuevo registro**:
   - **Plantilla**: Seleccionar plantilla creada
   - **Entidad**: Seleccionar entidad
   - **Rango de Fechas**: Seleccionar período
   - **Compañía**: Seleccionar compañía

### **Paso 2: Ingresar Valores**

El sistema creará automáticamente campos para cada item de la plantilla:

#### **Valores de Entrada**
- **REVENUE**: 100,000.00
- **COSTS**: 70,000.00

#### **Valores Calculados Automáticamente**
- **PROFIT**: 30,000.00 (REVENUE - COSTS)
- **MARGIN**: 30.0% (PROFIT / REVENUE * 100)

---

## 🔗 **Integración con MIS Builder**

### **Configuración de Fuente AEP**

1. **Ir a**: KPI Data Hub > Integración MIS > Fuentes AEP
2. **Crear nueva fuente**:
   - **Nombre**: "Fuente KPI Hub Principal"
   - **Plantilla**: Seleccionar plantilla de KPI
   - **Patrón de Expresión**: "kpi"
   - **Compañía**: Seleccionar compañía

### **Configuración de Integración MIS**

1. **Ir a**: KPI Data Hub > Integración MIS > Integraciones MIS
2. **Crear nueva integración**:
   - **Nombre**: "Integración Financiera"
   - **Plantilla KPI Hub**: Seleccionar plantilla
   - **Reporte MIS**: Seleccionar reporte MIS
   - **Mapeo Automático**: Activar

### **Mapeo de Items**

El sistema creará automáticamente mapeos entre:
- **REVENUE** → **KPI MIS Ingresos**
- **COSTS** → **KPI MIS Costos**
- **PROFIT** → **KPI MIS Beneficio**
- **MARGIN** → **KPI MIS Margen**

---

## 📈 **Creación de Reportes MIS**

### **Paso 1: Crear Plantilla de Reporte**

1. **Ir a**: Contabilidad > Configuración > MIS Reporting > Plantillas de Reporte MIS
2. **Crear nueva plantilla**:
   - **Nombre**: "Dashboard KPI Hub"
   - **Descripción**: "Reporte de KPIs del negocio"

### **Paso 2: Definir KPIs del Reporte**

#### **KPI Ingresos**
```
Nombre: REVENUE
Descripción: Ingresos del Período
Expresión: kpi[REVENUE]
Tipo: Numérico
Secuencia: 10
```

#### **KPI Costos**
```
Nombre: COSTS
Descripción: Costos del Período
Expresión: kpi[COSTS]
Tipo: Numérico
Secuencia: 20
```

#### **KPI Beneficio**
```
Nombre: PROFIT
Descripción: Beneficio del Período
Expresión: kpi[PROFIT]
Tipo: Numérico
Secuencia: 30
```

#### **KPI Margen**
```
Nombre: MARGIN
Descripción: Margen de Beneficio
Expresión: kpi[MARGIN]
Tipo: Porcentaje
Secuencia: 40
```

### **Paso 3: Crear Instancia del Reporte**

1. **Ir a**: Contabilidad > Reportes > MIS Reporting > Reportes MIS
2. **Crear nueva instancia**:
   - **Nombre**: "Dashboard Q1 2024"
   - **Plantilla**: Seleccionar plantilla creada
   - **Fecha Base**: 31/03/2024

### **Paso 4: Configurar Períodos**

1. **Agregar período**:
   - **Nombre**: "Q1 2024"
   - **Modo**: Fechas fijas
   - **Desde**: 01/01/2024
   - **Hasta**: 31/03/2024
   - **Fuente**: Actuales

---

## 🎯 **Casos de Uso Prácticos**

### **Caso 1: Dashboard Financiero Mensual**

#### **Objetivo**
Crear un dashboard que muestre KPIs financieros mensuales con comparativas.

#### **Configuración**
1. **Plantilla KPI Hub**: "Indicadores Financieros 2024"
2. **Items**: REVENUE, COSTS, PROFIT, MARGIN
3. **Períodos**: Enero, Febrero, Marzo 2024
4. **Reporte MIS**: Dashboard con columnas mensuales

#### **Resultado Esperado**
```
| KPI        | Enero | Febrero | Marzo | Total |
|------------|-------|---------|-------|-------|
| Ingresos   | 100K  | 120K    | 150K  | 370K  |
| Costos     | 70K   | 80K     | 100K  | 250K  |
| Beneficio  | 30K   | 40K     | 50K   | 120K  |
| Margen     | 30%   | 33%     | 33%   | 32%   |
```

### **Caso 2: Análisis de Rentabilidad por Producto**

#### **Objetivo**
Analizar la rentabilidad de diferentes líneas de producto.

#### **Configuración**
1. **Plantilla KPI Hub**: "Rentabilidad por Producto"
2. **Items**: VENTAS_PRODUCTO_A, COSTOS_PRODUCTO_A, MARGEN_PRODUCTO_A
3. **Entidades**: Producto A, Producto B, Producto C
4. **Reporte MIS**: Análisis comparativo por producto

### **Caso 3: Seguimiento de Objetivos Anuales**

#### **Objetivo**
Monitorear el progreso hacia objetivos anuales de ventas y rentabilidad.

#### **Configuración**
1. **Plantilla KPI Hub**: "Objetivos 2024"
2. **Items**: OBJETIVO_VENTAS, VENTAS_REALES, CUMPLIMIENTO
3. **Fórmula CUMPLIMIENTO**: (VENTAS_REALES / OBJETIVO_VENTAS) * 100
4. **Reporte MIS**: Seguimiento mensual con indicadores de progreso

---

## 🔧 **Fórmulas Avanzadas**

### **Operadores Disponibles**
- **Suma**: `ITEM1 + ITEM2`
- **Resta**: `ITEM1 - ITEM2`
- **Multiplicación**: `ITEM1 * ITEM2`
- **División**: `ITEM1 / ITEM2`
- **Porcentaje**: `(ITEM1 / ITEM2) * 100`
- **Potencia**: `ITEM1 ^ 2`
- **Raíz cuadrada**: `ITEM1 ^ 0.5`

### **Ejemplos de Fórmulas**

#### **Margen Bruto**
```
MARGEN_BRUTO = (VENTAS - COSTOS_VENTAS) / VENTAS * 100
```

#### **ROI (Retorno de Inversión)**
```
ROI = (BENEFICIO_NETO / INVERSION_TOTAL) * 100
```

#### **Ratio de Liquidez**
```
LIQUIDEZ = ACTIVO_CORRIENTE / PASIVO_CORRIENTE
```

#### **Rotación de Inventario**
```
ROTACION_INVENTARIO = COSTOS_VENTAS / INVENTARIO_PROMEDIO
```

---

## 📊 **Reportes y Exportación**

### **Vista Previa del Reporte**
1. **Ir a**: Reporte MIS > Botón "Vista Previa"
2. **Verificar datos**: Los valores de KPI Hub deben aparecer
3. **Ajustar filtros**: Usar filtros de fecha y entidad

### **Exportación**
- **PDF**: Botón "Imprimir PDF"
- **Excel**: Botón "Exportar XLSX"
- **Dashboard**: Agregar a dashboard de Odoo

### **Filtros Disponibles**
- **Período**: Rango de fechas
- **Entidad**: Empresa, departamento, proyecto
- **Compañía**: Filtro multi-compañía
- **KPI**: Selección específica de indicadores

---

## ⚠️ **Solución de Problemas**

### **Problema: KPIs no muestran datos**

#### **Causas Comunes**
1. **Fórmulas con división por cero**
2. **Mapeos no configurados**
3. **Fuente AEP no activa**
4. **Períodos sin datos**

#### **Solución**
1. **Verificar valores**: Asegurar que REVENUE > 0
2. **Revisar mapeos**: Verificar integración MIS
3. **Activar fuente**: Comprobar estado de fuente AEP
4. **Cargar datos**: Crear registros para el período

### **Problema: Cálculos incorrectos**

#### **Causas Comunes**
1. **Orden de dependencias**
2. **Fórmulas mal escritas**
3. **Tipos de datos incorrectos**

#### **Solución**
1. **Revisar secuencia**: Asegurar orden correcto
2. **Validar sintaxis**: Verificar fórmulas
3. **Comprobar tipos**: Asegurar consistencia de datos

### **Problema: Integración MIS no funciona**

#### **Causas Comunes**
1. **Expresiones KPI mal configuradas**
2. **Fuente AEP no configurada**
3. **Módulo MIS Builder no instalado**

#### **Solución**
1. **Verificar expresiones**: Usar formato `kpi[CODE]`
2. **Configurar fuente**: Crear fuente AEP válida
3. **Instalar dependencias**: Asegurar MIS Builder activo

---

## 🚀 **Mejores Prácticas**

### **Diseño de Plantillas**
1. **Planificar estructura**: Definir jerarquía de KPIs
2. **Usar códigos claros**: Nombres descriptivos y únicos
3. **Validar fórmulas**: Probar cálculos antes de producción
4. **Documentar**: Mantener registro de cambios

### **Gestión de Datos**
1. **Validación**: Usar restricciones de valor mínimo/máximo
2. **Consistencia**: Mantener tipos de datos uniformes
3. **Auditoría**: Revisar cambios y cálculos
4. **Backup**: Respaldo regular de configuraciones

### **Integración MIS**
1. **Mapeo automático**: Usar función de mapeo automático
2. **Expresiones simples**: Mantener expresiones KPI claras
3. **Pruebas**: Verificar reportes antes de compartir
4. **Mantenimiento**: Revisar integraciones regularmente

---

## 📚 **Referencias Técnicas**

### **Modelos del Sistema**
- `kpi_hub.template`: Plantillas de KPI
- `kpi_hub.item.template`: Items individuales
- `kpi_hub.entity`: Entidades organizacionales
- `kpi_hub.record`: Registros de datos
- `kpi_hub.item.value`: Valores de KPIs
- `kpi_hub.aep.source`: Fuentes de datos AEP
- `kpi_hub.mis.report`: Integración con MIS Builder

### **Campos Clave**
- **Código**: Identificador único del KPI
- **Fórmula**: Expresión matemática para cálculos
- **Tipo de Cálculo**: data, formula, group
- **Secuencia**: Orden de procesamiento
- **Validaciones**: Restricciones de valor

### **API y Extensiones**
- **Métodos de cálculo**: `_calculate_formulas()`
- **Validaciones**: `_check_value_constraints()`
- **Integración AEP**: `get_kpi_value()`
- **Mapeo MIS**: `_auto_map_items()`

---

## 🔮 **Roadmap y Futuras Funcionalidades**

### **Versión 17.0**
- **Dashboards interactivos**: Gráficos y visualizaciones
- **Alertas automáticas**: Notificaciones de KPIs críticos
- **Análisis predictivo**: Tendencias y forecasting
- **Integración BI**: Conexión con herramientas de Business Intelligence

### **Mejoras Planificadas**
- **Workflows**: Aprobación de datos y cambios
- **Versionado**: Historial de cambios en KPIs
- **APIs externas**: Conexión con sistemas externos
- **Machine Learning**: Análisis automático de patrones

---

## 📞 **Soporte y Contacto**

### **Documentación**
- **Manual de Usuario**: Este documento
- **Vídeos Tutoriales**: Disponibles en el portal
- **Base de Conocimientos**: FAQ y casos de uso

### **Soporte Técnico**
- **Email**: soporte@empresa.com
- **Teléfono**: +34 900 123 456
- **Horario**: Lunes a Viernes 9:00-18:00

### **Comunidad**
- **Foro de Usuarios**: Compartir experiencias
- **Grupo de Usuarios**: Encuentros presenciales
- **Blog**: Artículos y novedades

---

## 📄 **Licencia**

Este módulo está licenciado bajo **AGPL-3.0** y es desarrollado por la comunidad Odoo.

---

*Última actualización: Septiembre 2025*
*Versión del módulo: 16.0.1.0.1*

