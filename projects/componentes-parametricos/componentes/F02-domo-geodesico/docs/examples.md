# Ejemplos de Configuracion - F02 Domo Geodesico

Ejemplos de configuraciones tipicas para diferentes aplicaciones.

---

## Ejemplo 1: Invernadero Residencial

Domo pequeno para jardin con policarbonato.

### Aplicacion
- Invernadero de traspatio
- Cultivo de hortalizas
- Clima templado

### Configuracion

```yaml
geometry:
  radius: 4.0
  frequency: 2
  truncation: 0.5
  base_type: icosahedron

structure:
  strut_profile: D42x2.5
  node_type: flattened
  material: A500_Gr_B
  finish: galvanized

panels:
  type: triangle
  material: polycarbonate
  thickness: 16
  color: clear

base:
  foundation: concrete_pad
  anchor_type: embedded_bolts
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Altura | 4.0 m |
| Area de piso | 50.3 m² |
| Area superficial | 100.5 m² |
| Vertices | 21 |
| Barras | 60 |
| Paneles | 40 |

### Lista de Materiales

| Componente | Cantidad | Peso/Area | Total |
|------------|----------|-----------|-------|
| Barras tipo A | 30 | 2.45 kg/m x 2.2m | 162 kg |
| Barras tipo B | 30 | 2.45 kg/m x 2.5m | 184 kg |
| Nodos aplastados | 21 | 0.5 kg | 11 kg |
| Policarbonato | 40 | 2.5 m² avg | 100 m² |
| **Total estructura** | - | - | **357 kg** |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura | $1,250 |
| Paneles | $8,500 |
| Nodos y tornilleria | $525 |
| Montaje | $2,200 |
| **Total** | **$12,475** |
| **Costo/m²** | **$248/m²** |

---

## Ejemplo 2: Sala de Eventos

Domo de tamano medio para eventos y exposiciones.

### Aplicacion
- Eventos corporativos
- Exposiciones temporales
- Capacidad: 200 personas

### Configuracion

```yaml
geometry:
  radius: 12.0
  frequency: 4
  truncation: 0.5
  base_type: icosahedron

structure:
  strut_profile: D76x4
  node_type: spherical
  material: A500_Gr_C
  finish: powder_coated

panels:
  type: triangle
  material: glass_double
  thickness: 24
  coating: low_e

base:
  foundation: ring_beam
  anchor_type: base_plates
  ring_profile: W12x26

accessories:
  - entrance_portal
  - hvac_penetrations
  - lighting_grid
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Altura | 12.0 m |
| Area de piso | 452.4 m² |
| Area superficial | 904.8 m² |
| Volumen | 3,619 m³ |
| Vertices | 81 |
| Barras | 240 |
| Paneles | 160 |

### Diagrama de Planta

```
              N
              ^
              |
         ___________
       /             \
      /               \
     /                 \
    |        •          |     Radio = 12m
    |     Centro        |     Diametro = 24m
    |                   |
     \                 /
      \               /
       \_____________/
              |
          Entrada
```

### Lista de Materiales

| Componente | Cantidad | Especificacion |
|------------|----------|----------------|
| Barras tipo A | 60 | D76x4, L=3.04m |
| Barras tipo B | 60 | D76x4, L=3.53m |
| Barras tipo C | 60 | D76x4, L=3.61m |
| Barras tipo D | 60 | D76x4, L=3.77m |
| Nodos esfericos 5-way | 12 | R=100mm |
| Nodos esfericos 6-way | 60 | R=100mm |
| Nodos base | 12 | Con placa |
| DVH 24mm | 160 | ~5.6 m² avg |
| Anillo de base | 1 | W12x26, 75m |

### Peso por Componente

| Componente | Peso (kg) |
|------------|-----------|
| Barras | 6,120 |
| Nodos | 570 |
| Vidrio | 15,750 |
| Anillo base | 2,925 |
| **Total** | **25,365 kg** |
| **Peso/m²** | **28 kg/m²** |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura acero | $18,360 |
| Nodos esfericos | $6,120 |
| Vidrio DVH | $289,536 |
| Galvanizado | $5,202 |
| Montaje | $40,716 |
| Ingenieria | $28,795 |
| **Total** | **$388,729** |
| **Costo/m²** | **$430/m²** |

---

## Ejemplo 3: Centro de Visitantes

Domo grande con sistema ETFE para museo.

### Aplicacion
- Centro de visitantes de museo
- Exposiciones permanentes
- Capacidad: 500 personas

### Configuracion

```yaml
geometry:
  radius: 20.0
  frequency: 5
  truncation: 0.5
  base_type: icosahedron

structure:
  strut_profile: D114x5
  node_type: spherical
  material: A500_Gr_C
  finish: custom_color

panels:
  type: hexagon
  material: etfe
  configuration: double_cushion
  inflation: pneumatic

climate:
  hvac: integrated
  shading: printed_pattern
  ventilation: operable_panels

base:
  foundation: reinforced_ring
  structural_glazing: frameless_entrance
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Altura | 20.0 m |
| Diametro | 40.0 m |
| Area de piso | 1,256.6 m² |
| Area superficial | 2,513.3 m² |
| Volumen | 16,755 m³ |
| Vertices | 126 |
| Barras | 375 |
| Paneles (hex+pent) | 250 |

### Caracteristicas ETFE

```
Configuracion de cojin ETFE:
     _______________________
    /                       \      Capa exterior 0.2mm
   /         Aire            \
  /___________________________\    Capa interior 0.2mm

  Presion de inflado: 250-400 Pa
  Sistema de control automatico
```

| Propiedad | Valor |
|-----------|-------|
| Transmitancia luz | 90% |
| Peso | 1.0 kg/m² |
| U-value | 2.9 W/m²K |
| Vida util | 30+ anos |
| Limpieza | Auto-limpiante |

### Lista de Materiales

| Componente | Cantidad | Especificacion |
|------------|----------|----------------|
| Barras (5 tipos) | 375 | D114x5, L=3.9-4.9m |
| Nodos 5-way | 12 | Pentagonales |
| Nodos 6-way | 114 | Hexagonales |
| Cojines ETFE hex | 238 | ~10 m² avg |
| Cojines ETFE pent | 12 | ~8 m² avg |
| Sistema neumatico | 1 | Completo |

### Peso por Componente

| Componente | Peso (kg) |
|------------|-----------|
| Barras | 21,500 |
| Nodos | 1,890 |
| ETFE + marcos | 5,020 |
| Sistemas | 2,400 |
| **Total** | **30,810 kg** |
| **Peso/m²** | **12.3 kg/m²** |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura | $64,500 |
| Nodos | $16,065 |
| ETFE completo | $628,325 |
| Sistema neumatico | $85,000 |
| Montaje | $125,665 |
| Ingenieria | $73,244 |
| **Total** | **$992,799** |
| **Costo/m²** | **$395/m²** |

---

## Ejemplo 4: Observatorio Astronomico

Domo 5/8 esfera con apertura retractil.

### Aplicacion
- Observatorio universitario
- Telescopio de 0.6m
- Operacion nocturna

### Configuracion

```yaml
geometry:
  radius: 6.0
  frequency: 4
  truncation: 0.625
  base_type: icosahedron

structure:
  strut_profile: D60x3
  node_type: spherical
  material: A500_Gr_B
  finish: white_reflective

panels:
  type: triangle
  material: aluminum
  thickness: 4
  insulation: 50mm

aperture:
  type: rotating_dome
  width: 1.2
  mechanism: motorized
  weather_seal: inflatable

climate:
  hvac: precision_cooling
  humidity_control: active
  air_handling: laminar_flow
```

### Diagrama de Seccion

```
            ___________
          /      |      \
         /   Apertura    \
        /    retractil    \
       |         |         |      5/8 esfera
       |    Telescopio     |      R = 6m
       |         |         |
       |         *         |
        \       / \       /
         \_____/   \_____/
         _____|_____|_____
              Base giratoria
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Altura | 7.5 m |
| Area de piso | 113.1 m² |
| Area superficial | 226.2 m² |
| Apertura | 1.2 x 4.0 m |
| Paneles fijos | 140 |
| Paneles moviles | 20 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura fija | $8,450 |
| Sistema rotacion | $45,000 |
| Apertura motorizada | $28,000 |
| Paneles aluminio | $21,490 |
| Control climatico | $35,000 |
| **Total** | **$137,940** |

---

## Ejemplo 5: Cubierta de Piscina

Domo 3/8 esfera para piscina semiolimpica.

### Aplicacion
- Piscina 25m
- Uso recreativo
- Clima frio

### Configuracion

```yaml
geometry:
  radius: 18.0
  frequency: 4
  truncation: 0.375
  base_type: icosahedron

structure:
  strut_profile: D89x4
  node_type: plate
  material: stainless_316
  finish: polished

panels:
  type: triangle
  material: polycarbonate
  thickness: 25
  tint: bronze_10

environment:
  humidity: high
  chlorine_exposure: yes
  ventilation: natural + mechanical

base:
  integration: existing_walls
  waterproofing: continuous
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Altura | 6.75 m |
| Claro | 36.0 m |
| Area cubierta | 1,017.9 m² |
| Area superficial | 762.7 m² |
| Barras | 192 |
| Paneles | 128 |

### Consideraciones Especiales

| Aspecto | Solucion |
|---------|----------|
| Corrosion | Acero inoxidable 316 |
| Condensacion | Canaletas integradas |
| Ventilacion | Paneles operables en apice |
| Limpieza | Acceso por andamio movil |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura inox | $48,500 |
| Nodos | $8,640 |
| Policarbonato | $64,829 |
| Ventilacion | $12,000 |
| Montaje | $38,213 |
| **Total** | **$172,182** |
| **Costo/m²** | **$226/m²** |

---

## Resumen Comparativo

| Ejemplo | Radio | Freq | Area | Peso/m² | Costo/m² |
|---------|-------|------|------|---------|----------|
| Invernadero | 4m | 2V | 50 m² | 7.1 kg | $248 |
| Sala eventos | 12m | 4V | 452 m² | 28.0 kg | $430 |
| Centro visitantes | 20m | 5V | 1,257 m² | 12.3 kg | $395 |
| Observatorio | 6m | 4V | 113 m² | - | $1,220 |
| Piscina | 18m | 4V | 1,018 m² | - | $226 |

### Grafico de Costos por Material

```
Costo por m² segun material de panel:

ETFE         ████████████████░░░░░░░  $395
Vidrio DVH   █████████████████████░░  $430
Policarbonato ████████░░░░░░░░░░░░░░░  $226
Aluminio     █████████████░░░░░░░░░░  $350

0    100   200   300   400   500  USD/m²
```

---

## Notas de Aplicacion

### Seleccion de Frecuencia

| Frecuencia | Aplicacion Tipica |
|------------|-------------------|
| 2V | Domos pequenos, invernaderos |
| 3V | Viviendas, cubiertas simples |
| 4V | Edificios comerciales, piscinas |
| 5V | Grandes cubiertas, estadios |
| 6V+ | Proyectos especiales |

### Seleccion de Material

| Material | Mejor para |
|----------|------------|
| Vidrio | Vistas, estetica, permanente |
| Policarbonato | Economia, peso ligero, impacto |
| ETFE | Ultra ligero, grandes claros |
| Aluminio | Opaco, aislamiento |

---

*Documentacion de ejemplos v1.0 - F02 Domo Geodesico Parametrico*
