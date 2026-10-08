import unittest

from compiler import compilar
from compiler.lexer import tokenizar
from examples import RECETA_CON_ERRORES, RECETA_VALIDA


class PruebasLexer(unittest.TestCase):
    def test_tipos_de_token(self):
        tipos = [t.tipo for t in tokenizar("AGREGAR 2 tazas harina")]
        self.assertEqual(tipos, ["AGREGAR", "NUMERO", "UNIDAD_CANTIDAD", "IDENTIFICADOR"])

    def test_parametro_forma_y_comentario(self):
        tipos = [t.tipo for t in tokenizar("PICAR 3 tomates en cubos # nota")]
        self.assertEqual(tipos, ["PICAR", "NUMERO", "IDENTIFICADOR", "PARAMETRO_FORMA"])

    def test_instrucciones_sin_distinguir_mayusculas(self):
        self.assertEqual(tokenizar("servir plato")[0].tipo, "SERVIR")

    def test_simbolo_desconocido_es_error_lexico(self):
        self.assertEqual(tokenizar("AGREGAR 1 @sal")[2].tipo, "ERROR")


class PruebasCompilador(unittest.TestCase):
    def test_prueba_1_receta_valida(self):
        resultado = compilar(RECETA_VALIDA)
        self.assertTrue(resultado.exitosa)
        self.assertEqual(len(resultado.analisis.sentencias), 7)
        self.assertEqual(resultado.codigo[-1], "HALT")
        self.assertIn("CALL sys.hornear", resultado.codigo)

    def test_ejemplo_del_enunciado(self):
        resultado = compilar("AGREGAR 2 tazas harina\nPICAR 3 tomates\nMEZCLAR harina tomates\n")
        self.assertEqual(resultado.codigo[1:5], [
            "MOV R1, 2", 'MOV R2, "tazas"', 'MOV R3, "harina"', "CALL sys.agregar"])
        self.assertIn("CALL sys.mezclar", resultado.codigo)

    def test_prueba_2_errores_con_linea_y_continuacion(self):
        resultado = compilar(RECETA_CON_ERRORES)
        self.assertFalse(resultado.exitosa)
        self.assertEqual(resultado.analisis.lineas_con_error, [3, 4, 5, 6, 8, 9])
        mensajes = [str(d) for d in resultado.analisis.diagnosticos]
        self.assertTrue(mensajes[0].startswith(
            "Línea 3: Error sintáctico — se esperaba una cantidad numérica"))
        # Las líneas válidas 1, 2, 7 y 10 siguen traduciéndose.
        self.assertEqual([s.linea for s in resultado.analisis.sentencias], [1, 2, 7, 10])
        self.assertEqual(resultado.codigo[-1], "HALT")

    def test_programa_vacio_no_es_exitoso(self):
        self.assertFalse(compilar("").exitosa)
        self.assertEqual(compilar("# solo comentario").codigo, [])

    def test_sobran_elementos(self):
        diagnosticos = compilar("SERVIR plato mesa").analisis.diagnosticos
        self.assertEqual(len(diagnosticos), 1)
        self.assertIn("sobran elementos", diagnosticos[0].mensaje)


if __name__ == "__main__":
    unittest.main()
