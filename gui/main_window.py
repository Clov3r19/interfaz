"""Ventana principal con las dos pestañas independientes."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui import theme
from gui.compiler_view import VistaCompilador
from gui.sets_view import VistaConjuntos

TITULO = "Teoría Matemática de la Computación — Práctica Integral"


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITULO)
        self.geometry("1240x800")
        self.minsize(1050, 700)
        theme.aplicar_estilos(self)

        ttk.Label(self, text=TITULO, style="Titulo.TLabel").pack(anchor="w", padx=16, pady=(12, 0))
        ttk.Label(
            self, style="Suave.TLabel",
            text="Compiladores de Dominio Específico · Álgebra de Conjuntos · Lenguajes Regulares",
        ).pack(anchor="w", padx=16, pady=(0, 6))

        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        pestanas.add(VistaCompilador(pestanas), text="Compilador DSL")
        pestanas.add(VistaConjuntos(pestanas), text="Conjuntos y Lenguajes")
