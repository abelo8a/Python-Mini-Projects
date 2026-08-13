import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class TableroDamas(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 400, 400)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Maneja el turno del jugador humano (Fichas Blancas = 2)."""
        if not self.main_window.game_active or self.main_window.turno_actual != "HUMANO":
            return

        box_size = 50
        col = int(event.position().x() // box_size)
        fila = int(event.position().y() // box_size)

        if not (0 <= fila < 8 and 0 <= col < 8):
            return

        # 1. SELECCIONAR PIEZA BLANCA
        if self.main_window.MyBoard[fila][col] == 2:
            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos_humano(fila, col)
            self.main_window.status_bar.showMessage(f"Ficha seleccionada en ({fila}, {col})")

        # 2. EJECUTAR MOVIMIENTO SELECCIONADO
        elif (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # Si fue un salto de captura, eliminar la pieza roja intermedia
            if abs(fila - f_origen) == 2:
                f_intermedia = int((fila + f_origen) // 2)
                c_intermedia = int((col + c_origen) // 2)
                self.main_window.MyBoard[f_intermedia][c_intermedia] = 0
                self.main_window.status_bar.showMessage(f"¡Has capturado una ficha enemiga!")

            # Trasladar ficha en la matriz
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            # Limpiar selección y transferir turno al BOT
            self.main_window.pieza_seleccionada = None
            self.main_window.movimientos_validos.clear()
            self.update()

            self.main_window.cambiar_turno("BOT")

        else:
            self.main_window.pieza_seleccionada = None
            self.main_window.movimientos_validos.clear()
            self.main_window.status_bar.showMessage("Selección cancelada.")
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        box_size = 50
        radius = box_size / 2

        # 1. DIBUJAR CASILLAS
        for fila in range(8):
            for col in range(8):
                bg_color = QColor(240, 217, 181) if (fila + col) % 2 == 0 else QColor(181, 136, 99)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(bg_color))
                painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # Resaltado azul de pieza seleccionada
                if self.main_window.pieza_seleccionada == (fila, col):
                    painter.setBrush(QBrush(QColor(0, 255, 255, 80)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # Resaltado verde de movimientos posibles
                if (fila, col) in self.main_window.movimientos_validos:
                    painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # 2. DIBUJAR PIEZAS
                pieza = self.main_window.MyBoard[fila][col]
                if pieza == 0:
                    continue

                if pieza == 1:  # Rojas
                    color_pieza = QColor(200, 20, 20)
                    color_borde = QColor(100, 5, 5)
                elif pieza == 2:  # Blancas
                    color_pieza = QColor(240, 240, 240)
                    color_borde = QColor(150, 150, 150)

                center_x = int((col * box_size) + radius)
                center_y = int((fila * box_size) + radius)
                radio_pieza = int(radius * 0.8)

                painter.setPen(QPen(color_borde, 3))
                painter.setBrush(QBrush(color_pieza))
                painter.drawEllipse(QPoint(center_x, center_y), radio_pieza, radio_pieza)

                painter.setPen(QPen(color_borde, 1, Qt.PenStyle.DotLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPoint(center_x, center_y), int(radio_pieza * 0.6), int(radio_pieza * 0.6))

        painter.end()


class DamasGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.MyBoard = [[0 for _ in range(8)] for _ in range(8)]
        self.game_active = True

        self.pieza_seleccionada = None
        self.movimientos_validos = []
        self.turno_actual = "HUMANO"

        self.init_board_setup()
        self.init_ui()

    def init_board_setup(self):
        for fila in range(3):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 1

        for fila in range(5, 8):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 2

    def init_ui(self):
        self.setWindowTitle('Damas Game - IA Laboratory Engine v1.2')
        self.setFixedSize(580, 425)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroDamas(self)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tu turno (Fichas Blancas). Elige una pieza.")

    def cambiar_turno(self, nuevo_turno):
        """Alterna el control del juego e invoca el delay del BOT."""
        self.turno_actual = nuevo_turno
        if nuevo_turno == "BOT":
            self.status_bar.showMessage("El BOT Rojo está pensando...")
            QTimer.singleShot(600, self.ejecutar_turno_bot)
        else:
            self.status_bar.showMessage("Tu turno (Fichas Blancas).")

    def calcular_movimientos_validos_humano(self, fila, col):
        """Calcula las diagonales superiores válidas y capturas del Humano."""
        self.movimientos_validos.clear()

        # Movimiento simple (Blanco sube: fila - 1)
        f_simple = fila - 1
        if f_simple >= 0:
            for c_simple in [col - 1, col + 1]:
                if 0 <= c_simple < 8 and self.MyBoard[f_simple][c_simple] == 0:
                    self.movimientos_validos.append((f_simple, c_simple))

        # Capturas (Blanco salta 2 casillas)
        f_salto = fila - 2
        f_intermedia = fila - 1
        if f_salto >= 0:
            for c_dir in [-1, 1]:
                c_intermedia = col + c_dir
                c_salto = col + (c_dir * 2)
                if 0 <= c_salto < 8:
                    if self.MyBoard[f_intermedia][c_intermedia] == 1 and self.MyBoard[f_salto][c_salto] == 0:
                        self.movimientos_validos.append((f_salto, c_salto))

    def ejecutar_turno_bot(self):
        """Cerebro de la IA Roja (1. Captura obligatoria, 2. Movimiento Simple)"""
        if not self.game_active:
            return

        capturas_disponibles = []
        movimientos_simples = []

        # ESCANEAR TODO EL TABLERO BUSCANDO OPCIONES PARA LAS FICHAS ROJAS (1)
        for fila in range(8):
            for col in range(8):
                if self.MyBoard[fila][col] == 1:
                    f_simple = fila + 1
                    f_salto = fila + 2
                    f_intermedia = fila + 1

                    # Verificar movimientos simples hacia abajo
                    if f_simple < 8:
                        for c_simple in [col - 1, col + 1]:
                            if 0 <= c_simple < 8 and self.MyBoard[f_simple][c_simple] == 0:
                                movimientos_simples.append(((fila, col), (f_simple, c_simple)))

                    # Verificar saltos de captura sobre fichas blancas (2)
                    if f_salto < 8:
                        for c_dir in [-1, 1]:
                            c_intermedia = col + c_dir
                            c_salto = col + (c_dir * 2)
                            if 0 <= c_salto < 8:
                                if self.MyBoard[f_intermedia][c_intermedia] == 2 and self.MyBoard[f_salto][
                                    c_salto] == 0:
                                    capturas_disponibles.append(
                                        ((fila, col), (f_salto, c_salto), (f_intermedia, c_intermedia)))

        # DECISIÓN LOGICA DE LA IA
        if capturas_disponibles:
            origen, destino, intermedia = random.choice(capturas_disponibles)
            f_orig, c_orig = origen
            f_dest, c_dest = destino
            f_int, c_int = intermedia

            self.MyBoard[f_int][c_int] = 0
            self.MyBoard[f_dest][c_dest] = 1
            self.MyBoard[f_orig][c_orig] = 0
            self.status_bar.showMessage(f"El BOT te ha capturado una pieza en ({f_int}, {c_int})")

        elif movimientos_simples:
            origen, destino = random.choice(movimientos_simples)
            f_orig, c_orig = origen
            f_dest, c_dest = destino

            self.MyBoard[f_dest][c_dest] = 1
            self.MyBoard[f_orig][c_orig] = 0
            self.status_bar.showMessage(f"El BOT movió de ({f_orig}, {c_orig}) a ({f_dest}, {c_dest})")

        else:
            self.game_active = False
            self.status_bar.showMessage("¡Felicidades! El BOT se ha quedado sin movimientos. ¡Ganaste!")
            return

        self.tablero.update()
        self.cambiar_turno("HUMANO")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = DamasGame()
    game.show()
    sys.exit(app.exec())
