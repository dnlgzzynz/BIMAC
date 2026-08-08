# E03 - Conexion Viga-Columna Parametrica

Componente parametrico para generacion de conexiones estructurales acero viga-columna segun AISC y AWS D1.1.

## Descripcion

Este componente genera conexiones estructurales de acero incluyendo:
- Conexiones de momento (rigidas)
- Conexiones de corte (simples)
- Conexiones precalificadas sismicas (SMF, IMF, OMF)
- Placas de conexion, rigidizadores y soldaduras
- Validacion automatica segun AISC 360 y AWS D1.1

## Caracteristicas

### Tipologias de Conexion

| Tipo | Categoria | Rigidez | Aplicacion |
|------|-----------|---------|------------|
| `shear_tab` | Corte | Simple | Conexiones de gravedad |
| `clip_angle` | Corte | Simple | Conexiones ligeras |
| `end_plate` | Momento | FR | Marcos resistentes |
| `flange_plate` | Momento | FR | Marcos de gravedad |
| `extended_end_plate` | Momento | FR | Marcos sismicos |
| `reduced_beam_section` | Momento | FR | SMF sismico (RBS) |
| `bolted_flange_plate` | Momento | FR | Conexiones de campo |
| `welded_unreinforced` | Momento | FR | Pre-Northridge |
| `wuf_w` | Momento | FR | WUF-W sismico |

### Conexiones Sismicas Precalificadas (AISC 358)

- **SMF** (Special Moment Frame): Conexiones de alta ductilidad
- **IMF** (Intermediate Moment Frame): Ductilidad moderada
- **OMF** (Ordinary Moment Frame): Ductilidad limitada

### Elementos Generados

- Placas de conexion (shear tabs, end plates)
- Rigidizadores de columna (stiffeners)
- Placas de continuidad
- Placas de refuerzo (doubler plates)
- Soldaduras (filete, CJP, PJP)
- Tornillos de alta resistencia

## Estructura del Componente

```
E03-conexion-viga-columna/
├── README.md
├── config.yaml
├── src/
│   └── grasshopper/
│       ├── definitions/
│       │   └── E03_BeamColumnConnection.gh
│       └── scripts/
│           ├── connection_generator.py   # Generador principal
│           ├── plate_builder.py          # Constructor de placas
│           ├── weld_calculator.py        # Calculadora de soldaduras
│           ├── bolt_calculator.py        # Calculadora de tornillos
│           ├── connection_validator.py   # Validador AISC/AWS
│           └── cost_calculator.py        # Calculadora de costos
└── docs/
    ├── parameters.md
    └── examples.md
```

## Parametros Principales

### Perfiles

| Parametro | Tipo | Ejemplo | Descripcion |
|-----------|------|---------|-------------|
| `beam_profile` | str | W18x50 | Perfil de viga |
| `column_profile` | str | W14x90 | Perfil de columna |
| `beam_material` | enum | A992 | Material de viga |
| `column_material` | enum | A992 | Material de columna |

### Conexion

| Parametro | Tipo | Opciones | Default |
|-----------|------|----------|---------|
| `connection_type` | enum | ver tabla | shear_tab |
| `seismic_category` | enum | SMF, IMF, OMF, none | none |
| `connection_side` | enum | one_side, both_sides | one_side |
| `field_welded` | bool | true/false | true |

### Tornillos

| Parametro | Tipo | Opciones | Default |
|-----------|------|----------|---------|
| `bolt_diameter` | int | 20, 22, 24, 27, 30 | 22 |
| `bolt_grade` | enum | A325, A490 | A325 |
| `bolt_type` | enum | bearing, slip_critical | bearing |
| `hole_type` | enum | standard, oversize, slotted | standard |

### Soldaduras

| Parametro | Tipo | Opciones | Default |
|-----------|------|----------|---------|
| `weld_electrode` | enum | E70, E80 | E70 |
| `flange_weld` | enum | CJP, PJP, fillet | CJP |
| `web_weld` | enum | CJP, fillet | fillet |

## Normativas Aplicables

- **AISC 360**: Specification for Structural Steel Buildings
- **AISC 358**: Prequalified Connections for SMF and IMF
- **AISC 341**: Seismic Provisions for Structural Steel Buildings
- **AWS D1.1**: Structural Welding Code - Steel
- **RCDF NTC-Acero**: Normas Tecnicas Complementarias (Mexico)

## Uso Rapido

```python
# Grasshopper Python
from connection_generator import ConnectionGenerator
from connection_validator import ConnectionValidator

# Crear conexion
generator = ConnectionGenerator(
    connection_type='extended_end_plate',
    seismic_category='SMF'
)

connection = generator.generate(
    beam_profile='W21x62',
    column_profile='W14x132',
    beam_material='A992',
    bolt_diameter=25,
    bolt_grade='A490'
)

# Validar
validator = ConnectionValidator(code='AISC_360')
result = validator.validate(connection)
```

## Integracion BIM

### Parametros Compartidos

- `BIMAC_Connection_Type`: Tipologia de conexion
- `BIMAC_Connection_Capacity`: Capacidad (kN o kN-m)
- `BIMAC_Connection_Demand`: Demanda de diseno
- `BIMAC_Connection_DCR`: Demand/Capacity Ratio

### Clasificacion

- **Uniclass**: Ss_25_20_15 (Connection systems)
- **OmniClass**: 23-17 11 11 (Structural Connections)
- **IFC**: IfcFastener / IfcMechanicalFastener

## Autor

- **BIMAC** - BIM Advance Consulting
- **Version**: 1.0.0
- **Fecha**: 2025-12-27
- **Estado**: En desarrollo

## Licencia

Uso interno BIMAC. Consultar terminos de licenciamiento.
