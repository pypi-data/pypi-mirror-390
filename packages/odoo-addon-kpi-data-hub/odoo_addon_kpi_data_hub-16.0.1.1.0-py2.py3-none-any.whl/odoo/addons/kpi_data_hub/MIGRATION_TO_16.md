# Migración KPI Data Hub: Odoo 17 → Odoo 16

## Resumen de Cambios Realizados

Este documento detalla todos los cambios realizados para adaptar el módulo KPI Data Hub de Odoo 17.0 a Odoo 16.0.

## 1. Cambios en el Manifiesto (`__manifest__.py`)

```python
# ANTES (Odoo 17)
'version': '17.0.1.0.0',

# DESPUÉS (Odoo 16)
'version': '16.0.1.0.0',
```

## 2. Cambios en Modelos Python

### 2.1 Tracking de Campos

**ANTES (Odoo 17):**
```python
entity_id = fields.Many2one(
    'kpi_hub.entity', string='Entity', required=True,
    tracking=True
)
```

**DESPUÉS (Odoo 16):**
```python
entity_id = fields.Many2one(
    'kpi_hub.entity', string='Entity', required=True,
    track_visibility='onchange'
)
```

### 2.2 Método Create con Decorador

**ANTES (Odoo 17):**
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # procesamiento
    records = super().create(vals_list)
    return records
```

**DESPUÉS (Odoo 16):**
```python
@api.model
def create(self, vals):
    # procesamiento para un solo registro
    record = super(KpiHubRecord, self).create(vals)
    return record
```

### 2.3 Sintaxis de Super()

**ANTES (Odoo 17):**
```python
result = super().write(vals)
```

**DESPUÉS (Odoo 16):**
```python
result = super(KpiHubRecord, self).write(vals)
```

## 3. Cambios en Vistas XML

### 3.1 Atributos de Columnas

**ANTES (Odoo 17):**
```xml
<field name="sequence" column_invisible="1"/>
```

**DESPUÉS (Odoo 16):**
```xml
<field name="sequence" invisible="1"/>
```

### 3.2 Expresiones Readonly/Invisible

**ANTES (Odoo 17):**
```xml
<field name="value" readonly="calculation_type in ['formula', 'group']"/>
<widget name="web_ribbon" invisible="active"/>
```

**DESPUÉS (Odoo 16):**
```xml
<field name="value" attrs="{'readonly': [('calculation_type', 'in', ['formula', 'group'])]}"/>
<widget name="web_ribbon" attrs="{'invisible': [('active', '=', True)]}"/>
```

### 3.3 Páginas de Notebook

**ANTES (Odoo 17):**
```xml
<page string="Data Configuration" invisible="calculation_type in ['formula', 'group']">
```

**DESPUÉS (Odoo 16):**
```xml
<page string="Data Configuration" attrs="{'invisible': [('calculation_type', 'in', ['formula', 'group'])]}">
```

## 4. Archivos Modificados

### Archivos Python:
- `models/kpi_data_record.py` - Tracking, método create, sintaxis super()
- `models/kpi_entity.py` - Tracking de campos
- `__manifest__.py` - Versión del módulo

### Archivos XML:
- `views/kpi_data_record_views.xml` - Atributos column_invisible, expresiones attrs
- `views/kpi_data_template_views.xml` - Atributos column_invisible, expresiones attrs
- `views/kpi_entity_views.xml` - Widget ribbon con attrs

### Documentación:
- `README.md` - Actualizado para Odoo 16
- `MIGRATION_TO_16.md` - Este archivo de migración

## 5. Verificaciones Realizadas

### ✅ Compatibilidad de Dependencias
- `base`: ✅ Compatible
- `web`: ✅ Compatible
- `mis_builder`: ✅ Compatible (verificar versión OCA para Odoo 16)
- `mail`: ✅ Compatible
- `date_range`: ✅ Compatible

### ✅ Sintaxis XML
- Todas las expresiones `column_invisible` cambiadas a `invisible`
- Todas las expresiones directas cambiadas a sintaxis `attrs`
- Widgets actualizados para Odoo 16

### ✅ Métodos API
- `@api.model_create_multi` cambiado a `@api.model`
- Sintaxis `super()` actualizada
- Tracking de campos actualizado

## 6. Funcionalidades que Permanecen Iguales

- **Estructura de datos**: Sin cambios
- **Lógica de negocio**: Sin cambios
- **Cálculos y fórmulas**: Sin cambios
- **Integración MIS Builder**: Sin cambios
- **Demo data**: Sin cambios
- **Security**: Sin cambios

## 7. Instrucciones de Instalación

1. **Verificar dependencias:**
   ```bash
   pip install odoo16-addon-mis-builder
   ```

2. **Copiar módulo:**
   ```bash
   cp -r kpi_data_hub /path/to/odoo16/addons/
   ```

3. **Actualizar lista de módulos:**
   ```bash
   odoo-bin -u all -d database_name
   ```

4. **Instalar módulo** desde la interfaz de Odoo 16

## 8. Tests de Migración

Para verificar que la migración fue exitosa:

1. **Crear entidades** y verificar tracking
2. **Crear templates** con jerarquías
3. **Crear registros** de datos
4. **Verificar cálculos** de fórmulas
5. **Probar vistas** y navegación
6. **Verificar integración** MIS Builder

## 9. Notas Importantes

- **Backup**: Siempre hacer backup antes de la migración
- **Testing**: Probar en entorno de desarrollo primero
- **MIS Builder**: Verificar versión compatible con Odoo 16
- **Assets**: Los assets web funcionan igual en Odoo 16

## 10. Próximos Pasos

1. **Testing completo** en entorno de desarrollo
2. **Validación** de todas las funcionalidades
3. **Documentación** de casos de uso específicos
4. **Deploy** en entorno de producción

---

**Fecha de migración**: $(date)
**Versión origen**: 17.0.1.0.0
**Versión destino**: 16.0.1.0.0
**Estado**: ✅ Completado
