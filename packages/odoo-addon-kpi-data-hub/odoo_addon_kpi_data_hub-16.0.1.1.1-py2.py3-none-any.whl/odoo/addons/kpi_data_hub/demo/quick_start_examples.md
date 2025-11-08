# 🚀 Guía Rápida - Ejemplos de Expresiones KPI Hub en MIS Builder

## 📋 **Expresiones Básicas Disponibles**

### **1. Performance Financiera**
```
# Ingresos y Costos
kpi[REVENUE]                    # Ingresos operativos
kpi[COSTS]                      # Costos operativos
kpi[OTHER_INCOME]               # Otros ingresos

# Cálculos Automáticos
kpi[TOTAL_REVENUE]              # REVENUE + OTHER_INCOME
kpi[GROSS_PROFIT]               # TOTAL_REVENUE - COGS
kpi[OPERATING_PROFIT]           # GROSS_PROFIT - OPEX
kpi[NET_PROFIT]                 # OPERATING_PROFIT + OTHER_INCOME

# Márgenes
kpi[GROSS_MARGIN]               # (GROSS_PROFIT / TOTAL_REVENUE) * 100
kpi[OPERATING_MARGIN]           # (OPERATING_PROFIT / TOTAL_REVENUE) * 100
kpi[NET_MARGIN]                 # (NET_PROFIT / TOTAL_REVENUE) * 100
```

### **2. Dashboard de Ventas**
```
# Ventas por Trimestre
kpi[SALES_Q1]                   # Ventas Q1
kpi[SALES_Q2]                   # Ventas Q2
kpi[SALES_Q3]                   # Ventas Q3
kpi[SALES_Q4]                   # Ventas Q4

# Cálculos Automáticos
kpi[TOTAL_SALES]                # SALES_Q1 + SALES_Q2 + SALES_Q3 + SALES_Q4
kpi[AVG_QUARTERLY]              # TOTAL_SALES / 4
kpi[GROWTH_Q2]                  # ((SALES_Q2 - SALES_Q1) / SALES_Q1) * 100

# Cuotas de Mercado
kpi[MARKET_SHARE_NORTH]         # (SALES_NORTH / TOTAL_SALES) * 100
kpi[MARKET_SHARE_SOUTH]         # (SALES_SOUTH / TOTAL_SALES) * 100
kpi[MARKET_SHARE_EAST]          # (SALES_EAST / TOTAL_SALES) * 100
kpi[MARKET_SHARE_WEST]          # (SALES_WEST / TOTAL_SALES) * 100
```

### **3. Análisis de Productividad**
```
# Datos de Entrada
kpi[EMPLOYEES]                  # Número de empleados
kpi[HOURS_WORKED]               # Horas trabajadas
kpi[OUTPUT]                     # Producción total

# Cálculos Automáticos
kpi[PRODUCTIVITY_PER_HOUR]      # OUTPUT / HOURS_WORKED
kpi[PRODUCTIVITY_PER_EMPLOYEE]  # OUTPUT / EMPLOYEES
```

## 🔧 **Expresiones Combinadas**

### **1. Análisis de Rentabilidad**
```
# ROI del Negocio
(kpi[NET_PROFIT] / kpi[TOTAL_REVENUE]) * 100

# Eficiencia Operativa
(kpi[OPERATING_PROFIT] / kpi[OPERATING_EXPENSES]) * 100

# Comparación Trimestral
kpi[SALES_Q2] - kpi[SALES_Q1]
```

### **2. Análisis de Productividad vs Financiero**
```
# Ingresos por Empleado
kpi[TOTAL_REVENUE] / kpi[EMPLOYEES]

# Beneficio por Hora Trabajada
kpi[NET_PROFIT] / kpi[HOURS_WORKED]

# Eficiencia de Costos
kpi[TOTAL_REVENUE] / kpi[TOTAL_COSTS]
```

### **3. Análisis de Crecimiento**
```
# Crecimiento Anual
((kpi[TOTAL_SALES][2024] - kpi[TOTAL_SALES][2023]) / kpi[TOTAL_SALES][2023]) * 100

# Crecimiento Trimestral Promedio
(kpi[GROWTH_Q2] + kpi[GROWTH_Q3] + kpi[GROWTH_Q4]) / 3
```

## 📊 **Expresiones con Períodos Específicos**

### **1. Comparación de Períodos**
```
# Q1 2024 vs Q1 2023
kpi[REVENUE][Q1_2024] - kpi[REVENUE][Q1_2023]

# Crecimiento Anual
((kpi[REVENUE][2024] - kpi[REVENUE][2023]) / kpi[REVENUE][2023]) * 100

# Promedio de Últimos 3 Años
(kpi[REVENUE][2022] + kpi[REVENUE][2023] + kpi[REVENUE][2024]) / 3
```

### **2. Análisis de Tendencias**
```
# Tendencia Q1 a Q4 2024
kpi[SALES_Q4][2024] - kpi[SALES_Q1][2024]

# Promedio Trimestral 2024
(kpi[SALES_Q1][2024] + kpi[SALES_Q2][2024] + kpi[SALES_Q3][2024] + kpi[SALES_Q4][2024]) / 4
```

## 🎯 **Casos de Uso Prácticos**

### **1. Reporte de Performance Ejecutiva**
```
# Resumen Ejecutivo
kpi[NET_PROFIT]                 # Beneficio neto
kpi[NET_MARGIN]                 # Margen neto
kpi[TOTAL_REVENUE]              # Ingresos totales
kpi[EMPLOYEES]                  # Tamaño de la empresa

# KPIs de Eficiencia
kpi[NET_PROFIT] / kpi[EMPLOYEES]  # Beneficio por empleado
kpi[TOTAL_REVENUE] / kpi[EMPLOYEES]  # Ingresos por empleado
```

### **2. Dashboard de Ventas**
```
# Resumen de Ventas
kpi[TOTAL_SALES]                # Ventas totales
kpi[AVG_QUARTERLY]              # Promedio trimestral
kpi[GROWTH_Q2]                  # Crecimiento Q2

# Análisis por Región
kpi[MARKET_SHARE_NORTH]         # Cuota norte
kpi[MARKET_SHARE_SOUTH]         # Cuota sur
kpi[MARKET_SHARE_EAST]          # Cuota este
kpi[MARKET_SHARE_WEST]          # Cuota oeste
```

### **3. Reporte de Productividad**
```
# Métricas de Productividad
kpi[PRODUCTIVITY_PER_HOUR]      # Productividad por hora
kpi[PRODUCTIVITY_PER_EMPLOYEE]  # Productividad por empleado

# Análisis de Eficiencia
kpi[OUTPUT] / kpi[HOURS_WORKED]  # Producción por hora
kpi[OUTPUT] / kpi[EMPLOYEES]     # Producción por empleado
```

## ⚠️ **Notas Importantes**

### **1. Formato de Expresiones**
- ✅ **Correcto**: `kpi[REVENUE]`
- ❌ **Incorrecto**: `kpi[revenue]` (sensible a mayúsculas)
- ❌ **Incorrecto**: `kpi[REVENUE` (falta corchete de cierre)

### **2. Períodos Disponibles**
- **Trimestres**: `Q1_2024`, `Q2_2024`, `Q3_2024`, `Q4_2024`
- **Anuales**: `2023`, `2024`, `2025`
- **Sin período**: `kpi[REVENUE]` (usa período por defecto)

### **3. Cálculos Automáticos**
- Los KPIs con tipo "formula" se calculan automáticamente
- No es necesario escribir las fórmulas en MIS Builder
- Solo usar el código del KPI: `kpi[NET_PROFIT]`

## 🧪 **Ejemplos para Probar**

### **1. Expresiones Simples**
```
kpi[REVENUE]
kpi[COSTS]
kpi[PROFIT]
kpi[MARGIN]
```

### **2. Expresiones con Períodos**
```
kpi[REVENUE][Q1_2024]
kpi[SALES_Q1][2024]
kpi[NET_PROFIT][2024]
```

### **3. Expresiones Combinadas**
```
kpi[REVENUE] + kpi[OTHER_INCOME]
kpi[PROFIT] / kpi[REVENUE] * 100
kpi[TOTAL_SALES] / 4
```

### **4. Expresiones de Comparación**
```
kpi[SALES_Q2] - kpi[SALES_Q1]
kpi[REVENUE][2024] - kpi[REVENUE][2023]
```

## 📞 **Soporte**

Si tienes problemas con las expresiones:
1. Verifica que el código del KPI esté escrito correctamente
2. Comprueba que el período esté disponible
3. Revisa que la fuente AEP esté configurada
4. Contacta al equipo de desarrollo

---

**¡Ahora puedes empezar a usar estas expresiones en tus reportes MIS Builder!** 🎉
