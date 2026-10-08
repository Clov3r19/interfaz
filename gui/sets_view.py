"""Pestaña 'Conjuntos y Lenguajes': álgebra de conjuntos, clasificación, Σ* y gramática."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from examples import EJEMPLOS_ALFABETOS, EJEMPLOS_CONJUNTOS
from gui.widgets import anexar, crear_texto_con_scroll, escribir
from mathematics.kleene import (clausura_por_longitud, contar_cadenas, formula_conteo,
                                mostrar_palabra, parsear_alfabeto)
from mathematics.number_classifier import clasificar, pertenencia
from mathematics.regular_grammar import (derivar, formatear_gramatica, gramatica_acotada,
                                         gramatica_clausura)
from mathematics.sets_operations import (calcular_operaciones, formatear_conjunto,
                                         formatear_elemento, ordenar, parsear_conjunto)

LONGITUD_POR_DEFECTO = 3
LONGITUD_MAXIMA_UI = 6


class VistaConjuntos(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.columnconfigure(0, weight=3, uniform="columna")
        self.columnconfigure(1, weight=2, uniform="columna")
        self.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(self)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        izquierda.columnconfigure(0, weight=1)
        izquierda.rowconfigure(1, weight=1)
        izquierda.rowconfigure(2, weight=1)

        derecha = ttk.Frame(self)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        derecha.columnconfigure(0, weight=1)
        derecha.rowconfigure(1, weight=3)
        derecha.rowconfigure(2, weight=3)

        self._construir_entrada_conjuntos(izquierda)
        self._construir_operaciones(izquierda)
        self._construir_clasificacion(izquierda)
        self._construir_entrada_alfabeto(derecha)
        self._construir_clausura(derecha)
        self._construir_gramatica(derecha)

        self._cargar_conjuntos(next(iter(EJEMPLOS_CONJUNTOS)))
        self._cargar_alfabeto(next(iter(EJEMPLOS_ALFABETOS)))

    # ------------------------------------------------------------------ construcción
    def _construir_entrada_conjuntos(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Conjuntos A y B", padding=8)
        marco.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        marco.columnconfigure(1, weight=1)

        self.entrada_a = ttk.Entry(marco, font=("Consolas", 11))
        self.entrada_b = ttk.Entry(marco, font=("Consolas", 11))
        for fila, (etiqueta, entrada) in enumerate((("A =", self.entrada_a), ("B =", self.entrada_b))):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=(0, 6), pady=2)
            entrada.grid(row=fila, column=1, columnspan=3, sticky="ew", pady=2)

        fila_botones = ttk.Frame(marco)
        fila_botones.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        ttk.Button(fila_botones, text="Calcular", style="Accent.TButton",
                   command=self.calcular_conjuntos).pack(side="left")
        ttk.Button(fila_botones, text="Limpiar", command=self.limpiar_conjuntos).pack(
            side="left", padx=6)
        self.selector_conjuntos = ttk.Combobox(
            fila_botones, values=list(EJEMPLOS_CONJUNTOS), state="readonly", width=38)
        self.selector_conjuntos.pack(side="right")
        self.selector_conjuntos.set("Cargar un ejemplo…")
        self.selector_conjuntos.bind(
            "<<ComboboxSelected>>", lambda _e: self._cargar_conjuntos(self.selector_conjuntos.get()))
        self.entrada_a.bind("<Return>", lambda _e: self.calcular_conjuntos())
        self.entrada_b.bind("<Return>", lambda _e: self.calcular_conjuntos())

    def _construir_operaciones(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Operaciones de conjuntos", padding=6)
        marco.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        contenedor, self.texto_operaciones = crear_texto_con_scroll(marco, alto=10)
        contenedor.grid(row=0, column=0, sticky="nsew")

    def _construir_clasificacion(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Clasificación numérica de A", padding=6)
        marco.grid(row=2, column=0, sticky="nsew")
        marco.rowconfigure(0, weight=1)

        columnas = ("elemento", "n", "z", "q", "simbolo")
        self.tabla_clases = ttk.Treeview(marco, columns=columnas, show="headings", height=6)
        for columna, titulo, ancho in (("elemento", "Elemento", 80), ("n", "N", 36),
                                       ("z", "Z", 36), ("q", "Q", 36), ("simbolo", "Símbolo", 64)):
            self.tabla_clases.heading(columna, text=titulo)
            self.tabla_clases.column(columna, width=ancho, anchor="center", stretch=False)
        self.tabla_clases.column("elemento", anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_clases.yview)
        self.tabla_clases.configure(yscrollcommand=barra.set)
        self.tabla_clases.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        barra.grid(row=0, column=1, sticky="ns")

        contenedor, self.texto_clases = crear_texto_con_scroll(marco, alto=6)
        contenedor.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        marco.columnconfigure(2, weight=1)

    def _construir_entrada_alfabeto(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Alfabeto Σ", padding=8)
        marco.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Σ =").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.entrada_alfabeto = ttk.Entry(marco, font=("Consolas", 11))
        self.entrada_alfabeto.grid(row=0, column=1, columnspan=3, sticky="ew")
        self.entrada_alfabeto.bind("<Return>", lambda _e: self.generar_clausura())

        ttk.Label(marco, text="Longitud máxima k:").grid(row=1, column=0, columnspan=2,
                                                          sticky="w", pady=(6, 0))
        self.longitud = tk.IntVar(value=LONGITUD_POR_DEFECTO)
        ttk.Spinbox(marco, from_=0, to=LONGITUD_MAXIMA_UI, width=4, textvariable=self.longitud,
                    state="readonly").grid(row=1, column=2, sticky="w", pady=(6, 0))

        fila_botones = ttk.Frame(marco)
        fila_botones.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        ttk.Button(fila_botones, text="Generar Σ*", style="Accent.TButton",
                   command=self.generar_clausura).pack(side="left")
        ttk.Button(fila_botones, text="Limpiar", command=self.limpiar_alfabeto).pack(
            side="left", padx=6)
        self.selector_alfabetos = ttk.Combobox(
            fila_botones, values=list(EJEMPLOS_ALFABETOS), state="readonly", width=24)
        self.selector_alfabetos.pack(side="right")
        self.selector_alfabetos.set("Cargar un ejemplo…")
        self.selector_alfabetos.bind(
            "<<ComboboxSelected>>", lambda _e: self._cargar_alfabeto(self.selector_alfabetos.get()))

    def _construir_clausura(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Clausura de Kleene Σ* (|w| ≤ k)", padding=6)
        marco.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        contenedor, self.texto_clausura = crear_texto_con_scroll(marco, alto=8)
        contenedor.grid(row=0, column=0, sticky="nsew")

    def _construir_gramatica(self, padre) -> None:
        marco = ttk.LabelFrame(padre, text="Gramática regular derecha G = (VN, VT, P, S)", padding=6)
        marco.grid(row=2, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        contenedor, self.texto_gramatica = crear_texto_con_scroll(marco, alto=8, ajuste="none")
        contenedor.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------ ejemplos y limpieza
    def _cargar_conjuntos(self, nombre: str) -> None:
        if nombre not in EJEMPLOS_CONJUNTOS:
            return
        a, b = EJEMPLOS_CONJUNTOS[nombre]
        for entrada, valor in ((self.entrada_a, a), (self.entrada_b, b)):
            entrada.delete(0, "end")
            entrada.insert(0, valor)
        self._borrar_resultados_conjuntos()

    def _cargar_alfabeto(self, nombre: str) -> None:
        if nombre not in EJEMPLOS_ALFABETOS:
            return
        self.entrada_alfabeto.delete(0, "end")
        self.entrada_alfabeto.insert(0, EJEMPLOS_ALFABETOS[nombre])
        self._borrar_resultados_alfabeto()

    def _borrar_resultados_conjuntos(self) -> None:
        escribir(self.texto_operaciones)
        escribir(self.texto_clases)
        self.tabla_clases.delete(*self.tabla_clases.get_children())

    def _borrar_resultados_alfabeto(self) -> None:
        escribir(self.texto_clausura)
        escribir(self.texto_gramatica)

    def limpiar_conjuntos(self) -> None:
        self.entrada_a.delete(0, "end")
        self.entrada_b.delete(0, "end")
        self.selector_conjuntos.set("Cargar un ejemplo…")
        self._borrar_resultados_conjuntos()

    def limpiar_alfabeto(self) -> None:
        self.entrada_alfabeto.delete(0, "end")
        self.selector_alfabetos.set("Cargar un ejemplo…")
        self._borrar_resultados_alfabeto()

    # ------------------------------------------------------------------ conjuntos
    def calcular_conjuntos(self) -> None:
        try:
            a = parsear_conjunto(self.entrada_a.get())
            b = parsear_conjunto(self.entrada_b.get())
        except ValueError as error:
            messagebox.showwarning("Entrada inválida", str(error))
            return
        resultado = calcular_operaciones(a, b)
        self._mostrar_operaciones(a, b, resultado)
        self._mostrar_clasificacion(a)

    def _mostrar_operaciones(self, a, b, r) -> None:
        escribir(self.texto_operaciones)
        texto = self.texto_operaciones
        fuera_ab = formatear_conjunto(a - b)
        fuera_ba = formatear_conjunto(b - a)
        lineas = [
            ("A", formatear_conjunto(a)),
            ("B", formatear_conjunto(b)),
            ("|A|", str(r.cardinal_a)),
            ("|B|", str(r.cardinal_b)),
            ("A ∪ B", formatear_conjunto(r.union)),
            ("A ∩ B", formatear_conjunto(r.interseccion)),
            ("A \\ B", formatear_conjunto(r.diferencia_ab)),
            ("B \\ A", formatear_conjunto(r.diferencia_ba)),
            ("A △ B", formatear_conjunto(r.diferencia_simetrica)),
        ]
        for nombre, valor in lineas:
            anexar(texto, f"{nombre:<6}= ", "titulo")
            anexar(texto, valor + "\n")
        for nombre, cumple, sobrantes in (("A ⊆ B", r.a_contenido_en_b, fuera_ab),
                                          ("B ⊆ A", r.b_contenido_en_a, fuera_ba)):
            anexar(texto, f"{nombre:<6}: ", "titulo")
            if cumple:
                anexar(texto, "Verdadero\n", "ok")
            else:
                anexar(texto, f"Falso — elementos fuera: {sobrantes}\n", "error")

    # ------------------------------------------------------------------ clasificación
    def _mostrar_clasificacion(self, a) -> None:
        self.tabla_clases.delete(*self.tabla_clases.get_children())
        for elemento in ordenar(a):
            en_n, en_z, en_q = pertenencia(elemento)
            es_simbolo = not en_q
            marcas = ["✔" if bandera else "·" for bandera in (en_n, en_z, en_q, es_simbolo)]
            self.tabla_clases.insert("", "end", values=(formatear_elemento(elemento), *marcas))

        clases = clasificar(a)
        escribir(self.texto_clases)
        grupos = (
            ("Naturales N = {x ∈ Z | x ≥ 0}", clases.naturales),
            ("Enteros Z (negativos, Z \\ N)", clases.enteros),
            ("Racionales Q (no enteros, Q \\ Z)", clases.racionales),
            ("Símbolos no numéricos", clases.simbolos),
        )
        for titulo, elementos in grupos:
            anexar(self.texto_clases, titulo + "\n", "titulo")
            anexar(self.texto_clases, "  " + formatear_conjunto(elementos) + "\n")
        anexar(self.texto_clases,
               "Las colecciones son disjuntas; como N ⊂ Z ⊂ Q, cada elemento se ubica en la "
               "clase más pequeña que lo contiene.", "suave")

    # ------------------------------------------------------------------ Σ* y gramática
    def generar_clausura(self) -> None:
        try:
            alfabeto = parsear_alfabeto(self.entrada_alfabeto.get())
            k = int(self.longitud.get())
            grupos = clausura_por_longitud(alfabeto, k)
        except (ValueError, tk.TclError) as error:
            messagebox.showwarning("Entrada inválida", str(error))
            return
        self._mostrar_clausura(alfabeto, k, grupos)
        self._mostrar_gramatica(alfabeto, k, grupos)

    def _mostrar_clausura(self, alfabeto, k, grupos) -> None:
        texto = self.texto_clausura
        escribir(texto)
        n = len(alfabeto)
        anexar(texto, f"Σ = {{{', '.join(alfabeto)}}},  |Σ| = {n},  k = {k}\n", "titulo")
        anexar(texto, f"Total = {formula_conteo(n, k)} cadenas\n\n")
        for longitud, palabras in grupos.items():
            anexar(texto, f"Longitud {longitud} ({len(palabras)}):  ", "suave")
            anexar(texto, "  ".join(mostrar_palabra(p) for p in palabras) + "\n")

    def _mostrar_gramatica(self, alfabeto, k, grupos) -> None:
        texto = self.texto_gramatica
        escribir(texto)
        completa = gramatica_clausura(alfabeto)
        acotada = gramatica_acotada(alfabeto, k)
        palabra_ejemplo = grupos[k][-1]

        anexar(texto, "Gramática para Σ* completa\n", "titulo")
        anexar(texto, formatear_gramatica(completa, "G") + "\n")
        anexar(texto, "Derivación de " + mostrar_palabra(palabra_ejemplo) + ":\n  "
               + derivar(completa, palabra_ejemplo) + "\n\n")
        anexar(texto, f"Gramática restringida a |w| ≤ {k}\n", "titulo")
        anexar(texto, formatear_gramatica(acotada, f"G{k}") + "\n")
        anexar(texto, "Derivación de " + mostrar_palabra(palabra_ejemplo) + ":\n  "
               + derivar(acotada, palabra_ejemplo) + "\n")
