"""
Curvature Analyzer

Análisis de curvatura gaussiana para clasificación de paneles
y optimización de costos de fabricación.
"""

from collections import namedtuple

try:
    import Rhino.Geometry as rg
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False

# Estructura de resultado
PanelAnalysis = namedtuple('PanelAnalysis', [
    'panel',
    'panel_type',
    'curvature',
    'area'
])


class CurvatureAnalyzer:
    """
    Analizador de curvatura gaussiana de paneles.

    Clasifica paneles en tres categorías según su curvatura:
    - flat: Paneles prácticamente planos
    - single_curve: Curvatura simple (cilíndrica)
    - double_curve: Doble curvatura (sinclástica o anticlástica)

    Attributes:
        threshold_flat (float): Umbral para clasificar como plano
        threshold_single (float): Umbral para curvatura simple
        sample_count (int): Puntos de muestreo por panel

    Example:
        >>> analyzer = CurvatureAnalyzer()
        >>> results = analyzer.analyze(panels)
        >>> flat = results["flat"]
        >>> single = results["single_curve"]
        >>> double = results["double_curve"]
    """

    # Umbrales por defecto (calibrados para fabricación)
    DEFAULT_THRESHOLD_FLAT = 0.0001
    DEFAULT_THRESHOLD_SINGLE = 0.001

    def __init__(self, threshold_flat=None, threshold_single=None, sample_count=5):
        """
        Inicializa el analizador.

        Args:
            threshold_flat: Umbral para clasificar como plano
            threshold_single: Umbral para curvatura simple
            sample_count: Puntos de muestreo (grid sample_count x sample_count)
        """
        self.threshold_flat = threshold_flat or self.DEFAULT_THRESHOLD_FLAT
        self.threshold_single = threshold_single or self.DEFAULT_THRESHOLD_SINGLE
        self.sample_count = sample_count

    def analyze(self, panels):
        """
        Analiza una lista de paneles.

        Args:
            panels (list): Lista de paneles (Breps)

        Returns:
            dict: Resultados organizados por tipo
                - flat: Lista de paneles planos
                - single_curve: Lista de curvatura simple
                - double_curve: Lista de doble curvatura
                - types: Lista de tipos en orden original
                - curvatures: Lista de valores de curvatura
                - analyses: Lista de PanelAnalysis
        """
        results = {
            "flat": [],
            "single_curve": [],
            "double_curve": [],
            "types": [],
            "curvatures": [],
            "areas": [],
            "analyses": [],
        }

        if not panels:
            return results

        for panel in panels:
            analysis = self._analyze_panel(panel)

            results["analyses"].append(analysis)
            results["types"].append(analysis.panel_type)
            results["curvatures"].append(analysis.curvature)
            results["areas"].append(analysis.area)

            # Clasificar en lista correspondiente
            if analysis.panel_type == "flat":
                results["flat"].append(panel)
            elif analysis.panel_type == "single_curve":
                results["single_curve"].append(panel)
            elif analysis.panel_type == "double_curve":
                results["double_curve"].append(panel)

        return results

    def _analyze_panel(self, panel):
        """
        Analiza un panel individual.

        Args:
            panel: Brep del panel

        Returns:
            PanelAnalysis: Resultado del análisis
        """
        if panel is None:
            return PanelAnalysis(
                panel=None,
                panel_type="invalid",
                curvature=0,
                area=0
            )

        # Obtener superficie del panel
        surface = self._get_surface(panel)

        if surface is None:
            return PanelAnalysis(
                panel=panel,
                panel_type="flat",  # Asumir plano si no hay superficie
                curvature=0,
                area=self._get_area(panel)
            )

        # Calcular curvatura
        max_curvature = self._sample_curvature(surface)

        # Clasificar
        panel_type = self._classify(max_curvature)

        # Área
        area = self._get_area(panel)

        return PanelAnalysis(
            panel=panel,
            panel_type=panel_type,
            curvature=max_curvature,
            area=area
        )

    def _get_surface(self, panel):
        """Obtiene la superficie de un Brep."""
        if not RHINO_AVAILABLE:
            return None

        try:
            if isinstance(panel, rg.Brep):
                if panel.Faces.Count > 0:
                    return panel.Faces[0].ToNurbsSurface()
            elif isinstance(panel, rg.Surface):
                return panel
            elif isinstance(panel, rg.NurbsSurface):
                return panel
        except:
            pass

        return None

    def _sample_curvature(self, surface):
        """
        Muestrea la curvatura gaussiana en múltiples puntos.

        Args:
            surface: Superficie a analizar

        Returns:
            float: Valor absoluto máximo de curvatura gaussiana
        """
        if surface is None:
            return 0

        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)

        max_curvature = 0

        for i in range(self.sample_count):
            u = u_domain.ParameterAt(i / (self.sample_count - 1))

            for j in range(self.sample_count):
                v = v_domain.ParameterAt(j / (self.sample_count - 1))

                try:
                    curvature = surface.CurvatureAt(u, v)
                    if curvature:
                        k = abs(curvature.Gaussian)
                        max_curvature = max(max_curvature, k)
                except:
                    pass

        return max_curvature

    def _classify(self, curvature):
        """
        Clasifica según valor de curvatura.

        Args:
            curvature: Valor de curvatura gaussiana

        Returns:
            str: Tipo de panel
        """
        if curvature < self.threshold_flat:
            return "flat"
        elif curvature < self.threshold_single:
            return "single_curve"
        else:
            return "double_curve"

    def _get_area(self, panel):
        """
        Calcula el área de un panel en m².

        Args:
            panel: Brep del panel

        Returns:
            float: Área en metros cuadrados
        """
        if not RHINO_AVAILABLE or panel is None:
            return 0

        try:
            props = rg.AreaMassProperties.Compute(panel)
            if props:
                return props.Area / 1000000  # mm² a m²
        except:
            pass

        return 0

    def get_summary(self, results):
        """
        Genera un resumen del análisis.

        Args:
            results: Resultados de analyze()

        Returns:
            dict: Resumen con conteos y porcentajes
        """
        total = len(results["types"])

        if total == 0:
            return {
                "total": 0,
                "flat": {"count": 0, "percent": 0, "area": 0},
                "single_curve": {"count": 0, "percent": 0, "area": 0},
                "double_curve": {"count": 0, "percent": 0, "area": 0},
            }

        flat_count = len(results["flat"])
        single_count = len(results["single_curve"])
        double_count = len(results["double_curve"])

        # Calcular áreas por tipo
        flat_area = sum(a.area for a in results["analyses"] if a.panel_type == "flat")
        single_area = sum(a.area for a in results["analyses"] if a.panel_type == "single_curve")
        double_area = sum(a.area for a in results["analyses"] if a.panel_type == "double_curve")

        return {
            "total": total,
            "flat": {
                "count": flat_count,
                "percent": flat_count / total * 100,
                "area": flat_area,
            },
            "single_curve": {
                "count": single_count,
                "percent": single_count / total * 100,
                "area": single_area,
            },
            "double_curve": {
                "count": double_count,
                "percent": double_count / total * 100,
                "area": double_area,
            },
            "total_area": flat_area + single_area + double_area,
        }


# Funciones de conveniencia
def analyze_curvature(panels, threshold_flat=None, threshold_single=None):
    """
    Analiza la curvatura de una lista de paneles.

    Args:
        panels: Lista de paneles
        threshold_flat: Umbral para plano
        threshold_single: Umbral para curvatura simple

    Returns:
        dict: Resultados del análisis
    """
    analyzer = CurvatureAnalyzer(threshold_flat, threshold_single)
    return analyzer.analyze(panels)


def classify_panels(panels):
    """
    Clasifica paneles en flat, single_curve, double_curve.

    Args:
        panels: Lista de paneles

    Returns:
        tuple: (flat_panels, single_curve_panels, double_curve_panels)
    """
    results = analyze_curvature(panels)
    return results["flat"], results["single_curve"], results["double_curve"]
