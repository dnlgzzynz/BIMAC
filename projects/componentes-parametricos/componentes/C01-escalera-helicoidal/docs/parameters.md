# Tabla de Parametros - C01 Escalera Helicoidal

Referencia completa de parametros para diseno de escaleras helicoidales.

---

## Parametros de Geometria

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `floor_to_floor` | float | 2400 - 6000 | 3000 | mm | Altura de piso a piso |
| `outer_diameter` | float | 1400 - 4000 | 2000 | mm | Diametro exterior |
| `inner_diameter` | float | 100 - 500 | 200 | mm | Diametro interior (columna) |
| `rotation_angle` | float | 180 - 1080 | 360 | grados | Rotacion total |
| `rotation_direction` | enum | CCW, CW | CCW | - | Direccion de giro |
| `start_angle` | float | 0 - 360 | 0 | grados | Orientacion inicial |
| `riser_height` | float | 140 - 220 | 175 | mm | Altura de contrahuella |

### Tipologias de Estructura

| Tipo | Descripcion | Diametro Min | Diametro Max | Materiales |
|------|-------------|--------------|--------------|------------|
| `central_column` | Peldanos soldados a columna central | 1400 | 3000 | acero, concreto |
| `cantilever` | Peldanos empotrados en muro curvo | 1600 | 2500 | acero, concreto |
| `perimeter_beam` | Viga helicoidal perimetral | 1800 | 4000 | acero |
| `double_stringer` | Largueros interior y exterior | 1600 | 3500 | acero, madera |
| `suspended` | Colgada de estructura superior | 1600 | 3000 | acero |

---

## Parametros de Peldanos

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `tread_thickness` | float | 6 - 100 | 40 | mm | Espesor del peldano |
| `nosing` | float | 0 - 50 | 25 | mm | Proyeccion de nariz |
| `tread_material` | enum | ver tabla | steel | - | Material del peldano |
| `finish` | enum | ver tabla | antislip | - | Acabado superficial |
| `open_riser` | bool | true/false | true | - | Contrahuella abierta |

### Materiales de Peldanos

| Material | Espesor Min (mm) | Espesor Tipico (mm) | Peso (kg/m3) | Costo (MXN/m2) |
|----------|------------------|---------------------|--------------|----------------|
| `steel` | 6 | 8 | 7850 | 2,800 |
| `wood` | 35 | 45 | 700 | 4,500 |
| `glass` | 30 | 36 | 2500 | 8,500 |
| `concrete` | 50 | 80 | 2400 | 3,200 |
| `composite` | 30 | 40 | 1200 | 5,500 |

### Acabados Disponibles

| Acabado | Descripcion | Costo (MXN/m2) |
|---------|-------------|----------------|
| `primer` | Primario anticorrosivo | 180 |
| `paint` | Pintura esmalte | 280 |
| `powder_coat` | Pintura electrostatica | 450 |
| `galvanize` | Galvanizado en caliente | 15/kg |
| `antislip` | Tratamiento antiderrapante | 250 |
| `polish` | Pulido (acero inox) | 380 |
| `wood_stain` | Tinte para madera | 320 |
| `lacquer` | Laca para madera | 420 |

---

## Parametros de Estructura

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `structure_type` | enum | ver tabla | central_column | - | Tipo de estructura |
| `column_diameter` | float | 100 - 250 | 150 | mm | Diametro de columna |
| `column_thickness` | float | 4 - 12 | 6 | mm | Espesor de pared |
| `column_material` | enum | steel, concrete | steel | - | Material de columna |
| `base_plate_diameter` | float | 300 - 600 | 400 | mm | Diametro placa base |
| `base_plate_thickness` | float | 12 - 30 | 20 | mm | Espesor placa base |

---

## Parametros de Barandal

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `handrail_height` | float | 850 - 1100 | 1000 | mm | Altura de pasamanos |
| `handrail_diameter` | float | 32 - 57 | 42 | mm | Diametro de pasamanos |
| `handrail_material` | enum | steel, wood, aluminum | steel | - | Material |
| `inner_handrail` | bool | true/false | true | - | Pasamanos interior |
| `outer_handrail` | bool | true/false | true | - | Pasamanos exterior |
| `baluster_type` | enum | round, square, flat | round | - | Tipo de balaustre |
| `baluster_diameter` | float | 12 - 25 | 16 | mm | Diametro/dimension |
| `baluster_spacing` | float | 75 - 120 | 100 | mm | Espaciamiento |
| `infill_type` | enum | ver tabla | balusters | - | Tipo de relleno |

### Tipos de Balaustres

| Tipo | Descripcion | Dimension Tipica |
|------|-------------|------------------|
| `round` | Tubo redondo | D16mm |
| `square` | Perfil cuadrado | 14x14mm |
| `flat` | Solera plana | 30x6mm |
| `decorative` | Torneado decorativo | D20mm |

### Tipos de Relleno

| Tipo | Descripcion | Costo (MXN/m2) |
|------|-------------|----------------|
| `balusters` | Solo balaustres | incluido |
| `glass` | Panel de vidrio templado | 4,500 |
| `cable` | Cables tensados horizontales | 2,800 |
| `mesh` | Malla metalica | 1,800 |
| `perforated` | Lamina perforada | 2,200 |

---

## Parametros de Descanso

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `include_landing` | bool | true/false | false | - | Incluir descanso |
| `landing_angle` | float | 0 - 360 | 0 | grados | Posicion angular |
| `landing_width` | float | 800 - 1500 | 1000 | mm | Ancho del descanso |
| `landing_depth` | float | 800 - 1500 | 1000 | mm | Profundidad |

---

## Codigos Normativos

### NTC-RCDF (Mexico)

| Parametro | Residencial | Comercial | Industrial |
|-----------|-------------|-----------|------------|
| Contrahuella max | 200 mm | 180 mm | 220 mm |
| Huella min (linea paso) | 200 mm | 250 mm | 180 mm |
| Ancho min | 900 mm | 1200 mm | 750 mm |
| Altura libre min | 2050 mm | 2100 mm | 2000 mm |
| Altura pasamanos | 900-1070 mm | 900-1100 mm | 850-1100 mm |
| Espaciamiento balaustres | 100 mm max | 100 mm max | 150 mm max |
| Descanso cada | 16 escalones | 12 escalones | 20 escalones |
| Diametro min | 1400 mm | 1600 mm | 1200 mm |

### IBC (International Building Code)

| Parametro | Residencial | Comercial |
|-----------|-------------|-----------|
| Contrahuella max | 197 mm (7.75") | 178 mm (7") |
| Contrahuella min | 102 mm (4") | 102 mm (4") |
| Huella min (walkline) | 280 mm (11") | 280 mm (11") |
| Walkline radius | 305 mm (12") | 305 mm (12") |
| Ancho min | 660 mm (26") | 914 mm (36") |
| Altura libre min | 2032 mm (80") | 2032 mm (80") |
| Altura pasamanos | 864-965 mm | 864-965 mm |
| Agarre pasamanos | 32-51 mm | 32-51 mm |
| Espaciamiento balaustres | 102 mm (4") | 102 mm (4") |

### OSHA (Industrial)

| Parametro | Valor |
|-----------|-------|
| Contrahuella max | 241 mm (9.5") |
| Contrahuella min | 152 mm (6") |
| Huella min | 229 mm (9") |
| Ancho min | 559 mm (22") |
| Altura libre min | 1981 mm (78") |
| Altura pasamanos | 762-965 mm |
| Angulo inclinacion | 30° - 50° |

---

## Parametros Calculados

| Parametro | Formula | Descripcion |
|-----------|---------|-------------|
| `tread_count` | floor_to_floor / riser_height | Numero de peldanos |
| `actual_riser` | floor_to_floor / tread_count | Contrahuella real |
| `rotation_per_tread` | rotation_angle / tread_count | Rotacion por peldano |
| `clear_width` | (outer_diameter - inner_diameter) / 2 | Ancho libre |
| `walkline_tread` | (inner_r + 300) × rotation_rad | Huella en linea de paso |
| `helix_length` | sqrt((2πr × rotations)² + height²) | Longitud de helice |
| `headroom` | Calculado segun superposicion | Altura libre |

---

## Parametros BIM

| Parametro | Tipo | Grupo | Descripcion |
|-----------|------|-------|-------------|
| `BIMAC_Stair_Type` | Text | Identity Data | Tipologia de escalera |
| `BIMAC_Stair_Diameter` | Length | Dimensions | Diametro exterior |
| `BIMAC_Stair_Height` | Length | Dimensions | Altura de piso a piso |
| `BIMAC_Stair_TreadCount` | Integer | Dimensions | Numero de peldanos |
| `BIMAC_Stair_Rotation` | Angle | Dimensions | Rotacion total |
| `BIMAC_Stair_Material` | Text | Materials | Material de peldanos |
| `BIMAC_Stair_Weight` | Number | Other | Peso total (kg) |
| `BIMAC_Stair_Cost` | Currency | Other | Costo estimado |
| `BIMAC_Stair_CodeCompliance` | YesNo | Other | Cumple normativa |

### Clasificacion

| Sistema | Codigo |
|---------|--------|
| Uniclass | Ss_25_30_85 (Stair systems) |
| OmniClass | 23-21 11 11 (Spiral Stairs) |
| IFC Class | IfcStair |
| IFC Type | SPIRAL_STAIR |

---

## Restricciones de Diseno

### Geometria

| Restriccion | Minimo | Maximo |
|-------------|--------|--------|
| Diametro exterior | 1400 mm | 4000 mm |
| Diametro interior | 100 mm | 500 mm |
| Rotacion total | 180° | 1080° (3 vueltas) |
| Altura de piso | 2400 mm | 6000 mm |

### Peldanos

| Restriccion | Minimo | Maximo |
|-------------|--------|--------|
| Contrahuella | 140 mm | 220 mm |
| Huella (interior) | 100 mm | - |
| Nariz | 0 mm | 50 mm |
| Espesor | 6 mm | 100 mm |

### Barandal

| Restriccion | Minimo | Maximo |
|-------------|--------|--------|
| Altura pasamanos | 850 mm | 1100 mm |
| Diametro pasamanos | 32 mm | 57 mm |
| Espaciamiento balaustres | - | 100 mm |

---

## Formulas de Calculo

### Numero de Peldanos

```
n = ceil(H / h_max)

Donde:
  H = altura piso a piso (mm)
  h_max = contrahuella maxima segun codigo (mm)
  n = numero de peldanos
```

### Huella en Linea de Paso

```
t = (r_i + d_walkline) × θ

Donde:
  r_i = radio interior (mm)
  d_walkline = distancia walkline desde interior (300mm NTC, 305mm IBC)
  θ = angulo por peldano (radianes)
  t = huella en linea de paso (mm)
```

### Altura Libre (Headroom)

```
Para rotacion > 360°:
  overlap_treads = (rotation - 360) / rotation_per_tread
  headroom = H - (overlap_treads × h_actual)

Para rotacion <= 360°:
  headroom = H
```

### Peso Estimado

```
W_total = W_peldanos + W_estructura + W_barandal

W_peldanos = Σ(A_peldano × e × ρ)
W_estructura = V_columna × ρ_acero
W_barandal = L_pasamanos × A_tubo × ρ + n_balaustres × W_balaustre
```

---

*Documentacion de parametros v1.0 - C01 Escalera Helicoidal Parametrica*
