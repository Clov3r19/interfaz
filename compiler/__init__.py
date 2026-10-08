"""Compilador del DSL de recetario técnico: lexer -> parser -> generador de código."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from compiler.code_generator import generar_codigo
from compiler.parser import ResultadoAnalisis, analizar


@dataclass
class ResultadoCompilacion:
    analisis: ResultadoAnalisis
    codigo: List[str] = field(default_factory=list)

    @property
    def exitosa(self) -> bool:
        """Éxito = hay al menos una sentencia y ningún error."""
        return bool(self.analisis.sentencias) and not self.analisis.diagnosticos


def compilar(codigo_fuente: str) -> ResultadoCompilacion:
    """Ejecuta el pipeline completo sobre el texto de la receta."""
    analisis = analizar(codigo_fuente)
    codigo = generar_codigo(analisis.sentencias, len(analisis.lineas_con_error))
    return ResultadoCompilacion(analisis, codigo)
