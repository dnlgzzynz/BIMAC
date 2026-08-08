# C02 - Rampa Vehicular Helicoidal Parametrica

Sistema de generacion parametrica de rampas helicoidales para estacionamientos y accesos vehiculares.

## Descripcion

Componente Grasshopper para disenar rampas helicoidales que cumplen normativas de accesibilidad vehicular, con estructura optimizada y sistemas de drenaje integrados.

## Tipos de Rampa

### Por Direccion de Giro

| Tipo | Codigo | Ventaja |
|------|--------|---------|
| Horario (CW) | `clockwise` | Conductor ve borde exterior |
| Antihorario (CCW) | `counterclockwise` | Mejor visibilidad en curva |

### Por Configuracion

| Tipo | Carriles | Ancho Min | Aplicacion |
|------|----------|-----------|------------|
| Simple | 1 | 3.5 m | Estacionamientos pequenos |
| Doble | 2 | 6.5 m | Edificios de oficinas |
| Con separador | 2 | 7.0 m | Centros comerciales |
| Express | 3+ | 10.0 m | Estacionamientos grandes |

### Por Estructura

| Tipo | Descripcion | Claro Max |
|------|-------------|-----------|
| Losa maciza | Concreto reforzado | 8 m |
| Losa nervada | Vigas integradas | 12 m |
| Estructura metalica | Vigas de acero + deck | 15 m |
| Prefabricada | Elementos pretensados | 18 m |

## Capacidades

### Geometria
- Rampas de 1 a 5 vueltas completas
- Radios de 5 a 25 metros
- Pendientes de 5% a 15%
- Peralte variable automatico

### Estructura
- Losas de concreto con espesor variable
- Vigas radiales y perimetrales
- Columnas helicoidales o rectas
- Muros de contencion opcionales

### Sistemas
- Drenaje perimetral y central
- Barandales vehiculares (F-shape, Jersey)
- Senalizacion horizontal
- Iluminacion integrada

## Estructura de Archivos

```
C02-rampa-helicoidal/
├── README.md
├── config.yaml
├── src/
│   └── grasshopper/
│       ├── C02_Rampa_Helicoidal.gh
│       └── scripts/
│           ├── helix_generator.py
│           ├── slab_builder.py
│           ├── structure_builder.py
│           ├── barrier_builder.py
│           └── ramp_analyzer.py
└── docs/
    ├── parameters.md
    └── examples.md
```

## Parametros Principales

| Parametro | Rango | Default | Descripcion |
|-----------|-------|---------|-------------|
| inner_radius | 5-15 m | 7.5 m | Radio interior |
| outer_radius | 8-25 m | 12.5 m | Radio exterior |
| rise_per_turn | 2.5-4.0 m | 3.0 m | Altura por vuelta |
| total_turns | 0.5-5.0 | 2.0 | Numero de vueltas |
| slope | 5-15% | 10% | Pendiente longitudinal |
| superelevation | 2-6% | 4% | Peralte transversal |
| lane_count | 1-3 | 2 | Numero de carriles |

## Normativas

- IBC - International Building Code
- ACI 318 - Concrete Structures
- AISC 360 - Steel Structures
- AASHTO - Vehicle Barriers
- ADA - Accessibility Guidelines

## Autor

BIMAC - BIM Advance Consulting
Version 1.0.0
