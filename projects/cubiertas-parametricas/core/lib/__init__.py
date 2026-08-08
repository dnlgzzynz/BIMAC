"""
BIMAC Cubiertas Paramétricas - Core Library

Librería compartida para diseño y análisis de cubiertas paramétricas.

Módulos:
    - geometry: Generación de superficies y panelización
    - analysis: Análisis de curvatura y validación estructural
    - costs: Cálculo de costos y presupuestos
    - export: Exportación a Revit, IFC, Excel
    - utils: Utilidades generales

Uso:
    from core.lib import geometry, analysis, costs

    # Generar superficie
    surface = geometry.generate_surface(config)

    # Analizar
    panels = analysis.panelize(surface, config)
    curvature = analysis.classify_panels(panels)

    # Calcular costos
    budget = costs.calculate(panels, curvature, config)
"""

__version__ = "1.0.0"
__author__ = "BIMAC"

# Imports públicos
from . import geometry
from . import analysis
from . import costs
from . import export
from . import utils

# Constantes globales
MM_TO_FEET = 1.0 / 304.8
FEET_TO_MM = 304.8
M_TO_MM = 1000.0
MM_TO_M = 0.001

# Tipos de cubierta soportados
SURFACE_TYPES = [
    "organic",      # Superficies NURBS orgánicas
    "tensile",      # Membranas tensadas
    "gridshell",    # Mallas estructurales
    "folded",       # Placas plegadas
    "shell",        # Cascarones delgados
    "vault",        # Bóvedas paramétricas
]

# Tipos de panel
PANEL_TYPES = [
    "flat",           # Plano
    "single_curve",   # Curvatura simple
    "double_curve",   # Doble curvatura
]
