"""
Módulo de Análisis - Core Library

Funciones para análisis de curvatura, validación estructural
y clasificación de paneles.

Clases:
    - CurvatureAnalyzer: Análisis de curvatura gaussiana
    - StructuralValidator: Validación de restricciones
    - PanelClassifier: Clasificación por tipo

Funciones:
    - analyze_curvature: Analiza curvatura de paneles
    - validate_structure: Valida restricciones estructurales
    - classify_panels: Clasifica paneles por curvatura
"""

from .curvature import CurvatureAnalyzer, analyze_curvature, classify_panels
from .structural import StructuralValidator, validate_structure

__all__ = [
    'CurvatureAnalyzer',
    'StructuralValidator',
    'analyze_curvature',
    'validate_structure',
    'classify_panels',
]
