# Ejemplos de Configuracion - M02 Sistema HVAC Modular

Ejemplos de configuraciones tipicas para diferentes aplicaciones.

---

## Ejemplo 1: Oficina Corporativa (Sistema VAV)

Sistema VAV para piso tipico de oficinas.

### Aplicacion
- Edificio corporativo de 12 pisos
- Piso tipico: 1,500 m²
- 150 ocupantes por piso
- Horario: 7am - 8pm

### Configuracion

```yaml
system:
  type: VAV
  name: "AHU-PISO-TIPICO"
  building_type: office
  climate_zone: 4

airflows:
  total_supply_cfm: 12000
  outdoor_air_pct: 20
  return_air_ratio: 0.90
  exhaust_cfm: 1200

pressure:
  supply_static_pa: 875
  return_static_pa: 250
  building_pressure_pa: 12.5

ahu:
  cfm: 12000
  static_pa: 1250
  configuration: horizontal
  cooling_tons: 40
  heating_kw: 60
  filter_type: MERV13
  energy_recovery: enthalpy_wheel

zones:
  - id: Z01-PERIMETRO-N
    cfm: 2500
    vav_type: reheat
    reheat_kw: 8
  - id: Z02-PERIMETRO-S
    cfm: 2500
    vav_type: reheat
    reheat_kw: 8
  - id: Z03-PERIMETRO-E
    cfm: 1500
    vav_type: reheat
    reheat_kw: 5
  - id: Z04-PERIMETRO-O
    cfm: 1500
    vav_type: reheat
    reheat_kw: 5
  - id: Z05-INTERIOR
    cfm: 4000
    vav_type: cooling_only

ductwork:
  material: galvanized
  main_duct:
    size: 1000x500
    velocity_mps: 8.5
  branch_duct:
    size: 400x300
    velocity_mps: 6.0
  insulation:
    type: fiberglass
    thickness: 50
    facing: FSK

terminals:
  supply:
    type: square_4way
    sizes: [12x12, 14x14]
    cfm_per_diffuser: 250
  return:
    type: bar_grille
    sizes: [24x24, 36x12]
```

### Diagrama de Planta

```
    ┌──────────────────────────────────────────────────────────┐
    │                         NORTE                            │
    │  ┌─────────┐                              ┌─────────┐   │
    │  │ VAV-01  │  ═══════════════════════════ │ VAV-02  │   │
    │  │ 2500CFM │  ║  DUCTO PRINCIPAL 1000x500 │ 2500CFM │   │
    │  └────┬────┘  ╠═══════════════════════════╣ └────┬────┘   │
    │       │       ║                           ║       │       │
    │  O ┌──┴──┐    ║    ┌─────────────┐       ║  ┌──┴──┐ E   │
    │  E │Z-04 │    ║    │             │       ║  │Z-03 │ S   │
    │  S │1500 │    ║    │   Z-05      │       ║  │1500 │ T   │
    │  T │ CFM │────╬────│   INTERIOR  │───────╬──│ CFM │ E   │
    │  E └──┬──┘    ║    │   4000 CFM  │       ║  └──┬──┘     │
    │       │       ║    │             │       ║       │       │
    │       │       ║    └─────────────┘       ║       │       │
    │  └────┴───────╨───────────┬──────────────╨───────┴────┘  │
    │                           │                              │
    │                      ┌────┴────┐                         │
    │                      │  UMA    │                         │
    │                      │ 12000   │                         │
    │                      │  CFM    │                         │
    │                      └─────────┘                         │
    │                         SUR                              │
    └──────────────────────────────────────────────────────────┘
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| CFM total | 12,000 |
| CFM/m² | 8 |
| CFM/persona | 80 |
| Aire exterior | 2,400 CFM (20%) |
| Presion estatica | 875 Pa |
| Cajas VAV | 5 unidades |
| Difusores | 48 unidades |
| Rejillas retorno | 12 unidades |
| Longitud ducto principal | 45 m |
| Longitud ductos rama | 120 m |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| UMA 12,000 CFM | $42,000 |
| Cajas VAV (5) | $8,750 |
| Ductos galvanizados | $18,500 |
| Aislamiento 50mm | $4,200 |
| Difusores (48) | $5,280 |
| Rejillas (12) | $960 |
| Accesorios | $3,500 |
| Instalacion | $53,922 |
| **Total** | **$137,112** |
| **Costo/m²** | **$91/m²** |

---

## Ejemplo 2: Centro Comercial (Sistema VAV Multizona)

Sistema VAV grande para area comercial.

### Aplicacion
- Centro comercial regional
- Area total: 25,000 m²
- Tiendas ancla + locales menores
- Horario: 10am - 10pm

### Configuracion

```yaml
system:
  type: VAV
  name: "AHU-MALL-01"
  building_type: retail
  climate_zone: 3

airflows:
  total_supply_cfm: 80000
  outdoor_air_pct: 15
  return_air_ratio: 0.85
  exhaust_cfm: 12000

ahu:
  quantity: 2
  cfm_each: 40000
  static_pa: 1500
  cooling_tons: 133
  heating_kw: 200
  filter_type: MERV13

zones:
  - id: ANCLA-01
    cfm: 25000
    area_m2: 4000
    vav_count: 8
  - id: ANCLA-02
    cfm: 25000
    area_m2: 4000
    vav_count: 8
  - id: LOCALES-PLANTA-1
    cfm: 15000
    area_m2: 5000
    vav_count: 15
  - id: LOCALES-PLANTA-2
    cfm: 15000
    area_m2: 5000
    vav_count: 15

ductwork:
  main_duct:
    material: galvanized
    size: 1500x800
    velocity_mps: 10
  branches:
    velocity_mps: 7.5
  insulation:
    type: fiberglass
    thickness: 75
    exposed_areas: mineral_wool

food_court:
  exhaust_cfm: 8000
  makeup_air_cfm: 6000
  kitchen_hoods: 4
```

### Diagrama Esquematico

```
                    AZOTEA
    ┌─────────────────────────────────────────┐
    │  ┌────────┐              ┌────────┐    │
    │  │ AHU-01 │              │ AHU-02 │    │
    │  │ 40kCFM │              │ 40kCFM │    │
    │  └───┬────┘              └───┬────┘    │
    └──────┼───────────────────────┼─────────┘
           │                       │
    ═══════╧═══════════════════════╧═══════════
    ║                                         ║
    ╠════════╦════════╦════════╦════════╦════╣
    ║ ANCLA  ║ PASILLO║  FOOD  ║ PASILLO║ANCLA║
    ║   01   ║        ║  COURT ║        ║  02 ║
    ║25kCFM  ║ LOCALES║ 8kCFM  ║ LOCALES║25kCFM║
    ║        ║ 15kCFM ║ EXHAUST║ 15kCFM ║      ║
    ╚════════╩════════╩════════╩════════╩═════╝
```

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| UMAs (2 x 40kCFM) | $280,000 |
| Cajas VAV (46) | $69,000 |
| Ductos principales | $125,000 |
| Ductos secundarios | $85,000 |
| Aislamiento | $38,000 |
| Difusores (320) | $44,800 |
| Rejillas (80) | $7,200 |
| Sistema food court | $95,000 |
| Instalacion | $497,200 |
| **Total** | **$1,241,200** |
| **Costo/m²** | **$50/m²** |

---

## Ejemplo 3: Hospital (Sistema con 100% Aire Exterior)

Sistema para areas criticas de hospital.

### Aplicacion
- Hospital de especialidades
- Quirofanos y UTI
- 100% aire exterior
- Operacion 24/7

### Configuracion

```yaml
system:
  type: DOAS
  name: "AHU-QUIROFANOS"
  building_type: hospital
  climate_zone: 4

airflows:
  total_supply_cfm: 8000
  outdoor_air_pct: 100  # 100% aire exterior
  return_air_ratio: 0.0  # Sin recirculacion
  exhaust_cfm: 7500     # Presion positiva

ahu:
  cfm: 8000
  static_pa: 1500
  configuration: stacked
  filter_primary: MERV14
  filter_secondary: HEPA
  cooling_tons: 30
  heating_kw: 80
  humidifier: steam
  uv_sterilization: true

zones:
  - id: OR-01
    cfm: 1200
    pressure: +15Pa
    ach: 20
    temp_range: [18, 24]
    humidity_range: [30, 60]
  - id: OR-02
    cfm: 1200
    pressure: +15Pa
    ach: 20
  - id: OR-03
    cfm: 1200
    pressure: +15Pa
    ach: 20
  - id: UTI
    cfm: 2400
    pressure: +10Pa
    ach: 12
  - id: PREP-RECOVERY
    cfm: 2000
    pressure: +5Pa
    ach: 8

ductwork:
  material: stainless
  sealing: class_A
  leakage_max: 1%
  insulation:
    type: mineral_wool
    thickness: 75
    exterior_jacketing: aluminum

terminals:
  supply:
    type: laminar_flow
    size: 24x24
    hepa_integrated: true
  return:
    type: low_level
    position: wall_base

special_requirements:
  redundancy: N+1
  emergency_power: yes
  bms_integration: full
  monitoring: room_pressure
```

### Diagrama de Zona Quirofanos

```
    ┌──────────────────────────────────────────┐
    │              CUARTO MECANICO             │
    │  ┌────────────────────────────────────┐  │
    │  │  UMA-QX   HEPA   UV    HUMIDIF.   │  │
    │  │  8000CFM  FILTER STERIL STEAM     │  │
    │  └────────────────┬───────────────────┘  │
    └───────────────────┼──────────────────────┘
                        │
         ╔══════════════╧══════════════╗
         ║    DUCTO SUMINISTRO SS      ║
         ╠═══════╦═══════╦═══════╦═════╣
         ║       ║       ║       ║     ║
    ┌────╨────┐ ┌╨─────┐ ┌╨─────┐┌╨────╨────┐
    │ OR-01   │ │OR-02 │ │OR-03 ││   UTI    │
    │ +15Pa   │ │+15Pa │ │+15Pa ││  +10Pa   │
    │1200 CFM │ │1200  │ │1200  ││ 2400 CFM │
    │ HEPA    │ │ HEPA │ │ HEPA ││          │
    │ DIFUSOR │ │      │ │      ││          │
    └─────────┘ └──────┘ └──────┘└──────────┘
         │         │        │         │
         └─────────┴────────┴─────────┘
                   │
              EXTRACCION
              BAJA 7500CFM
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| CFM total | 8,000 |
| Aire exterior | 100% |
| Cambios/hora (OR) | 20 ACH |
| Presion (OR) | +15 Pa |
| Filtracion | MERV14 + HEPA |
| Redundancia | N+1 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| UMA con HEPA | $185,000 |
| Ductos inoxidables | $95,000 |
| Difusores laminar HEPA | $48,000 |
| Aislamiento mineral | $18,500 |
| Controles y monitoreo | $65,000 |
| Instalacion | $256,875 |
| **Total** | **$668,375** |
| **Costo/m²** | **$668/m²** |

---

## Ejemplo 4: Data Center (Precision Cooling)

Sistema de enfriamiento de precision para data center.

### Aplicacion
- Data center Tier III
- Carga: 500 kW IT
- PUE objetivo: 1.4
- Operacion 24/7/365

### Configuracion

```yaml
system:
  type: CRAC
  name: "COOLING-DC-01"
  building_type: data_center
  tier: III

cooling:
  it_load_kw: 500
  cooling_required_kw: 550
  crac_units: 6
  crac_capacity_kw: 100
  redundancy: N+1

airflow:
  total_cfm: 60000
  supply_temp_c: 15
  return_temp_c: 35
  delta_t_c: 20
  hot_aisle_containment: true

floor_plenum:
  depth_mm: 600
  tiles_perforated: 25%
  tile_cfm: 800

racks:
  total: 100
  kw_per_rack: 5
  cfm_per_rack: 600

ductwork:
  underfloor: true
  material: galvanized
  main_plenum: open
  distribution: perforated_tiles

terminals:
  supply:
    type: perforated_floor_tile
    size: 600x600
    cfm: 400-1200
    adjustable: true

monitoring:
  sensors:
    - temperature
    - humidity
    - differential_pressure
  points_per_rack: 3
  alarming: 24/7
```

### Diagrama de Contencion Pasillo Caliente

```
    ┌────────────────────────────────────────────────┐
    │                 TECHO TECNICO                  │
    │  ┌──────────────────────────────────────────┐  │
    │  │       RETORNO AIRE CALIENTE (35°C)       │  │
    │  └──────────────────┬───────────────────────┘  │
    │                     │                          │
    │   PASILLO      ┌────┴────┐      PASILLO       │
    │    FRIO        │ PASILLO │       FRIO         │
    │    (22°C)      │ CALIENTE│      (22°C)        │
    │                │ (35°C)  │                    │
    │  ┌─────┐       │ CONTENI-│       ┌─────┐     │
    │  │RACK │       │   DO    │       │RACK │     │
    │  │     │═══════│         │═══════│     │     │
    │  │ 5kW │ FLUJO │ ▲▲▲▲▲▲▲ │ FLUJO │ 5kW │     │
    │  └─────┘       │         │       └─────┘     │
    │                └─────────┘                    │
    │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
    │  ░░░░ PLENUM BAJO PISO (15°C) ░░░░░░░░░░░   │
    │  ░░░░░░░░░░░▲░░░░░░░░░░░░░░░▲░░░░░░░░░░░   │
    └──────────────┼─────────────────┼──────────────┘
                   │                 │
              CRAC-01           CRAC-02
              100kW             100kW
```

### Estadisticas

| Parametro | Valor |
|-----------|-------|
| Carga IT | 500 kW |
| Capacidad enfriamiento | 600 kW |
| CFM total | 60,000 |
| Delta T | 20°C |
| PUE esperado | 1.35 |
| Unidades CRAC | 6 (N+1) |
| Tiles perforados | 150 |

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| CRAC Units (6 x 100kW) | $540,000 |
| Piso elevado | $125,000 |
| Tiles perforados | $22,500 |
| Contencion | $85,000 |
| Controles y sensores | $95,000 |
| Instalacion | $521,700 |
| **Total** | **$1,389,200** |
| **Costo/kW** | **$2,778/kW** |

---

## Ejemplo 5: Laboratorio (Cabinas de Bioseguridad)

Sistema para laboratorio con cabinas de bioseguridad.

### Aplicacion
- Laboratorio BSL-2
- 10 cabinas de bioseguridad
- Presion negativa
- 100% aire exterior

### Configuracion

```yaml
system:
  type: LAB_EXHAUST
  name: "AHU-LAB-BSL2"
  building_type: laboratory
  biosafety_level: 2

airflows:
  supply_cfm: 6000
  exhaust_cfm: 7200  # Negativo
  outdoor_air_pct: 100
  room_pressure: -10Pa

ahu:
  supply_cfm: 6000
  exhaust_cfm: 7200
  filter_supply: MERV14
  filter_exhaust: HEPA
  exhaust_stack_height_m: 3

cabinets:
  type: class_II_A2
  quantity: 10
  cfm_each: 500
  total_exhaust_cfm: 5000

zones:
  - id: LAB-MAIN
    cfm_supply: 4000
    cfm_exhaust: 4800
    ach: 10
    pressure: -10Pa
  - id: PREP-AREA
    cfm_supply: 1200
    cfm_exhaust: 1400
    ach: 8
    pressure: -5Pa
  - id: ANTEROOM
    cfm_supply: 800
    cfm_exhaust: 1000
    ach: 6
    pressure: -2.5Pa

ductwork:
  exhaust_material: stainless
  supply_material: galvanized
  sealing: welded_exhaust
  insulation: 50mm

controls:
  type: variable_volume
  tracking: supply_follows_exhaust
  offset_cfm: 200
  pressure_control: active
```

### Diagrama de Presiones

```
    EXTERIOR (0 Pa)
         │
         ▼
    ┌─────────────────────────────────────────────┐
    │  ANTEROOM (-2.5 Pa)                         │
    │     ↓ Flujo de aire                         │
    │  ┌──────────────────────────────────────┐   │
    │  │  PREP AREA (-5 Pa)                   │   │
    │  │     ↓ Flujo de aire                  │   │
    │  │  ┌────────────────────────────────┐  │   │
    │  │  │  LABORATORIO PRINCIPAL (-10 Pa)│  │   │
    │  │  │                                │  │   │
    │  │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐  │  │   │
    │  │  │  │BSC │ │BSC │ │BSC │ │BSC │  │  │   │
    │  │  │  │ 01 │ │ 02 │ │ 03 │ │ 04 │  │  │   │
    │  │  │  └──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘  │  │   │
    │  │  │     └──────┴──────┴──────┘     │  │   │
    │  │  │              │                 │  │   │
    │  │  └──────────────┼─────────────────┘  │   │
    │  └─────────────────┼────────────────────┘   │
    └────────────────────┼────────────────────────┘
                         │
                    EXTRACCION
                    HEPA + STACK
                         │
                         ▼
                    ATMOSFERA
```

### Costo Estimado

| Concepto | Costo |
|----------|-------|
| UMA suministro | $45,000 |
| Sistema de extraccion HEPA | $85,000 |
| Cabinas BSC (10) | $350,000 |
| Ductos (SS exhaust) | $48,000 |
| Controles de presion | $35,000 |
| Instalacion | $338,100 |
| **Total** | **$901,100** |

---

## Resumen Comparativo

| Ejemplo | Tipo | CFM | Aire Ext. | Costo/m² |
|---------|------|-----|-----------|----------|
| Oficina | VAV | 12,000 | 20% | $91 |
| Mall | VAV | 80,000 | 15% | $50 |
| Hospital | DOAS | 8,000 | 100% | $668 |
| Data Center | CRAC | 60,000 | 15% | $556* |
| Laboratorio | LAB | 6,000 | 100% | $450 |

*Por m² de sala de servidores

### Grafico de Costos por Tipo

```
Costo por m² segun aplicacion:

Hospital OR     ████████████████████████████ $668
Data Center     ████████████████████████░░░░ $556
Laboratorio     ██████████████████░░░░░░░░░░ $450
Oficina         ████░░░░░░░░░░░░░░░░░░░░░░░░ $91
Centro Comercial███░░░░░░░░░░░░░░░░░░░░░░░░░ $50

0    100   200   300   400   500   600   700  USD/m²
```

---

## Notas de Aplicacion

### Seleccion de Tipo de Sistema

| Aplicacion | Sistema Recomendado | ACH | Aire Ext. |
|------------|---------------------|-----|-----------|
| Oficinas | VAV | 4-8 | 15-25% |
| Retail | VAV/CAV | 6-10 | 10-20% |
| Hospitales | DOAS | 6-25 | 100% |
| Data Centers | CRAC | 20+ | 15% |
| Laboratorios | VAV + Exhaust | 8-12 | 100% |
| Hoteles | FCU + DOAS | 6-8 | 15-20% |

### Velocidades Maximas Recomendadas

| Ubicacion | Velocidad Max (m/s) |
|-----------|---------------------|
| Ducto principal | 10 |
| Ducto de rama | 7.5 |
| Difusores | 2.5 |
| Rejillas retorno | 4.0 |
| Ducto de extraccion | 12 |

---

*Documentacion de ejemplos v1.0 - M02 Sistema HVAC Modular*
