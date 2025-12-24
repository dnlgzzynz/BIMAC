# Biblioteca de Familias Revit

**BIMAC Studio - www.bimacstudio.com**

---

## Ubicación de Biblioteca

| Entorno | Ruta |
|---------|------|
| **Local (Windows)** | `C:\Users\dyane\Documents\GitHub\BIMAC\assets\families\` |
| **Google Drive** | `H:\Mi unidad\00 BIMAC Live\PROYECTOS\000.BIM\RFA\` |
| **Repositorio** | `assets/families/` |

---

## Estructura de la Biblioteca

```
families/
├── Coleccion/                    # Familias generales organizadas
│   ├── Arquitectura/
│   ├── Mobiliario/
│   ├── Equipamiento/
│   └── ...
│
├── Coleccion_Muros_Cortinas/     # Curtain Walls y paneles
│   ├── Paneles/
│   ├── Montantes/
│   └── Esquinas/
│
├── Megapack_1/                   # Biblioteca amplia #1
│   └── [Categorías variadas]
│
├── Megapack_2/                   # Biblioteca amplia #2
│   └── [Categorías variadas]
│
├── Membretes/                    # Title Blocks
│   ├── BIMAC_A0.rfa
│   ├── BIMAC_A1.rfa
│   ├── BIMAC_A2.rfa
│   ├── BIMAC_A3.rfa
│   └── BIMAC_A4.rfa
│
└── README.md                     # Este archivo
```

---

## Convención de Nomenclatura

### Formato Estándar BIMAC

```
[EMPRESA]_[CATEGORÍA]_[TIPO]_[VARIANTE]_[DIMENSIÓN].rfa
```

### Ejemplos

| Familia | Nomenclatura BIMAC |
|---------|-------------------|
| Puerta sencilla 90cm | `BIMAC_Puerta_Abatible_Sencilla_90.rfa` |
| Ventana corrediza | `BIMAC_Ventana_Corrediza_120x150.rfa` |
| Silla de oficina | `BIMAC_Mobiliario_Silla_Oficina.rfa` |
| Luminaria empotrada | `BIMAC_Iluminacion_Empotrada_LED_60x60.rfa` |
| Membrete A1 | `BIMAC_Membrete_A1_Horizontal.rfa` |

### Prefijos por Categoría

| Categoría | Prefijo | Ejemplo |
|-----------|---------|---------|
| Puertas | `Puerta_` | `BIMAC_Puerta_...` |
| Ventanas | `Ventana_` | `BIMAC_Ventana_...` |
| Mobiliario | `Mobiliario_` | `BIMAC_Mobiliario_...` |
| Iluminación | `Iluminacion_` | `BIMAC_Iluminacion_...` |
| Sanitarios | `Sanitario_` | `BIMAC_Sanitario_...` |
| MEP | `MEP_` | `BIMAC_MEP_...` |
| Anotación | `Anotacion_` | `BIMAC_Anotacion_...` |
| Membrete | `Membrete_` | `BIMAC_Membrete_...` |

---

## Categorías Principales

### Arquitectura

| Subcategoría | Contenido |
|--------------|-----------|
| **Puertas** | Abatibles, corredizas, plegables, pivotantes |
| **Ventanas** | Fijas, proyectantes, corredizas, abatibles |
| **Muros Cortina** | Paneles, montantes, esquinas, remates |
| **Escaleras** | Rectas, en L, en U, helicoidales |
| **Barandales** | Vidrio, metal, mixtos |
| **Plafones** | Registrables, continuos, decorativos |

### Mobiliario

| Subcategoría | Contenido |
|--------------|-----------|
| **Oficina** | Escritorios, sillas, archiveros, libreros |
| **Residencial** | Salas, comedores, recámaras |
| **Comercial** | Mostradores, anaqueles, vitrinas |
| **Exterior** | Bancas, mesas, sombrillas |

### MEP

| Subcategoría | Contenido |
|--------------|-----------|
| **Mecánico** | Difusores, rejillas, equipos HVAC |
| **Eléctrico** | Luminarias, contactos, apagadores, tableros |
| **Hidráulico** | Muebles sanitarios, llaves, accesorios |

### Anotación

| Subcategoría | Contenido |
|--------------|-----------|
| **Etiquetas** | Puertas, ventanas, espacios, niveles |
| **Símbolos** | Norte, escala gráfica, cortes, detalles |
| **Membretes** | Formatos A0 a A4, horizontal y vertical |

---

## Parámetros Recomendados

### Parámetros de Identidad

| Parámetro | Tipo | Obligatorio |
|-----------|------|:-----------:|
| `BIMAC_Codigo` | Texto | ✓ |
| `BIMAC_Descripcion` | Texto | ✓ |
| `BIMAC_Fabricante` | Texto | ○ |
| `BIMAC_Modelo` | Texto | ○ |
| `BIMAC_URL` | URL | ○ |

### Parámetros de Clasificación

| Parámetro | Sistema | Ejemplo |
|-----------|---------|---------|
| `OmniClass` | OmniClass | 23-17 11 00 |
| `Uniformat` | Uniformat II | B2010 |
| `Masterformat` | MasterFormat | 08 11 00 |

---

## Control de Calidad de Familias

### Checklist antes de agregar familia

- [ ] Nombre sigue convención BIMAC
- [ ] Categoría correcta asignada
- [ ] Parámetros de identidad poblados
- [ ] Sin errores ni warnings
- [ ] Origen correctamente ubicado
- [ ] Planos de referencia definidos
- [ ] Tipos nombrados descriptivamente
- [ ] Materiales asignados (no <Por categoría>)
- [ ] Subcategorías de visibilidad configuradas
- [ ] LOD apropiado (no sobre-modelado)

### Verificación de Geometría

- [ ] Sin líneas/planos de modelo innecesarios
- [ ] Sólidos limpios (sin auto-intersecciones)
- [ ] Escala correcta (verificar en proyecto)
- [ ] Orientación correcta al insertar

---

## Uso en Proyectos

### Cargar Familias

```
Revit → Insert → Load Family → Navegar a carpeta
```

### Ruta Recomendada

Configurar en Revit Options → File Locations:
```
H:\Mi unidad\00 BIMAC Live\PROYECTOS\000.BIM\RFA
```

### Actualizar Familias en Proyecto

1. Abrir familia desde proyecto
2. Modificar según necesidad
3. Cargar en proyecto → Sobrescribir versión existente
4. Guardar familia en biblioteca si es mejora general

---

## Contribuir a la Biblioteca

### Proceso para agregar familias

1. Verificar que no exista familia similar
2. Aplicar nomenclatura BIMAC
3. Completar parámetros de identidad
4. Pasar checklist de calidad
5. Colocar en carpeta correspondiente
6. Documentar en catálogo si es familia principal

### Proceso para reportar problemas

1. Identificar familia con problema
2. Documentar el error
3. Notificar a BIM Manager
4. Proponer corrección si es posible

---

## Sincronización

### Google Drive → Repositorio

Las familias principales se mantienen en Google Drive por su tamaño. El repositorio contiene:
- Estructura de carpetas
- Documentación y catálogos
- Familias de anotación (ligeras)
- Membretes

### Archivos Excluidos del Repo

El `.gitignore` excluye archivos pesados:
```gitignore
# Familias Revit (muy pesadas para Git)
*.rfa
*.rte
!assets/families/Membretes/*.rfa
!assets/families/Anotacion/*.rfa
```

---

## Recursos Adicionales

| Recurso | Enlace |
|---------|--------|
| Revit Family Guide | help.autodesk.com/view/RVT |
| BIM Forum LOD Spec | bimforum.org/lod |
| NBS BIM Object Standard | nationalbimlibrary.com |

---

*Biblioteca de Familias BIMAC Studio - www.bimacstudio.com*
