"""
Módulo de Geometría - Core Library

Funciones para generación de superficies y panelización.

Clases:
    - BaseSurfaceGenerator: Clase base para generadores
    - OrganicGenerator: Superficies orgánicas NURBS
    - TensileGenerator: Membranas tensadas
    - GridshellGenerator: Mallas estructurales
    - FoldedGenerator: Placas plegadas

Funciones:
    - generate_surface: Genera superficie según tipo
    - panelize_surface: Subdivide en paneles
    - rationalize_panels: Racionaliza curvatura
"""

from .base import BaseSurfaceGenerator
from .organic import OrganicGenerator
from .tensile import TensileGenerator
from .panelizer import Panelizer, rationalize_panels

# Registro de generadores
GENERATORS = {
    "organic": OrganicGenerator,
    "tensile": TensileGenerator,
    # "gridshell": GridshellGenerator,
    # "folded": FoldedGenerator,
    # "shell": ShellGenerator,
    # "vault": VaultGenerator,
}


def generate_surface(config):
    """
    Genera una superficie según la configuración.

    Args:
        config (dict): Configuración del proyecto con:
            - type: Tipo de superficie
            - width, length, height: Dimensiones
            - Otros parámetros específicos del tipo

    Returns:
        Surface: Superficie generada

    Example:
        >>> config = {"type": "organic", "width": 15, "length": 26, "height": 8.5}
        >>> surface = generate_surface(config)
    """
    surface_type = config.get("type", "organic")

    if surface_type not in GENERATORS:
        raise ValueError(f"Tipo de superficie no soportado: {surface_type}")

    generator_class = GENERATORS[surface_type]
    generator = generator_class()

    return generator.generate(config)


def panelize_surface(surface, u_count, v_count, tolerance=5.0):
    """
    Subdivide una superficie en paneles.

    Args:
        surface: Superficie a panelizar
        u_count (int): Divisiones en U
        v_count (int): Divisiones en V
        tolerance (float): Tolerancia de planarización (mm)

    Returns:
        list: Lista de paneles (Breps)
    """
    panelizer = Panelizer(tolerance=tolerance)
    return panelizer.panelize(surface, u_count, v_count)
