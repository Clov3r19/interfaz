"""Clausura de Kleene truncada: todas las cadenas de Σ* con |w| ≤ k.

Complejidad: el número de cadenas es
    N(n, k) = 1 + n + n² + ... + n^k = (n^(k+1) - 1) / (n - 1)    (n ≥ 2)
que es Θ(n^k): crece exponencialmente en k. Como cada cadena de longitud i
cuesta O(i) construirla, el tiempo total es O(k · n^k) y la memoria también.
Para n = 1 la suma vale k + 1 (crecimiento lineal).
"""
from __future__ import annotations

import re
from itertools import product
from typing import Dict, List

EPSILON = "ε"
MAX_CADENAS = 20000
_PREFIJO = re.compile(r"^\s*(?:Σ|Sigma|sigma)\s*=\s*", re.IGNORECASE)
_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def parsear_alfabeto(texto: str) -> List[str]:
    """Lee 'Σ = {a,b}', '{a,b}' o 'a,b'. Cada símbolo debe ser un único carácter."""
    contenido = _PREFIJO.sub("", texto).strip()
    if contenido.startswith("{") or contenido.endswith("}"):
        if not (contenido.startswith("{") and contenido.endswith("}")):
            raise ValueError("Las llaves del alfabeto no están balanceadas.")
        contenido = contenido[1:-1]

    simbolos: List[str] = []
    for parte in (p.strip() for p in contenido.split(",")):
        if not parte:
            continue
        if len(parte) != 1 or parte == EPSILON:
            raise ValueError(
                f"El símbolo '{parte}' no es válido: cada símbolo debe ser un solo "
                f"carácter distinto de {EPSILON}."
            )
        if parte not in simbolos:
            simbolos.append(parte)
    if not simbolos:
        raise ValueError("El alfabeto debe contener al menos un símbolo (por ejemplo {a,b}).")
    return simbolos


def contar_cadenas(tamano_alfabeto: int, longitud_maxima: int) -> int:
    """1 + n + n² + ... + n^k (se suma directamente para incluir n = 1)."""
    return sum(tamano_alfabeto ** i for i in range(longitud_maxima + 1))


def formula_conteo(tamano_alfabeto: int, longitud_maxima: int) -> str:
    """Texto como '1 + 2 + 2² + 2³ = 15'."""
    terminos = []
    for i in range(longitud_maxima + 1):
        if i == 0:
            terminos.append("1")
        elif i == 1:
            terminos.append(str(tamano_alfabeto))
        else:
            terminos.append(f"{tamano_alfabeto}{str(i).translate(_SUPERINDICES)}")
    total = contar_cadenas(tamano_alfabeto, longitud_maxima)
    return " + ".join(terminos) + f" = {total}"


def clausura_por_longitud(alfabeto: List[str], longitud_maxima: int) -> Dict[int, List[str]]:
    """Cadenas agrupadas por longitud; la longitud 0 contiene la palabra vacía ''."""
    if longitud_maxima < 0:
        raise ValueError("La longitud máxima no puede ser negativa.")
    total = contar_cadenas(len(alfabeto), longitud_maxima)
    if total > MAX_CADENAS:
        raise ValueError(
            f"Se generarían {total} cadenas (máximo permitido: {MAX_CADENAS}). "
            "Reduzca el alfabeto o la longitud máxima."
        )
    return {
        longitud: ["".join(combinacion) for combinacion in product(alfabeto, repeat=longitud)]
        for longitud in range(longitud_maxima + 1)
    }


def mostrar_palabra(palabra: str) -> str:
    """La palabra vacía se muestra como ε."""
    return palabra if palabra else EPSILON
