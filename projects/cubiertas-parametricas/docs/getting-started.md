# Guía de Inicio Rápido - Cubiertas Paramétricas BIMAC

Esta guía te llevará paso a paso para crear tu primer proyecto de cubierta paramétrica.

---

## Requisitos Previos

### Software Requerido

| Software | Versión | Notas |
|----------|---------|-------|
| Rhino | 7 o 8 | Con Grasshopper incluido |
| Revit | 2024+ | Para exportación BIM |
| Rhino.inside.Revit | Última | [Descargar](https://www.rhino3d.com/inside/revit/) |
| Python | 3.9+ | Para scripts de gestión |
| Node.js | 18+ | Solo si usas n8n |

### Plugins de Grasshopper

- **Lunchbox** - Panelización
- **Pufferfish** - Deformación de superficies
- **Weaverbird** - Subdivisión de mallas
- **Kangaroo 2** - Optimización física (para tensile)
- **Karamba3D** *(opcional)* - Análisis estructural

### Dependencias Python

```bash
pip install pyyaml
```

---

## Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/dnlgzzynz/BIMAC.git
cd BIMAC/projects/cubiertas-parametricas
```

---

## Paso 2: Crear un Nuevo Proyecto

### Usando el Generador de Proyectos

```bash
# Crear proyecto de cubierta orgánica
python scripts/new_project.py --name "mi-museo" --type "organic" --client "Cliente ABC"

# Crear proyecto de tensoestructura
python scripts/new_project.py --name "estadio-municipal" --type "tensile" --budget 1500000

# Ver todos los proyectos existentes
python scripts/new_project.py --list
```

### Tipos de Cubierta Disponibles

| Tipo | Descripción | Caso de Uso |
|------|-------------|-------------|
| `organic` | Superficies NURBS orgánicas | Museos, centros culturales |
| `tensile` | Membranas tensadas | Estadios, plazas |
| `gridshell` | Mallas estructurales | Pabellones, invernaderos |
| `folded` | Placas plegadas | Naves industriales |
| `shell` | Cascarones delgados | Auditorios |
| `vault` | Bóvedas paramétricas | Espacios religiosos |

---

## Paso 3: Configurar el Proyecto

Edita el archivo `config.yaml` en tu proyecto:

```yaml
# proyectos/mi-museo/config.yaml

project:
  name: "Mi Museo - Cubierta Principal"
  code: "ORG-MUSEO-2512"
  client: "Cliente ABC"
  created: "2025-12-27"
  status: "En diseño"

geometry:
  type: "organic"              # Tipo de cubierta
  width: 15.0                  # metros
  length: 26.0                 # metros
  max_height: 8.5              # metros
  tension: 0.65                # Factor de curvatura (0-1)
  asymmetry: 0.0               # Asimetría (-1 a 1)

constraints:
  max_span: 15.0               # Luz libre máxima (m)
  min_slope: 2.0               # Pendiente mínima (%)
  max_deflection: 250          # L/X

panels:
  module_width: 2.0            # metros
  module_height: 1.5           # metros
  u_count: 13                  # Divisiones en U
  v_count: 10                  # Divisiones en V
  material: "polycarbonate_16mm"
  tolerance: 5.0               # mm de planarización

budget:
  total: 280000                # MXN
  currency: "MXN"
  target_flat_percent: 78      # % objetivo de paneles planos

export:
  revit_family: "Cubierta_Panel_Adaptive"
  ifc_version: "IFC4"
  units: "millimeters"
```

---

## Paso 4: Abrir en Grasshopper

### Cargar el Loader Principal

1. Abre **Rhino 7/8**
2. Inicia **Grasshopper** (comando `Grasshopper`)
3. Abre `core/grasshopper/components/main_loader.gh`

### Seleccionar Proyecto

1. En el panel de configuración, selecciona tu proyecto del dropdown
2. La configuración se cargará automáticamente
3. Ajusta los sliders según necesites

### Verificar Validaciones

El sistema valida en tiempo real:
- ✅ Luz libre máxima
- ✅ Pendiente mínima para drenaje
- ✅ Curvatura de paneles
- ✅ Presupuesto

---

## Paso 5: Analizar y Optimizar

### Ver Análisis de Curvatura

El panel de análisis muestra:
- Curvatura Gaussiana (K)
- Clasificación de paneles (plano/simple/doble)
- Porcentaje de cada tipo

### Optimizar para Presupuesto

1. Ajusta el slider de **tensión** para reducir curvatura
2. Ajusta las **divisiones U/V** para optimizar paneles
3. Observa el cálculo de costos en tiempo real

### Verificar Restricciones Estructurales

El validador muestra:
- Estado de cada verificación
- Puntos críticos en la geometría
- Advertencias y recomendaciones

---

## Paso 6: Calcular Costos

El sistema calcula automáticamente:

```
┌──────────────────────────────────────────────────────────────┐
│                    DESGLOSE DE COSTOS                         │
├──────────────────────────────────────────────────────────────┤
│ Paneles planos         ($450/m²)     →  $xxx,xxx             │
│ Curvatura simple       ($680/m²)     →  $xxx,xxx             │
│ Doble curvatura        ($1,250/m²)   →  $xxx,xxx             │
├──────────────────────────────────────────────────────────────┤
│ Subtotal paneles                      →  $xxx,xxx             │
│ Estructura (25%)                      →  $xxx,xxx             │
│ Instalación (15%)                     →  $xxx,xxx             │
│ Contingencia (10%)                    →  $xxx,xxx             │
├──────────────────────────────────────────────────────────────┤
│ TOTAL                                 →  $xxx,xxx MXN         │
└──────────────────────────────────────────────────────────────┘
```

### Descuentos por Volumen

| Área Total | Descuento |
|------------|-----------|
| > 500 m² | 5% |
| > 1,000 m² | 10% |
| > 2,000 m² | 15% |

---

## Paso 7: Exportar a Revit

### Con Rhino.inside.Revit

1. Abre tu proyecto de **Revit**
2. En la pestaña **Rhinoceros**, haz clic en **Grasshopper Player**
3. Selecciona `core/grasshopper/components/revit_exporter.gh`
4. Ejecuta la exportación

### Elementos Exportados

- Paneles como familias adaptativas
- Schedule de paneles con curvatura y costos
- Parámetros BIM por panel

### Verificar en Revit

1. Abre la vista 3D
2. Verifica que los paneles estén correctamente colocados
3. Abre el schedule `BIMAC_Cubierta_Paneles`
4. Confirma los datos de curvatura y costos

---

## Paso 8: Generar Reportes

### Exportar a Excel

```bash
# Desde Grasshopper (activa el componente de exportación)
# O usando el script Python:
python core/lib/export/excel_report.py --project "mi-museo"
```

### Webhook a n8n (Opcional)

Si tienes configurado n8n:

```yaml
# En config.yaml
notifications:
  enabled: true
  webhook_url: "http://localhost:5678/webhook/cubierta-cost-update"
  channels:
    - "slack"
    - "airtable"
```

---

## Estructura de Archivos del Proyecto

Después de crear tu proyecto:

```
proyectos/mi-museo/
├── config.yaml              # Configuración del proyecto
├── README.md                # Documentación del proyecto
├── src/
│   ├── grasshopper/
│   │   └── main.gh          # (copiar de template si necesario)
│   └── overrides/           # Customizaciones específicas
│       └── custom_scripts/
├── docs/
│   └── notes.md             # Notas del proyecto
└── exports/
    ├── ifc/                 # Archivos IFC exportados
    ├── excel/               # Reportes Excel
    └── images/              # Capturas y renders
```

---

## Comandos Útiles

```bash
# Crear nuevo proyecto
python scripts/new_project.py --name "nombre" --type "organic"

# Listar proyectos
python scripts/new_project.py --list

# Validar configuración
python scripts/validate_project.py --project "mi-museo"

# Sincronizar core actualizado a todos los proyectos
python scripts/sync_core.py --all

# Generar reporte de todos los proyectos
python scripts/report.py --all --format excel
```

---

## Solución de Problemas

### "PyYAML no está instalado"

```bash
pip install pyyaml
```

### "No se encuentra el proyecto"

Verifica que el proyecto exista en `proyectos/`:
```bash
python scripts/new_project.py --list
```

### "Error de curvatura al panelizar"

- Aumenta el valor de `tolerance` en `config.yaml`
- Reduce las divisiones U/V para paneles más grandes
- Ajusta el factor de tensión

### "Luz libre excedida"

- Revisa la geometría - puede requerir soportes adicionales
- Ajusta `max_span` en `constraints` si es estructuralmente viable
- Considera dividir la cubierta en secciones

### "Costos exceden presupuesto"

- Aumenta el porcentaje objetivo de paneles planos
- Considera un material más económico
- Reduce el área total de cubierta
- Verifica si aplica descuento por volumen

---

## Próximos Pasos

1. **Explorar ejemplos**: Revisa `proyectos/museo-cubierta-organica/` como referencia
2. **Personalizar materiales**: Edita `config/costs.yaml`
3. **Crear nuevos tipos**: Sigue la guía en `docs/architecture.md`
4. **Automatizar con n8n**: Configura webhooks para notificaciones
5. **Documentar**: Mantén `notes.md` actualizado con decisiones del proyecto

---

## Soporte

- **Documentación técnica**: `docs/architecture.md`
- **API Reference**: `docs/api-reference.md`
- **Email**: dev@bimac.io
- **Web**: [bimac.io](https://www.bimac.io)

---

*Guía creada para BIMAC - Cubiertas Paramétricas v1.0*
