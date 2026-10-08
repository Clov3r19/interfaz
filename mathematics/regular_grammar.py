"""Gramáticas regulares derechas G = (VN, VT, P, S) asociadas a Σ*.

Toda producción tiene la forma  A → ε,  A → a  o  A → aB  (lineal por la
derecha). Aquí se usan A → ε y A → aB, donde a ∈ VT y B ∈ VN.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from mathematics.kleene import EPSILON

_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


@dataclass(frozen=True)
class Produccion:
    izquierda: str
    terminal: Optional[str] = None   # None en A → ε
    siguiente: Optional[str] = None  # None en A → ε

    def lado_derecho(self) -> str:
        if self.terminal is None:
            return EPSILON
        return self.terminal + (self.siguiente or "")


@dataclass
class GramaticaRegular:
    no_terminales: List[str]
    terminales: List[str]
    producciones: List[Produccion]
    inicial: str


def gramatica_clausura(alfabeto: List[str]) -> GramaticaRegular:
    """G para Σ* completa:  S → ε | aS | bS | ..."""
    producciones = [Produccion("S")]
    producciones += [Produccion("S", simbolo, "S") for simbolo in alfabeto]
    return GramaticaRegular(["S"], list(alfabeto), producciones, "S")


def gramatica_acotada(alfabeto: List[str], longitud_maxima: int) -> GramaticaRegular:
    """G_k para Σ^≤k. El no terminal A_i recuerda que ya se leyeron i símbolos.

    S = A₀ → ε | aA₁ | bA₁,  A₁ → ε | aA₂ | ...,  A_k → ε
    """
    def nombre(i: int) -> str:
        return "S" if i == 0 else "A" + str(i).translate(_SUBINDICES)

    no_terminales = [nombre(i) for i in range(longitud_maxima + 1)]
    producciones: List[Produccion] = []
    for i in range(longitud_maxima + 1):
        producciones.append(Produccion(nombre(i)))
        if i < longitud_maxima:
            producciones += [Produccion(nombre(i), s, nombre(i + 1)) for s in alfabeto]
    return GramaticaRegular(no_terminales, list(alfabeto), producciones, "S")


def formatear_gramatica(gramatica: GramaticaRegular, nombre: str = "G") -> str:
    lineas = [
        f"{nombre} = (VN, VT, P, S)",
        f"VN = {{{', '.join(gramatica.no_terminales)}}}",
        f"VT = {{{', '.join(gramatica.terminales)}}}",
        f"S  = {gramatica.inicial}",
        "P  = {",
    ]
    for no_terminal in gramatica.no_terminales:
        lados = [p.lado_derecho() for p in gramatica.producciones if p.izquierda == no_terminal]
        lineas.append(f"       {no_terminal} → " + " | ".join(lados))
    lineas.append("     }")
    return "\n".join(lineas)


def derivar(gramatica: GramaticaRegular, palabra: str) -> str:
    """Derivación por la izquierda:  S ⇒ aS ⇒ abS ⇒ ab."""
    actual = gramatica.inicial
    prefijo = ""
    pasos = [actual]
    for simbolo in palabra:
        produccion = next(
            (p for p in gramatica.producciones
             if p.izquierda == actual and p.terminal == simbolo),
            None,
        )
        if produccion is None:
            raise ValueError(f"La gramática no puede derivar '{palabra}' (falla en '{simbolo}').")
        prefijo += simbolo
        actual = produccion.siguiente
        pasos.append(prefijo + actual)
    if not any(p.izquierda == actual and p.terminal is None for p in gramatica.producciones):
        raise ValueError(f"La gramática no puede terminar la derivación de '{palabra}'.")
    pasos.append(prefijo if prefijo else EPSILON)
    return " ⇒ ".join(pasos)
