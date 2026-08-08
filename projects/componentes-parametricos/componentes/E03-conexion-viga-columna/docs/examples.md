# Ejemplos de Configuracion - E03 Conexion Viga-Columna

Ejemplos de configuraciones tipicas para diferentes aplicaciones.

---

## Ejemplo 1: Shear Tab - Viga Secundaria

Conexion simple de cortante para viga secundaria a viga principal.

### Aplicacion
- Edificio de oficinas
- Viga secundaria W12x26 a viga principal W21x50
- Carga de servicio: 45 kN
- No sismico

### Configuracion

```yaml
connection_type: shear_tab

beam:
  profile: W12x26
  material: A992
  depth: 310
  flange_width: 165

support:
  type: beam
  profile: W21x50

plate:
  thickness: 10
  width: 100
  length: 230
  material: A36
  edge_distance: 38
  gage: 76

bolts:
  count: 3
  diameter: 22
  grade: A325
  type: N
  rows: 3
  columns: 1
  spacing: 76

welds:
  type: fillet
  size: 8
  electrode: E70
  both_sides: true

seismic:
  category: none
```

### Verificaciones

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Bolt shear | 45 kN | 217 kN | 0.21 |
| Bolt bearing (beam) | 45 kN | 318 kN | 0.14 |
| Plate gross shear | 45 kN | 267 kN | 0.17 |
| Plate net shear | 45 kN | 198 kN | 0.23 |
| Weld shear | 45 kN | 171 kN | 0.26 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $35.50 |
| Mano de obra | $82.00 |
| Total por conexion | $145.00 |

---

## Ejemplo 2: Extended End Plate - Marco Rigido

Conexion de momento para marco de nave industrial.

### Aplicacion
- Nave industrial
- Claro 20m, altura 8m
- Viga W21x62 a columna W14x82
- Momento ultimo: 450 kN-m
- Zona sismica baja (OMF)

### Configuracion

```yaml
connection_type: extended_end_plate

beam:
  profile: W21x62
  material: A992
  depth: 533
  flange_width: 210
  flange_thickness: 16
  web_thickness: 10

column:
  profile: W14x82
  material: A992
  depth: 363
  flange_width: 257
  flange_thickness: 22
  web_thickness: 13

plate:
  thickness: 25
  width: 254
  length: 635
  material: A572_Gr50
  edge_distance: 50
  gage: 127
  extension_above: 75
  extension_below: 75

bolts:
  count: 8
  diameter: 25
  grade: A490
  type: SC
  rows: 4
  columns: 2
  spacing_vertical: 127
  spacing_horizontal: 127

welds:
  flange_type: CJP
  flange_electrode: E70
  web_type: fillet
  web_size: 8
  backing_bar: true

stiffeners:
  continuity_plates: true
  continuity_thickness: 16
  doubler_plate: false

seismic:
  category: OMF
  prequalified: false
```

### Verificaciones

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Bolt tension | 225 kN | 351 kN | 0.64 |
| End plate yielding | 450 kN-m | 612 kN-m | 0.74 |
| End plate rupture | 450 kN-m | 558 kN-m | 0.81 |
| CJP weld (flange) | 843 kN | 1,134 kN | 0.74 |
| Column flange bending | 843 kN | 1,050 kN | 0.80 |
| Column web yielding | 843 kN | 985 kN | 0.86 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $285.00 |
| Mano de obra | $420.00 |
| Total por conexion | $875.00 |

---

## Ejemplo 3: RBS - Marco Especial SMF

Conexion sismica de alta ductilidad para edificio en zona de alto riesgo.

### Aplicacion
- Edificio de 12 niveles
- Zona sismica alta (SMF)
- Viga W24x84 a columna W14x176
- Momento probable: 1,200 kN-m
- Rotacion inelastica: 0.04 rad

### Configuracion

```yaml
connection_type: RBS

beam:
  profile: W24x84
  material: A992
  depth: 612
  flange_width: 229
  flange_thickness: 20
  web_thickness: 12
  Zx: 2530000  # mm³
  Ry: 1.1

column:
  profile: W14x176
  material: A992
  depth: 386
  flange_width: 381
  flange_thickness: 33
  web_thickness: 21
  strong_axis: true

rbs:
  a: 137  # 0.6 * bf
  b: 490  # 0.8 * d
  c: 46   # 0.2 * bf
  radius: 669
  Zrbs: 2150000  # mm³ reducido

plate:
  type: extended_end_plate
  thickness: 32
  width: 280
  length: 762
  material: A572_Gr50
  extension_above: 100
  extension_below: 100

bolts:
  count: 8
  diameter: 28
  grade: A490
  type: SC
  pretension: full

welds:
  flange_type: CJP
  flange_electrode: E70
  demand_critical: true
  web_type: CJP
  backing_bar_top: true
  backing_bar_bottom: removed
  weld_tabs: removed
  run_off_tabs: ground_smooth

stiffeners:
  continuity_plates:
    required: true
    thickness: 25
    material: A572_Gr50
    weld: CJP
  doubler_plate:
    required: true
    thickness: 12
    material: A572_Gr50
    plug_welded: true

access_holes:
  type: modified_AISC
  reinforced: true

seismic:
  category: SMF
  prequalified: true
  reference: AISC_358
  plastic_rotation: 0.04
  protected_zone: true
```

### Verificaciones RBS

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Plastic moment at RBS | 1,200 kN-m | 1,505 kN-m | 0.80 |
| Column-beam moment ratio | - | 1.25 | OK |
| Panel zone shear | 2,460 kN | 3,120 kN | 0.79 |
| Continuity plate | Required | Provided | OK |
| Doubler plate | Required | Provided | OK |
| Lateral bracing | Required | Provided | OK |

### Dimensiones RBS Calculadas

```
         ┌──── a = 137 mm ────┐
         │                    │
    ═════╪════════════════════╪═══════════════════
    ║    │    ╱──────────╲    │    ║
    ║    │   ╱            ╲   │    ║  c = 46 mm
    ║    │  ╱    RBS Cut   ╲  │    ║  (cada lado)
    ║    │ ╱                ╲ │    ║
    ║    │╱                  ╲│    ║
    ╠════╪════════════════════╪════╣
    ║                              ║
    ║         b = 490 mm           ║
    ║                              ║
    ╠════╪════════════════════╪════╣
    ║    │╲                  ╱│    ║
    ║    │ ╲                ╱ │    ║
    ║    │  ╲              ╱  │    ║
    ║    │   ╲            ╱   │    ║
    ║    │    ╲──────────╱    │    ║
    ═════╪════════════════════╪═══════════════════
         │                    │
         └──── a = 137 mm ────┘

    Radio del corte: R = 669 mm
    Reduccion de seccion: 40% del patin
```

### Inspeccion Requerida

| Elemento | Metodo | Frecuencia |
|----------|--------|------------|
| CJP welds flanges | UT | 100% |
| CJP weld web | UT | 100% |
| Continuity plates | MT | 100% |
| RBS cuts | VT + MT | 100% |
| Bolt pretension | Turn-of-nut | 100% |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $680.00 |
| Fabricacion | $850.00 |
| Inspeccion NDT | $320.00 |
| Total por conexion | $2,350.00 |

---

## Ejemplo 4: WUF-W - Marco Intermedio IMF

Conexion soldada para marco de momento intermedio.

### Aplicacion
- Edificio de 6 niveles
- Zona sismica moderada (IMF)
- Viga W18x50 a columna W14x109
- Momento ultimo: 380 kN-m

### Configuracion

```yaml
connection_type: WUF-W

beam:
  profile: W18x50
  material: A992
  depth: 457
  flange_width: 190
  flange_thickness: 14
  web_thickness: 9

column:
  profile: W14x109
  material: A992
  depth: 371
  flange_width: 371
  flange_thickness: 22
  web_thickness: 13

welds:
  flange:
    type: CJP
    electrode: E70
    backing_bar: true
    remove_backing: false
  web:
    type: CJP
    electrode: E70
  access_holes:
    type: standard_AISC
    dimensions: per_AISC_J1.6

shear_tab:
  thickness: 10
  width: 100
  length: 305
  bolts: 4
  bolt_diameter: 22
  bolt_grade: A325
  weld_to_column: fillet
  weld_size: 8

stiffeners:
  continuity_plates:
    required: true
    thickness: 14
    full_depth: true

seismic:
  category: IMF
  prequalified: true
  plastic_rotation: 0.02
```

### Verificaciones

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Beam flange force | 695 kN | 921 kN | 0.75 |
| CJP weld capacity | 695 kN | 921 kN | 0.75 |
| Web CJP weld | 127 kN | 185 kN | 0.69 |
| Column flange bending | OK | - | - |
| Panel zone | 1,520 kN | 1,890 kN | 0.80 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $320.00 |
| Mano de obra | $580.00 |
| Inspeccion | $150.00 |
| Total por conexion | $1,320.00 |

---

## Ejemplo 5: Clip Angle - Rehabilitacion

Conexion de cortante para proyecto de rehabilitacion.

### Aplicacion
- Edificio historico, renovacion
- Viga existente W10x22 a columna W12x65
- Carga de servicio: 35 kN
- Acceso limitado para soldadura

### Configuracion

```yaml
connection_type: clip_angle

beam:
  profile: W10x22
  material: A36
  depth: 254
  flange_width: 146
  web_thickness: 6

column:
  profile: W12x65
  material: A36
  flange_thickness: 15

angles:
  profile: L4x4x1/2
  length: 178
  material: A36
  quantity: 2
  orientation: outstanding_legs_vertical

bolts:
  beam_leg:
    count: 2
    diameter: 19
    grade: A325
    type: N
    rows: 2
  column_leg:
    count: 2
    diameter: 19
    grade: A325
    type: N
    rows: 2

installation:
  method: bolted_only
  field_welding: none
  shop_welding: none

notes:
  - Conexion completamente atornillada
  - No requiere soldadura en campo
  - Adecuada para rehabilitacion
```

### Verificaciones

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Bolt shear (beam leg) | 17.5 kN | 53.4 kN | 0.33 |
| Bolt shear (column leg) | 17.5 kN | 53.4 kN | 0.33 |
| Angle gross shear | 35 kN | 156 kN | 0.22 |
| Angle net shear | 35 kN | 108 kN | 0.32 |
| Block shear | 35 kN | 89 kN | 0.39 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $48.00 |
| Mano de obra | $95.00 |
| Total por conexion | $180.00 |

---

## Ejemplo 6: BFP - Marco Ordinario OMF

Conexion de placa atornillada a patin para sistema OMF.

### Aplicacion
- Bodega industrial
- Zona sismica baja
- Viga W16x36 a columna W10x68
- Marco de baja ductilidad

### Configuracion

```yaml
connection_type: BFP

beam:
  profile: W16x36
  material: A992
  depth: 403
  flange_width: 178
  flange_thickness: 11
  web_thickness: 8

column:
  profile: W10x68
  material: A992
  flange_thickness: 19

flange_plates:
  top:
    width: 178
    length: 380
    thickness: 16
    material: A572_Gr50
  bottom:
    width: 178
    length: 380
    thickness: 16
    material: A572_Gr50

bolts:
  flange_plates:
    count_per_plate: 6
    diameter: 22
    grade: A325
    type: SC
    rows: 2
    columns: 3

welds:
  plate_to_column:
    type: fillet
    size: 12
    electrode: E70

shear_tab:
  thickness: 10
  bolts: 3
  diameter: 19

seismic:
  category: OMF
  prequalified: true
  reference: AISC_358
```

### Verificaciones

| Check | Demanda | Capacidad | Ratio |
|-------|---------|-----------|-------|
| Bolt shear (plate) | 92 kN | 145 kN | 0.63 |
| Plate gross tension | 460 kN | 638 kN | 0.72 |
| Plate net tension | 460 kN | 512 kN | 0.90 |
| Fillet weld to column | 460 kN | 573 kN | 0.80 |
| Beam flange net | 460 kN | 521 kN | 0.88 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Materiales | $195.00 |
| Mano de obra | $310.00 |
| Total por conexion | $635.00 |

---

## Resumen Comparativo

| Ejemplo | Tipo | Momento | Costo | Aplicacion |
|---------|------|---------|-------|------------|
| 1 | Shear tab | No | $145 | Vigas secundarias |
| 2 | Extended EP | Si | $875 | Naves industriales |
| 3 | RBS | Si (SMF) | $2,350 | Edificios altos sismicos |
| 4 | WUF-W | Si (IMF) | $1,320 | Edificios medianos |
| 5 | Clip angle | No | $180 | Rehabilitacion |
| 6 | BFP | Si (OMF) | $635 | Bodegas |

---

*Documentacion de ejemplos v1.0 - E03 Conexion Viga-Columna Parametrica*
