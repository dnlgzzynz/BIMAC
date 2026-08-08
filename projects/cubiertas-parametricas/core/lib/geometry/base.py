"""
Base Surface Generator

Clase base abstracta para todos los generadores de superficies.
"""

from abc import ABC, abstractmethod


class BaseSurfaceGenerator(ABC):
    """
    Clase base para generadores de superficies.

    Todos los generadores específicos (organic, tensile, etc.)
    deben heredar de esta clase e implementar el método generate().

    Attributes:
        name (str): Nombre del tipo de generador
        description (str): Descripción del tipo
        default_params (dict): Parámetros por defecto
    """

    name = "base"
    description = "Generador base abstracto"

    default_params = {
        "width": 15.0,       # metros
        "length": 26.0,      # metros
        "height": 8.5,       # metros
        "tension": 0.65,     # factor de curvatura
        "rebuild_count": 50, # puntos de reconstrucción
    }

    def __init__(self):
        """Inicializa el generador."""
        self.params = self.default_params.copy()
        self.surface = None
        self.guide_curves = []

    @abstractmethod
    def generate(self, config):
        """
        Genera la superficie según la configuración.

        Args:
            config (dict): Diccionario de configuración

        Returns:
            Surface: Superficie generada

        Raises:
            NotImplementedError: Si no se implementa en subclase
        """
        raise NotImplementedError("Subclases deben implementar generate()")

    def validate_config(self, config):
        """
        Valida la configuración de entrada.

        Args:
            config (dict): Configuración a validar

        Returns:
            dict: Configuración validada con defaults aplicados

        Raises:
            ValueError: Si la configuración es inválida
        """
        validated = self.default_params.copy()
        validated.update(config)

        # Validaciones básicas
        if validated["width"] <= 0:
            raise ValueError("El ancho debe ser positivo")
        if validated["length"] <= 0:
            raise ValueError("El largo debe ser positivo")
        if validated["height"] <= 0:
            raise ValueError("La altura debe ser positiva")

        return validated

    def get_bounding_box(self):
        """
        Obtiene el bounding box de la superficie generada.

        Returns:
            BoundingBox o None
        """
        if self.surface is None:
            return None

        try:
            return self.surface.GetBoundingBox(True)
        except:
            return None

    def get_area(self):
        """
        Calcula el área de la superficie en m².

        Returns:
            float: Área en metros cuadrados
        """
        if self.surface is None:
            return 0.0

        try:
            import Rhino.Geometry as rg
            props = rg.AreaMassProperties.Compute(self.surface)
            if props:
                # Convertir de mm² a m²
                return props.Area / 1000000.0
        except:
            pass

        return 0.0

    def get_guide_curves(self):
        """
        Retorna las curvas guía usadas para generar la superficie.

        Returns:
            list: Lista de curvas
        """
        return self.guide_curves

    def to_brep(self):
        """
        Convierte la superficie a Brep.

        Returns:
            Brep o None
        """
        if self.surface is None:
            return None

        try:
            return self.surface.ToBrep()
        except:
            return None

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
