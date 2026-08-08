# Tabla de Parametros - E02 Cercha Parametrica

Referencia completa de parametros para diseno de cerchas.

---

## Parametros de Geometria

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `span` | float | 3000 - 100000 | 12000 | mm | Luz libre de la cercha |
| `height` | float | auto | span/8 | mm | Altura en el centro |
| `slope` | float | 0 - 45 | 15 | grados | Pendiente de cuerda superior |
| `bay_count` | int | 4 - 30 | 8 | - | Numero de modulos |
| `overhang` | float | 0 - 3000 | 0 | mm | Volado en extremos |
| `base_curve` | Curve | - | null | - | Curva base opcional |

### Tipologias Disponibles

| Tipo | Categoria | Rango de Luz | Ratio H/L | Descripcion |
|------|-----------|--------------|-----------|-------------|
| `fink` | triangular | 6-15m | 0.20 | Diagonales en W |
| `howe` | triangular | 8-25m | 0.15 | Verticales compresion |
| `pratt` | triangular | 8-30m | 0.12 | Diagonales al centro |
| `warren` | triangular | 10-50m | 0.10 | Solo diagonales |
| `warren_vertical` | triangular | 10-50m | 0.10 | Warren + montantes |
| `scissors` | triangular | 8-18m | 0.25 | Cuerdas cruzadas |
| `fan` | triangular | 6-15m | 0.18 | Radial desde apoyos |
| `parallel_pratt` | paralela | 15-60m | 0.08 | Cuerdas paralelas |
| `parallel_warren` | paralela | 20-80m | 0.07 | Warren paralela |
| `vierendeel` | paralela | 8-25m | 0.10 | Sin diagonales |
| `bowstring` | curva | 20-80m | 0.12 | Cuerda sup. curva |
| `crescent` | curva | 15-50m | 0.15 | Ambas cuerdas curvas |
| `lenticular` | curva | 30-100m | 0.08 | Forma de lente |

---

## Parametros de Perfiles

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `top_chord` | str | ver tabla | HSS_150x150x6 | Perfil cuerda superior |
| `bottom_chord` | str | ver tabla | HSS_150x150x6 | Perfil cuerda inferior |
| `web_diagonal` | str | ver tabla | HSS_100x100x4 | Perfil de diagonales |
| `web_vertical` | str | ver tabla | HSS_75x75x3 | Perfil de montantes |
| `material` | enum | A36, A500_Gr_B, A500_Gr_C, A572_Gr50 | A500_Gr_B | Material de acero |

### Perfiles HSS Disponibles

| Perfil | Dimensiones (mm) | Area (cm2) | I (cm4) | Peso (kg/m) |
|--------|------------------|------------|---------|-------------|
| HSS_50x50x3 | 50x50x3 | 5.41 | 14.8 | 4.25 |
| HSS_75x75x3 | 75x75x3 | 8.41 | 53.2 | 6.60 |
| HSS_75x75x4 | 75x75x4 | 10.9 | 66.5 | 8.56 |
| HSS_100x100x4 | 100x100x4 | 14.4 | 166 | 11.3 |
| HSS_100x100x6 | 100x100x6 | 20.9 | 228 | 16.4 |
| HSS_125x125x5 | 125x125x5 | 22.6 | 396 | 17.7 |
| HSS_125x125x6 | 125x125x6 | 26.6 | 457 | 20.9 |
| HSS_150x150x5 | 150x150x5 | 27.6 | 698 | 21.7 |
| HSS_150x150x6 | 150x150x6 | 32.9 | 833 | 25.8 |
| HSS_150x150x8 | 150x150x8 | 42.9 | 1050 | 33.7 |
| HSS_200x200x8 | 200x200x8 | 58.1 | 2560 | 45.6 |
| HSS_200x200x10 | 200x200x10 | 71.4 | 3050 | 56.1 |
| HSS_250x250x10 | 250x250x10 | 90.9 | 6180 | 71.4 |

### Materiales de Acero

| Material | Fy (MPa) | Fu (MPa) | E (MPa) | Uso Tipico |
|----------|----------|----------|---------|------------|
| A36 | 250 | 400 | 200,000 | Placas, perfiles laminados |
| A500 Gr. B | 290 | 400 | 200,000 | HSS, tubos |
| A500 Gr. C | 317 | 427 | 200,000 | HSS alta resistencia |
| A572 Gr. 50 | 345 | 450 | 200,000 | Perfiles laminados |

---

## Parametros de Conexiones

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `connection_type` | enum | welded, bolted, pinned | welded | Tipo de conexion |
| `gusset_plate` | bool | true/false | true | Usar placas de nodo |
| `gusset_thickness` | float | 6 - 25 | 12 | mm | Espesor de placa |
| `gusset_material` | str | A36 | A36 | Material de placas |
| `weld_size` | float | 3 - 16 | 6 | mm | Tamano de filete |
| `bolt_diameter` | int | 16, 20, 22, 24 | 20 | mm | Diametro de tornillos |
| `bolt_grade` | enum | A325, A490 | A325 | Grado de tornillos |

### Tamano Minimo de Soldadura (AWS D1.1)

| Espesor Material (mm) | Tamano Min. Filete (mm) |
|-----------------------|-------------------------|
| < 6 | 3 |
| 6 - 13 | 5 |
| 13 - 19 | 6 |
| > 19 | 8 |

### Distancias para Tornillos

| Parametro | Formula | Ejemplo M20 |
|-----------|---------|-------------|
| Distancia al borde | 1.5 x diametro | 30 mm |
| Espaciamiento min. | 3 x diametro | 60 mm |
| Espaciamiento max. | 24 x espesor | variable |

---

## Parametros de Apoyos

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `left_support` | enum | pinned, fixed, roller | pinned | Apoyo izquierdo |
| `right_support` | enum | pinned, fixed, roller | roller | Apoyo derecho |

### Tipos de Apoyo

| Tipo | Rx | Ry | Mz | Simbolo |
|------|----|----|----|---------|
| **pinned** | Si | Si | No | △ |
| **roller** | No | Si | No | ○ |
| **fixed** | Si | Si | Si | ▢ |

---

## Parametros de Cargas

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `dead_load` | float | 0.1 - 5.0 | 0.5 | kN/m | Carga muerta |
| `live_load` | float | 0.0 - 5.0 | 1.0 | kN/m | Carga viva |
| `snow_load` | float | 0.0 - 3.0 | 0.0 | kN/m | Carga de nieve |
| `wind_load` | float | 0.0 - 2.0 | 0.0 | kN/m | Carga de viento |

### Combinaciones de Carga (LRFD)

| Combinacion | Formula |
|-------------|---------|
| 1 | 1.4D |
| 2 | 1.2D + 1.6L |
| 3 | 1.2D + 1.6L + 0.5S |
| 4 | 1.2D + 1.0W + 1.0L |
| 5 | 0.9D + 1.0W |

---

## Parametros de Acabado

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `finishing` | enum | primer, paint, galvanize | paint | Tipo de acabado |
| `sandblast_grade` | enum | SA2, SA2.5, SA3 | SA2.5 | Preparacion superficie |
| `primer_type` | enum | alkyd, epoxy, zinc_rich | alkyd | Tipo de primario |
| `paint_type` | enum | alkyd, polyurethane, epoxy | alkyd | Tipo de pintura |

---

## Parametros BIM

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `BIMAC_Truss_Type` | Text | Tipologia de cercha |
| `BIMAC_Truss_Span` | Length | Luz de la cercha |
| `BIMAC_Truss_Height` | Length | Altura de la cercha |
| `BIMAC_Truss_Weight` | Number | Peso total (kg) |
| `BIMAC_Member_Force` | Number | Fuerza axial (kN) |
| `BIMAC_Member_Utilization` | Number | Utilizacion (0-1) |
| `BIMAC_Member_Profile` | Text | Perfil del miembro |

---

## Restricciones de Diseno

### Esbeltez Maxima (L/r)

| Tipo de Miembro | Limite |
|-----------------|--------|
| Cuerdas en compresion | 200 |
| Alma en compresion | 300 |
| Miembros en tension | 300 |

### Angulos de Diagonales

| Parametro | Rango Optimo | Limite |
|-----------|--------------|--------|
| Angulo diagonal | 40° - 50° | 30° - 60° |

### Deflexion

| Tipo de Carga | Limite |
|---------------|--------|
| Carga viva | L/360 |
| Carga total | L/240 |
| Voladizo | L/180 |

---

## Formulas de Diseno

### Capacidad a Compresion (AISC E3)

```
Para Lc/r <= 4.71√(E/Fy):
  Fcr = [0.658^(Fy/Fe)] × Fy

Para Lc/r > 4.71√(E/Fy):
  Fcr = 0.877 × Fe

Donde:
  Fe = π²E / (Lc/r)²
  Pn = Fcr × Ag
  φPn = 0.90 × Pn
```

### Capacidad a Tension (AISC D2)

```
Fluencia en seccion bruta:
  Pn = Fy × Ag
  φPn = 0.90 × Pn

Ruptura en seccion neta:
  Pn = Fu × Ae
  φPn = 0.75 × Pn
```

### Capacidad de Soldadura (AWS D1.1)

```
Filete:
  Rn = 0.60 × Fexx × (0.707 × w) × L
  φRn = 0.75 × Rn

Donde:
  Fexx = resistencia del electrodo (MPa)
  w = tamano del filete (mm)
  L = longitud de soldadura (mm)
```

---

## Validaciones Automaticas

| Verificacion | Criterio | Limite |
|--------------|----------|--------|
| Esbeltez cuerdas | Lc/r | < 200 |
| Esbeltez alma | Lc/r | < 300 |
| Utilizacion | φPn/Pu | < 1.0 |
| Deflexion | δ | < L/240 |
| Angulo diagonal | θ | 30° - 60° |
| Ratio H/L | h/L | 0.05 - 0.25 |

---

*Documentacion de parametros v1.0 - E02 Cercha Parametrica*
