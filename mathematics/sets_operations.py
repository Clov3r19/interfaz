"""Álgebra de conjuntos sobre elementos mixtos (enteros, racionales, símbolos).

Los números se guardan como `Fraction` (aritmética exacta), de modo que
2, 4/2 y 2.0 son el mismo elemento. Todo lo que no sea un número válido se
trata como símbolo (cadena).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from typing import FrozenSet, List, Union

Elemento = Union[Fraction, str]

_ENTERO = re.compile(r"^[+-]?\d+$")
_FRACCION = re.compile(r"^[+-]?\d+\s*/\s*\d+$")
_DECIMAL = re.compile(r"^[+-]?(?:\d+\.\d+|\.\d+)$")
_ETIQUETA = re.compile(r"^\s*\w+\s*=\s*(\{.*\})\s*$", re.DOTALL)


def parsear_elemento(texto: str) -> Elemento:
    """Interpreta un elemento: número exacto (Fraction) o símbolo (str)."""
    limpio = texto.strip()
    if _ENTERO.match(limpio) or _DECIMAL.match(limpio):
        return Fraction(limpio)
    if _FRACCION.match(limpio):
        compacto = re.sub(r"\s+", "", limpio)
        if int(compacto.split("/")[1]) == 0:
            raise ValueError(f"División entre cero en el elemento '{limpio}'.")
        return Fraction(compacto)
    return limpio


def parsear_conjunto(texto: str) -> FrozenSet[Elemento]:
    """Convierte '{1, 2, 1/2, x}' (con o sin llaves, con o sin 'A =') en un conjunto."""
    contenido = texto.strip()
    etiquetado = _ETIQUETA.match(contenido)
    if etiquetado:
        contenido = etiquetado.group(1)

    if contenido.startswith("{") or contenido.endswith("}"):
        if not (contenido.startswith("{") and contenido.endswith("}")):
            raise ValueError("Las llaves del conjunto no están balanceadas.")
        contenido = contenido[1:-1]
    if "{" in contenido or "}" in contenido:
        raise ValueError("No se admiten conjuntos anidados ni llaves dentro de los elementos.")

    elementos = [parte for parte in (p.strip() for p in contenido.split(",")) if parte]
    return frozenset(parsear_elemento(e) for e in elementos)


def clave_orden(elemento: Elemento):
    """Números primero (por valor), luego símbolos (alfabéticamente)."""
    if isinstance(elemento, Fraction):
        return (0, elemento)
    return (1, elemento)


def ordenar(conjunto) -> List[Elemento]:
    return sorted(conjunto, key=clave_orden)


def formatear_elemento(elemento: Elemento) -> str:
    return str(elemento)


def formatear_conjunto(conjunto) -> str:
    if not conjunto:
        return "∅"
    return "{" + ", ".join(formatear_elemento(e) for e in ordenar(conjunto)) + "}"


@dataclass
class ResultadoOperaciones:
    cardinal_a: int
    cardinal_b: int
    union: FrozenSet[Elemento]
    interseccion: FrozenSet[Elemento]
    diferencia_ab: FrozenSet[Elemento]
    diferencia_ba: FrozenSet[Elemento]
    diferencia_simetrica: FrozenSet[Elemento]
    a_contenido_en_b: bool
    b_contenido_en_a: bool


def calcular_operaciones(a: FrozenSet[Elemento], b: FrozenSet[Elemento]) -> ResultadoOperaciones:
    """Calcula |A|, |B|, ∪, ∩, A\\B, B\\A, △ y las dos contenciones."""
    return ResultadoOperaciones(
        cardinal_a=len(a),
        cardinal_b=len(b),
        union=a | b,
        interseccion=a & b,
        diferencia_ab=a - b,
        diferencia_ba=b - a,
        diferencia_simetrica=(a - b) | (b - a),
        a_contenido_en_b=a <= b,
        b_contenido_en_a=b <= a,
    )
