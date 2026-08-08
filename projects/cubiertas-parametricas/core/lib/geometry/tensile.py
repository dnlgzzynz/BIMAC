"""
Tensile Surface Generator

Generador de superficies tensadas para estadios, plazas y cubiertas
de grandes luces. Utiliza simulación de form-finding básica.
"""

from .base import BaseSurfaceGenerator

try:
    import Rhino.Geometry as rg
    import math
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False


class TensileGenerator(BaseSurfaceGenerator):
    """
    Generador de superficies tensadas (membranas).

    Crea superficies con forma anticlástica típica de tensoestructuras,
    con puntos altos y bajos que definen la forma tensada.

    Tipos de formas:
        - saddle: Silla de montar (paraboloide hiperbólico)
        - cone: Cónica con punta alta
        - arch: Arco tensado
        - wave: Ondulada

    Example:
        >>> generator = TensileGenerator()
        >>> config = {
        ...     "width": 45.0,
        ...     "length": 60.0,
        ...     "height": 18.0,
        ...     "form_type": "saddle",
        ...     "high_points": 4,
        ...     "low_points": 4
        ... }
        >>> surface = generator.generate(config)
    """

    name = "tensile"
    description = "Superficies tensadas para grandes luces"

    default_params = {
        "width": 45.0,           # metros
        "length": 60.0,          # metros
        "height": 18.0,          # altura máxima (metros)
        "sag": 3.0,              # flecha de catenaria (metros)
        "form_type": "saddle",   # saddle | cone | arch | wave
        "high_points": 4,        # número de puntos altos
        "low_points": 4,         # número de puntos bajos
        "pretension": 0.5,       # factor de pretensión (0-1)
        "mesh_density": 20,      # densidad de malla para simulación
    }

    def generate(self, config):
        """
        Genera una superficie tensada.

        Args:
            config (dict): Configuración con parámetros de tensoestructura

        Returns:
            Surface: Superficie tensada generada
        """
        if not RHINO_AVAILABLE:
            raise RuntimeError("Rhino.Geometry no disponible")

        params = self.validate_config(config)

        # Convertir a mm
        width = params["width"] * 1000
        length = params["length"] * 1000
        height = params["height"] * 1000
        sag = params["sag"] * 1000

        form_type = params["form_type"]

        # Generar según tipo de forma
        if form_type == "saddle":
            surface = self._create_saddle(width, length, height, sag, params)
        elif form_type == "cone":
            surface = self._create_cone(width, length, height, params)
        elif form_type == "arch":
            surface = self._create_arch(width, length, height, sag, params)
        elif form_type == "wave":
            surface = self._create_wave(width, length, height, sag, params)
        else:
            surface = self._create_saddle(width, length, height, sag, params)

        self.surface = surface
        return surface

    def _create_saddle(self, width, length, height, sag, params):
        """
        Crea una superficie tipo silla de montar (paraboloide hiperbólico).

        La forma característica de las tensoestructuras con puntos
        altos en las esquinas diagonales y bajos en las otras.
        """
        density = params["mesh_density"]

        # Crear grid de puntos
        points = []

        for i in range(density + 1):
            row = []
            u = i / density  # 0 a 1

            for j in range(density + 1):
                v = j / density  # 0 a 1

                x = u * width
                y = v * length

                # Forma de silla: z = k * (x² - y²)
                # Normalizado al centro
                nx = 2 * u - 1  # -1 a 1
                ny = 2 * v - 1  # -1 a 1

                # Paraboloide hiperbólico
                z_saddle = (nx ** 2 - ny ** 2)

                # Escalar y desplazar
                z = height / 2 + (height / 2) * z_saddle

                # Agregar catenaria en bordes
                edge_factor = self._edge_catenary(u, v, sag / height)
                z -= edge_factor * sag

                row.append(rg.Point3d(x, y, max(0, z)))

            points.append(row)

        # Crear superficie desde grid de puntos
        surface = self._create_surface_from_grid(points, 3, 3)

        return surface

    def _create_cone(self, width, length, height, params):
        """
        Crea una superficie cónica con punto alto central.

        Típica de cubiertas con mástil central.
        """
        density = params["mesh_density"]
        center_x = width / 2
        center_y = length / 2

        points = []

        for i in range(density + 1):
            row = []
            u = i / density

            for j in range(density + 1):
                v = j / density

                x = u * width
                y = v * length

                # Distancia al centro normalizada
                dx = (x - center_x) / (width / 2)
                dy = (y - center_y) / (length / 2)
                dist = math.sqrt(dx ** 2 + dy ** 2)

                # Forma cónica invertida
                z = height * (1 - min(dist, 1) ** 0.8)

                row.append(rg.Point3d(x, y, max(0, z)))

            points.append(row)

        return self._create_surface_from_grid(points, 3, 3)

    def _create_arch(self, width, length, height, sag, params):
        """
        Crea una superficie de arco tensado.

        Arco parabólico en una dirección con catenaria en la otra.
        """
        density = params["mesh_density"]

        points = []

        for i in range(density + 1):
            row = []
            u = i / density

            for j in range(density + 1):
                v = j / density

                x = u * width
                y = v * length

                # Arco parabólico en Y
                arch = 1 - (2 * v - 1) ** 2

                # Catenaria en X
                catenary = math.cosh((2 * u - 1) * 1.5) - 1

                z = height * arch - sag * catenary / 2

                row.append(rg.Point3d(x, y, max(0, z)))

            points.append(row)

        return self._create_surface_from_grid(points, 3, 3)

    def _create_wave(self, width, length, height, sag, params):
        """
        Crea una superficie ondulada.

        Múltiples ondas sinusoidales para cubiertas expresivas.
        """
        density = params["mesh_density"]
        waves = params.get("wave_count", 3)

        points = []

        for i in range(density + 1):
            row = []
            u = i / density

            for j in range(density + 1):
                v = j / density

                x = u * width
                y = v * length

                # Ondas sinusoidales
                wave_u = math.sin(u * math.pi * waves) * 0.5 + 0.5
                wave_v = math.cos(v * math.pi * 2) * 0.3 + 0.7

                z = height * wave_u * wave_v

                # Atenuar en bordes
                edge_u = 4 * u * (1 - u)
                edge_v = 4 * v * (1 - v)
                z *= edge_u * edge_v

                row.append(rg.Point3d(x, y, z))

            points.append(row)

        return self._create_surface_from_grid(points, 3, 3)

    def _edge_catenary(self, u, v, factor):
        """
        Calcula factor de catenaria en los bordes.

        Args:
            u, v: Parámetros normalizados (0-1)
            factor: Factor de escala

        Returns:
            float: Factor de depresión por catenaria
        """
        # Distancia al borde más cercano
        edge_dist = min(u, 1 - u, v, 1 - v)

        # Catenaria más pronunciada en bordes
        if edge_dist < 0.2:
            return (0.2 - edge_dist) / 0.2 * factor
        return 0

    def _create_surface_from_grid(self, points, u_degree, v_degree):
        """
        Crea superficie NURBS desde grid de puntos.

        Args:
            points: Lista 2D de Point3d
            u_degree: Grado en U
            v_degree: Grado en V

        Returns:
            NurbsSurface
        """
        u_count = len(points)
        v_count = len(points[0]) if points else 0

        if u_count < 2 or v_count < 2:
            return None

        # Crear superficie NURBS
        surface = rg.NurbsSurface.Create(
            3,  # dimensión
            False,  # racional
            u_degree + 1,  # orden U
            v_degree + 1,  # orden V
            u_count,
            v_count
        )

        # Asignar puntos de control
        for i in range(u_count):
            for j in range(v_count):
                surface.Points.SetPoint(i, j, points[i][j])

        return surface

    def validate_config(self, config):
        """Valida configuración específica para tensoestructuras."""
        validated = super().validate_config(config)

        valid_forms = ["saddle", "cone", "arch", "wave"]
        form_type = validated.get("form_type", "saddle")

        if form_type not in valid_forms:
            raise ValueError(f"form_type debe ser uno de: {valid_forms}")

        if validated.get("sag", 3.0) < 0:
            raise ValueError("sag debe ser positivo")

        return validated


# Función de conveniencia
def create_tensile_surface(width, length, height, form_type="saddle", sag=3.0):
    """
    Crea una superficie tensada.

    Args:
        width: Ancho en metros
        length: Largo en metros
        height: Altura máxima en metros
        form_type: Tipo de forma (saddle/cone/arch/wave)
        sag: Flecha de catenaria en metros

    Returns:
        Surface: Superficie generada
    """
    generator = TensileGenerator()
    config = {
        "width": width,
        "length": length,
        "height": height,
        "form_type": form_type,
        "sag": sag,
    }
    return generator.generate(config)
