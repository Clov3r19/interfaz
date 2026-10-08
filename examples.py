"""Datos de prueba de la práctica (los usa la interfaz y las pruebas automáticas)."""

# Prueba 1: receta de 7 pasos sin errores.
RECETA_VALIDA = """\
# Pan de tomate
AGREGAR 2 tazas harina
AGREGAR 1 pizca sal
PICAR 3 tomates en cubos
MEZCLAR harina tomates sal
CALENTAR 180 grados
HORNEAR 30 minutos
SERVIR plato
"""

# Prueba 2: cuatro tipos de error sintáctico, uno léxico y líneas válidas intercaladas.
RECETA_CON_ERRORES = """\
AGREGAR 2 tazas harina
PICAR 3 tomates
CORTAR cebolla
MEZCLAR harina
CALENTAR 180 minutos
FREIR 5 minutos
HORNEAR 30 minutos
AGREGAR 2 tazas
AGREGAR 1 @sal
SERVIR plato
"""

RECETAS = {
    "Prueba 1 — Receta de 7 pasos (válida)": RECETA_VALIDA,
    "Prueba 2 — Receta con errores": RECETA_CON_ERRORES,
}

# Prueba 3: conjuntos con enteros, racionales y símbolos.
EJEMPLOS_CONJUNTOS = {
    "Prueba 3 — Enteros, racional y símbolos": ("{1, 2, 3, -4, 1/2, x}", "{2, 3, 5, x, y}"),
    "Variante — Decimales, 0 y equivalentes": ("{0, 7, -3, 0.75, 4/2, 2, pi, x}", "{2, 3/4, x, z}"),
}

# Pruebas 4 y 5: alfabetos.
EJEMPLOS_ALFABETOS = {
    "Prueba 4 — Σ = {a,b}": "{a,b}",
    "Prueba 5 — Σ = {0,1}": "{0,1}",
    "Variante — Σ = {x,y,z}": "{x,y,z}",
}
