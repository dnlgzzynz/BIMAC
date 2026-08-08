# Guía de Parámetros - Cubierta Orgánica de Museo

## Índice

1. [Parámetros de Diseño](#parámetros-de-diseño)
2. [Parámetros de Panelización](#parámetros-de-panelización)
3. [Parámetros de Costos](#parámetros-de-costos)
4. [Parámetros de Validación](#parámetros-de-validación)
5. [Parámetros de Revit](#parámetros-de-revit)

---

## Parámetros de Diseño

### Geometría Base

| Parámetro | Tipo | Rango | Default | Unidad | Descripción |
|-----------|------|-------|---------|--------|-------------|
| `Ancho_Museo` | Number Slider | 10.0 - 18.0 | 15.0 | m | Ancho total del museo (define luz libre) |
| `Largo_Museo` | Number Slider | 20.0 - 30.0 | 26.0 | m | Largo total del museo |
| `Altura_Cenit` | Number Slider | 6.0 - 12.0 | 8.5 | m | Altura máxima de la cubierta en el cenit |
| `Tension_Curva` | Number Slider | 0.0 - 1.0 | 0.65 | - | Factor de curvatura (0=plano, 1=máx curva) |

### Relaciones Geométricas

```
Proporción recomendada:
  Altura_Cenit / Ancho_Museo ≈ 0.56 (proporción áurea aproximada)

Ejemplo:
  Ancho = 15.0m
  Altura = 15.0 × 0.56 = 8.4m ≈ 8.5m
```

### Curvas de Control

| Parámetro | Descripción | Efecto |
|-----------|-------------|--------|
| `grado_curva` | Grado de interpolación | 3 = suave, 5 = más control |
| `puntos_control` | Cantidad de puntos | Más puntos = mayor definición |
| `rebuild_count` | Puntos de reconstrucción | 50 = estándar para fabricación |

---

## Parámetros de Panelización

### Subdivisión

| Parámetro | Tipo | Rango | Default | Descripción |
|-----------|------|-------|---------|-------------|
| `U_Count` | Integer | 5 - 25 | 13 | Divisiones en dirección U (ancho) |
| `V_Count` | Integer | 5 - 20 | 10 | Divisiones en dirección V (largo) |

### Cálculo de Cantidad de Paneles

```python
# Fórmula
total_paneles = U_Count × V_Count

# Ejemplo con defaults
total_paneles = 13 × 10 = 130 paneles

# Área promedio por panel
area_promedio = (Ancho × Largo) / total_paneles
area_promedio = (15 × 26) / 130 = 3.0 m²
```

### Dimensiones de Módulo

| Configuración | U_Count | V_Count | Módulo (m) | Paneles |
|---------------|---------|---------|------------|---------|
| Económica | 10 | 8 | 2.6 × 3.25 | 80 |
| **Estándar** | **13** | **10** | **2.0 × 2.6** | **130** |
| Detallada | 15 | 13 | 1.73 × 2.0 | 195 |
| Premium | 20 | 17 | 1.3 × 1.53 | 340 |

### Racionalización

| Parámetro | Tipo | Rango | Default | Descripción |
|-----------|------|-------|---------|-------------|
| `tolerance` | Number | 1 - 20 | 5 | Tolerancia de planarización (mm) |
| `max_deviation` | Number | 5 - 50 | 10 | Desviación máxima permitida (mm) |

**Efecto de la tolerancia:**
- **1-5 mm**: Paneles casi planos, menor costo de fabricación
- **5-10 mm**: Balance entre forma y costo (recomendado)
- **10-20 mm**: Mayor expresión formal, mayor costo

---

## Parámetros de Costos

### Costos Unitarios

| Tipo de Panel | Costo (MXN/m²) | Material | Fabricación |
|---------------|----------------|----------|-------------|
| `flat` | 450.00 | Policarbonato celular 16mm | Corte CNC |
| `single_curve` | 680.00 | Policarbonato celular 16mm | Termoformado |
| `double_curve` | 1,250.00 | Policarbonato sólido 10mm | Molde CNC |

### Factores Adicionales

| Factor | Porcentaje | Base de Cálculo | Descripción |
|--------|------------|-----------------|-------------|
| `STRUCTURE_FACTOR` | 25% | Costo paneles | Estructura metálica |
| `INSTALLATION_FACTOR` | 15% | Subtotal | Mano de obra instalación |
| `CONTINGENCY_FACTOR` | 10% | Subtotal | Contingencia/imprevistos |

### Fórmula de Costo Total

```python
# Cálculo de costo total
subtotal_paneles = (
    area_flat × 450 +
    area_single × 680 +
    area_double × 1250
)

estructura = subtotal_paneles × 0.25
subtotal_1 = subtotal_paneles + estructura

instalacion = subtotal_1 × 0.15
subtotal_2 = subtotal_1 + instalacion

contingencia = subtotal_2 × 0.10
TOTAL = subtotal_2 + contingencia
```

### Umbrales de Curvatura

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `THRESHOLD_FLAT` | 0.0001 | K < 0.0001 = plano |
| `THRESHOLD_SINGLE` | 0.001 | 0.0001 ≤ K < 0.001 = curva simple |
| - | > 0.001 | K ≥ 0.001 = doble curvatura |

---

## Parámetros de Validación

### Restricciones Estructurales

| Parámetro | Valor | Unidad | Descripción |
|-----------|-------|--------|-------------|
| `MAX_SPAN` | 15,000 | mm | Luz libre máxima |
| `MIN_SLOPE` | 2.0 | % | Pendiente mínima para drenaje |
| `MAX_DEFLECTION` | L/250 | - | Flecha máxima admisible |

### Tolerancias

| Parámetro | Valor | Unidad | Uso |
|-----------|-------|--------|-----|
| `TOLERANCE_SPAN` | 100 | mm | Margen para luz libre |
| `TOLERANCE_SLOPE` | 0.1 | % | Margen para pendiente |

### Resolución de Muestreo

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `SAMPLE_RESOLUTION` | 20 | Grid de 20×20 = 400 puntos |
| `SAMPLE_POINTS` | 5 | 5×5 = 25 puntos por panel |

---

## Parámetros de Revit

### Familia Adaptativa

**Nombre:** `Cubierta_Panel_Adaptive.rfa`

### Parámetros de Instancia

| Nombre en Revit | Tipo | Grupo | Descripción |
|-----------------|------|-------|-------------|
| `BIMAC_PanelType` | Text | Identity Data | flat / single_curve / double_curve |
| `BIMAC_TotalCost` | Currency | Costing | Costo total del panel (MXN) |
| `BIMAC_CostPerM2` | Currency | Costing | Costo por metro cuadrado |
| `BIMAC_Material` | Text | Materials | Tipo de policarbonato |
| `BIMAC_UValue` | Number | Thermal | Coeficiente térmico (W/m²K) |
| `BIMAC_PanelID` | Text | Identity Data | ID único (PANEL-0001) |
| `BIMAC_Area` | Area | Dimensions | Área del panel (m²) |

### Valores por Tipo

| Tipo | Material | U-Value | Color Sugerido |
|------|----------|---------|----------------|
| flat | Policarbonato Celular 16mm - Plano | 2.3 | Verde (RGB: 150, 255, 150) |
| single_curve | Policarbonato Celular 16mm - Curvo | 2.3 | Amarillo (RGB: 255, 255, 150) |
| double_curve | Policarbonato Sólido 10mm - Premium | 4.5 | Rojo (RGB: 255, 150, 150) |

### Parámetros de Proyecto

| Nombre | Tipo | Valor | Descripción |
|--------|------|-------|-------------|
| `Project_Name` | Text | "Museo - Cubierta Orgánica" | Nombre del proyecto |
| `Project_Code` | Text | "MUSEO-CUBIERTA-001" | Código del proyecto |
| `Budget_Total` | Currency | 280,000.00 | Presupuesto asignado |

---

## Configuraciones Predefinidas

### Configuración Económica

```python
config_economica = {
    "U_Count": 10,
    "V_Count": 8,
    "tolerance": 15,
    "target_flat_percent": 90,
    "budget": 200000
}
# Resultado: ~80 paneles, 90% planos
```

### Configuración Estándar (Recomendada)

```python
config_estandar = {
    "U_Count": 13,
    "V_Count": 10,
    "tolerance": 5,
    "target_flat_percent": 78,
    "budget": 280000
}
# Resultado: ~130 paneles, 78% planos
```

### Configuración Premium

```python
config_premium = {
    "U_Count": 17,
    "V_Count": 13,
    "tolerance": 3,
    "target_flat_percent": 60,
    "budget": 450000
}
# Resultado: ~220 paneles, 60% planos
```

---

## Sensibilidad de Parámetros

### Impacto en Costo

| Cambio de Parámetro | Impacto en Costo | Notas |
|---------------------|------------------|-------|
| +1 en U_Count | +3-5% | Más paneles, similar curvatura |
| +1 en V_Count | +3-5% | Más paneles, similar curvatura |
| +5mm en tolerance | -5-8% | Más paneles planos |
| -1m en Ancho | -5-10% | Menor área total |
| +1m en Altura_Cenit | +2-5% | Mayor curvatura |

### Impacto en Geometría

| Cambio de Parámetro | Efecto Visual | Estructural |
|---------------------|---------------|-------------|
| ↑ Tension_Curva | Más orgánico | Mayor curvatura |
| ↓ Altura_Cenit | Más bajo, compacto | Menos pendiente |
| ↑ U_Count | Paneles más pequeños | Más uniones |

---

## Validación de Parámetros

### Pre-condiciones

```python
# Validaciones de entrada
assert 10 <= Ancho_Museo <= 18, "Ancho fuera de rango"
assert 20 <= Largo_Museo <= 30, "Largo fuera de rango"
assert 6 <= Altura_Cenit <= 12, "Altura fuera de rango"
assert 0 <= Tension_Curva <= 1, "Tensión fuera de rango"
assert Ancho_Museo <= MAX_SPAN / 1000, "Ancho excede luz libre"
```

### Post-condiciones

```python
# Verificaciones de salida
assert max_span <= 15000, "Luz libre excedida"
assert min_slope >= 2.0, "Pendiente insuficiente"
assert total_cost <= budget, "Presupuesto excedido"
assert len(panels) == U_Count * V_Count, "Paneles incompletos"
```
