# Parametros - M02 Sistema HVAC Modular

Documentacion completa de parametros para el componente de sistema HVAC modular.

---

## Indice

1. [Parametros de Sistema](#1-parametros-de-sistema)
2. [Parametros de Ductos](#2-parametros-de-ductos)
3. [Parametros de Terminales](#3-parametros-de-terminales)
4. [Parametros de Equipos](#4-parametros-de-equipos)
5. [Parametros de Aislamiento](#5-parametros-de-aislamiento)
6. [Parametros de Analisis](#6-parametros-de-analisis)
7. [Outputs](#7-outputs)

---

## 1. Parametros de Sistema

### 1.1 Tipo de Sistema

| Parametro | Tipo | Rango | Default | Descripcion |
|-----------|------|-------|---------|-------------|
| `system_type` | string | [VAV, CAV, FCU, VRF, DOAS] | VAV | Tipo de sistema HVAC |
| `system_name` | string | - | "HVAC-01" | Identificador del sistema |
| `building_type` | string | [office, retail, hospital, school, hotel] | office | Tipo de edificio |
| `climate_zone` | string | [1-8] | 4 | Zona climatica ASHRAE |

### 1.2 Caudales de Aire

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `total_supply_cfm` | float | CFM | 500-100,000 | 5000 | Caudal total de suministro |
| `outdoor_air_pct` | float | % | 10-100 | 20 | Porcentaje de aire exterior |
| `return_air_ratio` | float | ratio | 0.7-1.0 | 0.9 | Relacion retorno/suministro |
| `exhaust_cfm` | float | CFM | 0-50,000 | 500 | Caudal de extraccion |

### 1.3 Presiones

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `supply_static_pa` | float | Pa | 250-1500 | 750 | Presion estatica suministro |
| `return_static_pa` | float | Pa | 150-500 | 250 | Presion estatica retorno |
| `building_pressure_pa` | float | Pa | 5-25 | 12.5 | Presion positiva edificio |

---

## 2. Parametros de Ductos

### 2.1 Dimensionamiento

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `duct_shape` | string | - | [rectangular, round, oval] | rectangular | Forma del ducto |
| `max_velocity_mps` | float | m/s | 4-15 | 8 | Velocidad maxima en ducto |
| `friction_pa_m` | float | Pa/m | 0.5-2.0 | 1.0 | Perdida por friccion objetivo |
| `aspect_ratio_max` | float | ratio | 2-6 | 4 | Relacion de aspecto maxima |

### 2.2 Tamaños Estandar

**Ducto Rectangular (mm):**

| Ancho | Alturas Disponibles |
|-------|---------------------|
| 200 | 150, 200, 250, 300 |
| 250 | 150, 200, 250, 300, 400 |
| 300 | 200, 250, 300, 400, 500 |
| 400 | 200, 300, 400, 500, 600 |
| 500 | 250, 300, 400, 500, 600, 800 |
| 600 | 300, 400, 500, 600, 800, 1000 |
| 800 | 400, 500, 600, 800, 1000 |
| 1000 | 500, 600, 800, 1000, 1200 |
| 1200 | 600, 800, 1000, 1200 |
| 1500 | 800, 1000, 1200 |

**Ducto Circular (mm diametro):**

| Diametro | CFM Tipico |
|----------|------------|
| 100 | 25-50 |
| 125 | 40-80 |
| 150 | 60-120 |
| 200 | 100-250 |
| 250 | 200-400 |
| 300 | 350-700 |
| 350 | 500-1000 |
| 400 | 700-1400 |
| 450 | 900-1800 |
| 500 | 1100-2200 |
| 600 | 1600-3200 |

### 2.3 Materiales

| Parametro | Tipo | Opciones | Default | Descripcion |
|-----------|------|----------|---------|-------------|
| `duct_material` | string | [galvanized, stainless, aluminum] | galvanized | Material del ducto |
| `gauge_supply` | int | [18, 20, 22, 24, 26] | 24 | Calibre para suministro |
| `gauge_return` | int | [18, 20, 22, 24, 26] | 22 | Calibre para retorno |
| `gauge_exhaust` | int | [18, 20, 22, 24] | 20 | Calibre para extraccion |

**Seleccion de Calibre por Dimension (SMACNA):**

| Dimension Mayor (mm) | Presion Baja (22) | Presion Media (20) | Presion Alta (18) |
|----------------------|-------------------|--------------------|--------------------|
| ≤ 300 | 26 ga | 24 ga | 22 ga |
| 301 - 450 | 24 ga | 22 ga | 20 ga |
| 451 - 750 | 22 ga | 20 ga | 18 ga |
| 751 - 1200 | 20 ga | 18 ga | 16 ga |
| > 1200 | 18 ga | 16 ga | 14 ga |

### 2.4 Accesorios

| Parametro | Tipo | Opciones | Descripcion |
|-----------|------|----------|-------------|
| `elbow_type` | string | [mitered, radius] | Tipo de codo |
| `elbow_radius` | float | 0.5-2.0 D | Radio de curvatura |
| `transition_angle` | float | 15-45° | Angulo de transicion |
| `damper_type` | string | [parallel, opposed, fire] | Tipo de damper |

---

## 3. Parametros de Terminales

### 3.1 Difusores de Suministro

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `diffuser_type` | string | - | [square_4way, round, linear_slot, perforated] | square_4way | Tipo de difusor |
| `neck_size_in` | float | in | 6-14 | 10 | Tamaño de cuello |
| `pattern` | string | - | [radial, 4way, 1way, 2way] | 4way | Patron de descarga |
| `throw_ft` | float | ft | 4-25 | 12 | Alcance del chorro |
| `nc_max` | int | NC | 15-40 | 25 | Nivel de ruido maximo |

**Tamaños de Difusores Cuadrados:**

| Tamaño (in) | CFM Min | CFM Max | NC Rating | Throw (ft) |
|-------------|---------|---------|-----------|------------|
| 6x6 | 25 | 85 | 20 | 4 |
| 8x8 | 50 | 150 | 22 | 6 |
| 10x10 | 75 | 250 | 25 | 8 |
| 12x12 | 100 | 400 | 28 | 10 |
| 14x14 | 150 | 550 | 30 | 12 |
| 16x16 | 200 | 750 | 32 | 14 |
| 18x18 | 250 | 950 | 34 | 16 |
| 24x24 | 400 | 1400 | 38 | 20 |

**Difusores Lineales (por pie lineal):**

| Slots | CFM/ft Min | CFM/ft Max | Throw (ft) |
|-------|------------|------------|------------|
| 1 | 15 | 45 | 8 |
| 2 | 30 | 90 | 12 |
| 3 | 45 | 135 | 16 |
| 4 | 60 | 180 | 20 |

### 3.2 Rejillas de Retorno

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `grille_type` | string | - | [bar, egg_crate, perforated, linear] | bar | Tipo de rejilla |
| `blade_direction` | string | - | [horizontal, vertical] | horizontal | Direccion de aletas |
| `with_filter` | bool | - | true/false | false | Con marco para filtro |
| `damper_behind` | bool | - | true/false | true | Damper de balanceo |

**Tamaños de Rejillas de Retorno:**

| Tamaño (in) | CFM Min | CFM Max | Area Libre (%) |
|-------------|---------|---------|----------------|
| 8x8 | 50 | 200 | 75 |
| 10x10 | 100 | 350 | 75 |
| 12x12 | 150 | 500 | 75 |
| 14x14 | 200 | 700 | 75 |
| 16x16 | 300 | 950 | 75 |
| 18x18 | 400 | 1200 | 75 |
| 24x24 | 600 | 1800 | 75 |
| 12x6 | 75 | 250 | 75 |
| 24x6 | 150 | 500 | 75 |
| 36x8 | 300 | 900 | 75 |
| 48x8 | 400 | 1200 | 75 |

---

## 4. Parametros de Equipos

### 4.1 Unidades Manejadoras de Aire (UMA/AHU)

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `ahu_cfm` | float | CFM | 1000-50,000 | 5000 | Capacidad de flujo |
| `ahu_static_pa` | float | Pa | 500-2000 | 1000 | Presion estatica total |
| `ahu_configuration` | string | - | [horizontal, vertical, stacked] | horizontal | Configuracion fisica |
| `cooling_tons` | float | tons | 5-200 | 20 | Capacidad de enfriamiento |
| `heating_kw` | float | kW | 0-500 | 50 | Capacidad de calefaccion |
| `filter_type` | string | - | [MERV8, MERV13, HEPA] | MERV13 | Tipo de filtro |

**Dimensiones Tipicas de UMA:**

| CFM | Ancho (mm) | Alto (mm) | Largo (mm) | Peso (kg) |
|-----|------------|-----------|------------|-----------|
| 2,000 | 1200 | 1200 | 3000 | 450 |
| 5,000 | 1500 | 1500 | 4000 | 850 |
| 10,000 | 1800 | 1800 | 5500 | 1400 |
| 20,000 | 2400 | 2100 | 7000 | 2800 |
| 30,000 | 2700 | 2400 | 8500 | 4200 |

### 4.2 Cajas VAV

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `vav_cfm_max` | float | CFM | 200-3000 | 800 | CFM maximo |
| `vav_cfm_min` | float | CFM | 50-500 | 200 | CFM minimo |
| `vav_type` | string | - | [cooling_only, reheat, dual_duct, fan_powered] | cooling_only | Tipo de VAV |
| `reheat_kw` | float | kW | 0-20 | 5 | Capacidad de recalentamiento |
| `inlet_size_in` | int | in | 6-16 | 10 | Tamaño de entrada |

**Tamaños de Cajas VAV:**

| Inlet (in) | CFM Min | CFM Max | Dimensiones (mm) |
|------------|---------|---------|------------------|
| 6 | 100 | 400 | 300 x 300 x 450 |
| 8 | 200 | 700 | 400 x 400 x 500 |
| 10 | 300 | 1100 | 450 x 450 x 550 |
| 12 | 500 | 1600 | 500 x 500 x 600 |
| 14 | 700 | 2200 | 550 x 550 x 650 |
| 16 | 1000 | 3000 | 600 x 600 x 700 |

### 4.3 Fan Coils

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `fcu_cfm` | float | CFM | 200-2000 | 600 | Capacidad de flujo |
| `fcu_type` | string | - | [2pipe, 4pipe] | 4pipe | Configuracion de tuberia |
| `fcu_mounting` | string | - | [horizontal, vertical, console] | horizontal | Tipo de montaje |
| `fcu_cooling_mbh` | float | MBH | 6-60 | 18 | Capacidad enfriamiento |
| `fcu_heating_mbh` | float | MBH | 6-40 | 12 | Capacidad calefaccion |

### 4.4 Extractores

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `exhaust_cfm` | float | CFM | 50-5000 | 500 | Capacidad de extraccion |
| `exhaust_type` | string | - | [centrifugal, inline, roof, wall] | inline | Tipo de extractor |
| `exhaust_static_pa` | float | Pa | 50-500 | 150 | Presion estatica |
| `exhaust_application` | string | - | [general, toilet, kitchen, lab] | general | Aplicacion |

---

## 5. Parametros de Aislamiento

### 5.1 Especificaciones

| Parametro | Tipo | Unidad | Rango | Default | Descripcion |
|-----------|------|--------|-------|---------|-------------|
| `insulation_type` | string | - | [fiberglass, elastomeric, mineral_wool] | fiberglass | Tipo de aislamiento |
| `insulation_thickness` | int | mm | 25, 50, 75, 100 | 50 | Espesor |
| `vapor_barrier` | bool | - | true/false | true | Barrera de vapor |
| `facing` | string | - | [FSK, ASJ, none] | FSK | Acabado exterior |

### 5.2 Aplicacion por Tipo de Ducto

| Ubicacion | Espesor Minimo (mm) | R-Value Minimo |
|-----------|---------------------|----------------|
| Interior climatizado | 25 | R-4.2 |
| Plenum de retorno | 38 | R-6 |
| Exterior/no climatizado | 50 | R-8 |
| Ducto de suministro frio | 50 | R-8 |
| Ducto de extraccion cocina | 50 (mineral wool) | R-8 |

### 5.3 Densidad y Propiedades

| Material | Densidad (kg/m³) | k (W/m·K) | Temp Max (°C) |
|----------|------------------|-----------|---------------|
| Fiberglass | 24-48 | 0.035 | 230 |
| Elastomeric | 60-100 | 0.038 | 105 |
| Mineral Wool | 48-128 | 0.037 | 650 |

---

## 6. Parametros de Analisis

### 6.1 Caida de Presion

| Parametro | Tipo | Unidad | Descripcion |
|-----------|------|--------|-------------|
| `segment_id` | string | - | Identificador de segmento |
| `segment_length` | float | m | Longitud del segmento |
| `fitting_count` | dict | - | Conteo de accesorios por tipo |
| `velocity_mps` | float | m/s | Velocidad calculada |
| `friction_pa_m` | float | Pa/m | Perdida por friccion |
| `total_drop_pa` | float | Pa | Caida total del segmento |

### 6.2 Coeficientes de Perdida Local (K)

| Accesorio | K Factor | Notas |
|-----------|----------|-------|
| Codo 90° rectangular | 0.22 | Con vanes: 0.11 |
| Codo 90° circular | 0.15 | Radio 1.5D |
| Codo 45° | 0.10 | - |
| Tee (rama) | 1.00 | Divergente |
| Tee (principal) | 0.30 | - |
| Reduccion | 0.04 | 15° transicion |
| Damper abierto | 0.20 | - |
| Damper 50% | 2.50 | - |
| Fire damper | 0.15 | Abierto |
| Difusor | 0.50 | - |
| Rejilla | 0.40 | - |
| Filtro limpio | 0.50 | MERV 13 |
| Filtro sucio | 1.50 | MERV 13 |
| Serpentin 4 filas | 0.80 | - |
| Serpentin 6 filas | 1.20 | - |

### 6.3 Balanceo de Aire

| Parametro | Tipo | Unidad | Tolerancia | Descripcion |
|-----------|------|--------|------------|-------------|
| `design_cfm` | float | CFM | - | CFM de diseño |
| `actual_cfm` | float | CFM | ±10% | CFM medido |
| `deviation_pct` | float | % | ±10% | Desviacion del diseño |
| `pressure_pa` | float | Pa | - | Presion en terminal |

---

## 7. Outputs

### 7.1 Geometria

| Output | Tipo | Descripcion |
|--------|------|-------------|
| `duct_geometry` | List[Brep] | Geometria de ductos |
| `equipment_geometry` | List[Brep] | Geometria de equipos |
| `terminal_geometry` | List[Brep] | Geometria de terminales |
| `insulation_geometry` | List[Brep] | Geometria de aislamiento |
| `support_geometry` | List[Brep] | Geometria de soportes |

### 7.2 Datos de Sistema

| Output | Tipo | Descripcion |
|--------|------|-------------|
| `duct_schedule` | DataTable | Lista de ductos |
| `terminal_schedule` | DataTable | Lista de terminales |
| `equipment_schedule` | DataTable | Lista de equipos |
| `pressure_report` | Report | Analisis de presion |
| `balance_report` | Report | Reporte de balanceo |

### 7.3 Analisis de Costos

| Output | Tipo | Descripcion |
|--------|------|-------------|
| `ductwork_cost` | float | Costo de ductos |
| `insulation_cost` | float | Costo de aislamiento |
| `equipment_cost` | float | Costo de equipos |
| `terminal_cost` | float | Costo de terminales |
| `installation_cost` | float | Costo de instalacion |
| `total_cost` | float | Costo total del sistema |

---

## Diagramas de Referencia

### Diagrama de Sistema VAV Tipico

```
                    ┌─────────────────────────────────────────┐
                    │            AIRE EXTERIOR                │
                    └────────────────┬────────────────────────┘
                                     │
                                     ▼
    ┌────────────────────────────────────────────────────────────┐
    │                        UMA / AHU                           │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
    │  │ FILTRO  │→ │SERPENTIN│→ │ HUMIDI- │→ │VENTILADOR│      │
    │  │         │  │ FRIO    │  │ FICADOR │  │ SUMINISTRO│     │
    │  └─────────┘  └─────────┘  └─────────┘  └──────┬────┘     │
    └────────────────────────────────────────────────┼──────────┘
                                                     │
                    DUCTO PRINCIPAL SUMINISTRO       │
    ═════════════════════════════════════════════════╧══════════
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ VAV-01 │    │ VAV-02 │    │ VAV-03 │    │ VAV-04 │
    │ 500CFM │    │ 800CFM │    │ 600CFM │    │1000CFM │
    └───┬────┘    └───┬────┘    └───┬────┘    └───┬────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │DIFUSOR │    │DIFUSOR │    │DIFUSOR │    │DIFUSOR │
    │12"x12" │    │14"x14" │    │12"x12" │    │24"x24" │
    └────────┘    └────────┘    └────────┘    └────────┘
```

### Seccion de Ducto con Aislamiento

```
    ┌──────────────────────────────────────┐
    │░░░░░░░░░░░ AISLAMIENTO ░░░░░░░░░░░░░│ 50mm
    │░┌────────────────────────────────┐░░│
    │░│                                │░░│
    │░│      DUCTO GALVANIZADO         │░░│ Calibre 24
    │░│          INTERIOR              │░░│
    │░│                                │░░│
    │░└────────────────────────────────┘░░│
    │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
    └──────────────────────────────────────┘
      ▲
      └── FSK Facing (Barrera de vapor)
```

---

## Referencias Normativas

- **ASHRAE 62.1** - Ventilacion para Calidad de Aire
- **ASHRAE 90.1** - Eficiencia Energetica
- **SMACNA** - Estandares de Construccion de Ductos
- **NFPA 90A/90B** - Instalacion de Sistemas HVAC
- **IMC/UMC** - Codigo Mecanico Internacional

---

*Documentacion de parametros v1.0 - M02 Sistema HVAC Modular*
