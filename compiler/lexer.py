"""Analizador léxico (scanner) del DSL de recetario técnico.

Cada tipo de token se define con una expresión regular. Todas se combinan en
una única expresión "maestra" con grupos con nombre. El orden de la lista
importa: Python prueba las alternativas de izquierda a derecha, por eso las
instrucciones y las unidades van antes que el identificador genérico.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

COMANDOS = ("AGREGAR", "PICAR", "CORTAR", "MEZCLAR", "CALENTAR", "HORNEAR", "SERVIR")

# Una palabra termina donde no hay otra letra, dígito o guion bajo.
_FIN_PALABRA = r"(?!\w)"


@dataclass(frozen=True)
class EspecificacionToken:
    """Define un tipo de token: nombre, expresión regular y categoría."""

    nombre: str
    patron: str
    categoria: str
    descripcion: str
    ignorar: bool = False


ESPECIFICACIONES: List[EspecificacionToken] = (
    [
        EspecificacionToken("COMENTARIO", r"#[^\n]*", "Comentario",
                            "Texto libre desde # hasta el fin de la línea", ignorar=True),
        EspecificacionToken("ESPACIO", r"[ \t\r]+", "Espacio",
                            "Espacios y tabuladores", ignorar=True),
    ]
    + [
        EspecificacionToken(comando, comando + _FIN_PALABRA, "Instrucción",
                            f"Palabra reservada {comando}")
        for comando in COMANDOS
    ]
    + [
        EspecificacionToken("NUMERO", r"\d+(?:\.\d+)?(?![\w.])", "Cantidad",
                            "Entero o decimal sin signo"),
        EspecificacionToken("PARAMETRO_FORMA",
                            r"en\s+(?:cubos|rodajas|tiras|trozos|juliana)" + _FIN_PALABRA,
                            "Parámetro semántico", "Forma del corte: 'en' + forma"),
        EspecificacionToken("PARAMETRO",
                            r"(?:fino|fina|grueso|gruesa|suave|lento|rapido|rápido|fuerte)"
                            + _FIN_PALABRA,
                            "Parámetro semántico", "Modificador de la acción"),
        EspecificacionToken("UNIDAD_TEMPERATURA",
                            r"(?:grados|°C|celsius)" + _FIN_PALABRA,
                            "Unidad de medida", "Unidad de temperatura"),
        EspecificacionToken("UNIDAD_TIEMPO",
                            r"(?:segundos?|minutos?|horas?|seg|min|h)" + _FIN_PALABRA,
                            "Unidad de medida", "Unidad de tiempo"),
        EspecificacionToken("UNIDAD_CANTIDAD",
                            r"(?:tazas?|gramos?|kilogramos?|kg|g|mililitros?|ml|litros?|l"
                            r"|cucharadas?|cucharaditas?|piezas?|pizcas?|dientes?)"
                            + _FIN_PALABRA,
                            "Unidad de medida", "Unidad de masa, volumen o conteo"),
        EspecificacionToken("IDENTIFICADOR", r"[^\W\d]\w*", "Identificador",
                            "Nombre de ingrediente o utensilio (letra seguida de letras/dígitos)"),
        EspecificacionToken("ERROR", r"\S+", "Error léxico",
                            "Cualquier secuencia que no encaja en los tokens anteriores"),
    ]
)

CATEGORIA_POR_TIPO: Dict[str, str] = {e.nombre: e.categoria for e in ESPECIFICACIONES}

_REGEX_MAESTRA = re.compile(
    "|".join(f"(?P<{e.nombre}>{e.patron})" for e in ESPECIFICACIONES),
    re.IGNORECASE,
)
_IGNORADOS = {e.nombre for e in ESPECIFICACIONES if e.ignorar}


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    linea: int
    columna: int

    @property
    def categoria(self) -> str:
        return CATEGORIA_POR_TIPO[self.tipo]


def tokenizar_linea(texto: str, numero_linea: int) -> List[Token]:
    """Convierte una línea de texto en tokens (sin espacios ni comentarios)."""
    tokens: List[Token] = []
    for coincidencia in _REGEX_MAESTRA.finditer(texto):
        tipo = coincidencia.lastgroup
        if tipo in _IGNORADOS:
            continue
        tokens.append(Token(tipo, coincidencia.group(), numero_linea, coincidencia.start() + 1))
    return tokens


def tokenizar(codigo: str) -> List[Token]:
    """Tokeniza todo el programa fuente, línea por línea."""
    tokens: List[Token] = []
    for numero, texto in enumerate(codigo.splitlines(), start=1):
        tokens.extend(tokenizar_linea(texto, numero))
    return tokens
