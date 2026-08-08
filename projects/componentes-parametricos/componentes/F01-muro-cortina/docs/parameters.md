# Tabla de Parametros - F01 Muro Cortina Parametrico

Referencia completa de todos los parametros del componente.

---

## Parametros de Geometria Base

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `surface` | Surface | - | requerido | - | Superficie base del muro cortina (NURBS, Mesh, etc.) |
| `u_divisions` | int | 1 - 100 | 10 | - | Numero de divisiones en direccion U (horizontal) |
| `v_divisions` | int | 1 - 50 | 5 | - | Numero de divisiones en direccion V (vertical) |
| `module_width` | float | 600 - 3000 | 1500 | mm | Ancho objetivo del modulo |
| `module_height` | float | 1000 - 4500 | 3600 | mm | Alto objetivo del modulo |
| `corner_angle_min` | float | 30 - 90 | 45 | grados | Angulo minimo en esquinas |

### Notas de Geometria:
- Si se especifica `module_width`, el sistema calcula automaticamente `u_divisions`
- Si se especifica `module_height`, el sistema calcula automaticamente `v_divisions`
- Para superficies curvas, los modulos se ajustan a la curvatura local

---

## Parametros de Mullions

| Parametro | Tipo | Opciones | Default | Unidad | Descripcion |
|-----------|------|----------|---------|--------|-------------|
| `mullion_type` | enum | standard, thermal, structural | standard | - | Tipo de perfil de mullion |
| `mullion_width` | float | 40 - 150 | 65 | mm | Ancho visible del mullion |
| `mullion_depth` | float | 50 - 250 | 150 | mm | Profundidad del mullion |
| `mullion_material` | enum | aluminum_6063, aluminum_6061 | aluminum_6063 | - | Material del perfil |
| `mullion_finish` | enum | anodized_natural, anodized_bronze, powder_coat, pvdf | anodized_natural | - | Acabado del perfil |

### Tipos de Mullion:

| Tipo | Descripcion | U-value | Peso Aprox. |
|------|-------------|---------|-------------|
| **standard** | Perfil tubular basico | 5.8 W/m2K | 3.5 kg/m |
| **thermal** | Con rotura de puente termico | 2.5 W/m2K | 4.2 kg/m |
| **structural** | Reforzado para grandes luces | 5.8 W/m2K | 6.0 kg/m |

---

## Parametros de Travesanos

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `transom_width` | float | 40 - 150 | 50 | mm | Ancho visible del travesano |
| `transom_depth` | float | 50 - 200 | 120 | mm | Profundidad del travesano |
| `transom_type` | enum | standard, thermal | standard | - | Tipo de perfil |

---

## Parametros de Paneles

| Parametro | Tipo | Opciones | Default | Unidad | Descripcion |
|-----------|------|----------|---------|--------|-------------|
| `glass_type` | enum | single, double, triple | double | - | Tipo de vidrio |
| `glass_thickness` | float | 6 - 44 | 24 | mm | Espesor total del vidrio |
| `glass_coating` | enum | clear, tinted, low_e, reflective | low_e | - | Recubrimiento del vidrio |
| `spandrel_height` | float | 0 - 1200 | 900 | mm | Altura del panel opaco |
| `spandrel_insulation` | float | 0 - 100 | 50 | mm | Espesor de aislamiento |
| `panel_pattern` | enum | vision, mixed, alternating, horizontal_bands, custom | mixed | - | Patron de distribucion |
| `vision_percent` | float | 30 - 100 | 70 | % | Porcentaje objetivo de area de vision |

### Tipos de Vidrio Disponibles:

| ID | Descripcion | Espesor | U-value | SHGC | VLT |
|----|-------------|---------|---------|------|-----|
| single_clear | Vidrio claro simple | 6 mm | 5.8 | 0.82 | 88% |
| single_tinted | Vidrio tintado simple | 6 mm | 5.7 | 0.60 | 50% |
| double_clear | DVH claro | 24 mm | 2.8 | 0.70 | 78% |
| double_low_e | DVH Low-E | 24 mm | 1.6 | 0.42 | 70% |
| double_low_e_argon | DVH Low-E con Argon | 24 mm | 1.1 | 0.38 | 68% |
| triple_low_e | Triple Low-E | 44 mm | 0.8 | 0.35 | 60% |
| triple_low_e_argon | Triple Low-E con Argon | 44 mm | 0.5 | 0.30 | 55% |

### Patrones de Panel:

| Patron | Descripcion | Uso Tipico |
|--------|-------------|------------|
| **vision** | 100% paneles de vidrio | Fachadas de cristal puro |
| **mixed** | Spandrel en nivel inferior | Edificios de oficinas |
| **alternating** | Tablero de ajedrez | Efecto estetico |
| **horizontal_bands** | Bandas horizontales | Enfasis horizontal |
| **custom** | Definido por usuario | Disenos especiales |

---

## Parametros Estructurales

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `max_span` | float | 3000 - 6000 | 4500 | mm | Luz maxima sin soporte intermedio |
| `wind_load` | float | 0.5 - 3.0 | 1.2 | kPa | Carga de diseno por viento |
| `seismic_zone` | enum | A, B, C, D | C | - | Zona sismica (Mexico) |
| `anchor_spacing` | float | 1000 - 3000 | 1800 | mm | Espaciado de anclajes |
| `deflection_limit` | int | 120 - 240 | 175 | L/n | Limite de deflexion (luz/valor) |

### Zonas Sismicas:

| Zona | Factor | Regiones Ejemplo |
|------|--------|------------------|
| A | 0.10 | Yucatan, Campeche |
| B | 0.25 | Nuevo Leon, Coahuila |
| C | 0.40 | CDMX, Jalisco |
| D | 0.50 | Guerrero, Oaxaca, Chiapas |

---

## Parametros de Sistema

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `system_type` | enum | stick, unitized, structural_glazing, point_fixed | stick | Tipo de sistema de muro cortina |

### Comparacion de Sistemas:

| Sistema | Prefabricacion | Curvas | Altura Max | Costo Rel. |
|---------|----------------|--------|------------|------------|
| **Stick** | Baja | Si | 50m | 1.0x |
| **Unitized** | Alta | No | 200m | 1.35x |
| **Structural Glazing** | Media | Si | 30m | 1.25x |
| **Point-Fixed** | Alta | Si | 20m | 1.80x |

---

## Parametros de Costo

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `material_grade` | enum | basic, standard, premium | standard | Grado de materiales |
| `currency` | str | MXN, USD | MXN | Moneda para calculos |

### Grados de Material:

| Grado | Aluminio | Vidrio | Acabado |
|-------|----------|--------|---------|
| **basic** | 6063-T5 | DVH claro | Anodizado |
| **standard** | 6063-T5 | DVH Low-E | Powder coat |
| **premium** | 6061-T6 | Triple Low-E | PVDF |

---

## Parametros BIM

| Parametro | Tipo | Valor | Descripcion |
|-----------|------|-------|-------------|
| `BIMAC_CW_SystemType` | Text | - | Tipo de sistema |
| `BIMAC_CW_GlassType` | Text | - | Tipo de vidrio |
| `BIMAC_CW_UValue` | Number | W/m2K | Valor U promedio |
| `BIMAC_CW_SHGC` | Number | 0-1 | Coef. ganancia solar |
| `BIMAC_CW_VisionPercent` | Number | % | Porcentaje de vision |
| `BIMAC_CW_PanelArea` | Area | m2 | Area del panel |
| `BIMAC_CW_MullionLength` | Length | m | Longitud de mullion |
| `BIMAC_CW_CostEstimate` | Currency | MXN | Costo estimado |

---

## Parametros de Exportacion

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `export_lod` | enum | 200, 300, 350 | Nivel de detalle |
| `ifc_version` | enum | IFC2x3, IFC4 | Version IFC |
| `include_schedule` | bool | true | Incluir schedule en Revit |

---

## Formulas y Calculos

### Deflexion de Mullion

```
δ = (5 × w × L⁴) / (384 × E × I)

Donde:
- δ = deflexion maxima (mm)
- w = carga distribuida (N/mm)
- L = luz del mullion (mm)
- E = modulo de elasticidad (MPa)
- I = momento de inercia (mm⁴)
```

### Esfuerzo Flexionante

```
σ = M / S

Donde:
- σ = esfuerzo (MPa)
- M = momento maximo = w × L² / 8
- S = modulo de seccion (mm³)
```

### Movimiento Termico

```
ΔL = α × ΔT × L

Donde:
- ΔL = cambio de longitud (mm)
- α = coef. expansion (23.6×10⁻⁶ /°C para aluminio)
- ΔT = cambio de temperatura (°C)
- L = longitud original (mm)
```

---

## Validaciones Automaticas

| Validacion | Limite | Criterio |
|------------|--------|----------|
| Luz maxima | `max_span` | L < max_span |
| Deflexion | L/175 | δ < L/deflection_limit |
| Esfuerzo | Fy/1.5 | σ < 73 MPa (6063-T5) |
| Peso panel | 100 kg | Para manejo manual |
| Mov. termico | 10 mm | Capacidad de junta |
| Deriva sismica | h/300 | Capacidad del sistema |

---

*Documentacion de parametros v1.0 - F01 Muro Cortina*
