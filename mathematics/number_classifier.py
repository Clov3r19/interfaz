"""Clasificación de los elementos de A en N, Z, Q y símbolos no numéricos.

N = {x ∈ Z | x ≥ 0}.  Se cumple N ⊂ Z ⊂ Q.  Para obtener colecciones
DISJUNTAS cada elemento se asigna a la clase más pequeña que lo contiene:
  naturales  = N            (enteros ≥ 0)
  enteros    = Z \\ N        (enteros negativos)
  racionales = Q \\ Z        (racionales no enteros)
  simbolos   = todo lo que no es número
Los irracionales (π, √2) no son representables de forma exacta, por lo que
se tratan como símbolos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import FrozenSet, List, Tuple

from mathematics.sets_operations import Elemento, ordenar


@dataclass
class Clasificacion:
    naturales: List[Elemento] = field(default_factory=list)
    enteros: List[Elemento] = field(default_factory=list)
    racionales: List[Elemento] = field(default_factory=list)
    simbolos: List[Elemento] = field(default_factory=list)


def pertenencia(elemento: Elemento) -> Tuple[bool, bool, bool]:
    """Devuelve (∈ N, ∈ Z, ∈ Q) para un elemento."""
    if not isinstance(elemento, Fraction):
        return (False, False, False)
    es_entero = elemento.denominator == 1
    return (es_entero and elemento >= 0, es_entero, True)


def clasificar(conjunto: FrozenSet[Elemento]) -> Clasificacion:
    resultado = Clasificacion()
    for elemento in ordenar(conjunto):
        en_n, en_z, en_q = pertenencia(elemento)
        if en_n:
            resultado.naturales.append(elemento)
        elif en_z:
            resultado.enteros.append(elemento)
        elif en_q:
            resultado.racionales.append(elemento)
        else:
            resultado.simbolos.append(elemento)
    return resultado
