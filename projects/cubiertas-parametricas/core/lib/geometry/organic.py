"""
Organic Surface Generator

Generador de superficies orgánicas tipo NURBS para cubiertas de museos,
centros culturales y espacios con formas fluidas.
"""

from .base import BaseSurfaceGenerator

try:
    import Rhino.Geometry as rg
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False


class OrganicGenerator(BaseSurfaceGenerator):
    """
    Generador de superficies orgánicas mediante Loft de curvas NURBS.

    La superficie se genera interpolando entre curvas guía que definen
    el perfil de la cubierta. Ideal para museos y espacios culturales.

    Attributes:
        name: "organic"
        description: Superficies NURBS orgánicas

    Example:
        >>> generator = OrganicGenerator()
        >>> config = {
        ...     "width": 15.0,
        ...     "length": 26.0,
        ...     "height": 8.5,
        ...     "tension": 0.65
        ... }
        >>> surface = generator.generate(config)
    """

    name = "organic"
    description = "Superficies NURBS orgánicas para espacios culturales"

    default_params = {
        "width": 15.0,       # metros
        "length": 26.0,      # metros
        "height": 8.5,       # metros
        "tension": 0.65,     # factor de curvatura (0-1)
        "curve_degree": 3,   # grado de curvas
        "rebuild_count": 50, # puntos de reconstrucción
        "asymmetry": 0.0,    # factor de asimetría (-1 a 1)
    }

    def generate(self, config):
        """
        Genera una superficie orgánica mediante Loft.

        Args:
            config (dict): Configuración con:
                - width: Ancho (m)
                - length: Largo (m)
                - height: Altura máxima (m)
                - tension: Factor de curvatura (0-1)
                - curve_degree: Grado de interpolación
                - asymmetry: Factor de asimetría

        Returns:
            Surface: Superficie NURBS generada

        Raises:
            RuntimeError: Si Rhino no está disponible
        """
        if not RHINO_AVAILABLE:
            raise RuntimeError("Rhino.Geometry no disponible")

        # Validar y aplicar configuración
        params = self.validate_config(config)

        # Convertir metros a milímetros (unidades de Rhino)
        width = params["width"] * 1000
        length = params["length"] * 1000
        height = params["height"] * 1000
        tension = params["tension"]
        degree = params["curve_degree"]
        asymmetry = params.get("asymmetry", 0.0)

        # Generar curvas guía
        curves = self._create_guide_curves(
            width, length, height, tension, degree, asymmetry
        )

        self.guide_curves = curves

        # Crear superficie por Loft
        surface = self._create_loft_surface(curves, params["rebuild_count"])

        self.surface = surface
        return surface

    def _create_guide_curves(self, width, length, height, tension, degree, asymmetry):
        """
        Crea las curvas guía para el Loft.

        Genera un conjunto de curvas transversales que definen
        el perfil de la cubierta a lo largo de su longitud.

        Args:
            width: Ancho en mm
            length: Largo en mm
            height: Altura máxima en mm
            tension: Factor de tensión (0-1)
            degree: Grado de las curvas
            asymmetry: Factor de asimetría

        Returns:
            list: Lista de curvas NurbsCurve
        """
        curves = []
        num_sections = 5  # Número de secciones transversales

        for i in range(num_sections):
            # Posición Y de la sección
            t = i / (num_sections - 1)
            y = t * length

            # Altura de la sección (perfil parabólico)
            section_height = height * (1 - (2 * t - 1) ** 2) * tension

            # Puntos de control para esta sección
            points = self._create_section_points(
                width, y, section_height, asymmetry
            )

            # Crear curva interpolada
            curve = rg.Curve.CreateInterpolatedCurve(
                points,
                degree,
                rg.CurveKnotStyle.Chord
            )

            if curve:
                curves.append(curve)

        return curves

    def _create_section_points(self, width, y, height, asymmetry):
        """
        Crea los puntos de control para una sección transversal.

        Args:
            width: Ancho de la sección
            y: Posición Y de la sección
            height: Altura máxima de la sección
            asymmetry: Factor de asimetría

        Returns:
            list: Lista de Point3d
        """
        points = []

        # Número de puntos por sección
        num_points = 5

        for j in range(num_points):
            t = j / (num_points - 1)
            x = t * width

            # Perfil de altura (parábola modificada por asimetría)
            normalized_x = 2 * t - 1  # -1 a 1
            z = height * (1 - normalized_x ** 2)

            # Aplicar asimetría
            z *= (1 + asymmetry * normalized_x * 0.3)

            points.append(rg.Point3d(x, y, z))

        return points

    def _create_loft_surface(self, curves, rebuild_count):
        """
        Crea la superficie mediante Loft de las curvas.

        Args:
            curves: Lista de curvas guía
            rebuild_count: Número de puntos para reconstrucción

        Returns:
            Surface: Superficie resultante
        """
        if not curves:
            return None

        # Crear Loft
        loft_result = rg.Brep.CreateFromLoft(
            curves,
            rg.Point3d.Unset,
            rg.Point3d.Unset,
            rg.LoftType.Normal,
            False
        )

        if not loft_result or len(loft_result) == 0:
            return None

        brep = loft_result[0]

        if brep.Faces.Count == 0:
            return None

        surface = brep.Faces[0].ToNurbsSurface()

        # Reconstruir para suavizado
        if rebuild_count > 0:
            surface = surface.Rebuild(
                rebuild_count,
                rebuild_count,
                3, 3
            )

        return surface

    def validate_config(self, config):
        """
        Valida configuración específica para superficies orgánicas.

        Args:
            config: Configuración a validar

        Returns:
            dict: Configuración validada
        """
        validated = super().validate_config(config)

        # Validaciones específicas
        if not 0 <= validated.get("tension", 0.65) <= 1:
            raise ValueError("Tension debe estar entre 0 y 1")

        if not -1 <= validated.get("asymmetry", 0) <= 1:
            raise ValueError("Asymmetry debe estar entre -1 y 1")

        if validated.get("curve_degree", 3) < 1:
            raise ValueError("Curve degree debe ser al menos 1")

        return validated


# Función de conveniencia para uso en Grasshopper
def create_organic_surface(width, length, height, tension=0.65, asymmetry=0.0):
    """
    Función de conveniencia para crear superficie orgánica.

    Args:
        width: Ancho en metros
        length: Largo en metros
        height: Altura en metros
        tension: Factor de tensión (0-1)
        asymmetry: Factor de asimetría (-1 a 1)

    Returns:
        Surface: Superficie generada
    """
    generator = OrganicGenerator()
    config = {
        "width": width,
        "length": length,
        "height": height,
        "tension": tension,
        "asymmetry": asymmetry,
    }
    return generator.generate(config)
