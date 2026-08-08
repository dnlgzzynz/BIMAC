# M02 - Sistema HVAC Modular Parametrico

Sistema de generacion parametrica de instalaciones de climatizacion (HVAC) para edificios.

## Descripcion

Componente Grasshopper para disenar sistemas de aire acondicionado y ventilacion con distribucion automatica de ductos, equipos y difusores.

## Tipos de Sistema

### Por Configuracion

| Tipo | Codigo | Descripcion | Aplicacion |
|------|--------|-------------|------------|
| VAV | `vav` | Volumen de aire variable | Oficinas, comercial |
| CAV | `cav` | Volumen de aire constante | Industrial |
| Fan Coil | `fan_coil` | Unidades fan coil | Hoteles, hospitales |
| VRF | `vrf` | Flujo refrigerante variable | Edificios mixtos |
| DOAS | `doas` | Aire exterior dedicado | Alta eficiencia |

### Por Ducto

| Tipo | Descripcion | Velocidad Max | Aplicacion |
|------|-------------|---------------|------------|
| Rectangular | Lamina galvanizada | 10 m/s | Principal |
| Circular | Espiral galvanizado | 12 m/s | Ramales |
| Flexible | Aislado | 6 m/s | Conexion difusores |
| Fabric | Textil permeable | 3 m/s | Industrial, deportivo |

## Capacidades

### Distribucion
- Ruteo automatico de ductos principales
- Ramales secundarios optimizados
- Conexiones a difusores
- Evitacion de interferencias

### Equipos
- Unidades manejadoras de aire (UMA)
- Unidades paquete (RTU)
- Fan coils
- Cajas VAV
- Extractores

### Terminales
- Difusores cuadrados y lineales
- Rejillas de retorno
- Difusores de techo
- Rejillas de transferencia

## Estructura de Archivos

```
M02-hvac-modular/
├── README.md
├── config.yaml
├── src/
│   └── grasshopper/
│       ├── M02_HVAC_Modular.gh
│       └── scripts/
│           ├── duct_generator.py
│           ├── equipment_builder.py
│           ├── diffuser_builder.py
│           ├── routing_solver.py
│           └── hvac_analyzer.py
└── docs/
    ├── parameters.md
    └── examples.md
```

## Parametros Principales

| Parametro | Rango | Default | Descripcion |
|-----------|-------|---------|-------------|
| system_type | vav, cav, fan_coil | vav | Tipo de sistema |
| cfm_total | 1000-100000 | 10000 | Flujo total (CFM) |
| duct_material | galvanized, aluminum | galvanized | Material |
| velocity_main | 6-12 | 8 | Velocidad principal (m/s) |
| velocity_branch | 4-8 | 6 | Velocidad ramales (m/s) |
| insulation | none, 25mm, 50mm | 25mm | Aislamiento |

## Normativas

- ASHRAE 90.1 - Eficiencia energetica
- ASHRAE 62.1 - Calidad de aire
- SMACNA - Construccion de ductos
- NFPA 90A - Instalacion HVAC

## Autor

BIMAC - BIM Advance Consulting
Version 1.0.0
