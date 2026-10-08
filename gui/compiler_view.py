"""Pestaña 'Compilador DSL': editor de recetas, tokens, diagnósticos y código generado."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from compiler import ResultadoCompilacion, compilar
from compiler.grammar import describir_gramatica
from examples import RECETAS
from gui import theme
from gui.widgets import anexar, crear_texto_con_scroll, escribir

ESTADO_INICIAL = ("●  Sin analizar", theme.COLOR_SUAVE)


class VistaCompilador(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.columnconfigure(0, weight=1, uniform="columna")
        self.columnconfigure(1, weight=1, uniform="columna")
        self.rowconfigure(1, weight=1, uniform="fila")
        self.rowconfigure(2, weight=1, uniform="fila")

        self._construir_barra()
        self._construir_editor()
        self._construir_tokens()
        self._construir_diagnosticos()
        self._construir_codigo()

        self._cargar_receta(next(iter(RECETAS)))
        self.bind_all("<Control-Return>", lambda _e: self.analizar())

    # ------------------------------------------------------------------ construcción
    def _construir_barra(self) -> None:
        barra = ttk.Frame(self)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Button(barra, text="Analizar", style="Accent.TButton",
                   command=self.analizar).pack(side="left")
        ttk.Button(barra, text="Limpiar", command=self.limpiar).pack(side="left", padx=6)

        ttk.Label(barra, text="Ejemplo:").pack(side="left", padx=(18, 4))
        self.selector = ttk.Combobox(barra, values=list(RECETAS), state="readonly", width=38)
        self.selector.pack(side="left")
        self.selector.set("Cargar un ejemplo…")
        self.selector.bind("<<ComboboxSelected>>", lambda _e: self._cargar_receta(self.selector.get()))

        ttk.Button(barra, text="Ver gramática", command=self._mostrar_gramatica).pack(
            side="left", padx=12)

        self.etiqueta_estado = tk.Label(barra, font=theme.FUENTE_NEGRITA, background=theme.COLOR_FONDO)
        self.etiqueta_estado.pack(side="right")
        self._poner_estado(*ESTADO_INICIAL)

    def _construir_editor(self) -> None:
        marco = ttk.LabelFrame(self, text="Receta (Ctrl+Enter para analizar)", padding=6)
        marco.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(0, weight=1)

        fuente = theme.FUENTE_CODIGO
        self.numeros = tk.Text(marco, width=4, font=fuente, background=theme.COLOR_GUTTER,
                               foreground=theme.COLOR_SUAVE, relief="flat", takefocus=0,
                               padx=4, pady=6, state="disabled", highlightthickness=0)
        self.numeros.tag_configure("derecha", justify="right")
        self.editor = tk.Text(marco, wrap="none", font=fuente, undo=True, relief="solid",
                              borderwidth=1, background=theme.COLOR_CODIGO_FONDO,
                              foreground=theme.COLOR_TEXTO, padx=8, pady=6,
                              highlightthickness=0, insertbackground=theme.COLOR_TEXTO)
        self.editor.tag_configure("linea_error", background=theme.COLOR_ERROR_FONDO)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self._desplazar)
        self.editor.configure(yscrollcommand=lambda a, b: self._al_desplazar(barra, a, b))

        self.numeros.grid(row=0, column=0, sticky="ns")
        self.editor.grid(row=0, column=1, sticky="nsew")
        barra.grid(row=0, column=2, sticky="ns")
        self.editor.bind("<<Modified>>", self._al_modificar)

    def _construir_tokens(self) -> None:
        marco = ttk.LabelFrame(self, text="Tokens", padding=6)
        marco.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("linea", "tipo", "lexema", "categoria")
        self.tabla_tokens = ttk.Treeview(marco, columns=columnas, show="headings")
        for columna, titulo, ancho in (("linea", "Línea", 55), ("tipo", "Token", 160),
                                       ("lexema", "Lexema", 130), ("categoria", "Categoría", 150)):
            self.tabla_tokens.heading(columna, text=titulo)
            self.tabla_tokens.column(columna, width=ancho, anchor="w", stretch=columna != "linea")
        self.tabla_tokens.tag_configure("error", foreground=theme.COLOR_ERROR,
                                        background=theme.COLOR_ERROR_FONDO)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_tokens.yview)
        self.tabla_tokens.configure(yscrollcommand=barra.set)
        self.tabla_tokens.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")

    def _construir_diagnosticos(self) -> None:
        marco = ttk.LabelFrame(self, text="Errores y diagnósticos", padding=6)
        marco.grid(row=2, column=0, sticky="nsew", padx=(0, 6))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        contenedor, self.texto_diagnosticos = crear_texto_con_scroll(marco)
        contenedor.grid(row=0, column=0, sticky="nsew")

    def _construir_codigo(self) -> None:
        marco = ttk.LabelFrame(self, text="Código generado (ensamblador)", padding=6)
        marco.grid(row=2, column=1, sticky="nsew", padx=(6, 0))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        contenedor, self.texto_codigo = crear_texto_con_scroll(marco, ajuste="none")
        contenedor.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------ editor con números de línea
    def _desplazar(self, *argumentos) -> None:
        self.editor.yview(*argumentos)
        self.numeros.yview(*argumentos)

    def _al_desplazar(self, barra, primero, ultimo) -> None:
        barra.set(primero, ultimo)
        self.numeros.yview_moveto(primero)

    def _al_modificar(self, _evento=None) -> None:
        if self.editor.edit_modified():
            self._actualizar_numeros()
            self.editor.edit_modified(False)

    def _actualizar_numeros(self) -> None:
        total = int(self.editor.index("end-1c").split(".")[0])
        self.numeros.configure(state="normal")
        self.numeros.delete("1.0", "end")
        self.numeros.insert("1.0", "\n".join(str(n) for n in range(1, total + 1)), "derecha")
        self.numeros.configure(state="disabled")
        self.numeros.yview_moveto(self.editor.yview()[0])

    # ------------------------------------------------------------------ acciones
    def _poner_estado(self, texto: str, color: str) -> None:
        self.etiqueta_estado.configure(text=texto, foreground=color)

    def _cargar_receta(self, nombre: str) -> None:
        if nombre not in RECETAS:
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", RECETAS[nombre])
        self._limpiar_resultados()

    def _limpiar_resultados(self) -> None:
        self.editor.tag_remove("linea_error", "1.0", "end")
        self.tabla_tokens.delete(*self.tabla_tokens.get_children())
        escribir(self.texto_diagnosticos)
        escribir(self.texto_codigo)
        self._poner_estado(*ESTADO_INICIAL)

    def limpiar(self) -> None:
        self.editor.delete("1.0", "end")
        self.selector.set("Cargar un ejemplo…")
        self._limpiar_resultados()

    def analizar(self) -> None:
        codigo_fuente = self.editor.get("1.0", "end-1c")
        try:
            resultado = compilar(codigo_fuente)
        except Exception as error:  # defensa: la interfaz nunca debe cerrarse por un fallo interno
            messagebox.showerror("Error interno", f"No se pudo analizar la receta:\n{error}")
            return
        self._mostrar_resultado(resultado)

    def _mostrar_gramatica(self) -> None:
        ventana = tk.Toplevel(self)
        ventana.title("Gramática del recetario técnico")
        ventana.geometry("820x520")
        contenedor, texto = crear_texto_con_scroll(ventana, ajuste="none")
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)
        escribir(texto, describir_gramatica())

    # ------------------------------------------------------------------ presentación de resultados
    def _mostrar_resultado(self, resultado: ResultadoCompilacion) -> None:
        analisis = resultado.analisis
        self._limpiar_resultados()

        for token in analisis.tokens:
            etiqueta = ("error",) if token.tipo == "ERROR" else ()
            self.tabla_tokens.insert("", "end", tags=etiqueta, values=(
                token.linea, token.tipo, token.lexema, token.categoria))

        for linea in analisis.lineas_con_error:
            self.editor.tag_add("linea_error", f"{linea}.0", f"{linea}.end+1c")

        self._mostrar_diagnosticos(resultado)
        escribir(self.texto_codigo)
        for linea in resultado.codigo:
            if linea.startswith(";"):
                etiqueta = "suave"
            elif linea.startswith("CALL"):
                etiqueta = "llamada"
            elif linea == "HALT":
                etiqueta = "halt"
            else:
                etiqueta = None
            anexar(self.texto_codigo, linea + "\n", etiqueta)

        errores = len(analisis.diagnosticos)
        if resultado.exitosa:
            self._poner_estado("●  Compilación exitosa", theme.COLOR_OK)
        elif not analisis.sentencias and not errores:
            self._poner_estado("●  No hay instrucciones que compilar", theme.COLOR_SUAVE)
        else:
            self._poner_estado(f"●  Compilación con {errores} error(es)", theme.COLOR_ERROR)

    def _mostrar_diagnosticos(self, resultado: ResultadoCompilacion) -> None:
        analisis = resultado.analisis
        if not analisis.tokens:
            anexar(self.texto_diagnosticos, "No hay instrucciones: escriba una receta y pulse Analizar.\n",
                   "suave")
            return
        if not analisis.diagnosticos:
            anexar(self.texto_diagnosticos,
                   f"✔ Sin errores. {len(analisis.sentencias)} instrucción(es) válida(s) "
                   f"en {analisis.lineas_leidas} línea(s) analizada(s).\n", "ok")
            return
        anexar(self.texto_diagnosticos,
               f"✘ {len(analisis.diagnosticos)} error(es) en {analisis.lineas_leidas} línea(s). "
               f"Se tradujeron {len(analisis.sentencias)} instrucción(es) válida(s).\n\n", "error")
        for diagnostico in analisis.diagnosticos:
            anexar(self.texto_diagnosticos, str(diagnostico) + "\n", "error")
