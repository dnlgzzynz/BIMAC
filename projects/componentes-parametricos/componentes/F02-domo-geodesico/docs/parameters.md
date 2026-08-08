# Tabla de Parametros - F02 Domo Geodesico

Referencia completa de parametros para diseno de domos geodesicos.

---

## Parametros de Geometria Base

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `radius` | float | 3 - 50 | 10 | m | Radio del domo |
| `frequency` | int | 1 - 8 | 3 | - | Frecuencia de subdivision |
| `truncation` | float | 0.25 - 1.0 | 0.5 | - | Ratio de truncamiento |
| `base_type` | enum | icosahedron, octahedron, tetrahedron | icosahedron | - | Poliedro base |
| `center_x` | float | - | 0 | m | Coordenada X del centro |
| `center_y` | float | - | 0 | m | Coordenada Y del centro |
| `center_z` | float | - | 0 | m | Elevacion de la base |

---

## Frecuencias de Subdivision

### Icosaedro

| Frecuencia | Triangulos | Barras | Nodos | Tipos Unicos |
|------------|------------|--------|-------|--------------|
| 1V | 20 | 30 | 12 | 1 |
| 2V | 80 | 120 | 42 | 2 |
| 3V | 180 | 270 | 92 | 3 |
| 4V | 320 | 480 | 162 | 6 |
| 5V | 500 | 750 | 252 | 9 |
| 6V | 720 | 1080 | 362 | 9 |

*Valores para esfera completa

### Diagrama de Frecuencias

```
1V (Sin subdivision)      2V (Una subdivision)      3V (Dos subdivisiones)
      /\                      /\                          /\
     /  \                    /--\                        /--\
    /    \                  /\  /\                      /\  /\
   /______\                /__\/__\                    /__\/__\
                          /\  /\  /\                  /\/\  /\/\
                         /__\/__\/__\                /--\/--\/--\
                                                    /__\/__\/__\
```

---

## Tipos de Truncamiento

| Tipo | Ratio | Altura/Radio | Descripcion | Aplicacion |
|------|-------|--------------|-------------|------------|
| Full sphere | 1.00 | 2.00 | Esfera completa | Planetarios |
| 5/8 sphere | 0.625 | 1.25 | 5/8 de esfera | Observatorios |
| Hemisphere | 0.50 | 1.00 | Medio domo | Viviendas, eventos |
| 3/8 sphere | 0.375 | 0.75 | 3/8 de esfera | Cubiertas bajas |
| 1/4 sphere | 0.25 | 0.50 | Cuarto de esfera | Tragaluces |

### Diagrama de Truncamiento

```
        ___________
       /           \        Full sphere (1.0)
      /             \
     |               |
     |               |
     |      .        |
     |               |
     |               |
      \             /
       \___________/

        ___________
       /           \        5/8 sphere (0.625)
      /             \
     |               |
     |      .        |
     |               |
      \_____________/

        ___________
       /           \        Hemisphere (0.5)
      /      .      \
      \_____________/

           _____
          /     \           3/8 sphere (0.375)
         /   .   \
        /_________\
```

---

## Perfiles Estructurales

### Tubos Circulares (HSS Round)

| Perfil | OD (mm) | Espesor (mm) | Peso (kg/m) | Area (mm²) | I (mm⁴) | r (mm) |
|--------|---------|--------------|-------------|------------|---------|--------|
| D33x2 | 33.4 | 2.0 | 1.56 | 197 | 22,600 | 10.7 |
| D42x2.5 | 42.2 | 2.5 | 2.45 | 312 | 56,200 | 13.4 |
| D48x3 | 48.3 | 3.0 | 3.35 | 427 | 94,500 | 14.9 |
| D60x3 | 60.3 | 3.0 | 4.24 | 540 | 189,000 | 18.7 |
| D76x4 | 76.1 | 4.0 | 7.11 | 906 | 493,000 | 23.3 |
| D89x4 | 88.9 | 4.0 | 8.38 | 1,068 | 802,000 | 27.4 |
| D114x5 | 114.3 | 5.0 | 13.5 | 1,717 | 2,120,000 | 35.1 |
| D140x6 | 139.7 | 6.0 | 19.8 | 2,521 | 4,640,000 | 42.9 |
| D168x6 | 168.3 | 6.0 | 24.0 | 3,058 | 8,170,000 | 51.7 |

### Seleccion por Claro

| Claro (m) | Perfil Recomendado | Esbeltez Max |
|-----------|-------------------|--------------|
| < 1.0 | D33x2 | 93 |
| 1.0 - 1.5 | D42x2.5 | 112 |
| 1.5 - 2.0 | D48x3 | 134 |
| 2.0 - 3.0 | D60x3 | 160 |
| 3.0 - 4.0 | D76x4 | 172 |
| 4.0 - 5.0 | D89x4 | 183 |
| > 5.0 | D114x5+ | < 200 |

---

## Tipos de Nodo

### Nodo Esferico (Spherical Hub)

```
            ___
          /     \
    -----| o   o |-----
          \  o  /
           \___/
             |
```

| Parametro | Valor Tipico | Descripcion |
|-----------|--------------|-------------|
| Radio base | 50-100 mm | Radio del hub |
| Espesor pared | 8-12 mm | Espesor de acero |
| Conexiones | 5-12 | Numero de barras |
| Material | Acero fundido | A36 o superior |

### Nodo de Placas (Gusset Plate)

```
      /  \
     /    \
    /______\
    \      /
     \    /
      \  /
```

| Parametro | Valor Tipico | Descripcion |
|-----------|--------------|-------------|
| Espesor | 10-16 mm | Espesor de placa |
| Soldadura | Filete 6mm | Tipo de union |
| Conexiones | 5-8 | Numero de barras |

### Nodo Aplastado (Flattened End)

```
    ========O========
        |       |
        |       |
```

| Parametro | Valor Tipico | Descripcion |
|-----------|--------------|-------------|
| Ancho aplastado | 60 mm | Ancho del aplastado |
| Perno | M16 | Diametro del perno |
| Conexiones | 4-6 | Numero de barras |

---

## Materiales de Panel

### Vidrio

| Tipo | Espesor | Peso | U-Value | SHGC | Costo |
|------|---------|------|---------|------|-------|
| Simple templado | 8 mm | 20 kg/m² | 5.7 | 0.82 | $180/m² |
| Doble (DVH) | 24 mm | 35 kg/m² | 2.8 | 0.65 | $320/m² |
| Triple | 36 mm | 52 kg/m² | 1.8 | 0.50 | $480/m² |
| Low-E | 24 mm | 35 kg/m² | 1.6 | 0.35 | $420/m² |

### Policarbonato

| Tipo | Espesor | Peso | U-Value | Transmitancia | Costo |
|------|---------|------|---------|---------------|-------|
| Solido | 6 mm | 7.2 kg/m² | 4.8 | 0.88 | $65/m² |
| Multicelular 2 | 10 mm | 1.7 kg/m² | 3.1 | 0.82 | $45/m² |
| Multicelular 3 | 16 mm | 2.7 kg/m² | 2.3 | 0.78 | $85/m² |
| Multicelular 5 | 25 mm | 3.4 kg/m² | 1.8 | 0.65 | $120/m² |

### ETFE

| Configuracion | Espesor | Peso | U-Value | Transmitancia | Costo |
|---------------|---------|------|---------|---------------|-------|
| Simple capa | 0.25 mm | 0.4 kg/m² | 5.5 | 0.94 | $150/m² |
| Doble cojin | 0.2+0.2 mm | 0.8 kg/m² | 2.9 | 0.90 | $250/m² |
| Triple cojin | 3 capas | 1.2 kg/m² | 1.8 | 0.82 | $380/m² |

### Otros

| Material | Espesor | Peso | U-Value | Costo |
|----------|---------|------|---------|-------|
| Aluminio composite | 4 mm | 5.4 kg/m² | 6.0 | $95/m² |
| Acero galvanizado | 1.2 mm | 9.4 kg/m² | 6.5 | $65/m² |
| Panel sandwich | 50 mm | 12 kg/m² | 0.5 | $85/m² |

---

## Tipos de Panel

### Triangular

```
        /\
       /  \
      /    \
     /______\
```

| Caracteristica | Valor |
|----------------|-------|
| Lados | 3 |
| Ajuste a curvatura | Excelente |
| Desperdicio | Medio |
| Complejidad | Baja |

### Hexagonal (Fuller)

```
      ___
     /   \
    /     \
    \     /
     \___/
```

| Caracteristica | Valor |
|----------------|-------|
| Lados | 6 (+ 12 pentagonos) |
| Ajuste a curvatura | Bueno |
| Desperdicio | Bajo |
| Complejidad | Media |

---

## Cargas de Diseno

### Cargas Muertas

| Componente | Peso Tipico |
|------------|-------------|
| Estructura (barras + nodos) | 15-25 kg/m² |
| Paneles vidrio simple | 20 kg/m² |
| Paneles policarbonato | 3-5 kg/m² |
| Paneles ETFE | 0.5-1.5 kg/m² |

### Cargas Vivas

| Tipo | Carga |
|------|-------|
| Mantenimiento | 0.5 kN/m² |
| Limpieza | 1.0 kN/m² |

### Cargas de Viento (ASCE 7)

| Zona | Cp Externo | Cp Interno |
|------|------------|------------|
| Barlovento | +0.8 | ±0.18 |
| Sotavento | -0.5 | ±0.18 |
| Lateral | -0.7 | ±0.18 |
| Succion techo | -1.0 | ±0.18 |

Factor de forma para domos: 0.5 (reduccion por curvatura)

### Cargas de Nieve

| Parametro | Valor |
|-----------|-------|
| Factor de forma Cs | 0.7 |
| Factor termico Ct | 1.0 (calentado) |
| Factor de importancia Is | 1.0 |

---

## Formulas de Geometria

### Elementos por Frecuencia (Icosaedro)

```
Vertices:   V = 10 * n² + 2
Aristas:    E = 30 * n²
Caras:      F = 20 * n²

donde n = frecuencia
```

### Longitudes de Cuerda

Para frecuencia n, radio R:

| Frecuencia | Cuerdas Unicas | Longitud Tipica (R=1) |
|------------|----------------|----------------------|
| 2V | 2 | A: 0.5465, B: 0.6180 |
| 3V | 3 | A: 0.3486, B: 0.4035, C: 0.4124 |
| 4V | 6 | A-F: 0.2533 - 0.3128 |

### Area Superficial

```
Esfera completa:    A = 4 * pi * R²
Hemisferio:         A = 2 * pi * R²
Casquete altura h:  A = 2 * pi * R * h
```

### Volumen

```
Esfera completa:    V = (4/3) * pi * R³
Casquete altura h:  V = (pi * h² / 3) * (3R - h)
```

---

## Parametros BIM

| Parametro | Tipo | Grupo | Descripcion |
|-----------|------|-------|-------------|
| `BIMAC_Dome_Radius` | Length | Dimensions | Radio del domo |
| `BIMAC_Dome_Frequency` | Integer | Geometry | Frecuencia |
| `BIMAC_Dome_Truncation` | Number | Geometry | Truncamiento |
| `BIMAC_Dome_Height` | Length | Dimensions | Altura total |
| `BIMAC_Surface_Area` | Area | Quantities | Area superficial |
| `BIMAC_Floor_Area` | Area | Quantities | Area de piso |
| `BIMAC_Volume` | Volume | Quantities | Volumen interior |
| `BIMAC_Strut_Count` | Integer | Quantities | Numero de barras |
| `BIMAC_Node_Count` | Integer | Quantities | Numero de nodos |
| `BIMAC_Panel_Count` | Integer | Quantities | Numero de paneles |
| `BIMAC_Total_Weight` | Number | Structural | Peso total (kg) |

### Clasificacion

| Sistema | Codigo |
|---------|--------|
| Uniclass | Ss_25_10_30 (Dome structures) |
| OmniClass | 23-13 17 00 (Domes) |
| IFC Class | IfcRoof |
| IFC Type | DOME |

---

## Normativas Aplicables

| Codigo | Descripcion | Aplicacion |
|--------|-------------|------------|
| ASCE 7 | Minimum Design Loads | Cargas de viento/nieve |
| AISC 360 | Steel Construction | Diseno de estructura |
| AAMA TIR-A7 | Sloped Glazing | Vidrio inclinado |
| IGCC | Insulating Glass | Unidades de vidrio |
| EN 13830 | Curtain Walling | Fachadas |

---

## Restricciones de Diseno

### Geometria

| Restriccion | Limite |
|-------------|--------|
| Radio minimo | 3 m |
| Radio maximo | 50 m |
| Frecuencia minima | 1V |
| Frecuencia maxima | 8V |
| Altura minima | Radio * 0.4 |

### Estructura

| Restriccion | Limite |
|-------------|--------|
| Esbeltez de barras (KL/r) | < 200 |
| Deflexion | L/180 (viento) |
| Relacion D/C | < 1.0 |

### Fabricacion

| Restriccion | Valor |
|-------------|-------|
| Longitud maxima de barra | 12 m |
| Peso maximo de pieza | 500 kg |
| Tolerancia de longitud | ±2 mm |
| Tolerancia de angulo | ±0.5° |

---

*Documentacion de parametros v1.0 - F02 Domo Geodesico Parametrico*
