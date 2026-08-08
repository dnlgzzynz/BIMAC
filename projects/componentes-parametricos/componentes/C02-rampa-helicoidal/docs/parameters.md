# Tabla de Parametros - C02 Rampa Vehicular Helicoidal

Referencia completa de parametros para diseno de rampas helicoidales vehiculares.

---

## Parametros Geometricos Principales

| Parametro | Tipo | Rango | Default | Unidad | Descripcion |
|-----------|------|-------|---------|--------|-------------|
| `inner_radius` | float | 5 - 15 | 7.5 | m | Radio interior |
| `outer_radius` | float | 8 - 25 | 12.5 | m | Radio exterior |
| `rise_per_turn` | float | 2.5 - 4.0 | 3.0 | m | Altura por vuelta |
| `total_turns` | float | 0.5 - 5.0 | 2.0 | - | Numero de vueltas |
| `slope` | float | 5 - 15 | 10 | % | Pendiente longitudinal |
| `superelevation` | float | 2 - 6 | 4 | % | Peralte transversal |
| `direction` | enum | cw, ccw | cw | - | Direccion de giro |

---

## Diagrama de Geometria

### Vista en Planta

```
           Exterior
              ↓
        ╭─────────────╮
       ╱               ╲
      ╱    ╭───────╮    ╲
     │    ╱         ╲    │
     │   │    ●      │   │     ● = Centro
     │    ╲         ╱    │     Ri = Radio interior
      ╲    ╰───────╯    ╱      Ro = Radio exterior
       ╲               ╱       W = Ancho = Ro - Ri
        ╰─────────────╯
              ↑
           Interior

        ├── Ri ──┤
        ├────── Ro ──────┤
```

### Vista en Seccion

```
     Exterior                Interior
         │                       │
         │      Peralte (e%)     │
         │    ╱─────────────╲    │
         │   ╱               ╲   │
         ├──╱    Pendiente    ╲──┤
         │ ╱     (s%)          ╲ │
         │╱                     ╲│
    ─────┴───────────────────────┴─────
              Ancho (W)
```

---

## Configuracion de Carriles

| Tipo | Carriles | Ancho Carril | Acotamiento Int | Acotamiento Ext | Ancho Total |
|------|----------|--------------|-----------------|-----------------|-------------|
| Simple | 1 | 3.50 m | 0.30 m | 0.50 m | 4.30 m |
| Doble | 2 | 3.25 m | 0.30 m | 0.50 m | 7.30 m |
| Doble separado | 2 | 3.25 m + 0.50 m sep | 0.30 m | 0.50 m | 7.80 m |
| Triple | 3 | 3.00 m | 0.30 m | 0.50 m | 9.80 m |

### Anchos Minimos por Tipo de Vehiculo

| Vehiculo | Ancho | Radio Min Interior | Radio Min Exterior |
|----------|-------|-------------------|-------------------|
| Automovil | 1.8 m | 5.0 m | 8.5 m |
| SUV/Pickup | 2.0 m | 5.5 m | 9.0 m |
| Van | 2.2 m | 6.0 m | 10.0 m |
| Camion ligero | 2.5 m | 7.5 m | 12.0 m |

---

## Pendientes y Peraltes

### Pendientes Recomendadas

| Aplicacion | Pendiente Max | Pendiente Recomendada |
|------------|---------------|----------------------|
| Estacionamiento residencial | 15% | 10-12% |
| Estacionamiento comercial | 12% | 8-10% |
| Estacionamiento publico | 10% | 6-8% |
| Acceso vehicular | 8% | 5-6% |
| Rampas de emergencia | 6% | 4-5% |

### Peralte (Superelevacion)

| Radio Interior | Peralte Minimo | Peralte Maximo |
|----------------|----------------|----------------|
| < 7.5 m | 4% | 6% |
| 7.5 - 10 m | 3% | 5% |
| 10 - 15 m | 2% | 4% |
| > 15 m | 2% | 3% |

### Transicion de Peralte

```
                    Peralte maximo
                   ┌──────────────────────────────┐
                  ╱                                ╲
                 ╱                                  ╲
                ╱      Zona de peralte constante    ╲
               ╱                                      ╲
              ╱                                        ╲
─────────────╱                                          ╲─────────────
   Entrada  ╱←── Transicion ──→╱         ╲←── Transicion ──→╲  Salida
            └─── Lt = 6m ──────┘           └─── Lt = 6m ─────┘
```

---

## Tipos de Estructura

### Losa Maciza

| Parametro | Valor |
|-----------|-------|
| Espesor | claro/30, min 200mm |
| fc' concreto | 28 MPa |
| Refuerzo | Bidireccional |
| Claro maximo | 8 m |

### Losa Nervada

| Parametro | Valor |
|-----------|-------|
| Espesor losa | 100 mm |
| Peralte nervadura | 300-400 mm |
| Ancho nervadura | 200 mm |
| Espaciamiento | 1200 mm |
| Claro maximo | 12 m |

### Estructura Metalica

| Parametro | Valor |
|-----------|-------|
| Vigas radiales | W14x30 a W21x50 |
| Vigas perimetrales | W14x30 a W18x40 |
| Deck | Cal. 20, 75mm |
| Concreto sobre deck | 100 mm |
| Claro maximo beam-beam | 4 m |

---

## Perfiles Estructurales

### Vigas Radiales

| Claro (m) | Perfil Recomendado | Peso (kg/m) |
|-----------|-------------------|-------------|
| < 3.0 | W12x26 | 38.7 |
| 3.0 - 4.0 | W14x30 | 44.6 |
| 4.0 - 5.0 | W16x36 | 53.6 |
| 5.0 - 6.0 | W18x40 | 59.5 |
| > 6.0 | W21x50 | 74.4 |

### Columnas

| Altura (m) | Perfil Redondo | Perfil Cuadrado |
|------------|----------------|-----------------|
| < 4.0 | D400 | 400x400 |
| 4.0 - 6.0 | D450 | 450x450 |
| 6.0 - 8.0 | D500 | 500x500 |
| > 8.0 | D600 | 600x600 |

---

## Barreras Vehiculares

### Perfiles de Barrera

| Tipo | Altura | Base | Tope | Test Level |
|------|--------|------|------|------------|
| F-Shape | 810 mm | 610 mm | 150 mm | TL-4 |
| Jersey | 810 mm | 355 mm | 150 mm | TL-4 |
| Single Slope | 810 mm | 230 mm | 150 mm | TL-4 |
| Low Profile | 510 mm | 355 mm | 150 mm | TL-2 |

### Diagrama Barrera Jersey

```
      ← 150 →
       ┌───┐
       │   │
       │   │ 480mm
      ╱    ╲
     ╱      ╲ 330mm
    ╱        ╲
   └──────────┘
    ← 355mm →
```

### Niveles de Prueba MASH

| Nivel | Vehiculo | Velocidad | Angulo |
|-------|----------|-----------|--------|
| TL-1 | 1100 kg | 50 km/h | 25° |
| TL-2 | 2000 kg | 70 km/h | 25° |
| TL-3 | 2000 kg | 100 km/h | 25° |
| TL-4 | 8000 kg | 90 km/h | 15° |
| TL-5 | 36000 kg | 80 km/h | 15° |

---

## Sistema de Drenaje

### Canal Perimetral

| Parametro | Valor |
|-----------|-------|
| Ubicacion | Borde interior |
| Ancho | 150 mm |
| Profundidad | 100 mm |
| Pendiente | 1% hacia registros |

### Registros de Captacion

| Parametro | Valor |
|-----------|-------|
| Tamano | 450 x 450 mm |
| Profundidad | 600 mm |
| Espaciamiento | 15 m max |
| Rejilla | Antiderrapante |

### Pendiente Transversal

| Direccion | Pendiente |
|-----------|-----------|
| Hacia borde interior | 2% |
| Adicional en curva | Peralte |

---

## Senalizacion

### Marcas Horizontales

| Elemento | Ancho | Color | Tipo |
|----------|-------|-------|------|
| Linea de borde | 100 mm | Blanco | Continua |
| Linea central | 100 mm | Amarillo | Discontinua |
| Flecha direccional | - | Blanco | Cada 15 m |
| Cebra peatonal | 400 mm | Blanco | Zona acceso |

### Senales Verticales

| Senal | Ubicacion | Mensaje |
|-------|-----------|---------|
| Velocidad maxima | Entrada | 15 km/h |
| Altura libre | Entrada | 2.20 m min |
| Direccion | Cada nivel | Flecha |
| Salida | Final | EXIT |

---

## Iluminacion

| Parametro | Valor |
|-----------|-------|
| Nivel de iluminacion | 50 lux min |
| Tipo de luminaria | LED |
| Montaje | Techo |
| Espaciamiento | 6 m |
| Iluminacion emergencia | Si |
| Autonomia emergencia | 90 min |

---

## Formulas de Calculo

### Longitud Desarrollada

```
L = 2 * π * Rc * n

Donde:
  L = Longitud total (m)
  Rc = Radio al centro del carril
  n = Numero de vueltas
```

### Pendiente Real

```
s = (H / L) * 100

Donde:
  s = Pendiente (%)
  H = Altura total de la rampa
  L = Longitud desarrollada
```

### Velocidad de Diseno

```
V = √(127 * R * (e + f))

Donde:
  V = Velocidad (km/h)
  R = Radio (m)
  e = Peralte (decimal)
  f = Friccion (0.16 tipico)
```

---

## Cargas de Diseno

### Cargas Vivas

| Tipo | Carga |
|------|-------|
| Vehiculos livianos | 2.5 kN/m² |
| Vehiculos pesados | 5.0 kN/m² |
| Impacto | 25% adicional |

### Cargas Muertas

| Componente | Carga |
|------------|-------|
| Losa 250mm | 6.0 kN/m² |
| Acabado | 1.0 kN/m² |
| Instalaciones | 0.5 kN/m² |
| Barreras | 8.0 kN/m lineal |

---

## Parametros BIM

| Parametro | Tipo | Grupo |
|-----------|------|-------|
| `BIMAC_Ramp_InnerRadius` | Length | Dimensions |
| `BIMAC_Ramp_OuterRadius` | Length | Dimensions |
| `BIMAC_Ramp_TotalRise` | Length | Dimensions |
| `BIMAC_Ramp_Turns` | Number | Geometry |
| `BIMAC_Ramp_Slope` | Number | Geometry |
| `BIMAC_Ramp_LaneCount` | Integer | Traffic |
| `BIMAC_Ramp_Direction` | Text | Geometry |
| `BIMAC_Ramp_Length` | Length | Quantities |
| `BIMAC_Ramp_Area` | Area | Quantities |
| `BIMAC_Ramp_ConcreteVolume` | Volume | Quantities |
| `BIMAC_Ramp_SteelWeight` | Number | Quantities |

### Clasificacion

| Sistema | Codigo |
|---------|--------|
| Uniclass | Ss_25_70_65 (Ramp structures) |
| OmniClass | 23-13 23 17 (Vehicular Ramps) |
| IFC Class | IfcRamp |
| IFC Type | SPIRAL |

---

## Normativas

| Codigo | Descripcion | Aplicacion |
|--------|-------------|------------|
| IBC | International Building Code | General |
| ACI 318 | Building Code for Concrete | Estructura |
| AISC 360 | Steel Construction | Acero |
| AASHTO | Highway Design | Barreras |
| ITE | Parking Standards | Dimensiones |
| NFPA | Fire Code | Emergencias |
| ADA | Accessibility | Accesibilidad |

---

*Documentacion de parametros v1.0 - C02 Rampa Vehicular Helicoidal*
