"""Gramática formal G = (VN, VT, P, S) del recetario técnico.

Los terminales son los tipos de token que produce el lexer; NL representa el
fin de línea. La gramática es LL(1), por eso basta un parser de descenso
recursivo sin retroceso.
"""
from __future__ import annotations

from typing import Dict, List

SIMBOLO_INICIAL = "PROGRAMA"

NO_TERMINALES: List[str] = [
    "PROGRAMA", "LINEA", "SENTENCIA", "AGREGACION", "CORTE", "CORTADOR", "MEZCLA",
    "LISTA_ID", "CALOR", "HORNEADO", "SERVICIO", "OPT_UNIDAD", "PARAMS",
]

TERMINALES: List[str] = [
    "AGREGAR", "PICAR", "CORTAR", "MEZCLAR", "CALENTAR", "HORNEAR", "SERVIR",
    "NUMERO", "UNIDAD_CANTIDAD", "UNIDAD_TEMPERATURA", "UNIDAD_TIEMPO",
    "IDENTIFICADOR", "PARAMETRO", "PARAMETRO_FORMA", "NL",
]

PRODUCCIONES: Dict[str, List[str]] = {
    "PROGRAMA": ["LINEA PROGRAMA", "ε"],
    "LINEA": ["SENTENCIA NL", "NL"],
    "SENTENCIA": ["AGREGACION", "CORTE", "MEZCLA", "CALOR", "HORNEADO", "SERVICIO"],
    "AGREGACION": ["AGREGAR NUMERO OPT_UNIDAD IDENTIFICADOR PARAMS"],
    "CORTE": ["CORTADOR NUMERO OPT_UNIDAD IDENTIFICADOR PARAMS"],
    "CORTADOR": ["PICAR", "CORTAR"],
    "MEZCLA": ["MEZCLAR IDENTIFICADOR LISTA_ID PARAMS"],
    "LISTA_ID": ["IDENTIFICADOR LISTA_ID", "IDENTIFICADOR"],
    "CALOR": ["CALENTAR NUMERO UNIDAD_TEMPERATURA PARAMS"],
    "HORNEADO": ["HORNEAR NUMERO UNIDAD_TIEMPO PARAMS"],
    "SERVICIO": ["SERVIR IDENTIFICADOR PARAMS"],
    "OPT_UNIDAD": ["UNIDAD_CANTIDAD", "ε"],
    "PARAMS": ["PARAMETRO PARAMS", "PARAMETRO_FORMA PARAMS", "ε"],
}


def describir_gramatica() -> str:
    """Texto legible con VN, VT, P y S para mostrar en la interfaz."""
    lineas = [
        "G = (VN, VT, P, S)",
        "",
        "VN = {" + ", ".join(NO_TERMINALES) + "}",
        "",
        "VT = {" + ", ".join(TERMINALES) + "}",
        "",
        f"S = {SIMBOLO_INICIAL}",
        "",
        "P:",
    ]
    for izquierda in NO_TERMINALES:
        lineas.append(f"  {izquierda:<11} → " + "  |  ".join(PRODUCCIONES[izquierda]))
    lineas += [
        "",
        "Notas:",
        "  • Los comentarios (# ...) y los espacios no producen tokens.",
        "  • LISTA_ID obliga a que MEZCLAR reciba al menos dos ingredientes.",
        "  • Las instrucciones no distinguen mayúsculas de minúsculas.",
    ]
    return "\n".join(lineas)
