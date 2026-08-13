import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class TableroDamas(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 400, 400)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Detecta el clic del mouse y calcula la casilla de la matriz."""
        if not self.main_window.game_active:
            return

        box_size = 50
        col = int(event.position().x() // box_size)
        fila = int(event.position().y() // box_size)

        # Validar límites estrictos de la matriz de damas (8x8)
        if not (0 <= fila < 8 and 0 <= col < 8):
            return

        # 1. SI HACE CLIC EN UNA PIEZA BLANCA (JUGADOR ACTUAL)
        if self.main_window.MyBoard[fila][col] == 2:
            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos(fila, col)
            self.main_window.status_bar.showMessage(f"Pieza seleccionada en casilla: Fila {fila}, Columna {col}")

        # 2. SI HACE CLIC EN UNA CASILLA INDICADA EN VERDE (EJECUTAR MOVIMIENTO / CAPTURA)
        elif (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada

            # CORRECCIÓN DE DETECCIÓN: Traslado físico seguro usando fila y columna de origen correctas
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # Detectar si el movimiento fue un salto de captura (distancia absoluta de 2 filas)
            if abs(fila - f_origen) == 2:
                # Calcular la posición exacta de la pieza intermedia comida
                f_intermedia = int((fila + f_origen) // 2)
                c_intermedia = int((col + c_origen) // 2)
                self.main_window.MyBoard[f_intermedia][c_intermedia] = 0  # Eliminar pieza enemiga
                self.main_window.status_bar.showMessage(
                    f"¡Pieza enemiga capturada en ({f_intermedia}, {c_intermedia})!")
            else:
                self.main_window.status_bar.showMessage(f"Movimiento simple a ({fila}, {col})")

            # Registrar el movimiento en el destino y vaciar el origen
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            # Limpiar la memoria de selección para el siguiente turno
            self.main_window.pieza_seleccionada = None
            self.main_window.movimientos_validos.clear()

        # 3. INTERRUPCIÓN EN ZONA VACÍA: LIMPIAR SELECCIÓN
        else:
            self.main_window.pieza_seleccionada = None
            self.main_window.movimientos_validos.clear()
            self.main_window.status_bar.showMessage("Selección cancelada por el usuario.")

        self.update()  # Forzar refresco visual del tablero

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        box_size = 50
        radius = box_size / 2

        # 1. GENERACIÓN DEL PATRÓN DE ESCAQUES (8x8)
        for fila in range(8):
            for col in range(8):
                if (fila + col) % 2 == 0:
                    bg_color = QColor(240, 217, 181)  # Claro
                else:
                    bg_color = QColor(181, 136, 99)  # Oscuro

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(bg_color))
                painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # ILUMINACIÓN AZUL: Casilla seleccionada
                if self.main_window.pieza_seleccionada == (fila, col):
                    painter.setBrush(QBrush(QColor(0, 255, 255, 80)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # ILUMINACIÓN VERDE: Movimientos viables
                if (fila, col) in self.main_window.movimientos_validos:
                    painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                # 2. RENDERIZADO VECTORIAL DE FICHAS
                pieza = self.main_window.MyBoard[fila][col]
                if pieza == 0:
                    continue

                if pieza == 1:  # Rojas (Enemigo)
                    color_pieza = QColor(200, 20, 20)
                    color_borde = QColor(100, 5, 5)
                elif pieza == 2:  # Blancas (Usuario)
                    color_pieza = QColor(240, 240, 240)
                    color_borde = QColor(150, 150, 150)

                center_x = int((col * box_size) + radius)
                center_y = int((fila * box_size) + radius)
                radio_pieza = int(radius * 0.8)

                painter.setPen(QPen(color_borde, 3))
                painter.setBrush(QBrush(color_pieza))
                painter.drawEllipse(QPoint(center_x, center_y), radio_pieza, radio_pieza)

                # Alivio interno estético
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

        self.init_board_setup()
        self.init_ui()

    def init_board_setup(self):
        # Fichas Rojas: Primeras 3 filas
        for fila in range(3):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 1

        # Fichas Blancas: Últimas 3 filas
        for fila in range(5, 8):
            for col in range(8):
                if (fila + col) % 2 != 0:
                    self.MyBoard[fila][col] = 2

    def init_ui(self):
        self.setWindowTitle('Damas Game - IA Laboratory Engine v1.1')
        self.setFixedSize(580, 425)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroDamas(self)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Engine reparado. Selecciona una ficha blanca.")

    def calcular_movimientos_validos(self, fila, col):
        """Calcula movimientos simples y saltos para capturar piezas rojas."""
        self.movimientos_validos.clear()

        # 1. ESCANEAR MOVIMIENTOS SIMPLES (1 Casilla diagonal hacia adelante)
        fila_simple = fila - 1
        if fila_simple >= 0:
            for col_simple in [col - 1, col + 1]:
                if 0 <= col_simple < 8:
                    if self.MyBoard[fila_simple][col_simple] == 0:
                        self.movimientos_validos.append((fila_simple, col_simple))

        # 2. ESCANEAR SALTOS DE CAPTURA (2 Casillas diagonales para comer pieza roja)
        fila_salto = fila - 2
        fila_intermedia = fila - 1

        if fila_salto >= 0:
            # Evaluar diagonal izquierda
            if col - 2 >= 0:
                if self.MyBoard[fila_intermedia][col - 1] == 1 and self.MyBoard[fila_salto][col - 2] == 0:
                    self.movimientos_validos.append((fila_salto, col - 2))

            # Evaluar diagonal derecha
            if col + 2 < 8:
                if self.MyBoard[fila_intermedia][col + 1] == 1 and self.MyBoard[fila_salto][col + 2] == 0:
                    self.movimientos_validos.append((fila_salto, col + 2))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = DamasGame()
    game.show()
    sys.exit(app.exec())
