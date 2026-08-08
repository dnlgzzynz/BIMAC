"""
Panelizer - Módulo de Panelización

Subdivide superficies en paneles fabricables con racionalización
de curvatura y optimización de costos.
"""

try:
    import Rhino.Geometry as rg
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False


class Panelizer:
    """
    Panelizador de superficies con racionalización.

    Subdivide una superficie en paneles cuadriláteros o triangulares,
    con opciones de planarización y optimización.

    Attributes:
        tolerance (float): Tolerancia de planarización en mm
        panel_type (str): Tipo de panel (quad/tri)
        rationalize (bool): Si aplicar racionalización

    Example:
        >>> panelizer = Panelizer(tolerance=5.0)
        >>> panels = panelizer.panelize(surface, u_count=13, v_count=10)
        >>> rationalized = panelizer.rationalize_panels(panels)
    """

    def __init__(self, tolerance=5.0, panel_type="quad", rationalize=True):
        """
        Inicializa el panelizador.

        Args:
            tolerance: Tolerancia de planarización (mm)
            panel_type: Tipo de panel ("quad" o "tri")
            rationalize: Si aplicar racionalización automática
        """
        self.tolerance = tolerance
        self.panel_type = panel_type
        self.do_rationalize = rationalize

    def panelize(self, surface, u_count, v_count):
        """
        Subdivide la superficie en paneles.

        Args:
            surface: Superficie a panelizar
            u_count (int): Número de divisiones en U
            v_count (int): Número de divisiones en V

        Returns:
            list: Lista de paneles (Brep)
        """
        if not RHINO_AVAILABLE:
            raise RuntimeError("Rhino.Geometry no disponible")

        if surface is None:
            return []

        panels = []

        u_domain = surface.Domain(0)
        v_domain = surface.Domain(1)

        u_step = (u_domain.Max - u_domain.Min) / u_count
        v_step = (v_domain.Max - v_domain.Min) / v_count

        for i in range(u_count):
            for j in range(v_count):
                # Parámetros de las esquinas
                u0 = u_domain.Min + i * u_step
                u1 = u_domain.Min + (i + 1) * u_step
                v0 = v_domain.Min + j * v_step
                v1 = v_domain.Min + (j + 1) * v_step

                if self.panel_type == "quad":
                    panel = self._create_quad_panel(surface, u0, u1, v0, v1)
                    if panel:
                        panels.append(panel)
                elif self.panel_type == "tri":
                    # Crear dos triángulos por celda
                    tri1, tri2 = self._create_tri_panels(surface, u0, u1, v0, v1)
                    if tri1:
                        panels.append(tri1)
                    if tri2:
                        panels.append(tri2)

        # Aplicar racionalización si está habilitada
        if self.do_rationalize:
            panels = self.rationalize_panels(panels)

        return panels

    def _create_quad_panel(self, surface, u0, u1, v0, v1):
        """
        Crea un panel cuadrilátero.

        Args:
            surface: Superficie base
            u0, u1: Rango de parámetro U
            v0, v1: Rango de parámetro V

        Returns:
            Brep: Panel como Brep
        """
        try:
            # Obtener los 4 puntos de las esquinas
            p00 = surface.PointAt(u0, v0)
            p10 = surface.PointAt(u1, v0)
            p11 = surface.PointAt(u1, v1)
            p01 = surface.PointAt(u0, v1)

            # Crear superficie plana desde 4 puntos
            corners = [p00, p10, p11, p01]

            # Crear curvas de borde
            edges = []
            for i in range(4):
                p1 = corners[i]
                p2 = corners[(i + 1) % 4]
                edge = rg.LineCurve(p1, p2)
                edges.append(edge)

            # Crear Brep desde bordes
            brep = rg.Brep.CreateEdgeSurface(edges)

            if brep and brep.IsValid:
                return brep

            # Alternativa: crear superficie desde puntos
            srf = rg.NurbsSurface.CreateFromCorners(p00, p10, p11, p01)
            if srf:
                return srf.ToBrep()

        except Exception as ex:
            pass

        return None

    def _create_tri_panels(self, surface, u0, u1, v0, v1):
        """
        Crea dos paneles triangulares de una celda.

        Args:
            surface: Superficie base
            u0, u1, v0, v1: Rangos de parámetros

        Returns:
            tuple: (tri1, tri2) - Dos Breps triangulares
        """
        try:
            p00 = surface.PointAt(u0, v0)
            p10 = surface.PointAt(u1, v0)
            p11 = surface.PointAt(u1, v1)
            p01 = surface.PointAt(u0, v1)

            # Triángulo 1: p00, p10, p11
            mesh1 = rg.Mesh()
            mesh1.Vertices.Add(p00)
            mesh1.Vertices.Add(p10)
            mesh1.Vertices.Add(p11)
            mesh1.Faces.AddFace(0, 1, 2)
            brep1 = rg.Brep.CreateFromMesh(mesh1, False)

            # Triángulo 2: p00, p11, p01
            mesh2 = rg.Mesh()
            mesh2.Vertices.Add(p00)
            mesh2.Vertices.Add(p11)
            mesh2.Vertices.Add(p01)
            mesh2.Faces.AddFace(0, 1, 2)
            brep2 = rg.Brep.CreateFromMesh(mesh2, False)

            return brep1, brep2

        except Exception:
            return None, None

    def rationalize_panels(self, panels):
        """
        Aplica racionalización para reducir curvatura.

        Los paneles con curvatura alta se ajustan para ser más
        planos o de curvatura simple, reduciendo costos de fabricación.

        Args:
            panels (list): Lista de paneles

        Returns:
            list: Paneles racionalizados
        """
        if not panels:
            return []

        rationalized = []

        for panel in panels:
            if panel is None:
                continue

            # Analizar planaridad
            deviation = self._calculate_planarity_deviation(panel)

            if deviation <= self.tolerance:
                # Ya es suficientemente plano
                rationalized.append(panel)
            else:
                # Intentar planarizar
                planarized = self._planarize_panel(panel)
                rationalized.append(planarized if planarized else panel)

        return rationalized

    def _calculate_planarity_deviation(self, panel):
        """
        Calcula la desviación de planaridad de un panel.

        Args:
            panel: Brep del panel

        Returns:
            float: Desviación máxima en mm
        """
        if panel is None:
            return float('inf')

        try:
            # Obtener vértices
            vertices = []
            for vertex in panel.Vertices:
                vertices.append(vertex.Location)

            if len(vertices) < 3:
                return 0

            # Calcular plano de mejor ajuste
            result, plane = rg.Plane.FitPlaneToPoints(vertices)

            if not result:
                return float('inf')

            # Calcular desviación máxima al plano
            max_deviation = 0
            for pt in vertices:
                dist = abs(plane.DistanceTo(pt))
                max_deviation = max(max_deviation, dist)

            return max_deviation

        except Exception:
            return float('inf')

    def _planarize_panel(self, panel):
        """
        Intenta planarizar un panel.

        Args:
            panel: Brep del panel

        Returns:
            Brep: Panel planarizado o None
        """
        try:
            # Obtener vértices
            vertices = [v.Location for v in panel.Vertices]

            if len(vertices) < 3:
                return None

            # Calcular plano de mejor ajuste
            result, plane = rg.Plane.FitPlaneToPoints(vertices)

            if not result:
                return None

            # Proyectar vértices al plano
            projected = [plane.ClosestPoint(pt) for pt in vertices]

            # Reconstruir panel con vértices proyectados
            if len(projected) == 4:
                srf = rg.NurbsSurface.CreateFromCorners(
                    projected[0], projected[1],
                    projected[2], projected[3]
                )
                if srf:
                    return srf.ToBrep()

            elif len(projected) == 3:
                mesh = rg.Mesh()
                for pt in projected:
                    mesh.Vertices.Add(pt)
                mesh.Faces.AddFace(0, 1, 2)
                return rg.Brep.CreateFromMesh(mesh, False)

        except Exception:
            pass

        return None

    def get_panel_stats(self, panels):
        """
        Obtiene estadísticas de los paneles.

        Args:
            panels: Lista de paneles

        Returns:
            dict: Estadísticas
        """
        stats = {
            "total_count": len(panels),
            "total_area": 0,
            "planar_count": 0,
            "non_planar_count": 0,
            "avg_deviation": 0,
            "max_deviation": 0,
        }

        if not panels:
            return stats

        deviations = []

        for panel in panels:
            if panel is None:
                continue

            # Área
            props = rg.AreaMassProperties.Compute(panel)
            if props:
                stats["total_area"] += props.Area / 1000000  # mm² a m²

            # Planaridad
            dev = self._calculate_planarity_deviation(panel)
            deviations.append(dev)

            if dev <= self.tolerance:
                stats["planar_count"] += 1
            else:
                stats["non_planar_count"] += 1

        if deviations:
            stats["avg_deviation"] = sum(deviations) / len(deviations)
            stats["max_deviation"] = max(deviations)

        return stats


def rationalize_panels(panels, tolerance=5.0):
    """
    Función de conveniencia para racionalizar paneles.

    Args:
        panels: Lista de paneles
        tolerance: Tolerancia de planarización (mm)

    Returns:
        list: Paneles racionalizados
    """
    panelizer = Panelizer(tolerance=tolerance)
    return panelizer.rationalize_panels(panels)
