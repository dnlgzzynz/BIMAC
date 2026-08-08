# Ejemplos de Configuracion - C02 Rampa Vehicular Helicoidal

Ejemplos de configuraciones tipicas para diferentes aplicaciones.

---

## Ejemplo 1: Estacionamiento Residencial

Rampa compacta de un carril para edificio residencial.

### Aplicacion
- Edificio de 8 departamentos
- 2 niveles de sotano
- Vehiculos livianos unicamente

### Configuracion

```yaml
geometry:
  inner_radius: 5.5
  outer_radius: 9.0
  rise_per_turn: 3.0
  total_turns: 2.0
  direction: clockwise
  superelevation: 5.0

lanes:
  count: 1
  width: 3.5
  shoulder_inner: 0.3
  shoulder_outer: 0.5

structure:
  type: solid_slab
  thickness: 220
  concrete_fc: 28
  reinforcement: bidirectional

barriers:
  inner: low_profile
  outer: jersey

drainage:
  channel: inner_edge
  catch_basins: every_15m
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Longitud total | 91.1 m |
| Altura total | 6.0 m |
| Pendiente | 6.6% |
| Ancho | 3.5 m |
| Area de rampa | 319 m² |

### Diagrama en Planta

```
                  N
                  ↑
            ╭─────────╮
           ╱           ╲
          ╱   Nivel 0   ╲
         │               │
    ←────│       ●       │────→ Entrada
         │               │
          ╲   Nivel -1  ╱
           ╲           ╱
            ╰────│────╯
                 ↓
             Nivel -2
```

### Costo Estimado

| Concepto | Cantidad | Unidad | Costo |
|----------|----------|--------|-------|
| Concreto losa | 70 m³ | $180/m³ | $12,600 |
| Acero refuerzo | 5,600 kg | $1.35/kg | $7,560 |
| Barreras | 182 m | $380/m | $69,160 |
| Drenaje | 1 sistema | - | $8,500 |
| Senalizacion | 1 lote | - | $4,200 |
| **Total** | | | **$102,020** |
| **Costo/m²** | | | **$320/m²** |

---

## Ejemplo 2: Edificio de Oficinas

Rampa de dos carriles para edificio corporativo.

### Aplicacion
- Edificio de 15 pisos
- 4 niveles de estacionamiento
- 400 cajones
- Trafico mixto (subida/bajada)

### Configuracion

```yaml
geometry:
  inner_radius: 7.5
  outer_radius: 14.0
  rise_per_turn: 3.3
  total_turns: 4.0
  direction: counterclockwise
  superelevation: 4.0

lanes:
  count: 2
  width_per_lane: 3.25
  separator: 0.0
  shoulder_inner: 0.3
  shoulder_outer: 0.5

structure:
  type: steel_deck
  beams_radial: W14x30
  beams_perimeter: W16x36
  columns: D500
  column_spacing: 45deg
  deck: 20ga
  concrete_topping: 100

barriers:
  inner: f_shape
  outer: f_shape
  material: concrete

drainage:
  channel: inner_edge
  catch_basins: every_12m
  piping: PVC_150

lighting:
  type: LED
  spacing: 6.0
  lux_level: 75
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Longitud por vuelta | 67.5 m |
| Longitud total | 270.2 m |
| Altura total | 13.2 m |
| Pendiente | 4.9% |
| Ancho total | 6.5 m |
| Area de rampa | 1,756 m² |

### Seccion Estructural

```
         6500 mm
    ├────────────────────┤

    ┌────────────────────┐ ← Barrera exterior
    │▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ ← Concreto 100mm
    │════════════════════│ ← Deck metalico
    │                    │
    │    W14x30 (rad)    │ ← Viga radial
    │                    │
    │         │          │
    │         │ D500     │ ← Columna
    │         │          │
    ┴─────────┴──────────┴
```

### Lista de Materiales

| Componente | Cantidad | Peso/Vol |
|------------|----------|----------|
| Vigas radiales W14x30 | 32 pcs | 14,300 kg |
| Viga perim. int. W14x30 | 270 m | 12,040 kg |
| Viga perim. ext. W16x36 | 352 m | 18,870 kg |
| Columnas D500 | 16 pcs | 28,800 kg |
| Deck metalico | 1,756 m² | 15,800 kg |
| Concreto | 176 m³ | 422,400 kg |
| Barreras concreto | 540 m | 194,400 kg |
| **Total estructura** | | **706,610 kg** |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Acero estructura | $187,275 |
| Deck metalico | $52,680 |
| Concreto | $31,680 |
| Barreras | $243,000 |
| Drenaje | $28,500 |
| Iluminacion | $18,000 |
| Senalizacion | $12,500 |
| Montaje | $115,200 |
| **Total** | **$688,835** |
| **Costo/m²** | **$392/m²** |

---

## Ejemplo 3: Centro Comercial

Rampa express de tres carriles para centro comercial.

### Aplicacion
- Centro comercial regional
- 2,500 cajones de estacionamiento
- 5 niveles
- Alto volumen de trafico

### Configuracion

```yaml
geometry:
  inner_radius: 10.0
  outer_radius: 20.0
  rise_per_turn: 3.5
  total_turns: 5.0
  direction: clockwise
  superelevation: 3.5

lanes:
  count: 3
  width_per_lane: 3.0
  separator: 0.0
  shoulder_inner: 0.5
  shoulder_outer: 0.5

structure:
  type: precast
  elements: hollow_core
  element_width: 2400
  element_depth: 400
  topping: 75
  supports: ledger_beams

barriers:
  inner: jersey
  outer: f_shape
  height: 1070

systems:
  drainage: comprehensive
  lighting: high_output
  ventilation: jet_fans
  fire_protection: sprinklers

signage:
  wayfinding: dynamic_LED
  speed_limit: 20
  clearance: 2.40
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Longitud por vuelta | 94.2 m |
| Longitud total | 471.2 m |
| Altura total | 17.5 m |
| Pendiente | 3.7% |
| Ancho total | 10.0 m |
| Area de rampa | 4,712 m² |
| Volumen interior | 82,460 m³ |

### Vista en Seccion

```
                   10.0 m
    ├──────────────────────────────────┤

    ▓│  3.0m  │  3.0m  │  3.0m  │0.5│▓
    ▓├────────┼────────┼────────┼───┤▓
    ▓│   ↑    │   ↑    │   ↑    │   │▓
    ▓│ Carril │ Carril │ Carril │Hom│▓
    ▓│   1    │   2    │   3    │bro│▓
    ▓└────────┴────────┴────────┴───┘▓
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
          Barrera F-Shape
```

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura precolada | $895,280 |
| Barreras | $424,080 |
| Drenaje | $85,000 |
| Iluminacion | $62,500 |
| Ventilacion | $125,000 |
| Proteccion contra incendio | $95,000 |
| Senalizacion digital | $48,000 |
| Acabados | $141,360 |
| **Total** | **$1,876,220** |
| **Costo/m²** | **$398/m²** |

---

## Ejemplo 4: Acceso Subterraneo

Rampa de acceso profundo para estacionamiento de hospital.

### Aplicacion
- Hospital de especialidades
- Estacionamiento 3 sotanos
- Acceso vehiculos de emergencia
- Alta seguridad

### Configuracion

```yaml
geometry:
  inner_radius: 8.0
  outer_radius: 13.5
  rise_per_turn: 4.0
  total_turns: 2.25
  direction: counterclockwise
  superelevation: 4.5

lanes:
  count: 2
  width_per_lane: 3.5
  separator: 0.5
  shoulder_inner: 0.3
  shoulder_outer: 0.5

structure:
  type: ribbed_slab
  slab_thickness: 120
  rib_depth: 400
  rib_spacing: 1200
  retaining_walls: both_sides

barriers:
  inner: single_slope
  outer: single_slope
  height: 1070

special:
  emergency_access: yes
  ambulance_clearance: 3.0
  security: controlled_access
  ventilation: forced
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Longitud total | 152.7 m |
| Profundidad | 9.0 m |
| Pendiente | 5.9% |
| Ancho | 5.5 m |
| Altura libre | 3.0 m |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura + muros | $485,000 |
| Barreras | $116,050 |
| Sistemas MEP | $145,000 |
| Seguridad y control | $68,000 |
| **Total** | **$814,050** |

---

## Ejemplo 5: Estacionamiento Automatizado

Rampa de alta tecnologia para estacionamiento robotizado.

### Aplicacion
- Torre de oficinas premium
- Sistema de estacionamiento automatizado
- Rampa solo para entrada/salida de robots

### Configuracion

```yaml
geometry:
  inner_radius: 4.5
  outer_radius: 7.0
  rise_per_turn: 2.8
  total_turns: 3.0
  direction: clockwise
  superelevation: 6.0

lanes:
  count: 1
  width: 2.8  # Ancho para plataforma robotica
  shoulder_inner: 0.2
  shoulder_outer: 0.2

structure:
  type: solid_slab
  thickness: 180
  finish: precision_level
  flatness: FF50/FL30

barriers:
  inner: low_profile
  outer: low_profile
  sensors: laser_guided

automation:
  guidance: magnetic_tape
  sensors: laser + camera
  safety: multiple_redundancy
  speed_control: variable
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Longitud | 108.4 m |
| Altura | 8.4 m |
| Pendiente | 7.7% |
| Ancho | 2.5 m |
| Area | 271 m² |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| Estructura precision | $95,000 |
| Sistema guiado | $125,000 |
| Sensores y control | $185,000 |
| Integracion | $75,000 |
| **Total** | **$480,000** |

---

## Resumen Comparativo

| Ejemplo | Carriles | Radio Ext | Vueltas | Pendiente | Costo/m² |
|---------|----------|-----------|---------|-----------|----------|
| Residencial | 1 | 9.0 m | 2.0 | 6.6% | $320 |
| Oficinas | 2 | 14.0 m | 4.0 | 4.9% | $392 |
| C. Comercial | 3 | 20.0 m | 5.0 | 3.7% | $398 |
| Hospital | 2 | 13.5 m | 2.25 | 5.9% | - |
| Automatizado | 1 | 7.0 m | 3.0 | 7.7% | - |

### Relacion Radio vs Pendiente

```
Pendiente
  (%)
   8 ┤                    ● Automatizado
     │          ● Residencial
   6 ┤                    ● Hospital
     │
   4 ┤          ● Oficinas
     │                         ● C. Comercial
   2 ┤
     │
   0 ┼────┬────┬────┬────┬────┬────
     5    10   15   20   25   30   Radio (m)
```

---

## Notas de Aplicacion

### Seleccion de Numero de Carriles

| Capacidad (veh/hora) | Carriles | Configuracion |
|----------------------|----------|---------------|
| < 200 | 1 | Unidireccional |
| 200 - 400 | 2 | Bidireccional |
| > 400 | 3+ | Separados |

### Seleccion de Estructura

| Claro (m) | Tipo Recomendado |
|-----------|------------------|
| < 5 | Losa maciza |
| 5 - 8 | Losa nervada |
| 8 - 12 | Estructura metalica |
| > 12 | Precolado |

---

*Documentacion de ejemplos v1.0 - C02 Rampa Vehicular Helicoidal*
