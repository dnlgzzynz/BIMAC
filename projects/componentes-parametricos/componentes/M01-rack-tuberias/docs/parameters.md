# Tabla de Parametros - M01 Rack de Tuberias

Referencia completa de parametros para diseno de pipe racks.

---

## Parametros de Geometria

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `total_length` | float | 6000 - 200000 | 30000 | mm | Longitud total del rack |
| `bay_spacing` | float | 3000 - 12000 | 6000 | mm | Espaciamiento entre marcos |
| `width` | float | 1500 - 8000 | 3000 | mm | Ancho del rack |
| `height` | float | 3000 - 15000 | 6000 | mm | Altura total |
| `elevation` | float | 0 - 10000 | 0 | mm | Elevacion desde NPT |
| `tier_count` | int | 1 - 6 | 3 | - | Numero de niveles |
| `tier_spacing` | float | 600 - 2000 | 1000 | mm | Espaciamiento entre niveles |
| `first_tier_height` | float | 2000 - 6000 | 3500 | mm | Altura del primer nivel |

---

## Tipologias de Marco

| Tipo | Claro Max | Altura Max | Aplicaciones |
|------|-----------|------------|--------------|
| `portal_frame` | 12000 mm | 12000 mm | Plantas de proceso, refinerias |
| `truss_frame` | 24000 mm | 15000 mm | Claros largos, cruces de vialidad |
| `cantilever` | 6000 mm | 10000 mm | Junto a edificios, ampliaciones |
| `elevated` | 15000 mm | 15000 mm | Cruces de vialidad, accesos |
| `ground_mounted` | 8000 mm | 4000 mm | Tuberias bajas, areas de proceso |

### Portal Frame

Marco estructural simple con columnas y vigas.

```
    ┌─────────────┐
    │    Viga     │
    │             │
    │             │
  ┌─┤             ├─┐
  │ │   Columna   │ │
  │ │             │ │
══╧═╧═════════════╧═╧══
```

### Truss Frame

Marco con armadura para claros mayores.

```
    ╱╲    ╱╲    ╱╲
   ╱  ╲  ╱  ╲  ╱  ╲
  ├────┼────┼────┤
  │    │    │    │
  │         │
══╧═════════════════╧══
```

---

## Parametros de Estructura

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `frame_type` | enum | portal_frame, truss_frame, cantilever | portal_frame | Tipo de marco |
| `column_profile` | str | ver tabla | W12x26 | Perfil de columnas |
| `beam_profile` | str | ver tabla | W10x22 | Perfil de vigas principales |
| `strut_profile` | str | ver tabla | W8x18 | Perfil de puntales |
| `bracing_profile` | str | ver tabla | L4x4x3/8 | Perfil de arriostramientos |
| `bracing_type` | enum | none, X, V, K | X | Tipo de arriostramiento |
| `material` | enum | A36, A572_Gr50, A500_Gr_B | A36 | Material estructural |

### Perfiles W (Vigas I)

| Perfil | d (mm) | bf (mm) | Peso (kg/m) | Uso Tipico |
|--------|--------|---------|-------------|------------|
| W6x15 | 152 | 152 | 22.3 | Puntales ligeros |
| W8x18 | 203 | 133 | 26.8 | Puntales, vigas secundarias |
| W10x22 | 254 | 146 | 32.7 | Vigas, puntales |
| W12x26 | 305 | 165 | 38.7 | Columnas, vigas |
| W12x40 | 305 | 203 | 59.5 | Columnas pesadas |
| W14x30 | 356 | 171 | 44.6 | Vigas principales |
| W14x48 | 356 | 203 | 71.4 | Columnas pesadas |
| W16x36 | 406 | 178 | 53.6 | Vigas largas |

### Perfiles HSS (Tubo Cuadrado)

| Perfil | Dimension (mm) | Peso (kg/m) | Uso Tipico |
|--------|----------------|-------------|------------|
| HSS6x6x1/4 | 152x152 | 21.6 | Columnas ligeras |
| HSS8x8x5/16 | 203x203 | 37.4 | Columnas medias |
| HSS10x10x3/8 | 254x254 | 58.1 | Columnas pesadas |
| HSS12x12x1/2 | 305x305 | 93.3 | Columnas muy pesadas |

### Perfiles L (Angulos)

| Perfil | Dimension (mm) | Peso (kg/m) | Uso |
|--------|----------------|-------------|-----|
| L3x3x1/4 | 76x76 | 7.11 | Arriostramientos ligeros |
| L4x4x3/8 | 102x102 | 14.2 | Arriostramientos estandar |
| L5x5x1/2 | 127x127 | 23.6 | Arriostramientos pesados |
| L6x6x1/2 | 152x152 | 28.7 | Arriostramientos muy pesados |

---

## Parametros de Soportes

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `support_type` | enum | shoe, guide, anchor, hanger | shoe | Tipo de soporte |
| `support_spacing` | float | 1500 - 6000 | 3000 | mm | Espaciamiento de soportes |
| `insulation_gap` | float | 0 - 150 | 50 | mm | Gap para aislamiento |
| `shoe_height` | float | 50 - 200 | 100 | mm | Altura de zapata |

### Tipos de Soporte

| Tipo | Movimiento Axial | Movimiento Lateral | Aplicacion |
|------|------------------|-------------------|------------|
| `shoe` | Permitido | Restringido | Soportes intermedios |
| `guide` | Permitido | Restringido | Cambios de direccion |
| `anchor` | Restringido | Restringido | Puntos fijos |
| `hanger` | Segun tipo | Permitido | Tuberias suspendidas |
| `roller` | Libre | Restringido | Alta expansion termica |
| `spring` | Variable | Restringido | Cargas variables |

### Espaciamiento de Soportes por Tamano (mm)

| NPS | Agua | Vapor | Gas/Aire |
|-----|------|-------|----------|
| 2" | 2400 | 2700 | 3000 |
| 3" | 3000 | 3300 | 3600 |
| 4" | 3600 | 3900 | 4200 |
| 6" | 4200 | 4800 | 5100 |
| 8" | 4800 | 5400 | 5800 |
| 10" | 5200 | 6000 | 6400 |
| 12" | 5800 | 6600 | 7000 |

---

## Parametros de Tuberia

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `pipe_size` | int | 2 - 24 | 6 | Tamano nominal (NPS) |
| `schedule` | str | 40, 80, 160 | 40 | Cedula de tuberia |
| `material` | enum | carbon_steel, stainless_304, stainless_316 | carbon_steel | Material |
| `service` | enum | ver tabla | process | Tipo de servicio |
| `insulated` | bool | true/false | true | Requiere aislamiento |

### Dimensiones de Tuberia

| NPS | OD (mm) | Wall Sch40 (mm) | Peso vacio (kg/m) | Peso con agua (kg/m) |
|-----|---------|-----------------|-------------------|---------------------|
| 2" | 60.3 | 3.91 | 5.4 | 8.2 |
| 3" | 88.9 | 5.49 | 11.3 | 18.4 |
| 4" | 114.3 | 6.02 | 16.1 | 28.3 |
| 6" | 168.3 | 7.11 | 28.3 | 56.7 |
| 8" | 219.1 | 8.18 | 43.8 | 94.6 |
| 10" | 273.0 | 9.27 | 60.3 | 140.2 |
| 12" | 323.8 | 10.31 | 77.0 | 190.0 |
| 14" | 355.6 | 11.13 | 106.0 | 261.0 |
| 16" | 406.4 | 12.70 | 136.0 | 349.0 |
| 20" | 508.0 | 15.09 | 206.0 | 571.0 |
| 24" | 609.6 | 17.48 | 283.0 | 844.0 |

### Tipos de Servicio

| Servicio | Descripcion | Temp Tipica | Aislamiento |
|----------|-------------|-------------|-------------|
| `cold_water` | Agua fria | 5-25°C | Condensacion |
| `hot_water` | Agua caliente | 60-90°C | Termica |
| `steam_low` | Vapor baja presion | 100-180°C | Termica |
| `steam_high` | Vapor alta presion | 200-400°C | Termica |
| `chilled` | Agua helada | 5-12°C | Condensacion |
| `process` | Proceso general | Variable | Segun proceso |
| `gas` | Aire/gas | Ambiente | No |
| `oil` | Aceite/combustible | Variable | Seguridad |

---

## Parametros de Aislamiento

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `insulation_type` | enum | mineral_wool, calcium_silicate, cellular_glass | mineral_wool | Tipo de aislamiento |
| `cladding` | enum | aluminum, stainless, galvanized | aluminum | Recubrimiento |
| `vapor_barrier` | bool | true/false | true | Barrera de vapor |

### Espesor de Aislamiento (mm)

| Servicio | 2-4" | 6-8" | 10-12" |
|----------|------|------|--------|
| Agua fria | 25-38 | 50 | 63 |
| Agua caliente | 38-50 | 63-75 | 75-88 |
| Vapor BP | 50-63 | 75-88 | 100 |
| Vapor AP | 75-88 | 100-113 | 125 |
| Agua helada | 50-63 | 75-88 | 100 |

---

## Parametros de Bandeja de Cables

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `tray_type` | enum | ladder, solid, mesh, channel | ladder | Tipo de bandeja |
| `tray_width` | int | 300, 450, 600, 900 | 600 | mm | Ancho |
| `tray_height` | int | 75, 100, 150 | 100 | mm | Altura lateral |
| `tray_tier` | int | 0 - tier_count | 0 | - | Nivel de bandeja |

### Tipos de Bandeja

| Tipo | Ventilacion | Capacidad | Costo/m |
|------|-------------|-----------|---------|
| `ladder` | 95% | 150 kg/m | $850 |
| `solid` | 0% | 100 kg/m | $1,200 |
| `mesh` | 80% | 50 kg/m | $650 |
| `channel` | 0% | 25 kg/m | $350 |

---

## Cargas de Diseno

### Cargas Muertas

| Componente | Factor |
|------------|--------|
| Peso propio estructura | 1.0 |
| Tuberia llena | 1.2 |
| Aislamiento | 1.0 |
| Bandeja de cables | 1.0 |

### Cargas Vivas

| Tipo | Carga (kN/m2) |
|------|---------------|
| Mantenimiento | 1.0 |
| Pasarela | 2.0 |

### Cargas Ambientales

| Tipo | Parametro | Valor Tipico |
|------|-----------|--------------|
| Viento | Presion | 1.0 kPa |
| Sismo | Sds | 0.5 |
| Termico | Rango | -20 a 150°C |

---

## Parametros BIM

| Parametro | Tipo | Grupo | Descripcion |
|-----------|------|-------|-------------|
| `BIMAC_Rack_Type` | Text | Identity Data | Tipologia de rack |
| `BIMAC_Rack_Length` | Length | Dimensions | Longitud total |
| `BIMAC_Rack_Width` | Length | Dimensions | Ancho |
| `BIMAC_Rack_Height` | Length | Dimensions | Altura |
| `BIMAC_Rack_TierCount` | Integer | Dimensions | Numero de niveles |
| `BIMAC_Rack_BayCount` | Integer | Dimensions | Numero de crujias |
| `BIMAC_Rack_Capacity` | Number | Structural | Capacidad (kg/m) |
| `BIMAC_Rack_Weight` | Number | Structural | Peso estructura (kg) |

### Clasificacion

| Sistema | Codigo |
|---------|--------|
| Uniclass | Ss_25_60_65 (Pipe support systems) |
| OmniClass | 23-33 11 00 (Pipe Racks) |
| IFC Class | IfcBuildingElementProxy |
| IFC Type | PIPE_RACK |

---

## Normativas Aplicables

| Codigo | Descripcion | Aplicacion |
|--------|-------------|------------|
| AISC 360 | Especificacion de acero estructural | Diseno de estructura |
| ASCE 7 | Cargas minimas de diseno | Cargas de viento/sismo |
| MSS SP-58 | Soportes de tuberia | Diseno de soportes |
| MSS SP-69 | Guias y anclajes | Puntos de restriccion |
| NFPA 30 | Liquidos inflamables | Plantas de proceso |
| API 650 | Tanques de almacenamiento | Facilidades petroleras |

---

## Restricciones de Diseno

### Geometria

| Restriccion | Minimo | Maximo |
|-------------|--------|--------|
| Espaciamiento de crujia | 3000 mm | 12000 mm |
| Ancho de rack | 1500 mm | 8000 mm |
| Altura total | 3000 mm | 15000 mm |
| Espaciamiento de niveles | 600 mm | 2000 mm |

### Estructura

| Restriccion | Limite |
|-------------|--------|
| Deflexion de viga | L/240 |
| Esbeltez de columna (Kl/r) | 200 |
| Esbeltez de viga (Lb/ry) | 240 |
| Empalme minimo de columna | 1500 mm |

### Acceso

| Elemento | Dimension |
|----------|-----------|
| Ancho de pasarela | 750 mm min |
| Altura de barandal | 1070 mm |
| Ancho de escalera | 450 mm |
| Espaciamiento de escalones | 300 mm |

---

*Documentacion de parametros v1.0 - M01 Rack de Tuberias Parametrico*
