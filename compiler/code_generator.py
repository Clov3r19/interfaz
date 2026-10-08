"""Generador de código: sentencias válidas -> ensamblador de máquina abstracta.

Convención de registros (cada sentencia usa R1, R2, ... en orden):
  AGREGAR/PICAR/CORTAR : R1=cantidad, R2=unidad, R3=ingrediente
  MEZCLAR              : R1..Rn = ingredientes
  CALENTAR/HORNEAR     : R1=valor, R2=unidad
  SERVIR               : R1=elemento servido
Los parámetros semánticos (si existen) se cargan en el siguiente registro libre.
Después de cargar los registros se invoca la subrutina del sistema con CALL.
"""
from __future__ import annotations

from typing import List

from compiler.parser import Sentencia

UNIDAD_POR_DEFECTO = "unidad"

SUBRUTINAS = {
    "AGREGAR": "sys.agregar",
    "PICAR": "sys.picar",
    "CORTAR": "sys.cortar",
    "MEZCLAR": "sys.mezclar",
    "CALENTAR": "sys.calentar",
    "HORNEAR": "sys.hornear",
    "SERVIR": "sys.servir",
}


def _traducir(sentencia: Sentencia) -> List[str]:
    valores: List[str] = []
    if sentencia.cantidad is not None:
        valores.append(sentencia.cantidad)
        valores.append(f'"{sentencia.unidad or UNIDAD_POR_DEFECTO}"')
    valores.extend(f'"{ingrediente}"' for ingrediente in sentencia.ingredientes)
    if sentencia.parametros:
        valores.append('"' + ",".join(sentencia.parametros) + '"')

    instrucciones = [f"MOV R{indice}, {valor}" for indice, valor in enumerate(valores, start=1)]
    instrucciones.append(f"CALL {SUBRUTINAS[sentencia.comando]}")
    return instrucciones


def generar_codigo(sentencias: List[Sentencia], lineas_omitidas: int = 0) -> List[str]:
    """Devuelve las líneas del programa ensamblador (vacío si no hay sentencias)."""
    if not sentencias:
        return []

    programa: List[str] = []
    if lineas_omitidas:
        programa.append(f"; AVISO: {lineas_omitidas} línea(s) con error no se tradujeron")
    for sentencia in sentencias:
        programa.append(f"; Línea {sentencia.linea}: {sentencia.texto}")
        programa.extend(_traducir(sentencia))
    programa.append("HALT")
    return programa
