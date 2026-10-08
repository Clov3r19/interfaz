# Práctica Integral — Teoría Matemática de la Computación

Aplicación de escritorio (Python + Tkinter) con dos módulos independientes en pestañas:

1. **Compilador DSL**: analizador léxico, sintáctico y generador de código ensamblador para un recetario técnico.
2. **Conjuntos y Lenguajes**: álgebra de conjuntos, clasificación N/Z/Q/símbolos, clausura de Kleene Σ* (|w| ≤ k) y gramática regular derecha.

## Requisitos

- Python 3.9 o superior (probado en Windows con Python 3.9).
- Tkinter (viene incluido en el instalador oficial de Python para Windows; en la instalación marque *tcl/tk and IDLE*).
- **Ninguna librería externa**: solo biblioteca estándar.

## Instalación y ejecución

```bash
python main.py
```

Pruebas automáticas (opcional):

```bash
python -m unittest discover -v
```

## Estructura

```
main.py                      Punto de entrada
examples.py                  Datos de prueba (los usa la GUI y los tests)
gui/                         Capa de presentación (solo Tkinter)
  main_window.py             Ventana y pestañas
  compiler_view.py           Pestaña "Compilador DSL"
  sets_view.py               Pestaña "Conjuntos y Lenguajes"
  theme.py, widgets.py       Estilos y componentes reutilizables
compiler/                    Motor del compilador (sin Tkinter)
  lexer.py                   Tokens y expresiones regulares
  parser.py                  Análisis sintáctico + diagnósticos por línea
  code_generator.py          Traducción a MOV / CALL / HALT
  grammar.py                 Gramática formal G = (VN, VT, P, S) del DSL
mathematics/                 Motor matemático (sin Tkinter)
  sets_operations.py         |A|, ∪, ∩, \, △, ⊆
  number_classifier.py       N, Z, Q, símbolos
  kleene.py                  Σ* hasta longitud k y conteo
  regular_grammar.py         Gramática regular derecha y derivaciones
tests/                       Pruebas unitarias
docs/REPORTE_TECNICO.md      Contenido del reporte técnico (6 secciones)
```

La GUI solo importa de `compiler` y `mathematics`; ninguno de ellos importa Tkinter.

## El lenguaje del recetario

```
AGREGAR  <cantidad> [<unidad>] <ingrediente> [parámetros]
PICAR    <cantidad> [<unidad>] <ingrediente> [parámetros]
CORTAR   <cantidad> [<unidad>] <ingrediente> [parámetros]
MEZCLAR  <ingrediente> <ingrediente>+ [parámetros]
CALENTAR <número> <grados|°C|celsius> [parámetros]
HORNEAR  <número> <segundos|minutos|horas> [parámetros]
SERVIR   <nombre> [parámetros]
```

- Una instrucción por línea; `#` inicia un comentario; no distingue mayúsculas.
- Unidades: `tazas, gramos, kg, ml, litros, cucharadas, cucharaditas, piezas, pizcas, dientes`, tiempo y temperatura.
- Parámetros semánticos: `fino, grueso, suave, lento, rápido, fuerte` y `en cubos|rodajas|tiras|trozos|juliana`.
- Decisiones propias (el PDF no las fija): `MEZCLAR` exige al menos dos ingredientes; si falta la unidad se carga `"unidad"` en R2.

Código generado (convención de registros: R1, R2, … en orden; ver `compiler/code_generator.py`):

```
MOV R1, 2
MOV R2, "tazas"
MOV R3, "harina"
CALL sys.agregar
...
HALT
```

Si hay errores, las líneas válidas igualmente se traducen y la barra de estado indica "Compilación con N error(es)".

## Módulo B: notas

- Elementos: enteros (`-4`), fracciones (`1/2`), decimales (`0.75`) y símbolos (`x`, `pi`). Los números son exactos (`Fraction`): `2`, `4/2` y `2.0` son el mismo elemento, y los decimales se muestran como fracción (`0.75` → `3/4`). Los irracionales (π, √2) no son representables, por eso se tratan como símbolos.
- Clasificación en colecciones **disjuntas**: N (enteros ≥ 0), Z \ N (enteros negativos), Q \ Z (racionales no enteros) y símbolos. La tabla también marca la pertenencia inclusiva (N ⊂ Z ⊂ Q).
- Alfabeto: cada símbolo es un solo carácter. k va de 0 a 6 en la interfaz y se rechazan generaciones de más de 20 000 cadenas.
- Complejidad: |Σ*≤k| = 1 + n + n² + … + nᵏ = (n^(k+1) − 1)/(n − 1) = Θ(nᵏ); tiempo O(k·nᵏ) (ver el reporte).

## Pruebas manuales (datos exactos)

Se cargan desde los menús *Ejemplo* de cada sección.

| # | Dónde | Datos | Resultado esperado |
|---|-------|-------|--------------------|
| 1 | Compilador DSL | Ejemplo "Prueba 1" (7 pasos) | "Compilación exitosa" y código terminado en `HALT` |
| 2 | Compilador DSL | Ejemplo "Prueba 2" | 6 errores (líneas 3, 4, 5, 6, 8, 9); se traducen las líneas 1, 2, 7, 10 |
| 3 | Conjuntos | `A = {1, 2, 3, -4, 1/2, x}`, `B = {2, 3, 5, x, y}` | \|A\|=6, \|B\|=5, A∩B={2, 3, x}, A△B={-4, 1/2, 1, 5, y} |
| 4 | Alfabeto | `{a,b}`, k=3 | ε, a, b, aa … bbb (15 cadenas) |
| 5 | Alfabeto | `{0,1}` o `{x,y,z}`, k=3 | 15 y 40 cadenas respectivamente |
