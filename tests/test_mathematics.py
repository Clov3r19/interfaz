import unittest
from fractions import Fraction

from mathematics.kleene import (clausura_por_longitud, contar_cadenas, formula_conteo,
                                parsear_alfabeto)
from mathematics.number_classifier import clasificar
from mathematics.regular_grammar import (derivar, formatear_gramatica, gramatica_acotada,
                                         gramatica_clausura)
from mathematics.sets_operations import (calcular_operaciones, formatear_conjunto,
                                         parsear_conjunto)


class PruebasConjuntos(unittest.TestCase):
    def setUp(self):
        self.a = parsear_conjunto("{1, 2, 3, -4, 1/2, x}")
        self.b = parsear_conjunto("{2, 3, 5, x, y}")
        self.r = calcular_operaciones(self.a, self.b)

    def test_cardinales(self):
        self.assertEqual((self.r.cardinal_a, self.r.cardinal_b), (6, 5))

    def test_operaciones(self):
        self.assertEqual(formatear_conjunto(self.r.union), "{-4, 1/2, 1, 2, 3, 5, x, y}")
        self.assertEqual(formatear_conjunto(self.r.interseccion), "{2, 3, x}")
        self.assertEqual(formatear_conjunto(self.r.diferencia_ab), "{-4, 1/2, 1}")
        self.assertEqual(formatear_conjunto(self.r.diferencia_ba), "{5, y}")
        self.assertEqual(formatear_conjunto(self.r.diferencia_simetrica), "{-4, 1/2, 1, 5, y}")

    def test_contencion(self):
        self.assertFalse(self.r.a_contenido_en_b)
        self.assertFalse(self.r.b_contenido_en_a)
        sub = calcular_operaciones(parsear_conjunto("{2, x}"), self.b)
        self.assertTrue(sub.a_contenido_en_b)

    def test_equivalentes_se_unifican(self):
        self.assertEqual(parsear_conjunto("{2, 4/2, 2.0}"), frozenset({Fraction(2)}))

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            parsear_conjunto("{1, 2")
        with self.assertRaises(ValueError):
            parsear_conjunto("{1/0}")

    def test_conjunto_vacio(self):
        self.assertEqual(formatear_conjunto(parsear_conjunto("{}")), "∅")


class PruebasClasificacion(unittest.TestCase):
    def test_clases_disjuntas(self):
        c = clasificar(parsear_conjunto("{0, 7, -3, 0.75, 2, pi, x}"))
        self.assertEqual([str(e) for e in c.naturales], ["0", "2", "7"])
        self.assertEqual([str(e) for e in c.enteros], ["-3"])
        self.assertEqual([str(e) for e in c.racionales], ["3/4"])
        self.assertEqual(c.simbolos, ["pi", "x"])


class PruebasKleene(unittest.TestCase):
    def test_prueba_4_alfabeto_ab(self):
        grupos = clausura_por_longitud(parsear_alfabeto("Σ = {a,b}"), 3)
        self.assertEqual(grupos[0], [""])
        self.assertEqual(grupos[2], ["aa", "ab", "ba", "bb"])
        self.assertEqual(grupos[3], ["aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb"])
        self.assertEqual(sum(len(g) for g in grupos.values()), 15)

    def test_prueba_5_otro_alfabeto(self):
        grupos = clausura_por_longitud(parsear_alfabeto("0,1,2"), 3)
        self.assertEqual(sum(len(g) for g in grupos.values()), contar_cadenas(3, 3))
        self.assertEqual(contar_cadenas(3, 3), 40)

    def test_formula(self):
        self.assertEqual(formula_conteo(2, 3), "1 + 2 + 2² + 2³ = 15")

    def test_alfabeto_invalido(self):
        for texto in ("{}", "{ab,c}", "{a,b"):
            with self.assertRaises(ValueError):
                parsear_alfabeto(texto)

    def test_limite_de_cadenas(self):
        with self.assertRaises(ValueError):
            clausura_por_longitud(list("abcdefghij"), 5)


class PruebasGramatica(unittest.TestCase):
    def test_gramatica_completa(self):
        g = gramatica_clausura(["a", "b"])
        self.assertIn("S → ε | aS | bS", formatear_gramatica(g))
        self.assertEqual(derivar(g, "ab"), "S ⇒ aS ⇒ abS ⇒ ab")
        self.assertEqual(derivar(g, ""), "S ⇒ ε")

    def test_gramatica_acotada(self):
        g = gramatica_acotada(["a", "b"], 2)
        self.assertEqual(g.no_terminales, ["S", "A₁", "A₂"])
        self.assertEqual(derivar(g, "ba"), "S ⇒ bA₁ ⇒ baA₂ ⇒ ba")
        with self.assertRaises(ValueError):
            derivar(g, "aaa")


if __name__ == "__main__":
    unittest.main()
