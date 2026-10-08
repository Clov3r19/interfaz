"""Punto de entrada: python main.py"""
import sys


def main() -> int:
    try:
        from gui.main_window import VentanaPrincipal
    except ImportError as error:
        print("No se pudo iniciar la interfaz (¿está instalado Tkinter?):", error)
        return 1

    VentanaPrincipal().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
