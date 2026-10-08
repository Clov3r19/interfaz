"""Componentes reutilizables: áreas de texto de solo lectura con barra de desplazamiento."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple

from gui import theme


def crear_texto_con_scroll(padre, alto: int = 8, ajuste: str = "word",
                           solo_lectura: bool = True) -> Tuple[ttk.Frame, tk.Text]:
    """Devuelve (marco, texto). El llamador coloca el marco con grid/pack."""
    marco = ttk.Frame(padre)
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)

    texto = tk.Text(
        marco, height=alto, width=10, wrap=ajuste, font=theme.FUENTE_CODIGO,
        background=theme.COLOR_CODIGO_FONDO, foreground=theme.COLOR_TEXTO,
        relief="solid", borderwidth=1, highlightthickness=0, padx=8, pady=6, undo=not solo_lectura,
    )
    barra = ttk.Scrollbar(marco, orient="vertical", command=texto.yview)
    texto.configure(yscrollcommand=barra.set)
    texto.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")

    texto.tag_configure("error", foreground=theme.COLOR_ERROR)
    texto.tag_configure("ok", foreground=theme.COLOR_OK, font=theme.FUENTE_CODIGO + ("bold",))
    texto.tag_configure("titulo", foreground=theme.COLOR_PRIMARIO,
                        font=theme.FUENTE_CODIGO + ("bold",))
    texto.tag_configure("suave", foreground=theme.COLOR_SUAVE)
    texto.tag_configure("llamada", foreground="#0b5cad")
    texto.tag_configure("halt", foreground=theme.COLOR_OK, font=theme.FUENTE_CODIGO + ("bold",))
    if solo_lectura:
        texto.configure(state="disabled")
    return marco, texto


def escribir(texto: tk.Text, contenido: str = "", etiqueta: Optional[str] = None) -> None:
    """Reemplaza todo el contenido de un Text de solo lectura."""
    texto.configure(state="normal")
    texto.delete("1.0", "end")
    if contenido:
        texto.insert("end", contenido, etiqueta or ())
    texto.configure(state="disabled")


def anexar(texto: tk.Text, contenido: str, etiqueta: Optional[str] = None) -> None:
    """Agrega texto al final de un Text de solo lectura."""
    texto.configure(state="normal")
    texto.insert("end", contenido, etiqueta or ())
    texto.configure(state="disabled")
