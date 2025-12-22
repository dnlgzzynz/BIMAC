# AIR - Asset Information Requirements

**Requisitos de Información del Activo**

---

## Información del Documento

| Campo | Valor |
|-------|-------|
| **Organización** | BIMAC Studio |
| **Activo** | [Nombre del Activo] |
| **Código de Activo** | [ACT-000] |
| **Documento** | AIR-[Código]-001 |
| **Versión** | 1.0 |
| **Fecha** | [DD/MM/AAAA] |
| **Estado** | Borrador / En Revisión / Aprobado |

### Control de Versiones

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | | | Versión inicial |

### Aprobaciones

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| Gerente de Operaciones | | | |
| Gerente de Mantenimiento | | | |
| Director de Activos | | | |

---

## 1. Información del Activo

### 1.1 Datos Generales

| Campo | Descripción |
|-------|-------------|
| **Nombre del Activo** | |
| **Tipo de Activo** | Edificio / Infraestructura / Instalación |
| **Ubicación** | |
| **Dirección** | |
| **Propietario** | |
| **Operador** | |
| **Año de Construcción** | |
| **Superficie Total** | m² |
| **Niveles** | |
| **Ocupación** | personas |

### 1.2 Descripción del Activo

[Descripción narrativa del activo, uso principal, características relevantes para operación]

### 1.3 Ciclo de Vida del Activo

| Etapa | Fecha/Período | Estado |
|-------|---------------|--------|
| Diseño | | Completado |
| Construcción | | Completado |
| Operación actual | | En curso |
| Próxima renovación | | Planificado |
| Fin de vida estimado | | Proyectado |

---

## 2. Propósitos de la Información del Activo

### 2.1 Objetivos de Gestión del Activo

| # | Objetivo | Indicador | Meta |
|---|----------|-----------|------|
| 1 | Maximizar disponibilidad | Uptime de sistemas críticos | >99% |
| 2 | Optimizar costos de O&M | Costo por m² | Benchmark -10% |
| 3 | Cumplimiento normativo | Auditorías aprobadas | 100% |
| 4 | Eficiencia energética | kWh/m²/año | Reducción 5% anual |
| 5 | Satisfacción de ocupantes | Encuestas | >85% |
| 6 | Gestión de riesgos | Incidentes mayores | 0 |

### 2.2 Usos de la Información del Activo

| Uso | Descripción | Responsable | Frecuencia |
|-----|-------------|-------------|------------|
| **Mantenimiento preventivo** | Programar intervenciones según vida útil | FM | Continuo |
| **Mantenimiento correctivo** | Localizar y reparar fallas | FM | Por evento |
| **Gestión de espacios** | Asignar y optimizar espacios | Operaciones | Mensual |
| **Cumplimiento normativo** | Verificar certificaciones y permisos | Legal/HSE | Anual |
| **Gestión energética** | Monitorear y optimizar consumos | Sustentabilidad | Mensual |
| **Presupuesto de O&M** | Planificar gastos operativos | Finanzas | Anual |
| **Planeación de capital** | Renovaciones y mejoras mayores | Dirección | Anual |
| **Respuesta a emergencias** | Localizar sistemas y rutas | Seguridad | Por evento |
| **Renovaciones** | Información base para proyectos | Proyectos | Por proyecto |

---

## 3. Requisitos de Información por Sistema

### 3.1 Información General de Equipos

Todos los equipos deben incluir como mínimo:

| Atributo | Descripción | Obligatorio |
|----------|-------------|-------------|
| ID único | Identificador en sistema FM | Sí |
| Nombre | Descripción del equipo | Sí |
| Tipo | Clasificación del equipo | Sí |
| Ubicación | Nivel, zona, espacio | Sí |
| Fabricante | Marca del equipo | Sí |
| Modelo | Número de modelo | Sí |
| Número de serie | S/N del fabricante | Sí |
| Fecha de instalación | Fecha de puesta en marcha | Sí |
| Garantía | Vigencia y cobertura | Sí |
| Vida útil esperada | Años | Sí |
| Proveedor/Instalador | Empresa que instaló | Sí |
| Contacto de servicio | Teléfono/email | Sí |

### 3.2 Sistemas Arquitectónicos

#### Envolvente

| Componente | Información Requerida |
|------------|----------------------|
| Muros exteriores | Material, R-value, acabado, mantenimiento |
| Techos | Tipo, impermeabilización, aislamiento, último mantenimiento |
| Ventanas | Tipo de vidrio, marco, U-value, SHGC |
| Puertas exteriores | Material, herrajes, cerraduras |

#### Interiores

| Componente | Información Requerida |
|------------|----------------------|
| Pisos | Material, acabado, área, mantenimiento |
| Muros interiores | Material, acabado, resistencia fuego |
| Plafones | Tipo, altura libre, acceso a plenum |
| Puertas interiores | Tipo, dimensiones, cerraduras |

### 3.3 Sistemas Estructurales

| Componente | Información Requerida |
|------------|----------------------|
| Cimentación | Tipo, capacidad de carga, nivel freático |
| Estructura | Sistema, materiales, capacidad de carga de pisos |
| Juntas | Ubicación, tipo, mantenimiento |

### 3.4 Sistemas Mecánicos (HVAC)

| Equipo | Atributos Específicos |
|--------|----------------------|
| Unidades manejadoras | Capacidad CFM, filtros, motor, bandas |
| Chillers | Capacidad TR, refrigerante, COP |
| Calderas | Capacidad BTU, combustible, eficiencia |
| Bombas | GPM, HP, presión |
| Torres de enfriamiento | Capacidad, tratamiento químico |
| Fancoils/VRF | Capacidad, refrigerante, controles |
| Difusores | Tipo, CFM, ubicación |
| Ductos | Material, aislamiento, limpieza |
| Controles | Sistema BMS, protocolos, puntos |

### 3.5 Sistemas Eléctricos

| Equipo | Atributos Específicos |
|--------|----------------------|
| Subestación | Capacidad kVA, voltajes, protecciones |
| Tableros principales | Capacidad, circuitos, protecciones |
| Transformadores | kVA, relación, enfriamiento |
| Generador emergencia | kW, combustible, autonomía |
| UPS | kVA, autonomía, baterías |
| Luminarias | Tipo, watts, lúmenes, controles |
| Sistemas de control | Iluminación, ocupación, horarios |
| Sistemas especiales | Datos, CCTV, control de acceso |

### 3.6 Sistemas Hidráulicos y Sanitarios

| Equipo | Atributos Específicos |
|--------|----------------------|
| Cisternas | Capacidad, material, tratamiento |
| Bombas | GPM, HP, presión, tipo |
| Calentadores | Capacidad, tipo, eficiencia |
| Muebles sanitarios | Tipo, consumo, marca |
| Tratamiento de agua | Tipo, capacidad, mantenimiento |
| Sistema pluvial | Capacidad, bajadas, drenaje |
| Sistema sanitario | Material, diámetros, conexión municipal |

### 3.7 Sistemas de Protección Contra Incendio

| Equipo | Atributos Específicos |
|--------|----------------------|
| Rociadores | Tipo, cobertura, temperatura |
| Bombas contra incendio | GPM, PSI, pruebas |
| Gabinetes | Ubicación, equipamiento |
| Extintores | Tipo, capacidad, ubicación, vencimiento |
| Detección | Tipo, cobertura, panel |
| Alarmas | Tipo, ubicación, integración |
| Supresión especial | Tipo, agente, áreas protegidas |

### 3.8 Sistemas de Transporte Vertical

| Equipo | Atributos Específicos |
|--------|----------------------|
| Elevadores | Capacidad, velocidad, paradas, marca |
| Escaleras eléctricas | Capacidad, velocidad, dirección |
| Montacargas | Capacidad, dimensiones |

---

## 4. Documentos Requeridos del Activo

### 4.1 Documentos Legales y Administrativos

| Documento | Descripción | Retención | Responsable |
|-----------|-------------|-----------|-------------|
| Escrituras | Propiedad del inmueble | Permanente | Legal |
| Licencia de construcción | Permisos de obra | Permanente | Legal |
| Licencia de uso de suelo | Uso autorizado | Permanente | Legal |
| Dictamen estructural | Condición estructural | 5 años | Mantenimiento |
| Certificado de seguridad | Protección civil | Anual | HSE |
| Pólizas de seguro | Cobertura del activo | Vigente | Finanzas |

### 4.2 Documentos Técnicos

| Documento | Descripción | Formato | Vinculación |
|-----------|-------------|---------|-------------|
| Planos As-Built | Condición final construida | PDF/DWG | AIM |
| Modelo BIM As-Built | Modelo 3D verificado | RVT/IFC | AIM |
| Memorias de cálculo | Diseño estructural, MEP | PDF | Archivo |
| Especificaciones | Materiales y sistemas | PDF | AIM |
| Diagramas unifilares | Sistemas eléctricos | PDF/DWG | AIM |
| Isométricos | Sistemas hidráulicos | PDF/DWG | AIM |
| Balances de aire | Sistemas HVAC | PDF/XLSX | AIM |

### 4.3 Manuales y Guías

| Documento | Descripción | Formato | Vinculación |
|-----------|-------------|---------|-------------|
| Manuales de operación | Por sistema | PDF | Equipo en AIM |
| Manuales de mantenimiento | Por equipo | PDF | Equipo en AIM |
| Fichas técnicas | Por equipo | PDF | Equipo en AIM |
| Procedimientos de emergencia | Respuesta a eventos | PDF | General |
| Guías de usuario | Para ocupantes | PDF | General |

### 4.4 Historial del Activo

| Registro | Descripción | Retención |
|----------|-------------|-----------|
| Órdenes de trabajo | Historial de intervenciones | 5 años |
| Inspecciones | Resultados de inspecciones | 5 años |
| Incidentes | Registro de eventos | 10 años |
| Modificaciones | Cambios al activo | Permanente |
| Consumos | Energía, agua, gas | 5 años |

---

## 5. Estructura del AIM

### 5.1 Organización del Modelo

```
AIM/
├── 01_Modelos/
│   ├── ARQ_AsBuilt.rvt
│   ├── EST_AsBuilt.rvt
│   ├── MEP_AsBuilt.rvt
│   └── COORD_Federado.nwd
│
├── 02_Datos/
│   ├── COBie_[Activo].xlsx
│   ├── Inventario_Equipos.xlsx
│   └── Espacios.xlsx
│
├── 03_Documentos/
│   ├── Legales/
│   ├── Planos/
│   ├── Manuales/
│   └── Certificados/
│
└── 04_Historial/
    ├── Ordenes_Trabajo/
    ├── Inspecciones/
    └── Modificaciones/
```

### 5.2 Entrega COBie

| Hoja COBie | Contenido | Responsable |
|------------|-----------|-------------|
| Facility | Datos del inmueble | FM |
| Floor | Niveles | Arquitectura |
| Space | Espacios | Arquitectura |
| Zone | Zonas funcionales | FM |
| Type | Tipos de equipos | Todas |
| Component | Instancias de equipos | Todas |
| System | Sistemas | MEP |
| Spare | Refacciones | MEP |
| Resource | Recursos necesarios | Todas |
| Job | Tareas de mantenimiento | FM |
| Document | Documentos vinculados | Todas |
| Contact | Proveedores y contactos | FM |

---

## 6. Integración con Sistemas de Gestión

### 6.1 Sistema CMMS/CAFM

| Aspecto | Requisito |
|---------|-----------|
| Plataforma | [Nombre del sistema] |
| Integración | Bidireccional con AIM |
| Datos a sincronizar | Equipos, ubicaciones, OT, historial |
| Frecuencia | Tiempo real / Diaria |

### 6.2 Sistema BMS

| Aspecto | Requisito |
|---------|-----------|
| Plataforma | [Nombre del sistema] |
| Protocolos | BACnet / Modbus / LON |
| Puntos monitoreados | [Cantidad] |
| Datos a integrar | Temperaturas, estados, alarmas |

### 6.3 Medición y Monitoreo

| Sistema | Datos | Frecuencia | Integración |
|---------|-------|------------|-------------|
| Energía eléctrica | kWh, kW demanda | 15 min | Dashboard |
| Gas | m³ | Diaria | Dashboard |
| Agua | m³ | Diaria | Dashboard |
| Condiciones interiores | T°, HR, CO2 | Continuo | BMS |

---

## 7. Mantenimiento de la Información

### 7.1 Actualización del AIM

| Evento | Actualización Requerida | Responsable | Plazo |
|--------|------------------------|-------------|-------|
| Reemplazo de equipo | Actualizar datos del nuevo equipo | FM | 5 días |
| Modificación de espacio | Actualizar modelo y datos | Arquitectura | 10 días |
| Renovación mayor | Actualización completa de zona | Proyectos | Al cierre |
| Cambio de proveedor | Actualizar contactos | Compras | 2 días |

### 7.2 Validación de Información

| Validación | Frecuencia | Responsable | Método |
|------------|------------|-------------|--------|
| Inventario físico | Anual | FM | Recorrido vs AIM |
| Datos de equipos | Semestral | Mantenimiento | Muestreo |
| Documentos vigentes | Trimestral | Administración | Revisión |
| Contactos y garantías | Semestral | Compras | Verificación |

### 7.3 Control de Calidad

| Métrica | Definición | Meta |
|---------|------------|------|
| Completitud | Campos llenos / Campos requeridos | >95% |
| Precisión | Datos correctos / Datos verificados | >98% |
| Actualidad | Registros actualizados en plazo | >90% |
| Disponibilidad | Tiempo de acceso a información | <30 seg |

---

## 8. Seguridad y Acceso

### 8.1 Clasificación de Información

| Nivel | Ejemplos | Acceso |
|-------|----------|--------|
| Público | Información general del edificio | Sin restricción |
| Interno | Layouts, contactos | Personal autorizado |
| Confidencial | Sistemas de seguridad, unifilares | Solo FM y Seguridad |
| Restringido | Accesos, claves | Solo autorizados |

### 8.2 Roles y Permisos

| Rol | Ver | Editar | Aprobar | Admin |
|-----|-----|--------|---------|-------|
| Director de Activos | ✓ | ✓ | ✓ | ✓ |
| Gerente FM | ✓ | ✓ | ✓ | |
| Supervisor | ✓ | ✓ | | |
| Técnico | ✓ (asignados) | | | |
| Ocupante | Limitado | | | |

---

## 9. Anexos

### Anexo A: Lista de Sistemas del Activo

| Código | Sistema | Ubicación | Criticidad |
|--------|---------|-----------|------------|
| HVAC-01 | Aire acondicionado central | Cuarto de máquinas | Alta |
| ELEC-01 | Subestación principal | Subestación | Crítica |
| HIDR-01 | Sistema hidroneumático | Cuarto de bombas | Alta |
| | | | |

### Anexo B: Contactos de Proveedores

| Sistema | Proveedor | Contacto | Teléfono | Contrato |
|---------|-----------|----------|----------|----------|
| Elevadores | | | | |
| HVAC | | | | |
| Eléctrico | | | | |
| | | | | |

### Anexo C: Calendario de Mantenimiento Mayor

| Sistema | Actividad | Frecuencia | Próxima Fecha |
|---------|-----------|------------|---------------|
| HVAC | Limpieza de ductos | 2 años | |
| Elevadores | Modernización | 15 años | |
| Impermeabilización | Renovación | 10 años | |
| | | | |

---

**BIMAC Studio** | www.bimacstudio.com

*Este documento es propiedad de BIMAC Studio. Su reproducción o distribución requiere autorización.*
