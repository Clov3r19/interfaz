"""Analizador sintáctico (descenso recursivo, una línea = una sentencia).

Cada línea se valida de forma independiente: si una falla, se registra un
diagnóstico con su número de línea y el análisis continúa con la siguiente.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from compiler.lexer import COMANDOS, Token, tokenizar_linea

COMANDOS_CON_CANTIDAD = ("AGREGAR", "PICAR", "CORTAR")
TIPOS_PARAMETRO = ("PARAMETRO", "PARAMETRO_FORMA")


@dataclass
class Sentencia:
    """Nodo del árbol sintáctico para una instrucción válida."""

    linea: int
    comando: str
    texto: str
    cantidad: Optional[str] = None
    unidad: Optional[str] = None
    ingredientes: List[str] = field(default_factory=list)
    parametros: List[str] = field(default_factory=list)


@dataclass
class Diagnostico:
    linea: int
    tipo: str  # "léxico" o "sintáctico"
    mensaje: str

    def __str__(self) -> str:
        return f"Línea {self.linea}: Error {self.tipo} — {self.mensaje}"


@dataclass
class ResultadoAnalisis:
    tokens: List[Token] = field(default_factory=list)
    sentencias: List[Sentencia] = field(default_factory=list)
    diagnosticos: List[Diagnostico] = field(default_factory=list)
    lineas_leidas: int = 0

    @property
    def lineas_con_error(self) -> List[int]:
        return sorted({d.linea for d in self.diagnosticos})


class ErrorSintactico(Exception):
    """Error de una sola línea; lo captura `analizar` y sigue con la siguiente."""


class _Cursor:
    """Recorre la lista de tokens de una línea."""

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._posicion = 0

    def actual(self) -> Optional[Token]:
        if self._posicion < len(self._tokens):
            return self._tokens[self._posicion]
        return None

    def avanzar(self) -> Token:
        token = self._tokens[self._posicion]
        self._posicion += 1
        return token

    def es(self, *tipos: str) -> bool:
        token = self.actual()
        return token is not None and token.tipo in tipos


def _describir(token: Optional[Token]) -> str:
    if token is None:
        return "el fin de la línea"
    if token.tipo == "NUMERO":
        return f"el número {token.lexema}"
    if token.tipo.startswith("UNIDAD_"):
        return f"la unidad '{token.lexema}'"
    if token.tipo in COMANDOS:
        return f"la instrucción {token.lexema.upper()}"
    if token.tipo in TIPOS_PARAMETRO:
        return f"el parámetro '{token.lexema}'"
    return f"el identificador '{token.lexema}'"


def _esperar(cursor: _Cursor, tipo: str, que_se_esperaba: str) -> Token:
    if not cursor.es(tipo):
        raise ErrorSintactico(
            f"se esperaba {que_se_esperaba} (se encontró {_describir(cursor.actual())})"
        )
    return cursor.avanzar()


def _parsear_linea(tokens: List[Token], texto: str, numero: int) -> Sentencia:
    cursor = _Cursor(tokens)
    primero = cursor.actual()
    if primero.tipo not in COMANDOS:
        lista = ", ".join(COMANDOS)
        if primero.tipo == "IDENTIFICADOR":
            raise ErrorSintactico(
                f"instrucción desconocida '{primero.lexema}'; se esperaba una de: {lista}"
            )
        raise ErrorSintactico(
            f"la línea debe iniciar con una instrucción ({lista}); "
            f"se encontró {_describir(primero)}"
        )

    comando = cursor.avanzar().tipo
    sentencia = Sentencia(linea=numero, comando=comando, texto=texto)

    if comando in COMANDOS_CON_CANTIDAD:
        sentencia.cantidad = _esperar(cursor, "NUMERO", "una cantidad numérica").lexema
        if cursor.es("UNIDAD_CANTIDAD"):
            sentencia.unidad = cursor.avanzar().lexema.lower()
        sentencia.ingredientes.append(
            _esperar(cursor, "IDENTIFICADOR", "el nombre de un ingrediente").lexema
        )
    elif comando == "MEZCLAR":
        sentencia.ingredientes.append(
            _esperar(cursor, "IDENTIFICADOR", "el nombre de un ingrediente").lexema
        )
        while cursor.es("IDENTIFICADOR"):
            sentencia.ingredientes.append(cursor.avanzar().lexema)
        if len(sentencia.ingredientes) < 2:
            raise ErrorSintactico(
                "MEZCLAR necesita al menos dos ingredientes "
                f"(solo se encontró '{sentencia.ingredientes[0]}')"
            )
    elif comando == "CALENTAR":
        sentencia.cantidad = _esperar(cursor, "NUMERO", "una temperatura numérica").lexema
        sentencia.unidad = _esperar(
            cursor, "UNIDAD_TEMPERATURA", "una unidad de temperatura (grados, °C, celsius)"
        ).lexema.lower()
    elif comando == "HORNEAR":
        sentencia.cantidad = _esperar(cursor, "NUMERO", "una duración numérica").lexema
        sentencia.unidad = _esperar(
            cursor, "UNIDAD_TIEMPO", "una unidad de tiempo (segundos, minutos, horas)"
        ).lexema.lower()
    else:  # SERVIR
        sentencia.ingredientes.append(
            _esperar(cursor, "IDENTIFICADOR", "el nombre de lo que se sirve").lexema
        )

    while cursor.es(*TIPOS_PARAMETRO):
        sentencia.parametros.append(" ".join(cursor.avanzar().lexema.lower().split()))

    if cursor.actual() is not None:
        raise ErrorSintactico(
            "sobran elementos al final de la línea "
            f"(se encontró {_describir(cursor.actual())})"
        )
    return sentencia


def analizar(codigo: str) -> ResultadoAnalisis:
    """Analiza todo el programa y acumula tokens, sentencias y diagnósticos."""
    resultado = ResultadoAnalisis()
    for numero, texto in enumerate(codigo.splitlines(), start=1):
        tokens = tokenizar_linea(texto, numero)
        resultado.tokens.extend(tokens)
        if not tokens:
            continue
        resultado.lineas_leidas += 1

        errores_lexicos = [t for t in tokens if t.tipo == "ERROR"]
        if errores_lexicos:
            for token in errores_lexicos:
                resultado.diagnosticos.append(Diagnostico(
                    numero, "léxico",
                    f"símbolo no reconocido '{token.lexema}' (columna {token.columna})",
                ))
            continue

        try:
            resultado.sentencias.append(_parsear_linea(tokens, texto.strip(), numero))
        except ErrorSintactico as error:
            resultado.diagnosticos.append(Diagnostico(numero, "sintáctico", str(error)))
    return resultado
