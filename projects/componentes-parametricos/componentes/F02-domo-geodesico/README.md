# F02 - Domo Geodesico Parametrico

Sistema de generacion parametrica de domos geodesicos basados en subdivision icosaedrica.

## Descripcion

Componente Grasshopper para disenar domos geodesicos con multiples frecuencias de subdivision, tipos de estructura y sistemas de panelizacion.

## Tipos de Domo

### Por Geometria Base

| Tipo | Base | Vertices | Caras | Caracteristicas |
|------|------|----------|-------|-----------------|
| Icosaedro | 20 triangulos | 12 | 20 | Mas uniforme, estandar |
| Octaedro | 8 triangulos | 6 | 8 | Simétrico, menos piezas |
| Tetraedro | 4 triangulos | 4 | 4 | Simple, economico |

### Por Frecuencia (V)

| Frecuencia | Subdivisiones | Triangulos* | Barras* | Nodos* |
|------------|---------------|-------------|---------|--------|
| 1V | 1 | 20 | 30 | 12 |
| 2V | 2 | 80 | 120 | 42 |
| 3V | 3 | 180 | 270 | 92 |
| 4V | 4 | 320 | 480 | 162 |
| 5V | 5 | 500 | 750 | 252 |
| 6V | 6 | 720 | 1080 | 362 |

*Para esfera completa basada en icosaedro

### Por Truncamiento

| Tipo | Porcion | Angulo Base | Aplicacion |
|------|---------|-------------|------------|
| Full sphere | 100% | 180° | Esferas completas, planetarios |
| 5/8 sphere | 62.5% | 112.5° | Observatorios, invernaderos |
| 1/2 sphere | 50% | 90° | Domos estandar, viviendas |
| 3/8 sphere | 37.5% | 67.5° | Cubiertas bajas, patios |
| 1/4 sphere | 25% | 45° | Lucernarios, tragaluces |

## Capacidades

### Estructura
- Generacion de barras con perfiles tubulares
- Nodos tipo hub (esfericos o personalizados)
- Conexiones atornilladas o soldadas
- Anillo de tension perimetral

### Panelizacion
- Paneles triangulares simples
- Paneles hexagonales (Buckminster Fuller)
- Paneles mixtos tri-hex
- Vidrio, policarbonato, ETFE, metal

### Analisis
- Calculo de areas y volumenes
- Estimacion de peso estructural
- Factor de forma aerodinamico
- Cargas de viento y nieve

## Estructura de Archivos

```
F02-domo-geodesico/
├── README.md
├── config.yaml
├── src/
│   └── grasshopper/
│       ├── F02_Domo_Geodesico.gh
│       └── scripts/
│           ├── geodesic_generator.py
│           ├── node_builder.py
│           ├── strut_builder.py
│           ├── panel_builder.py
│           └── dome_analyzer.py
└── docs/
    ├── parameters.md
    └── examples.md
```

## Parametros Principales

| Parametro | Rango | Default | Descripcion |
|-----------|-------|---------|-------------|
| radius | 3-50 m | 10 m | Radio del domo |
| frequency | 1-8 | 3 | Frecuencia de subdivision |
| truncation | 0.25-1.0 | 0.5 | Porcion de esfera |
| base_type | icosahedron/octahedron | icosahedron | Poliedro base |
| strut_profile | ver tabla | D60x3 | Perfil de barras |
| panel_type | triangle/hexagon/mixed | triangle | Tipo de panel |

## Normativas

- ASCE 7 - Cargas de viento en estructuras
- AISC 360 - Diseno de acero estructural
- AAMA TIR-A7 - Vidrio estructural
- EN 13830 - Muros cortina

## Autor

BIMAC - BIM Advance Consulting
Version 1.0.0
