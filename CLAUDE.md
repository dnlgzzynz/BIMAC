# CLAUDE.md - Guía para Desarrollo BIM/AEC en BIMAC

**Última Actualización:** 2025-12-27
**Proyecto:** BIMAC (BIM Advance Consulting)
**Repositorio:** dnlgzzynz/BIMAC
**Sitios:** [bimac.io](https://www.bimac.io) | [bimacstudio.com](https://www.bimacstudio.com)

---

## Tabla de Contenidos

1. [Contexto del Proyecto](#1-contexto-del-proyecto)
2. [Entorno de Desarrollo](#2-entorno-de-desarrollo)
3. [Estándares de Código](#3-estándares-de-código)
4. [Patrones de Arquitectura](#4-patrones-de-arquitectura)
5. [Lineamientos BIM](#5-lineamientos-bim)
6. [Estrategia de Testing](#6-estrategia-de-testing)
7. [Deployment](#7-deployment)
8. [Tareas y Comandos Comunes](#8-tareas-y-comandos-comunes)
9. [Estructura de Proyectos](#9-estructura-de-proyectos)
10. [Comportamiento del Asistente IA](#10-comportamiento-del-asistente-ia)

---

## 1. Contexto del Proyecto

### Sobre BIMAC

BIMAC (BIM Advance Consulting) es una consultora especializada en:
- **Desarrollo de plugins** para Autodesk Revit 2024/2026
- **Scripts de automatización** con PyRevit y Dynamo
- **Herramientas paramétricas** Grasshopper/Rhino
- **Integración de workflows** con n8n, Airtable, Flowise
- **Automatización BIM** según ISO 19650

### Tipos de Proyectos

| Tipo | Descripción | Stack Principal |
|------|-------------|-----------------|
| **Plugin Revit** | Extensiones .NET para Revit API | C#, .NET 4.8, WPF |
| **Script PyRevit** | Automatización Python en Revit | IronPython 2.7, PyRevit |
| **Dynamo** | Nodos visuales y Python | Python 3, DesignScript |
| **Grasshopper** | Diseño paramétrico | RhinoCommon, Python, C# |
| **Rhino.inside.Revit** | Integración Rhino-Revit | RiR API, Grasshopper |
| **Automatización n8n** | Workflows cloud | JavaScript, REST APIs |
| **Web/Dashboard** | Visualización de datos BIM | TypeScript, React |

### Plataformas BIM Principales

```
┌─────────────────────────────────────────────────────────┐
│                    AUTODESK STACK                       │
├─────────────────────────────────────────────────────────┤
│  Revit 2024/2026    │  API .NET Framework 4.8 (C#)     │
│  Civil 3D           │  API .NET                        │
│  Navisworks         │  API .NET                        │
│  ACC (Cloud)        │  REST API, Forge/APS             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    MCNEEL STACK                         │
├─────────────────────────────────────────────────────────┤
│  Rhino 7/8          │  RhinoCommon, Python, C#         │
│  Grasshopper        │  GH_Component, Python, C#        │
│  Rhino.inside.Revit │  RiR API                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Entorno de Desarrollo

### Versiones de Software

| Software | Versión | Notas |
|----------|---------|-------|
| **Revit** | 2024 / 2026 | API principal |
| **Visual Studio** | 2022 (17.x) | .NET development |
| **VS Code** | Latest | Python, JS, scripting |
| **Rhino** | 7 / 8 | Grasshopper incluido |
| **.NET Framework** | 4.8 | Requerido por Revit |
| **Python** | 3.9+ / IronPython 2.7 | PyRevit usa IronPython |
| **Node.js** | 18+ LTS | Para n8n y web |

### Variables de Entorno

```batch
:: Windows - Variables requeridas
set REVIT_SDK=C:\Program Files\Autodesk\Revit 2024\SDK
set PYREVIT_PATH=%APPDATA%\pyRevit-Master
set RHINO_PATH=C:\Program Files\Rhino 7
set GRASSHOPPER_LIBS=%APPDATA%\Grasshopper\Libraries

:: Python virtual environment
set PYTHONPATH=%PYTHONPATH%;C:\BIM\Scripts\Python
```

### Rutas Importantes

```
# Revit API References
C:\Program Files\Autodesk\Revit 2024\
├── RevitAPI.dll
├── RevitAPIUI.dll
├── RevitAPIIFC.dll
└── AdWindows.dll

# PyRevit Extensions
%APPDATA%\pyRevit-Master\extensions\

# Grasshopper Components
%APPDATA%\Grasshopper\Libraries\

# Familias Revit corporativas
\\server\BIM\Familias\
├── Arquitectura\
├── Estructura\
├── MEP\
└── Genéricas\

# Templates de proyecto
\\server\BIM\Templates\
├── Revit\
├── Grasshopper\
└── Python\
```

### Dependencias por Tipo de Proyecto

**Plugin Revit (.csproj):**
```xml
<ItemGroup>
  <Reference Include="RevitAPI">
    <HintPath>$(REVIT_SDK)\RevitAPI.dll</HintPath>
    <Private>False</Private>
  </Reference>
  <Reference Include="RevitAPIUI">
    <HintPath>$(REVIT_SDK)\RevitAPIUI.dll</HintPath>
    <Private>False</Private>
  </Reference>
</ItemGroup>
```

**Python/PyRevit (requirements.txt):**
```
# PyRevit compatible (IronPython 2.7)
# No pip install - usar librerías embebidas

# Python 3.9+ (scripts externos)
requests>=2.28.0
airtable-python-wrapper>=0.15.3
python-dotenv>=1.0.0
openpyxl>=3.1.0
```

**Node.js (package.json):**
```json
{
  "dependencies": {
    "n8n": "^1.0.0",
    "axios": "^1.6.0",
    "dotenv": "^16.3.0"
  }
}
```

---

## 3. Estándares de Código

### 3.1 C# / Revit API

**Nomenclatura:**
```csharp
// Clases: PascalCase
public class WallScheduleCreator { }

// Métodos: PascalCase
public void CreateSchedule() { }

// Variables locales: camelCase
int wallCount = 0;
Element selectedElement = null;

// Constantes: UPPER_SNAKE_CASE
private const string SCHEDULE_NAME_PREFIX = "BIMAC_";

// Campos privados: _camelCase
private Document _document;
private UIDocument _uiDocument;
```

**Transacciones (CRÍTICO):**
```csharp
// CORRECTO: Transacción con using
using (Transaction trans = new Transaction(doc, "Crear Schedule"))
{
    trans.Start();
    try
    {
        // Operaciones en el modelo
        ViewSchedule schedule = ViewSchedule.CreateSchedule(doc, categoryId);
        trans.Commit();
    }
    catch (Exception ex)
    {
        trans.RollBack();
        TaskDialog.Show("Error", ex.Message);
    }
}

// INCORRECTO: Transacción sin cierre garantizado
Transaction trans = new Transaction(doc, "Operación");
trans.Start();
// Si hay excepción aquí, la transacción queda abierta
trans.Commit();
```

**Manejo de Errores:**
```csharp
public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
{
    try
    {
        // Lógica principal
        return Result.Succeeded;
    }
    catch (Autodesk.Revit.Exceptions.InvalidOperationException ex)
    {
        // Error específico de Revit
        message = $"Operación inválida: {ex.Message}";
        return Result.Failed;
    }
    catch (Exception ex)
    {
        // Error general
        message = $"Error inesperado: {ex.Message}";
        TaskDialog.Show("BIMAC - Error", ex.ToString());
        return Result.Failed;
    }
}
```

**Documentación XML:**
```csharp
/// <summary>
/// Crea un schedule de cantidades para elementos estructurales.
/// </summary>
/// <param name="doc">Documento de Revit activo.</param>
/// <param name="categoryId">ID de categoría (ej: BuiltInCategory.OST_StructuralColumns).</param>
/// <param name="scheduleName">Nombre del schedule a crear.</param>
/// <returns>ViewSchedule creado o null si falla.</returns>
/// <exception cref="ArgumentNullException">Si doc es null.</exception>
public ViewSchedule CreateStructuralSchedule(Document doc, ElementId categoryId, string scheduleName)
{
    // Implementación
}
```

### 3.2 Python / PyRevit

**Estilo PEP 8:**
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script: Exportar Schedules a Excel
Autor: BIMAC
Versión: 1.0.0
Descripción: Exporta todos los schedules del proyecto a archivos Excel.
"""

# Imports organizados
from __future__ import print_function  # Compatibilidad IronPython

# Standard library
import os
import sys
from datetime import datetime

# Revit API
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    ViewSchedule,
    BuiltInCategory
)

# PyRevit
from pyrevit import revit, DB, forms, script

# Local modules
from lib import utils


# Constantes
EXPORT_PATH = r"C:\BIM\Exports"
FILE_PREFIX = "BIMAC_Schedule_"


def get_all_schedules(doc):
    """
    Obtiene todos los schedules del documento.

    Args:
        doc (Document): Documento de Revit.

    Returns:
        list[ViewSchedule]: Lista de schedules encontrados.

    Example:
        >>> schedules = get_all_schedules(revit.doc)
        >>> print(f"Encontrados: {len(schedules)} schedules")
    """
    collector = FilteredElementCollector(doc).OfClass(ViewSchedule)
    return [s for s in collector if not s.IsTemplate]


# Entry point
if __name__ == "__main__":
    doc = revit.doc
    schedules = get_all_schedules(doc)
```

**Type Hints (Python 3.9+):**
```python
from typing import List, Optional, Dict, Union
from Autodesk.Revit.DB import Element, Document, ViewSchedule


def filter_elements_by_parameter(
    doc: Document,
    elements: List[Element],
    param_name: str,
    param_value: Union[str, int, float]
) -> List[Element]:
    """Filtra elementos por valor de parámetro."""
    pass
```

### 3.3 JavaScript / n8n

**ES6+ Syntax:**
```javascript
/**
 * Procesa datos de Airtable y sincroniza con Revit via webhook.
 * @param {Object} items - Items del nodo anterior
 * @returns {Promise<Object[]>} Items procesados
 */
const processAirtableData = async (items) => {
  const results = [];

  try {
    for (const item of items) {
      const { fields } = item.json;

      // Validación de campos requeridos
      if (!fields.ElementId || !fields.ParameterName) {
        console.warn(`Item sin campos requeridos: ${JSON.stringify(fields)}`);
        continue;
      }

      // Procesamiento
      const processed = {
        elementId: fields.ElementId,
        parameter: fields.ParameterName,
        value: fields.NewValue,
        timestamp: new Date().toISOString()
      };

      results.push({ json: processed });
    }

    return results;
  } catch (error) {
    console.error(`Error procesando datos: ${error.message}`);
    throw error;
  }
};

return processAirtableData($input.all());
```

### 3.4 Grasshopper / Python Script

```python
"""
Grasshopper Python Script: Panelización de Superficie
Inputs:
    surface (Surface): Superficie NURBS a panelizar
    u_count (int): Divisiones en U
    v_count (int): Divisiones en V
Outputs:
    panels (List[Brep]): Paneles generados
    types (List[str]): Tipo de cada panel
    costs (List[float]): Costo estimado por panel
"""

import Rhino.Geometry as rg
import math

# Constantes de costo (MXN/m²)
COST_FLAT = 450.0
COST_SINGLE_CURVE = 680.0
COST_DOUBLE_CURVE = 1250.0


def analyze_panel_curvature(panel_surface):
    """
    Analiza curvatura gaussiana para clasificar panel.

    Args:
        panel_surface: Superficie del panel

    Returns:
        tuple: (tipo, costo_por_m2)
    """
    u_mid = panel_surface.Domain(0).Mid
    v_mid = panel_surface.Domain(1).Mid

    curvature = panel_surface.CurvatureAt(u_mid, v_mid)

    if curvature is None:
        return ("flat", COST_FLAT)

    gauss = abs(curvature.Gaussian)

    if gauss < 0.0001:
        return ("flat", COST_FLAT)
    elif gauss < 0.001:
        return ("single_curve", COST_SINGLE_CURVE)
    else:
        return ("double_curve", COST_DOUBLE_CURVE)
```

---

## 4. Patrones de Arquitectura

### 4.1 Plugins de Revit

**Estructura de Proyecto:**
```
PluginRevit/
├── src/
│   ├── Commands/           # External Commands
│   │   ├── CreateScheduleCommand.cs
│   │   └── ExportDataCommand.cs
│   ├── Applications/       # External Applications
│   │   └── MainApplication.cs
│   ├── UI/                 # Interfaz WPF
│   │   ├── Views/
│   │   └── ViewModels/
│   ├── Services/           # Lógica de negocio
│   ├── Models/             # Modelos de datos
│   ├── Handlers/           # Event Handlers
│   └── Utils/              # Utilidades
├── resources/
│   └── icons/
├── Plugin.addin            # Manifest
├── Plugin.csproj
└── README.md
```

**External Command Pattern:**
```csharp
[Transaction(TransactionMode.Manual)]
[Regeneration(RegenerationOption.Manual)]
public class CreateScheduleCommand : IExternalCommand
{
    public Result Execute(
        ExternalCommandData commandData,
        ref string message,
        ElementSet elements)
    {
        UIApplication uiApp = commandData.Application;
        UIDocument uiDoc = uiApp.ActiveUIDocument;
        Document doc = uiDoc.Document;

        try
        {
            var service = new ScheduleService(doc);
            service.CreateQuantitySchedule();
            return Result.Succeeded;
        }
        catch (Exception ex)
        {
            message = ex.Message;
            return Result.Failed;
        }
    }
}
```

**Modeless Dialog Pattern (IExternalEventHandler):**
```csharp
public class UpdateParameterHandler : IExternalEventHandler
{
    public string ParameterName { get; set; }
    public string ParameterValue { get; set; }

    public void Execute(UIApplication app)
    {
        Document doc = app.ActiveUIDocument.Document;

        using (Transaction trans = new Transaction(doc, "Update Parameter"))
        {
            trans.Start();
            // Actualizar parámetros
            trans.Commit();
        }
    }

    public string GetName() => "BIMAC Update Parameter Handler";
}
```

**Archivo .addin:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<RevitAddIns>
  <AddIn Type="Application">
    <Name>BIMAC Tools</Name>
    <Assembly>BIMACTools.dll</Assembly>
    <FullClassName>BIMACTools.MainApplication</FullClassName>
    <ClientId>A1B2C3D4-E5F6-7890-ABCD-EF1234567890</ClientId>
    <VendorId>BIMAC</VendorId>
    <VendorDescription>BIM Advance Consulting, www.bimac.io</VendorDescription>
  </AddIn>
</RevitAddIns>
```

### 4.2 Integraciones API

**RESTful Pattern con Retry:**
```csharp
public class AccApiClient
{
    private readonly HttpClient _httpClient;
    private readonly int _maxRetries = 3;
    private readonly TimeSpan _retryDelay = TimeSpan.FromSeconds(2);

    public async Task<T> GetWithRetryAsync<T>(string endpoint)
    {
        int attempts = 0;
        Exception lastException = null;

        while (attempts < _maxRetries)
        {
            try
            {
                var response = await _httpClient.GetAsync(endpoint);

                if (response.StatusCode == HttpStatusCode.TooManyRequests)
                {
                    await Task.Delay(_retryDelay * (attempts + 1));
                    attempts++;
                    continue;
                }

                response.EnsureSuccessStatusCode();
                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<T>(json);
            }
            catch (HttpRequestException ex)
            {
                lastException = ex;
                attempts++;
                await Task.Delay(_retryDelay * attempts);
            }
        }

        throw new Exception($"Failed after {_maxRetries} attempts", lastException);
    }
}
```

---

## 5. Lineamientos BIM

### 5.1 Estándares ISO 19650

**Nomenclatura de Archivos:**
```
{Proyecto}-{Origen}-{Volumen}-{Nivel}-{Tipo}-{Rol}-{Clasificación}-{Número}

Ejemplos:
MUSEO-ARC-ZZ-00-M3-A-0001.rvt      # Modelo arquitectura general
MUSEO-EST-ZZ-00-M3-S-0001.rvt      # Modelo estructura
MUSEO-MEP-ZZ-01-M3-M-0001.rvt      # Modelo MEP nivel 1

Donde:
- Proyecto: Código de proyecto (4-6 caracteres)
- Origen: Disciplina origen (ARC, EST, MEP, etc.)
- Volumen: Zona/Volumen (ZZ = todos)
- Nivel: Nivel (00 = general, 01, 02, etc.)
- Tipo: Tipo de archivo (M3 = modelo 3D, DR = dibujo)
- Rol: Rol (A = arquitectura, S = estructura, M = MEP)
- Número: Secuencial (0001-9999)
```

**Niveles de Información (LOD/LOI):**

| LOD | Geometría | LOI | Información | Uso |
|-----|-----------|-----|-------------|-----|
| 100 | Conceptual | Básica | Nombre, tipo | Esquemático |
| 200 | Aproximada | Genérica | Dimensiones aproximadas | Diseño preliminar |
| 300 | Precisa | Detallada | Especificaciones técnicas | Desarrollo |
| 350 | Constructiva | Completa | Fabricación/instalación | Documentación |
| 400 | Fabricación | Total | Detalle constructivo | Producción |

**Parámetros Compartidos Estándar:**
```
BIMAC_CodigoElemento    (Text)     - Código único de elemento
BIMAC_Fase              (Text)     - Fase constructiva
BIMAC_Proveedor         (Text)     - Proveedor asignado
BIMAC_CostoUnitario     (Currency) - Costo por unidad
BIMAC_FechaInstalacion  (Text)     - Fecha programada
BIMAC_EstadoQA          (Text)     - Estado control calidad
```

### 5.2 Interoperabilidad

**Configuración IFC Export:**
```
Setup Name: BIMAC_IFC4_COBie
IFC Version: IFC4
File Type: .ifc
Space Boundaries: 2nd Level
Phase to Export: Current Phase
Split Walls/Columns: By Level

Property Sets:
- Export Revit property sets
- Export IFC common property sets
- Export base quantities
- Export schedules as property sets
```

**BCF Issue Template:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Markup>
  <Topic Guid="{GUID}" TopicType="Issue" TopicStatus="Open">
    <Title>Descripción breve del issue</Title>
    <Priority>High</Priority>
    <AssignedTo>usuario@bimac.io</AssignedTo>
    <Labels>
      <Label>Clash</Label>
      <Label>MEP</Label>
    </Labels>
  </Topic>
</Markup>
```

### 5.3 Unidades (CRÍTICO)

```csharp
// Revit trabaja internamente en PIES (feet)
// Siempre convertir al crear/leer geometría

public static class UnitConverter
{
    public const double FeetToMm = 304.8;
    public const double FeetToM = 0.3048;
    public const double MmToFeet = 1.0 / 304.8;
    public const double MToFeet = 1.0 / 0.3048;

    /// <summary>
    /// Convierte milímetros a pies (unidades internas de Revit).
    /// </summary>
    public static double MmToInternalUnits(double mm)
    {
        return mm * MmToFeet;
    }

    /// <summary>
    /// Convierte pies (unidades internas) a milímetros.
    /// </summary>
    public static double InternalUnitsToMm(double feet)
    {
        return feet * FeetToMm;
    }
}

// Ejemplo de uso
XYZ point = new XYZ(
    UnitConverter.MmToInternalUnits(5000),  // X: 5000mm
    UnitConverter.MmToInternalUnits(3000),  // Y: 3000mm
    UnitConverter.MmToInternalUnits(2700)   // Z: 2700mm
);
```

---

## 6. Estrategia de Testing

### 6.1 Unit Tests (C#)

```csharp
using NUnit.Framework;

[TestFixture]
public class ScheduleServiceTests
{
    [Test]
    public void CreateSchedule_WithValidCategory_ReturnsSchedule()
    {
        // Arrange
        var categoryId = new ElementId(BuiltInCategory.OST_Walls);

        // Act
        var result = _service.CreateSchedule(categoryId, "Test Schedule");

        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual("Test Schedule", result.Name);
    }

    [TestCase(1000, 304.8)]
    [TestCase(0, 0)]
    [TestCase(-500, -152.4)]
    public void MmToFeet_VariousInputs_ReturnsCorrectConversion(
        double inputMm, double expectedFeet)
    {
        var result = UnitConverter.MmToInternalUnits(inputMm);
        Assert.AreEqual(expectedFeet, result, 0.001);
    }
}
```

### 6.2 Manual Testing Checklist (UI Revit)

```markdown
## Checklist de Testing Manual - Plugin Revit

### Pre-requisitos
- [ ] Revit 2024 instalado y funcionando
- [ ] Plugin compilado en modo Debug
- [ ] Modelo de prueba cargado

### Funcionalidad Básica
- [ ] Plugin aparece en Ribbon
- [ ] Iconos se muestran correctamente
- [ ] Comando se ejecuta sin errores

### Manejo de Errores
- [ ] Modelo sin elementos de la categoría
- [ ] Elementos en grupos
- [ ] Documento de solo lectura

### Performance
- [ ] Modelo pequeño (<100 elementos): < 2 seg
- [ ] Modelo mediano (100-1000 elementos): < 10 seg
- [ ] Modelo grande (>1000 elementos): < 30 seg

### Undo/Redo
- [ ] Cambios se pueden deshacer
- [ ] Transaction name aparece en historial
```

---

## 7. Deployment

### 7.1 Build de Plugins

**Script de Build:**
```powershell
# build.ps1
param(
    [string]$Version = "1.0.0",
    [string]$Configuration = "Release"
)

$ProjectName = "BIMACTools"
$OutputDir = ".\dist\$Version"

Write-Host "Building $ProjectName v$Version..." -ForegroundColor Cyan

# Compilar
dotnet build -c $Configuration

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Copiar archivos
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
Copy-Item ".\bin\$Configuration\$ProjectName.dll" $OutputDir
Copy-Item ".\$ProjectName.addin" $OutputDir

# Crear ZIP
$ZipPath = ".\dist\$ProjectName-$Version.zip"
Compress-Archive -Path "$OutputDir\*" -DestinationPath $ZipPath -Force

Write-Host "Build complete: $ZipPath" -ForegroundColor Green
```

### 7.2 Instalación

**Rutas de Instalación:**
```
# Usuario actual
%APPDATA%\Autodesk\Revit\Addins\2024\

# Todos los usuarios (requiere admin)
C:\ProgramData\Autodesk\Revit\Addins\2024\

# Estructura de instalación
Addins\2024\
├── BIMACTools.addin
└── BIMACTools\
    ├── BIMACTools.dll
    └── resources\
        └── icons\
```

### 7.3 Versionado Semántico

```
MAJOR.MINOR.PATCH

MAJOR: Cambios incompatibles (breaking changes)
MINOR: Nueva funcionalidad compatible
PATCH: Correcciones de bugs

Ejemplos:
1.0.0 → Lanzamiento inicial para Revit 2024
1.1.0 → Agregado comando de exportación
1.1.1 → Fix en conversión de unidades
2.0.0 → Actualización para Revit 2025
```

---

## 8. Tareas y Comandos Comunes

### 8.1 Desarrollo

```bash
# Compilar plugin de Revit
dotnet build -c Debug
dotnet build -c Release

# Ejecutar tests
dotnet test --logger "console;verbosity=detailed"

# PyRevit - Recargar extensiones
pyrevit reload

# Grasshopper - Abrir definición
rhino -command "Grasshopper" -script "C:\BIM\Scripts\definition.gh"
```

### 8.2 Git Workflow

```bash
# Nueva feature
git checkout -b feature/schedule-exporter
git add .
git commit -m "feat(schedule): add Excel export functionality"
git push -u origin feature/schedule-exporter

# Hotfix
git checkout -b fix/unit-conversion
git commit -m "fix(units): correct mm to feet conversion"
git push origin fix/unit-conversion
```

### 8.3 Empaquetado

```bash
# Empaquetar para distribución
python scripts/package.py --version 1.2.3

# Subir a network share
robocopy dist\1.2.3 \\server\BIM\Addins\BIMACTools\1.2.3 /MIR
```

---

## 9. Estructura de Proyectos

### 9.1 Plugin Revit Completo

```
proyecto-plugin-revit/
├── src/
│   ├── Commands/
│   ├── Applications/
│   ├── UI/
│   │   ├── Views/
│   │   └── ViewModels/
│   ├── Services/
│   ├── Models/
│   ├── Handlers/
│   └── Utils/
├── tests/
├── resources/
│   └── icons/
├── docs/
├── scripts/
├── dist/
├── Plugin.addin
├── Plugin.csproj
└── README.md
```

### 9.2 Extensión PyRevit

```
pyrevit-extension.extension/
├── lib/
│   ├── __init__.py
│   └── utils.py
├── BIMACTools.tab/
│   ├── Schedules.panel/
│   │   ├── ExportSchedule.pushbutton/
│   │   │   ├── script.py
│   │   │   ├── icon.png
│   │   │   └── bundle.yaml
│   │   └── CreateSchedule.pushbutton/
│   └── Parameters.panel/
├── hooks/
├── startup.py
└── extension.json
```

### 9.3 Proyecto Grasshopper

```
proyecto-grasshopper/
├── definitions/
│   ├── main_definition.gh
│   └── components/
├── scripts/
│   ├── python/
│   └── csharp/
├── clusters/
├── docs/
├── examples/
├── tests/
└── README.md
```

---

## 10. Comportamiento del Asistente IA

### 10.1 Directrices Generales

**Cuando generes código:**
- Siempre incluir manejo de errores robusto
- Agregar comentarios explicativos en español para lógica compleja
- Usar nombres descriptivos en inglés para variables/funciones
- Optimizar para rendimiento (operaciones en Revit pueden ser lentas)
- Considerar usuarios finales (arquitectos/ingenieros, no programadores)
- Código primero, explicación después
- Incluir ejemplos de uso
- Mencionar posibles edge cases
- Sugerir mejoras de performance cuando sea relevante

**Cuando trabajes con Revit API:**
- Verificar que transacciones se cierren correctamente (usar `using`)
- No asumir que elementos existen, siempre validar con null checks
- Recordar que Revit trabaja en unidades internas (pies)
- Considerar impacto en modelo (undo/redo debe funcionar)
- Validar que documento no sea de solo lectura
- Manejar elementos en grupos y Design Options
- Usar `FilteredElementCollector` eficientemente (agregar filtros)

### 10.2 Patrones de Respuesta

**Para preguntas de implementación:**
```
1. Código completo y funcional
2. Explicación breve de decisiones técnicas
3. Ejemplo de uso
4. Consideraciones de performance (si aplica)
5. Edge cases a considerar
```

**Para debugging:**
```
1. Identificar causa probable
2. Código corregido
3. Explicación del error
4. Cómo prevenir en futuro
```

### 10.3 Preguntas de Aclaración

Cuando la información sea insuficiente, preguntar específicamente:

- **Plugin Revit**: ¿Versión de Revit? ¿Requiere UI? ¿Qué categorías de elementos?
- **PyRevit**: ¿Es para un pushbutton o script standalone? ¿Necesita formulario?
- **Grasshopper**: ¿Es para definición o componente compilado? ¿Plugins requeridos?
- **Integración**: ¿Qué servicios involucra? ¿Autenticación requerida?

### 10.4 Seguridad

**Nunca incluir en código:**
- Credenciales hardcodeadas
- API keys en código fuente
- Rutas absolutas específicas de usuario
- Datos personales o de proyectos reales

**Siempre recomendar:**
- Variables de entorno para secretos
- Archivos de configuración externos
- Validación de inputs de usuario
- Sanitización de paths

### 10.5 Recursos de Referencia

**Documentación oficial:**
- [Revit API Docs](https://www.revitapidocs.com/)
- [PyRevit Docs](https://pyrevit.readthedocs.io/)
- [RhinoCommon API](https://developer.rhino3d.com/api/RhinoCommon/)
- [Grasshopper SDK](https://developer.rhino3d.com/guides/grasshopper/)
- [Rhino.inside.Revit](https://www.rhino3d.com/inside/revit/)
- [Autodesk Platform Services](https://aps.autodesk.com/developer/documentation)

**Comunidades:**
- [Revit API Forum](https://forums.autodesk.com/t5/revit-api-forum/bd-p/160)
- [pyRevit GitHub](https://github.com/eirannejad/pyRevit)
- [McNeel Forum](https://discourse.mcneel.com/)
- [The Building Coder](https://thebuildingcoder.typepad.com/)

---

## Changelog

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2025-12-27 | 2.0.0 | Reescritura completa para stack BIM/AEC |
| 2025-11-14 | 1.0.0 | Creación inicial |

---

**Recuerda:** Este documento es una guía viva. Actualízalo cuando descubras nuevos patrones, convenciones o mejores prácticas en el desarrollo BIM/AEC.
