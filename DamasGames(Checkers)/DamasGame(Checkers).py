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

        # 1. SELECCIONAR PIEZA HUMANA (Pieza normal = 2, Reina = 4)
        if self.main_window.MyBoard[fila][col] in (2, 4):
            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos_humano(fila, col)
            self.main_window.status_bar.showMessage(f"Ficha seleccionada en ({fila}, {col})")

        # 2. EJECUTAR MOVIMIENTO SELECCIONADO (CON NUEVO BARRIDO INTEGRADO)
        elif (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # NUEVO BARRIDO: Detectar si fue un salto (distancia mayor a 1 cuadro)
            if abs(fila - f_origen) > 1:
                # Determinar el sentido del vector diagonal (-1 o 1)
                paso_f = 1 if fila > f_origen else -1
                paso_c = 1 if col > c_origen else -1

                # Avanzar celda por celda escaneando la línea hasta dar con la pieza comida
                f_scan = f_origen + paso_f
                c_scan = c_origen + paso_c
                while f_scan != fila and c_scan != col:
                    if self.main_window.MyBoard[f_scan][c_scan] in (1, 3):
                        self.main_window.MyBoard[f_scan][c_scan] = 0  # ¡Pieza eliminada!
                        break
                    f_scan += paso_f
                    c_scan += paso_c

                self.main_window.status_bar.showMessage(f"¡Has capturado una ficha enemiga!")
                self.main_window.actualizar_contadores_interfaz()
            else:
                self.main_window.status_bar.showMessage(f"Movimiento simple a ({fila}, {col})")

            # Trasladar la ficha en la matriz real
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            # Evaluar si el movimiento genera una coronación inmediata
            self.main_window.evaluar_coronacion(fila, col, valor_pieza)

            # Limpiar la memoria de selección y transferir el turno al BOT
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

    def obtener_capturas_recursivas_reina(self, fila, col, visitados_piezas=None, vector_anterior=None):
        """
        NUEVO: Escanea de forma recursiva todos los saltos de combo para la Reina Voladora
        impidiendo estrictamente regresar por el vector opuesto.
        """
        if visitados_piezas is None:
            visitados_piezas = set()

        saltos_validos = []
        # Las 4 direcciones diagonales del espacio bidimensional
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in direcciones:
            # REGLA DE NO-RETORNO: Bloquear el vector inverso exacto del salto anterior
            if vector_anterior and (df == -vector_anterior[0] and dc == -vector_anterior[1]):
                continue

            pieza_enemiga_detectada = None
            f_actual, c_actual = fila + df, col + dc

            # Lanzar el rayo vectorial de la Reina Voladora
            while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                val_celda = self.MyBoard[f_actual][c_actual]

                if val_celda == 0:
                    if pieza_enemiga_detectada:
                        # Hemos encontrado una casilla de aterrizaje válida tras saltar al enemigo
                        f_enemiga, c_enemiga = pieza_enemiga_detectada
                        if (f_enemiga, c_enemiga) not in visitados_piezas:
                            # Guardamos este salto válido
                            saltos_validos.append({
                                "destino": (f_actual, c_actual),
                                "comida": (f_enemiga, c_enemiga),
                                "vector": (df, dc)
                            })
                    # Si no hay enemigo aún, la reina sigue deslizándose por las celdas vacías
                elif val_celda in (1, 3): # Enemigo detectado (Rojo normal o Reina)
                    if pieza_enemiga_detectada:
                        break # Bloqueo: No se pueden saltar dos piezas enemigas juntas
                    pieza_enemiga_detectada = (f_actual, c_actual)
                else:
                    break # Bloqueo: Chocó con una pieza aliada propia

                f_actual += df
                c_actual += dc

        return saltos_validos

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
        """Calcula movimientos simples y saltos para peones (2) y Reinas Voladoras (4)."""
        self.movimientos_validos.clear()
        tipo_pieza = self.MyBoard[fila][col]

        # 1. SI ES UN PEÓN NORMAL (Mantiene su lógica de corto alcance hacia arriba)
        if tipo_pieza == 2:
            f_simple = fila - 1
            if f_simple >= 0:
                for c_simple in [col - 1, col + 1]:
                    if 0 <= c_simple < 8 and self.MyBoard[f_simple][c_simple] == 0:
                        self.movimientos_validos.append((f_simple, c_simple))

            f_salto = fila - 2
            f_intermedia = fila - 1
            if f_salto >= 0:
                for c_dir in [-1, 1]:
                    c_intermedia = col + c_dir
                    c_salto = col + (c_dir * 2)
                    if 0 <= c_salto < 8:
                        vecino = self.MyBoard[f_intermedia][c_intermedia]
                        if vecino in (1, 3) and self.MyBoard[f_salto][c_salto] == 0:
                            self.movimientos_validos.append((f_salto, c_salto))

        # 2. SI ES UNA REINA VOLADORA (Nuevo rayo vectorial continuo a larga distancia)
        elif tipo_pieza == 4:
            # Las 4 direcciones diagonales posibles
            direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for df, dc in direcciones:
                f_actual = fila + df
                c_actual = col + dc
                pieza_enemiga_detectada = None

                # Avanzar en línea recta diagonal hasta los límites del tablero
                while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                    val_celda = self.MyBoard[f_actual][c_actual]

                    if not pieza_enemiga_detectada:
                        if val_celda == 0:
                            # Casilla vacía en el camino: movimiento simple legal
                            self.movimientos_validos.append((f_actual, c_actual))
                        elif val_celda in (1, 3):
                            # Encontró pieza enemiga: registrar posición y evaluar salto
                            pieza_enemiga_detectada = (f_actual, c_actual)
                        else:
                            # Encontró pieza aliada: rayo bloqueado por completo
                            break
                    else:
                        # Ya encontramos una pieza enemiga antes, ahora evaluamos dónde aterrizar
                        if val_celda == 0:
                            # ¡Aterrizaje libre! Se registra como salto de captura legal a larga distancia
                            self.movimientos_validos.append((f_actual, c_actual))
                            # En damas internacionales/españolas, tras pasar la pieza comida, la reina
                            # puede elegir en cuál de las casillas vacías posteriores frenar su deslizamiento.
                        else:
                            # Si hay otra pieza inmediatamente detrás de la enemiga, el salto se bloquea
                            break

                    f_actual += df
                    c_actual += dc

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
