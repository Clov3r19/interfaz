"""Colores, fuentes y estilos ttk compartidos por todas las vistas."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

COLOR_FONDO = "#eef1f7"
COLOR_PANEL = "#ffffff"
COLOR_PRIMARIO = "#1f4e8c"
COLOR_TEXTO = "#1d2433"
COLOR_SUAVE = "#5b6577"
COLOR_OK = "#1b7f3b"
COLOR_ERROR = "#b3261e"
COLOR_ERROR_FONDO = "#fde7e5"
COLOR_CODIGO_FONDO = "#fbfcfe"
COLOR_GUTTER = "#e3e8f1"

FUENTE_UI = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI Semibold", 10)
FUENTE_TITULO = ("Segoe UI Semibold", 16)
FUENTE_CODIGO = ("Consolas", 11)


def aplicar_estilos(raiz: tk.Tk) -> None:
    raiz.configure(background=COLOR_FONDO)
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")

    estilo.configure(".", font=FUENTE_UI, background=COLOR_FONDO, foreground=COLOR_TEXTO)
    estilo.configure("TFrame", background=COLOR_FONDO)
    estilo.configure("TLabel", background=COLOR_FONDO)
    estilo.configure("TLabelframe", background=COLOR_FONDO, bordercolor="#c5cde0")
    estilo.configure("TLabelframe.Label", background=COLOR_FONDO,
                     foreground=COLOR_PRIMARIO, font=FUENTE_NEGRITA)

    estilo.configure("TButton", padding=(12, 5), background="#dfe5f1", bordercolor="#c5cde0")
    estilo.map("TButton", background=[("active", "#cdd7ea")])
    estilo.configure("Accent.TButton", background=COLOR_PRIMARIO, foreground="#ffffff",
                     font=FUENTE_NEGRITA)
    estilo.map("Accent.TButton", background=[("active", "#173c6e")])

    estilo.configure("TNotebook", background=COLOR_FONDO, tabmargins=(2, 6, 2, 0))
    estilo.configure("TNotebook.Tab", padding=(18, 8), font=FUENTE_NEGRITA,
                     background="#d5dcec")
    estilo.map("TNotebook.Tab", background=[("selected", COLOR_PANEL)],
               foreground=[("selected", COLOR_PRIMARIO)])

    estilo.configure("Treeview", rowheight=24, background=COLOR_PANEL,
                     fieldbackground=COLOR_PANEL, bordercolor="#c5cde0")
    estilo.configure("Treeview.Heading", font=FUENTE_NEGRITA, background="#dfe5f1")
    estilo.configure("Titulo.TLabel", font=FUENTE_TITULO, foreground=COLOR_PRIMARIO)
    estilo.configure("Suave.TLabel", foreground=COLOR_SUAVE)
