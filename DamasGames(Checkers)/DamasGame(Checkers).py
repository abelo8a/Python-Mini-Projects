import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar, QLabel
from PyQt6.QtCore import Qt, QPoint, QTimer
# CORREGIDO: Se añade QFont a las importaciones de QtGui
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class TableroDamas(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 400, 400)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Maneja el turno del jugador humano apoyando piezas normales (2) y Reinas (4)."""
        if not self.main_window.game_active or self.main_window.turno_actual != "HUMANO":
            return

        box_size = 50
        col = int(event.position().x() // box_size)
        fila = int(event.position().y() // box_size)

        if not (0 <= fila < 8 and 0 <= col < 8):
            return

        # Seleccionar pieza humana (normal 2 o reina 4)
        if self.main_window.MyBoard[fila][col] in (2, 4):
            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos_humano(fila, col)
            self.main_window.status_bar.showMessage(f"Ficha seleccionada en ({fila}, {col})")

        # Ejecutar movimiento seleccionado
        elif (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # Si fue un salto de captura, eliminar la pieza roja intermedia
            if abs(fila - f_origen) == 2:
                f_intermedia = int((fila + f_origen) // 2)
                c_intermedia = int((col + c_origen) // 2)
                self.main_window.MyBoard[f_intermedia][c_intermedia] = 0
                self.main_window.status_bar.showMessage(f"¡Has capturado una ficha enemiga!")
                self.main_window.actualizar_contadores_interfaz()
            else:
                self.main_window.status_bar.showMessage(f"Movimiento simple a ({fila}, {col})")

            # Trasladar ficha en la matriz
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            # Evaluar si el movimiento genera una coronación
            self.main_window.evaluar_coronacion(fila, col, valor_pieza)

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

        for fila in range(8):
            for col in range(8):
                bg_color = QColor(240, 217, 181) if (fila + col) % 2 == 0 else QColor(181, 136, 99)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(bg_color))
                painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                if self.main_window.pieza_seleccionada == (fila, col):
                    painter.setBrush(QBrush(QColor(0, 255, 255, 80)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                if (fila, col) in self.main_window.movimientos_validos:
                    painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                pieza = self.main_window.MyBoard[fila][col]
                if pieza == 0:
                    continue

                if pieza in (1, 3):  # Rojas
                    color_pieza = QColor(200, 20, 20)
                    color_borde = QColor(100, 5, 5)
                elif pieza in (2, 4):  # Blancas
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

                # Renderizado de corona dorada para Reinas
                if pieza in (3, 4):
                    painter.setPen(QPen(QColor(218, 165, 32), 2))
                    painter.setBrush(QBrush(QColor(255, 215, 0)))

                    puntos_corona = [
                        QPoint(center_x - 10, center_y + 6),
                        QPoint(center_x - 12, center_y - 6),
                        QPoint(center_x - 4, center_y + 0),
                        QPoint(center_x + 0, center_y - 10),
                        QPoint(center_x + 4, center_y + 0),
                        QPoint(center_x + 12, center_y - 6),
                        QPoint(center_x + 10, center_y + 6),
                    ]
                    painter.drawPolygon(puntos_corona)

        painter.end()


# =====================================================================
# SEGUNDA PARTE: MOTOR DE JUEGO, CONTADORES E IA DEL BOT
# =====================================================================

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
        # Fichas Rojas (IA): Primeras 3 filas
        for fila in range(3):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 1

        # Fichas Blancas (Humano): Últimas 3 filas
        for fila in range(5, 8):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 2

    def init_ui(self):
        self.setWindowTitle('Damas Game - IA Laboratory Engine v1.4')
        self.setFixedSize(580, 425)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroDamas(self)

        # --- PANEL DE CONTROL LATERAL DERECHO ---
        self.panel_control = QWidget(self.central_widget)
        self.panel_control.setGeometry(405, 0, 175, 400)
        self.panel_control.setStyleSheet("background-color: #111; border-left: 2px solid #333;")

        font_titulos = QFont('MS Sans Serif', 10, QFont.Weight.Bold)
        font_valores = QFont('MS Sans Serif', 14, QFont.Weight.Bold)

        # Etiquetas de Bajas del Humano (Fichas rojas eliminadas)
        self.label_titulo_humano = QLabel('Comidas por ti:', self.panel_control)
        self.label_titulo_humano.setGeometry(10, 20, 155, 20)
        self.label_titulo_humano.setFont(font_titulos)
        self.label_titulo_humano.setStyleSheet("color: #55FF55; border: none;")

        self.label_bajas_humano = QLabel('0 / 12', self.panel_control)
        self.label_bajas_humano.setGeometry(10, 45, 155, 25)
        self.label_bajas_humano.setFont(font_valores)
        self.label_bajas_humano.setStyleSheet("color: #00FF00; border: none;")

        # Etiquetas de Bajas del BOT (Fichas blancas eliminadas)
        self.label_titulo_bot = QLabel('Comidas por BOT:', self.panel_control)
        self.label_titulo_bot.setGeometry(10, 100, 155, 20)
        self.label_titulo_bot.setFont(font_titulos)
        self.label_titulo_bot.setStyleSheet("color: #FF5555; border: none;")

        self.label_bajas_bot = QLabel('0 / 12', self.panel_control)
        self.label_bajas_bot.setGeometry(10, 125, 155, 25)
        self.label_bajas_bot.setFont(font_valores)
        self.label_bajas_bot.setStyleSheet("color: #FF3333; border: none;")

        # --- BARRA DE ESTADO ---
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tu turno (Fichas Blancas). Elige una pieza.")

    def cambiar_turno(self, nuevo_turno):
        self.turno_actual = nuevo_turno
        if nuevo_turno == "BOT":
            self.status_bar.showMessage("El BOT Rojo está pensando...")
            QTimer.singleShot(600, self.ejecutar_turno_bot)
        else:
            self.status_bar.showMessage("Tu turno (Fichas Blancas).")

    def evaluar_coronacion(self, fila, col, bando):
        if bando == 2 and fila == 0:
            self.MyBoard[fila][col] = 4
            self.status_bar.showMessage(f"👑 ¡Tu pieza se ha coronado como REINA en ({fila}, {col})!")
        elif bando == 1 and fila == 7:
            self.MyBoard[fila][col] = 3
            self.status_bar.showMessage(f"👑 El BOT ha coronado una REINA en ({fila}, {col})")

    def actualizar_contadores_interfaz(self):
        """Escanea la matriz para calcular las bajas de forma exacta en tiempo real."""
        vivas_rojas = 0
        vivas_blancas = 0

        for fila in range(8):
            for col in range(8):
                val = self.MyBoard[fila][col]
                if val in (1, 3):
                    vivas_rojas += 1
                elif val in (2, 4):
                    vivas_blancas += 1

        comidas_por_humano = 12 - vivas_rojas
        comidas_por_bot = 12 - vivas_blancas

        self.label_bajas_humano.setText(f"{comidas_por_humano} / 12")
        self.label_bajas_bot.setText(f"{comidas_por_bot} / 12")

    def calcular_movimientos_validos_humano(self, fila, col):
        self.movimientos_validos.clear()
        tipo_pieza = self.MyBoard[fila][col]

        direcciones_fila = [-1] if tipo_pieza == 2 else [-1, 1]

        for df in direcciones_fila:
            f_simple = fila + df
            if 0 <= f_simple < 8:
                for c_simple in [col - 1, col + 1]:
                    if 0 <= c_simple < 8 and self.MyBoard[f_simple][c_simple] == 0:
                        self.movimientos_validos.append((f_simple, c_simple))

            f_salto = fila + (df * 2)
            f_intermedia = fila + df
            if 0 <= f_salto < 8:
                for c_dir in [-1, 1]:
                    c_intermedia = col + c_dir
                    c_salto = col + (c_dir * 2)
                    if 0 <= c_salto < 8:
                        vecino = self.MyBoard[f_intermedia][c_intermedia]
                        if vecino in (1, 3) and self.MyBoard[f_salto][c_salto] == 0:
                            self.movimientos_validos.append((f_salto, c_salto))

    def ejecutar_turno_bot(self):
        if not self.game_active:
            return

        capturas_disponibles = []
        movimientos_simples = []

        for fila in range(8):
            for col in range(8):
                tipo_pieza = self.MyBoard[fila][col]

                if tipo_pieza in (1, 3):
                    direcciones_fila = [1] if tipo_pieza == 1 else [-1, 1]

                    for df in direcciones_fila:
                        f_simple = fila + df
                        f_salto = fila + (df * 2)
                        f_intermedia = fila + df

                        if 0 <= f_simple < 8:
                            for c_simple in [col - 1, col + 1]:
                                if 0 <= c_simple < 8 and self.MyBoard[f_simple][c_simple] == 0:
                                    movimientos_simples.append(((fila, col), (f_simple, c_simple)))

                        if 0 <= f_salto < 8:
                            for c_dir in [-1, 1]:
                                c_intermedia = col + c_dir
                                c_salto = col + (c_dir * 2)
                                if 0 <= c_salto < 8:
                                    vecino = self.MyBoard[f_intermedia][c_intermedia]
                                    if vecino in (2, 4) and self.MyBoard[f_salto][c_salto] == 0:
                                        capturas_disponibles.append(
                                            ((fila, col), (f_salto, c_salto), (f_intermedia, c_intermedia)))

        if capturas_disponibles:
            origen, destino, intermedia = random.choice(capturas_disponibles)
            f_orig, c_orig = origen
            f_dest, c_dest = destino
            f_int, c_int = intermedia

            valor_bot = self.MyBoard[f_orig][c_orig]
            self.MyBoard[f_int][c_int] = 0
            self.MyBoard[f_dest][c_dest] = valor_bot
            self.MyBoard[f_orig][c_orig] = 0

            self.evaluar_coronacion(f_dest, c_dest, valor_bot)
            self.status_bar.showMessage(f"El BOT te ha capturado una pieza en ({f_int}, {c_int})")
            self.actualizar_contadores_interfaz()

        elif movimientos_simples:
            origen, destino = random.choice(movimientos_simples)
            f_orig, c_orig = origen
            f_dest, c_dest = destino

            valor_bot = self.MyBoard[f_orig][c_orig]
            self.MyBoard[f_dest][c_dest] = valor_bot
            self.MyBoard[f_orig][c_orig] = 0

            self.evaluar_coronacion(f_dest, c_dest, valor_bot)
            self.status_bar.showMessage(f"El BOT movió de ({f_orig}, {c_orig}) a ({f_dest}, {c_dest})")
        else:
            self.game_active = False
            self.status_bar.showMessage("¡Felicidades! El BOT no tiene movimientos. ¡Ganaste!")
            return

        self.tablero.update()
        self.cambiar_turno("HUMANO")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = DamasGame()
    game.show()
    sys.exit(app.exec())
