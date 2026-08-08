# Tabla de Parametros - E03 Conexion Viga-Columna

Referencia completa de parametros para conexiones estructurales de acero.

---

## Tipos de Conexion

| Tipo | Categoria | Precalificada | Momento | Cortante | Aplicacion |
|------|-----------|---------------|---------|----------|------------|
| `shear_tab` | Cortante | N/A | No | Si | Conexiones simples, vigas secundarias |
| `clip_angle` | Cortante | N/A | No | Si | Conexiones tradicionales, renovaciones |
| `end_plate` | Momento | No | Parcial | Si | Marcos rigidos no sismicos |
| `extended_end_plate` | Momento | AISC 358 | Total | Si | Marcos de momento, SMF/IMF |
| `directly_welded` | Momento | No | Total | Si | Conexiones especiales, vigas pesadas |
| `RBS` | Sismico | AISC 358 | Total | Si | SMF, alta ductilidad |
| `WUF-W` | Sismico | AISC 358 | Total | Si | SMF, alma soldada |
| `WUF-B` | Sismico | AISC 358 | Total | Si | IMF, alma atornillada |
| `BUEEP` | Sismico | AISC 358 | Total | Si | SMF, Extended end plate |
| `BFP` | Sismico | AISC 358 | Total | Si | OMF, Bolted flange plate |

---

## Diagramas de Conexion

### Shear Tab (Simple Shear Connection)

```
     Columna            Viga
    ┌────────┐        ┌─────────
    │        │        │
    │    ┌───┤O O O O─┤─────────
    │    │   │  Tab   │  Alma
    │    │   │        │
    │    └───┤O O O O─┤─────────
    │        │        │
    └────────┘        └─────────
         Soldadura    Tornillos
```

### Extended End Plate

```
      Columna         End Plate        Viga
    ┌─────────┐      ┌───────┐     ╔═════════╗
    │   O     │──────│   O   │     ║ Flange  ║
    │         │      │       │     ╠═════════╣
    │   O     │──────│   O   │     ║         ║
    │         │      │       │     ║   Web   ║
    │   O     │──────│   O   │     ║         ║
    │         │      │       │     ╠═════════╣
    │   O     │──────│   O   │     ║ Flange  ║
    └─────────┘      └───────┘     ╚═════════╝
      Tornillos      CJP Weld
```

### RBS (Reduced Beam Section)

```
    Columna      Zona Plastica       Viga
    ┌──────┐    ┌──────────────────────────────
    │      │    │    ╱────────╲    ╔═════════
    │      │═══════╱            ╲══║
    │      │    │                  ║   Alma
    │      │═══════╲            ╱══║
    │      │    │    ╲────────╱    ╚═════════
    └──────┘    └──────────────────────────────
                     Corte RBS
                  (Hueso de perro)
```

---

## Parametros Geometricos

### Perfiles de Viga

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `beam_profile` | str | ver tabla | W18x50 | Designacion AISC del perfil |
| `beam_material` | enum | A992, A572_Gr50, A36 | A992 | Material de la viga |

#### Perfiles W Disponibles

| Perfil | d (mm) | bf (mm) | tf (mm) | tw (mm) | k (mm) | Zx (mm³) |
|--------|--------|---------|---------|---------|--------|----------|
| W12x26 | 310 | 165 | 10 | 6 | 22 | 442,000 |
| W14x22 | 349 | 127 | 8 | 6 | 19 | 377,000 |
| W14x30 | 352 | 171 | 10 | 7 | 24 | 557,000 |
| W16x36 | 403 | 178 | 11 | 8 | 27 | 721,000 |
| W18x35 | 450 | 152 | 11 | 8 | 25 | 770,000 |
| W18x50 | 457 | 190 | 14 | 9 | 30 | 1,130,000 |
| W21x50 | 529 | 166 | 13 | 9 | 28 | 1,260,000 |
| W21x62 | 533 | 210 | 16 | 10 | 33 | 1,600,000 |
| W24x68 | 603 | 228 | 15 | 10 | 32 | 2,020,000 |
| W24x84 | 612 | 229 | 20 | 12 | 38 | 2,530,000 |
| W27x84 | 678 | 253 | 16 | 12 | 34 | 2,790,000 |
| W30x99 | 753 | 265 | 17 | 13 | 37 | 3,570,000 |
| W33x118 | 835 | 292 | 19 | 14 | 40 | 4,510,000 |
| W36x135 | 903 | 303 | 20 | 15 | 43 | 5,540,000 |

### Perfiles de Columna

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `column_profile` | str | ver tabla | W14x82 | Designacion AISC del perfil |
| `column_material` | enum | A992, A572_Gr50, A36 | A992 | Material de la columna |

#### Perfiles W para Columnas

| Perfil | d (mm) | bf (mm) | tf (mm) | tw (mm) | k (mm) |
|--------|--------|---------|---------|---------|--------|
| W10x49 | 254 | 254 | 14 | 9 | 28 |
| W10x68 | 260 | 256 | 19 | 12 | 35 |
| W12x65 | 308 | 305 | 15 | 10 | 29 |
| W12x87 | 318 | 308 | 20 | 13 | 36 |
| W12x106 | 327 | 311 | 25 | 15 | 41 |
| W14x61 | 353 | 254 | 16 | 10 | 30 |
| W14x82 | 363 | 257 | 22 | 13 | 37 |
| W14x109 | 371 | 371 | 22 | 13 | 40 |
| W14x132 | 373 | 374 | 26 | 16 | 47 |
| W14x176 | 386 | 381 | 33 | 21 | 56 |
| W14x211 | 399 | 401 | 40 | 26 | 64 |
| W14x257 | 416 | 406 | 48 | 31 | 74 |

---

## Parametros de Tornilleria

| Parametro | Tipo | Rango/Opciones | Default | Unidad | Descripcion |
|-----------|------|----------------|---------|--------|-------------|
| `bolt_diameter` | int | 16, 19, 22, 25, 28, 32 | 22 | mm | Diametro nominal |
| `bolt_grade` | enum | A325, A490 | A325 | - | Grado del tornillo |
| `bolt_type` | enum | N, X, SC | N | - | Tipo de conexion |
| `hole_type` | enum | standard, oversized, short_slot, long_slot | standard | - | Tipo de agujero |

### Capacidades de Tornillos (kN)

#### A325-N (Hilos incluidos en plano de corte)

| Diametro | Cortante Simple | Cortante Doble | Tension |
|----------|-----------------|----------------|---------|
| 16 mm | 37.4 | 74.8 | 57.4 |
| 19 mm | 53.4 | 106.8 | 80.1 |
| 22 mm | 72.5 | 145.0 | 108.1 |
| 25 mm | 93.4 | 186.8 | 140.1 |
| 28 mm | 118.0 | 236.0 | 175.7 |
| 32 mm | 154.0 | 308.0 | 229.5 |

#### A325-X (Hilos excluidos del plano de corte)

| Diametro | Cortante Simple | Cortante Doble | Tension |
|----------|-----------------|----------------|---------|
| 16 mm | 46.7 | 93.4 | 57.4 |
| 19 mm | 66.7 | 133.4 | 80.1 |
| 22 mm | 90.7 | 181.4 | 108.1 |
| 25 mm | 116.8 | 233.6 | 140.1 |
| 28 mm | 147.4 | 294.8 | 175.7 |
| 32 mm | 192.5 | 385.0 | 229.5 |

#### A490-N

| Diametro | Cortante Simple | Cortante Doble | Tension |
|----------|-----------------|----------------|---------|
| 16 mm | 46.8 | 93.6 | 72.1 |
| 19 mm | 66.8 | 133.6 | 100.5 |
| 22 mm | 90.8 | 181.6 | 135.7 |
| 25 mm | 116.9 | 233.8 | 175.8 |
| 28 mm | 147.6 | 295.2 | 220.5 |
| 32 mm | 192.8 | 385.6 | 288.0 |

### Distancias Minimas (mm)

| Diametro | Distancia al Borde | Espaciamiento Min | Espaciamiento Pref |
|----------|-------------------|-------------------|-------------------|
| 16 mm | 28 | 44 | 54 |
| 19 mm | 32 | 51 | 63 |
| 22 mm | 38 | 59 | 73 |
| 25 mm | 42 | 67 | 83 |
| 28 mm | 48 | 76 | 94 |
| 32 mm | 54 | 86 | 108 |

---

## Parametros de Soldadura

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `weld_electrode` | enum | E70, E80 | E70 | Electrodo (FEXX en ksi) |
| `weld_type` | enum | fillet, CJP, PJP | fillet | Tipo de soldadura |
| `weld_position` | enum | flat, horizontal, vertical, overhead | flat | Posicion |
| `backing_bar` | bool | true/false | true | Usar backing bar (CJP) |

### Tamanos de Soldadura de Filete

| Espesor Material (mm) | Tamano Minimo (mm) | Tamano Maximo (mm) |
|-----------------------|--------------------|-------------------|
| hasta 6 | 3 | 5 |
| 6 - 13 | 5 | 10 |
| 13 - 19 | 6 | 16 |
| mayor a 19 | 8 | 19 |

### Capacidad de Soldadura de Filete (kN/mm)

| Electrodo | 5 mm | 6 mm | 8 mm | 10 mm | 12 mm |
|-----------|------|------|------|-------|-------|
| E70 | 0.464 | 0.557 | 0.743 | 0.928 | 1.114 |
| E80 | 0.530 | 0.636 | 0.849 | 1.061 | 1.273 |

### Soldadura CJP

| Parametro | Valor |
|-----------|-------|
| Resistencia | Igual al metal base |
| Factor phi (tension) | 0.90 |
| Factor phi (cortante) | 0.80 |
| Precalentamiento | Segun AWS D1.1 |
| NDT requerido | 100% para SMF |

---

## Parametros de Placas

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `plate_thickness` | float | 6 - 50 | 12 | mm | Espesor de placa |
| `plate_material` | enum | A36, A572_Gr50 | A36 | - | Material |
| `plate_edge_distance` | float | 25 - 75 | 38 | mm | Distancia al borde |
| `plate_gage` | float | 50 - 150 | 76 | mm | Separacion de lineas |

### Placas por Tipo de Conexion

| Tipo Conexion | Placas Requeridas | Espesor Tipico | Material |
|---------------|-------------------|----------------|----------|
| Shear tab | 1 | 10 mm | A36 |
| Clip angle | 2 | 10 mm | A36 |
| End plate | 1 | 16-25 mm | A572 Gr50 |
| Extended end plate | 1 | 20-32 mm | A572 Gr50 |

---

## Parametros RBS (Reduced Beam Section)

| Parametro | Tipo | Formula/Rango | Unidad | Descripcion |
|-----------|------|---------------|--------|-------------|
| `rbs_a` | float | 0.50bf - 0.75bf | mm | Distancia desde cara columna |
| `rbs_b` | float | 0.65d - 0.85d | mm | Longitud del corte |
| `rbs_c` | float | 0.10bf - 0.25bf | mm | Profundidad del corte |
| `rbs_radius` | float | calculado | mm | Radio del arco |

### Formulas AISC 358

```
a = (0.5 a 0.75) * bf
b = (0.65 a 0.85) * d
c = 0.25 * bf  (maximo)

Donde:
  bf = ancho del patin de viga
  d = peralte de viga

Radio del corte:
  R = (4c² + b²) / (8c)

Reduccion de momento plastico:
  Zrbs = Zx - 2*c*tf*(d - tf)
```

### Limites de Precalificacion RBS

| Parametro | Limite |
|-----------|--------|
| Peralte viga | hasta W36 |
| Peso viga | hasta 135 lb/ft |
| Claro libre / peralte | mayor o igual a 7 |
| Espesor patin viga | hasta 44 mm |
| bf/2tf (viga) | segun AISC 341 |

---

## Parametros de Rigidizadores

### Placas de Continuidad

| Parametro | Tipo | Formula/Valor | Descripcion |
|-----------|------|---------------|-------------|
| `continuity_required` | bool | Verificar AISC J10 | Si se requieren |
| `continuity_thickness` | float | mayor o igual tf_viga | Espesor |
| `continuity_width` | float | (bf_col - tw_col)/2 - clip | Ancho |
| `continuity_weld` | str | CJP a patines, fillet a alma | Soldaduras |

### Criterios de Necesidad (AISC J10)

```
Placas de continuidad requeridas si:

1. Flexion local del patin de columna:
   tf_col < 0.4 * sqrt(1.8 * bf_viga * tf_viga * Fyb/Fyc)

2. Fluencia local del alma de columna:
   Resistencia < Pu (fuerza del patin)

3. Pandeo local del alma de columna:
   Resistencia < Pu (compresion del patin)
```

### Placa Doble (Doubler Plate)

| Parametro | Tipo | Formula/Valor | Descripcion |
|-----------|------|---------------|-------------|
| `doubler_required` | bool | Verificar panel zone | Si se requiere |
| `doubler_thickness` | float | calculado | Espesor adicional |
| `doubler_weld` | str | Fillet o PJP perimetral | Tipo de soldadura |

---

## Categorias Sismicas

| Sistema | Descripcion | R | Cd | Omega_0 | Conexiones |
|---------|-------------|---|----|---------|-----------:|
| OMF | Ordinary Moment Frame | 3.5 | 3.0 | 3.0 | BFP, WUF-B |
| IMF | Intermediate Moment Frame | 4.5 | 4.0 | 3.0 | WUF-B, End plate |
| SMF | Special Moment Frame | 8.0 | 5.5 | 3.0 | RBS, WUF-W, BUEEP |

### Requisitos por Categoria

| Requisito | OMF | IMF | SMF |
|-----------|-----|-----|-----|
| Rotacion plastica | 0.01 rad | 0.02 rad | 0.04 rad |
| Ductilidad | Baja | Media | Alta |
| Zona protegida | No | Parcial | Si |
| NDT soldaduras | Visual | 25% UT | 100% UT |
| Precalificacion | Opcional | Recomendada | Requerida |
| Panel zone | Verificar | Verificar | Detallado |

---

## Verificaciones AISC

### Tornillos (AISC J3)

| Verificacion | Formula | Factor phi |
|--------------|---------|------------|
| Cortante | phi*Rn = phi*Fnv*Ab | 0.75 |
| Tension | phi*Rn = phi*Fnt*Ab | 0.75 |
| Combinado | Fnt' = 1.3Fnt - (Fnt/phi*Fnv)*frv | - |
| Aplastamiento | phi*Rn = phi*1.2*Lc*t*Fu | 0.75 |
| Desgarramiento | phi*Rn = phi*2.4*d*t*Fu | 0.75 |

### Soldaduras (AISC J2)

| Verificacion | Formula | Factor phi |
|--------------|---------|------------|
| Filete - cortante | phi*Rn = phi*0.6*FEXX*Aw | 0.75 |
| CJP - tension | phi*Rn = phi*Fy*Ag | 0.90 |
| CJP - cortante | phi*Rn = phi*0.6*Fy*Aw | 0.80 |

### Placas (AISC J4)

| Verificacion | Formula | Factor phi |
|--------------|---------|------------|
| Fluencia bruta | phi*Rn = phi*Fy*Ag | 0.90 |
| Ruptura neta | phi*Rn = phi*Fu*An*U | 0.75 |
| Block shear | phi*Rn = phi*(0.6Fu*Anv + Ubs*Fu*Ant) | 0.75 |

### Columna (AISC J10)

| Verificacion | Formula | Factor phi |
|--------------|---------|------------|
| Flexion patin | phi*Rn = phi*6.25*tf²*Fyf | 0.90 |
| Fluencia alma | phi*Rn = phi*(5k+N)*Fyw*tw | 1.00 |
| Pandeo alma | phi*Rn = formula AISC J10.5 | 0.90 |
| Panel zone | phi*Rv = phi*0.6*Fy*dc*tw | 0.90 |

---

## Parametros BIM

| Parametro | Tipo | Grupo | Descripcion |
|-----------|------|-------|-------------|
| `BIMAC_Connection_Type` | Text | Identity | Tipo de conexion |
| `BIMAC_Connection_Category` | Text | Identity | Shear/Moment/Seismic |
| `BIMAC_Beam_Profile` | Text | Structural | Perfil de viga |
| `BIMAC_Column_Profile` | Text | Structural | Perfil de columna |
| `BIMAC_Bolt_Count` | Integer | Connections | Numero de tornillos |
| `BIMAC_Bolt_Grade` | Text | Connections | Grado de tornillos |
| `BIMAC_Weld_Type` | Text | Connections | Tipo de soldadura |
| `BIMAC_Seismic_Category` | Text | Structural | OMF/IMF/SMF |
| `BIMAC_Prequalified` | YesNo | Structural | Precalificada AISC 358 |
| `BIMAC_Connection_Weight` | Number | Quantities | Peso total (kg) |
| `BIMAC_Connection_Cost` | Currency | Costs | Costo estimado |

### Clasificacion

| Sistema | Codigo |
|---------|--------|
| Uniclass | Pr_70_60_72 (Connection assemblies) |
| OmniClass | 23-17 11 00 (Structural Steel Connections) |
| IFC Class | IfcMechanicalFastener / IfcFastener |
| IFC Type | BOLT_ASSEMBLY / WELD |

---

## Normativas Aplicables

| Codigo | Descripcion | Aplicacion |
|--------|-------------|------------|
| AISC 360 | Specification for Structural Steel Buildings | Diseno general |
| AISC 341 | Seismic Provisions for Structural Steel Buildings | Requisitos sismicos |
| AISC 358 | Prequalified Connections for SMF and IMF | Conexiones precalificadas |
| AWS D1.1 | Structural Welding Code - Steel | Soldadura |
| RCSC | Specification for Structural Joints | Tornillos alta resistencia |
| ASTM A325 | High-Strength Bolts, Type 1 | Tornillos |
| ASTM A490 | High-Strength Bolts, Alloy Steel | Tornillos alta resistencia |
| ASTM A992 | Structural Steel Shapes | Perfiles W |

---

## Restricciones de Diseno

### Geometricas

| Restriccion | Valor |
|-------------|-------|
| Distancia minima al borde | 1.25 * diametro agujero |
| Espaciamiento minimo | 2.67 * diametro nominal |
| Espaciamiento maximo | min(24t, 305mm) |
| Longitud minima soldadura | 4 * tamano filete |

### Resistencia

| Restriccion | Valor |
|-------------|-------|
| Relacion demanda/capacidad | menor a 1.0 |
| Sobrerresistencia tornillos | 20% sobre soldadura |
| Panel zone | Verificar para SMF |
| Zona protegida | Sin perforaciones ni soldaduras |

### Fabricacion

| Restriccion | Valor |
|-------------|-------|
| Tolerancia de agujeros | +2mm para estandar |
| Gap de raiz CJP | 0-3mm |
| Angulo de bisel | 45-60 grados |
| Backing bar | Remover en SMF inferior |

---

*Documentacion de parametros v1.0 - E03 Conexion Viga-Columna Parametrica*
