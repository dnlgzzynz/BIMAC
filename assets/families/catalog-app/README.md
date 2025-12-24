# Catálogo de Familias Revit - BIMAC Studio

Aplicación React para visualizar y buscar familias Revit de la biblioteca BIMAC.

---

## Características

- Búsqueda por nombre, descripción o tags
- Filtrado por categoría y colección
- Vista de tarjetas (grid) o tabla
- Exportación a CSV
- Diseño responsivo
- Optimizado para embed en WordPress

---

## Estructura del Proyecto

```
catalog-app/
├── src/
│   ├── components/
│   │   ├── FamilyCard.jsx      # Tarjeta de familia
│   │   ├── FamilyTable.jsx     # Vista de tabla
│   │   ├── SearchBar.jsx       # Barra de búsqueda
│   │   └── FilterPanel.jsx     # Panel de filtros
│   ├── data/
│   │   └── families.json       # Datos de familias
│   ├── styles/
│   │   └── index.css           # Estilos Tailwind
│   ├── App.jsx                 # Componente principal
│   └── main.jsx                # Entry point
├── public/
│   └── thumbnails/             # Imágenes de preview
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

---

## Desarrollo Local

### Requisitos

- Node.js 18+
- npm o yarn

### Instalación

```bash
cd assets/families/catalog-app
npm install
```

### Ejecutar en desarrollo

```bash
npm run dev
```

Abre http://localhost:5173

### Build para producción

```bash
npm run build
```

Genera archivos en `/dist`:
- `bimac-catalog.js` - JavaScript bundle
- `bimac-catalog.css` - Estilos
- `index.html` - HTML de referencia

---

## Deploy en WordPress (bimac.io)

### Opción 1: Subir archivos a Hostinger

1. **Build del proyecto**
   ```bash
   npm run build
   ```

2. **Subir a Hostinger**
   - Conecta por FTP o File Manager
   - Crea carpeta: `public_html/catalog/`
   - Sube contenido de `/dist`

3. **Crear página en WordPress**
   - Nueva página: "Catálogo de Familias"
   - Usar bloque HTML personalizado:

   ```html
   <div id="bimac-family-catalog"></div>
   <link rel="stylesheet" href="/catalog/bimac-catalog.css">
   <script type="module" src="/catalog/bimac-catalog.js"></script>
   ```

### Opción 2: Embed con iframe

1. Sube los archivos a una subcarpeta
2. En WordPress usa:

```html
<iframe
  src="https://bimac.io/catalog/"
  width="100%"
  height="800px"
  frameborder="0"
  style="border: none;">
</iframe>
```

### Opción 3: Plugin de React

Usar plugin como "flavor" o "flavor" para cargar React apps:

1. Instalar plugin "flavor" o "flavor"
2. Configurar la ruta al build
3. Insertar shortcode en la página

---

## Agregar Nuevas Familias

### Editar families.json

Agregar objetos al array en `src/data/families.json`:

```json
{
  "id": "26",
  "name": "BIMAC_NuevaFamilia",
  "description": "Descripción de la familia",
  "category": "Arquitectura",
  "collection": "Coleccion",
  "file": "BIMAC_NuevaFamilia.rfa",
  "thumbnail": "/thumbnails/nueva-familia.png",
  "tags": ["tag1", "tag2", "tag3"],
  "lod": 300
}
```

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único |
| `name` | string | Nombre de la familia |
| `description` | string | Descripción breve |
| `category` | string | Categoría (Arquitectura, MEP, etc.) |
| `collection` | string | Colección a la que pertenece |
| `file` | string | Nombre del archivo .rfa |
| `thumbnail` | string/null | Ruta a imagen de preview |
| `tags` | array | Tags para búsqueda |
| `lod` | number/null | Level of Development |

### Categorías disponibles

- `Arquitectura`
- `Estructura`
- `MEP`
- `Mobiliario`
- `Muros Cortina`
- `Anotacion`
- `Membretes`

### Agregar thumbnails

1. Exporta imagen desde Revit (PNG, 200x200px recomendado)
2. Guarda en `public/thumbnails/`
3. Referencia en JSON: `"/thumbnails/nombre.png"`

---

## Personalización

### Colores BIMAC

Editar `tailwind.config.js`:

```javascript
colors: {
  bimac: {
    primary: '#1e3a5f',    // Azul oscuro
    secondary: '#3d5a80',  // Azul medio
    accent: '#ee6c4d',     // Naranja
    light: '#e0fbfc',      // Azul claro
    dark: '#293241'        // Gris oscuro
  }
}
```

### Agregar categorías

1. Agregar color en `src/styles/index.css`:
   ```css
   .category-nueva { @apply bg-red-100 text-red-800; }
   ```

2. Agregar mapping en `FamilyCard.jsx` y `FamilyTable.jsx`:
   ```javascript
   const categoryColors = {
     'Nueva': 'category-nueva',
     // ...
   }
   ```

---

## Scripts de Automatización

### Generar JSON desde carpeta (Python)

```python
import os
import json

def scan_families(folder_path):
    families = []
    id_counter = 1

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.rfa'):
                families.append({
                    "id": str(id_counter),
                    "name": file.replace('.rfa', ''),
                    "description": "",
                    "category": os.path.basename(root),
                    "collection": os.path.basename(os.path.dirname(root)),
                    "file": file,
                    "thumbnail": None,
                    "tags": [],
                    "lod": None
                })
                id_counter += 1

    return families

# Uso
families = scan_families("H:/Mi unidad/00 BIMAC Live/PROYECTOS/000.BIM/RFA")
with open('families.json', 'w', encoding='utf-8') as f:
    json.dump(families, f, indent=2, ensure_ascii=False)
```

---

## Mantenimiento

### Actualizar dependencias

```bash
npm update
```

### Re-build después de cambios

```bash
npm run build
```

### Subir cambios a Hostinger

1. Build local
2. Subir `/dist` por FTP
3. Limpiar caché de WordPress si es necesario

---

## Soporte

**BIMAC Studio**
- Web: www.bimacstudio.com
- Email: arq.dnlgzz@bimacstudio.com

---

*Catálogo de Familias Revit - BIMAC Studio © 2025*
