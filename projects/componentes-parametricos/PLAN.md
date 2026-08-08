# Plan de Componentes Parametricos Compuestos - BIMAC

## Vision General

Crear una biblioteca de **componentes BIM parametricos compuestos y complejos** que sirvan como ejemplos de referencia y plantillas reutilizables para proyectos de arquitectura, estructura y MEP.

---

## Categorias de Componentes

### 1. FACHADAS Y ENVOLVENTES

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| F01 | **Muro Cortina Parametrico** | Alta | GH + RiR | Sistema de muro cortina con mullions variables, paneles mixtos (vidrio/solido), y adaptacion a curvas |
| F02 | **Fachada Ventilada** | Media | GH + Revit | Sistema multicapa: estructura, aislamiento, camara de aire, revestimiento modular |
| F03 | **Brise Soleil Adaptativo** | Alta | GH + Ladybug | Parasoles que responden a analisis solar, angulos variables por orientacion |
| F04 | **Panel Sandwich Curvo** | Media | GH + RiR | Paneles compuestos con nucleo aislante, adaptables a superficies curvas |
| F05 | **Doble Piel de Vidrio** | Alta | GH + RiR | Sistema de fachada doble con cavidad ventilada y control climatico |

### 2. SISTEMAS ESTRUCTURALES

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| E01 | **Nudo Espacial 3D** | Alta | GH + Karamba | Conexion multiaxial para estructuras espaciales (hasta 12 barras) |
| E02 | **Cercha Parametrica** | Media | GH + RiR | Armaduras con geometria variable (Warren, Pratt, Howe, etc.) |
| E03 | **Columna Compuesta** | Media | Revit API | Columna mixta acero-concreto con refuerzo parametrico |
| E04 | **Losa Nervada Bidireccional** | Alta | Dynamo + Revit | Sistema waffle slab con nervaduras optimizadas |
| E05 | **Conexion Viga-Columna** | Alta | GH + Tekla | Conexion atornillada/soldada con placas y rigidizadores |

### 3. ESCALERAS Y CIRCULACIONES

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| C01 | **Escalera Helicoidal** | Alta | GH + RiR | Escalera de caracol con peldanos, barandal y estructura central |
| C02 | **Rampa Curva Accesible** | Media | Dynamo + Revit | Rampa con pendientes normativas, descansos automaticos |
| C03 | **Escalera Flotante** | Media | GH + RiR | Peldanos empotrados con calculo estructural integrado |
| C04 | **Pasarela Tensada** | Alta | GH + Karamba | Puente peatonal con cables de suspension |

### 4. INSTALACIONES MEP

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| M01 | **Rack de Tuberias** | Media | Dynamo + Revit | Sistema de soporteria para multiples tuberias con espaciado automatico |
| M02 | **Plenum HVAC** | Alta | GH + RiR | Distribucion de aire con difusores parametricos |
| M03 | **Cuarto de Maquinas** | Alta | Dynamo + Revit | Layout optimizado de equipos con clearances |
| M04 | **Sistema de Rociadores** | Media | Dynamo + Revit | Red de sprinklers con calculo de cobertura |
| M05 | **Bandeja de Cables** | Media | Dynamo + Revit | Ruteo automatico con cruces y derivaciones |

### 5. MOBILIARIO Y EQUIPAMIENTO

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| Q01 | **Sistema Modular de Oficina** | Media | GH + RiR | Workstations configurables con mamparas |
| Q02 | **Graderia Retractil** | Alta | GH + RiR | Tribunas telescopicas con filas variables |
| Q03 | **Estanteria Industrial** | Media | Dynamo + Revit | Racks de almacen con carga parametrica |
| Q04 | **Cocina Industrial** | Alta | Dynamo + Revit | Layout de equipos con zonas y flujos |

### 6. ELEMENTOS ESPECIALES

| ID | Componente | Complejidad | Herramientas | Descripcion |
|----|------------|-------------|--------------|-------------|
| X01 | **Domo Geodesico** | Alta | GH + RiR | Estructura geodesica con paneles triangulares |
| X02 | **Piscina con Desborde** | Media | Revit API | Vaso + canaleta perimetral + cuarto de maquinas |
| X03 | **Jardinera Modular** | Baja | Dynamo + Revit | Sistema de macetas con drenaje y riego |
| X04 | **Pergola Parametrica** | Media | GH + RiR | Estructura con lamas orientables |
| X05 | **Muro Verde** | Media | GH + RiR | Sistema de paneles vegetales con riego integrado |

---

## Prioridades de Desarrollo

### Fase 1: Componentes Fundamentales (Semana 1-2)
1. **F01 - Muro Cortina Parametrico** - Alta demanda en proyectos comerciales
2. **E02 - Cercha Parametrica** - Base para cubiertas
3. **C01 - Escalera Helicoidal** - Complejidad geometrica alta
4. **M01 - Rack de Tuberias** - Utilidad en coordinacion MEP

### Fase 2: Componentes Intermedios (Semana 3-4)
5. **F03 - Brise Soleil Adaptativo** - Integracion con analisis ambiental
6. **E01 - Nudo Espacial 3D** - Complemento para cubiertas
7. **C02 - Rampa Curva Accesible** - Cumplimiento normativo
8. **X01 - Domo Geodesico** - Geometria compleja

### Fase 3: Componentes Avanzados (Semana 5-6)
9. **F05 - Doble Piel de Vidrio** - Sistema de alto rendimiento
10. **E04 - Losa Nervada Bidireccional** - Optimizacion estructural
11. **M02 - Plenum HVAC** - Coordinacion espacial
12. **Q02 - Graderia Retractil** - Mecanismo complejo

---

## Estructura por Componente

```
componentes-parametricos/
├── core/                          # Libreria compartida
│   ├── lib/
│   │   ├── geometry/              # Utilidades geometricas
│   │   ├── connections/           # Logica de conexiones
│   │   ├── materials/             # Base de datos de materiales
│   │   └── validation/            # Validadores normativos
│   ├── grasshopper/
│   │   └── clusters/              # Clusters reutilizables
│   └── revit/
│       └── families/              # Familias base
│
├── config/
│   ├── materials.yaml             # Catalogo de materiales
│   ├── standards.yaml             # Normas aplicables
│   └── costs.yaml                 # Costos unitarios
│
├── componentes/                   # Componentes individuales
│   ├── F01-muro-cortina/
│   │   ├── config.yaml            # Configuracion
│   │   ├── README.md              # Documentacion
│   │   ├── src/
│   │   │   ├── grasshopper/
│   │   │   │   ├── main.gh        # Definicion principal
│   │   │   │   └── scripts/       # Python scripts
│   │   │   └── revit/
│   │   │       ├── families/      # Familias especificas
│   │   │       └── scripts/       # PyRevit/Dynamo
│   │   ├── docs/
│   │   │   ├── parameters.md      # Tabla de parametros
│   │   │   └── examples.md        # Casos de uso
│   │   └── exports/
│   │       ├── ifc/
│   │       └── images/
│   │
│   ├── E01-nudo-espacial/
│   ├── C01-escalera-helicoidal/
│   └── ...
│
├── templates/                     # Plantillas base
│   └── component-template/
│
├── scripts/
│   ├── new_component.py           # Generador de componentes
│   └── validate_component.py      # Validador
│
└── docs/
    ├── architecture.md
    ├── getting-started.md
    └── component-guide.md
```

---

## Criterios de Diseno por Componente

### Cada componente debe incluir:

1. **Parametros de Entrada**
   - Dimensiones principales (ancho, alto, profundidad)
   - Materiales (desde catalogo)
   - Opciones de configuracion
   - Restricciones normativas

2. **Geometria**
   - Modelo 3D parametrico
   - Niveles de detalle (LOD 200, 300, 350)
   - Variantes tipologicas

3. **Conexiones**
   - Puntos de anclaje
   - Interfaces con otros sistemas
   - Tolerancias constructivas

4. **Informacion BIM**
   - Parametros compartidos BIMAC
   - Clasificacion (Uniclass, OmniClass)
   - Propiedades IFC

5. **Validaciones**
   - Restricciones geometricas
   - Cumplimiento normativo
   - Fabricabilidad

6. **Documentacion**
   - Tabla de parametros
   - Ejemplos de uso
   - Casos de aplicacion

---

## Siguiente Paso

Seleccionar los primeros 4 componentes de la Fase 1 para desarrollo inmediato:

1. [ ] F01 - Muro Cortina Parametrico
2. [ ] E02 - Cercha Parametrica
3. [ ] C01 - Escalera Helicoidal
4. [ ] M01 - Rack de Tuberias

Confirmar prioridades antes de proceder con la implementacion.

---

*Plan creado: 2025-12-27*
*BIMAC - Componentes Parametricos v1.0*
