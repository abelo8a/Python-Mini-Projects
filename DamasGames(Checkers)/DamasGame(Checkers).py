import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar, QLabel, QMenuBar, QPushButton, QCheckBox
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
        """Maneja el turno del humano con soporte de combos múltiples reales de largo alcance y no-retorno."""
        if not self.main_window.game_active or self.main_window.turno_actual != "HUMANO":
            return

        # BLOQUEO DE SEGURIDAD: Impedir clics si está corriendo la animación de parpadeo de castigo
        if self.main_window.en_penalizacion_parpadeo:
            return

        box_size = 50
        col = int(event.position().x() // box_size)
        fila = int(event.position().y() // box_size)

        if not (0 <= fila < 8 and 0 <= col < 8):
            return

        # --- CASO A: EL JUGADOR YA SE ENCUENTRA EN MEDIO DE UN COMBO DE CAPTURA ACTIVO ---
        if self.main_window.en_combo_captura:
            if (fila, col) in self.main_window.movimientos_validos:
                f_origen, c_origen = self.main_window.pieza_en_combo
                valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

                df_usado = 1 if fila > f_origen else -1
                dc_usado = 1 if col > c_origen else -1

                # Barrido diagonal para eliminar la pieza enemiga comida
                f_scan = f_origen + df_usado
                c_scan = c_origen + dc_usado
                while f_scan != fila and c_scan != col:
                    if self.main_window.MyBoard[f_scan][c_scan] in (1, 3):
                        self.main_window.MyBoard[f_scan][c_scan] = 0
                        break
                    f_scan += df_usado
                    c_scan += dc_usado

                self.main_window.MyBoard[fila][col] = valor_pieza
                self.main_window.MyBoard[f_origen][c_origen] = 0
                self.main_window.actualizar_contadores_interfaz()

                # Regla de Oro: Si corona en la fila 0, el combo finaliza reglamentariamente de inmediato
                # Regla de Oro: Si corona en la fila 0 durante un combo, finaliza de inmediato
                if valor_pieza == 2 and fila == 0:
                    self.main_window.MyBoard[fila][col] = 4  # Forzar transformación física en la matriz
                    self.main_window.status_bar.showMessage(
                        f"👑 ¡Tu pieza se ha coronado como REINA en ({fila}, {col})!")
                    self.main_window.interrumpir_timers_combo()
                    self.main_window.en_combo_captura = False
                    self.main_window.pieza_en_combo = None
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
                    return

                # Escanear si nacerán MÁS saltos legales desde esta nueva posición de aterrizaje
                # Se pasa el vector inverso para prohibir el regreso hacia atrás en zigzag
                saltos_siguientes = self.main_window.calcular_saltos_continuos(fila, col,
                                                                               vector_prohibido=(-df_usado, -dc_usado))

                if saltos_siguientes:
                    # El combo se extiende: Bloquear la selección en la ficha actual
                    self.main_window.pieza_en_combo = (fila, col)
                    self.main_window.pieza_seleccionada = (fila, col)
                    self.main_window.movimientos_validos = saltos_siguientes
                    self.main_window.status_bar.showMessage("¡Combo activo! Tienes 3 segundos para el siguiente salto.")
                    self.update()
                    self.main_window.iniciar_cuenta_regresiva_combo(fila, col, saltos_siguientes)
                else:
                    # El combo terminó de forma natural: Apagar timers y transferir al BOT
                    self.main_window.interrumpir_timers_combo()
                    self.main_window.en_combo_captura = False
                    self.main_window.pieza_en_combo = None
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
            return

        # --- CASO B: TURNO NORMAL ESTÁNDAR (PRIMER CLIC DEL MOVIMIENTO DEL JUGADOR) ---
        if self.main_window.MyBoard[fila][col] in (2, 4):
            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos_humano(fila, col)

            # INYECCIÓN INTELIGENTE: Si está activado "Forzar Captura", filtramos dejando SOLO los saltos
            if self.main_window.regla_forzar_captura:
                # El método calcular_movimientos_validos_humano obtiene tanto pasos simples como saltos.
                # Identificamos un salto porque la distancia de filas es mayor a 1 celda (tanto para peón como reina)
                saltos_obligatorios = []
                for f_v, c_v in self.main_window.movimientos_validos:
                    # Validar si en el trayecto intermedio existe una captura real
                    df_u = 1 if f_v > fila else -1
                    dc_u = 1 if c_v > col else -1
                    f_s, c_s = fila + df_u, col + dc_u
                    while f_s != f_v and c_s != c_v:
                        if self.main_window.MyBoard[f_s][c_s] in (1, 3):
                            saltos_obligatorios.append((f_v, c_v))
                            break
                        f_s += df_u
                        c_s += dc_u

                # Si existen capturas obligatorias en esta ficha, borramos los pasos simples de aproximación
                if saltos_obligatorios:
                    self.main_window.movimientos_validos = saltos_obligatorios
                    self.main_window.status_bar.showMessage("¡Modo Torneo! Estás obligado a ejecutar la captura.")

            self.main_window.status_bar.showMessage(f"Ficha seleccionada en ({fila}, {col})")
            self.update()


        elif (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # 1. DETECTAR SI EN LA DIAGONAL CRUZADA EXISTIÓ UNA CAPTURA REAL
            fue_salto_captura = False
            df_usado = 1 if fila > f_origen else -1
            dc_usado = 1 if col > c_origen else -1

            f_scan = f_origen + df_usado
            c_scan = c_origen + dc_usado
            while f_scan != fila and c_scan != col:
                if self.main_window.MyBoard[f_scan][c_scan] in (1, 3):
                    self.main_window.MyBoard[f_scan][c_scan] = 0  # ¡Eliminada!
                    fue_salto_captura = True
                    break
                f_scan += df_usado
                c_scan += dc_usado

            # Trasladar la pieza en la matriz real
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            if fue_salto_captura:
                self.main_window.actualizar_contadores_interfaz()
                self.main_window.status_bar.showMessage("¡Has capturado una ficha enemiga!")

                # 1. Evaluar e inyectar la coronación de forma inmediata si corresponde
                self.main_window.evaluar_coronacion(fila, col, valor_pieza)

                # 2. Freno estricto de combo si se acaba de coronar en este turno (Nace pasiva)
                if self.main_window.MyBoard[fila][col] == 4 and valor_pieza == 2:
                    self.main_window.interrumpir_timers_combo()
                    self.main_window.en_combo_captura = False
                    self.main_window.pieza_en_combo = None
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
                    return

                # 3. ESCANEAR SI NACE UN COMBO MÚLTIPLE DESDE LA NUEVA CASILLA DE ATERRIZAJE
                saltos_siguientes = self.main_window.calcular_saltos_continuos(
                    fila, col, vector_prohibido=(-df_usado, -dc_usado)
                )

                if saltos_siguientes:
                    # El combo continúa en la misma ficha: levantar estado de combo
                    self.main_window.en_combo_captura = True
                    self.main_window.pieza_en_combo = (fila, col)
                    self.main_window.pieza_seleccionada = (fila, col)
                    self.main_window.movimientos_validos = saltos_siguientes
                    self.main_window.status_bar.showMessage(
                        "¡Captura múltiple detectada! Tienes 3 segundos para continuar.")
                    self.update()
                    self.main_window.iniciar_cuenta_regresiva_combo(fila, col, saltos_siguientes)
                    return
                else:
                    # Si no hay más capturas continuas en esta cadena, el turno termina limpiamente
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
                    return



            else:

                # --- CASO: EL MOVIMIENTO FUE UN PASO SIMPLE REGULAR DE APROXIMACIÓN ---

                self.main_window.status_bar.showMessage(f"Movimiento simple a ({fila}, {col})")

                # REGLA DE SOPLADO INMEDIATO GLOBAL

                if self.main_window.regla_soplado_automatico:

                    # 1. Aislamiento matemático: Revertimos temporalmente el tablero al inicio del turno

                    self.main_window.MyBoard[f_origen][c_origen] = valor_pieza

                    self.main_window.MyBoard[fila][col] = 0

                    # 2. El radar busca si existía CUALQUIER ficha con posibilidad de comer en el tablero

                    fichas_infractoras = self.main_window.obtener_todas_las_piezas_con_captura_humano()

                    # 3. Devolvemos la matriz a su estado post-movimiento

                    self.main_window.MyBoard[f_origen][c_origen] = 0

                    self.main_window.MyBoard[fila][col] = valor_pieza

                    if fichas_infractoras:

                        # ¡Infracción global detectada! Alguien omitió comer.

                        # Castigamos eliminando la ficha infractora real (o la primera de la lista si hay varias)

                        f_inf, c_inf = fichas_infractoras[0]

                        # Si la ficha infractora era la misma que se movió, la borramos de su nueva posición

                        if (f_inf, c_inf) == (f_origen, c_origen):

                            self.main_window.MyBoard[fila][col] = 0

                            self.main_window.status_bar.showMessage(
                                f"💨 ¡BOBA! Ficha soplada en ({fila}, {col}) por omitir su captura.")

                        else:

                            # Si movió OTRA ficha, la que se movió queda a salvo, pero la infractora desaparece de su lugar estático

                            self.main_window.MyBoard[f_inf][c_inf] = 0

                            self.main_window.status_bar.showMessage(
                                f"💨 ¡BOBA! Ficha soplada en ({f_inf}, {c_inf}) por distraído.")

                        self.main_window.actualizar_contadores_interfaz()

                # Evaluamos la coronación si la pieza que se movió sigue viva en la matriz

                if self.main_window.MyBoard[fila][col] == valor_pieza:
                    self.main_window.evaluar_coronacion(fila, col, valor_pieza)

                # Limpieza absoluta de estados estándar para el movimiento simple

                self.main_window.pieza_seleccionada = None

                self.main_window.movimientos_validos.clear()

                self.update()

                self.main_window.cambiar_turno("BOT")

                return




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

                if self.main_window.pieza_seleccionada == (fila, col):
                    painter.setBrush(QBrush(QColor(0, 255, 255, 80)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                if (fila, col) in self.main_window.movimientos_validos:
                    painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
                    painter.drawRect(col * box_size, fila * box_size, box_size, box_size)

                pieza = self.main_window.MyBoard[fila][col]
                if pieza == 0:
                    continue

                # 2. ASIGNAR COLORES DE LAS PIEZAS CONSIDERANDO EL PARPADEO
                # Si la pieza está en la lista de infracción y el ciclo de parpadeo está encendido
                if self.main_window.en_penalizacion_parpadeo and (fila,
                                                                  col) in self.main_window.piezas_a_parpadear and self.main_window.color_parpadeo_activo:
                    color_pieza = QColor(255, 140, 0)  # Naranja/Oro brillante de advertencia
                    color_borde = QColor(255, 0, 0)  # Rojo penalización
                else:
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

                # Renderizar corona dorada para Reinas
                if pieza in (3, 4):
                    painter.setPen(QPen(QColor(218, 165, 32), 2))
                    painter.setBrush(QBrush(QColor(255, 215, 0)))
                    puntos_corona = [
                        QPoint(center_x - 10, center_y + 6), QPoint(center_x - 12, center_y - 6),
                        QPoint(center_x - 4, center_y + 0), QPoint(center_x + 0, center_y - 10),
                        QPoint(center_x + 4, center_y + 0), QPoint(center_x + 12, center_y - 6),
                        QPoint(center_x + 10, center_y + 6)
                    ]
                    painter.drawPolygon(puntos_corona)
        painter.end()


# =====================================================================
# SEGUNDA PARTE: MOTOR DE JUEGO, CONTADORES E IA DEL BOT
# =====================================================================

class DamasGame(QMainWindow):
    def __init__(self):
        super().__init__()
        # NUEVAS: Reglas booleanas configurables de captura y soplado
        self.regla_forzar_captura = False  # Por defecto False (Libertad estratégica)
        self.regla_soplado_automatico = True  # Por defecto True (Castigo implacable de "bobas")

        self.MyBoard = [[0 for _ in range(8)] for _ in range(8)]
        self.game_active = True

        self.pieza_seleccionada = None
        self.movimientos_validos = []
        self.turno_actual = "HUMANO"

        # NUEVAS: Variables para el control de combos encadenados
        self.en_combo_captura = False
        self.pieza_en_combo = None      # Guardará la tupla (fila, col) de la ficha bloqueada
        self.ultimo_vector_salto = None # Guardará (df, dc) para calcular el no-retorno

        # NUEVAS: Variables para el control de la penalización por tiempo
        self.timer_oportunidad = None  # QTimer de 3 segundos
        self.timer_parpadeo = None     # QTimer para la animación de 2 segundos
        self.timer_ciclo_color = None  # QTimer rápido (200ms) para alternar el color
        self.en_penalizacion_parpadeo = False
        self.color_parpadeo_activo = True
        self.piezas_a_parpadear = []   # Lista de tuplas [(f1, c1), (f2, c2)]

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
        self.setWindowTitle('Damas Game - IA Laboratory Engine v1.5')
        self.setFixedSize(580, 425)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroDamas(self)

        # --- BARRA DE MENÚ SUPERIOR ---
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.setStyleSheet("""
            QMenuBar { background-color: #222; color: white; border-bottom: 1px solid #333; }
            QMenuBar::item:selected { background-color: #444; }
            QMenu { background-color: #222; color: white; border: 1px solid #333; }
            QMenu::item:selected { background-color: #00FF00; color: black; }
        """)

        menu_juego = self.menu_bar.addMenu("&Juego")
        accion_reiniciar = menu_juego.addAction("&Reiniciar Partida")
        accion_reiniciar.triggered.connect(self.reiniciar_partida)

        accion_salir = menu_juego.addAction("&Salir")
        accion_salir.triggered.connect(QApplication.instance().quit)

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

        # --- CHECKBOXES DE CONFIGURACIÓN DE REGLAS COMPETITIVAS ---
        font_checkbox = QFont('MS Sans Serif', 8, QFont.Weight.Bold)
        stylesheet_chk = """
            QCheckBox { color: #BBB; border: none; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 2px solid #555; border-radius: 3px; background: #222; }
            QCheckBox::indicator:checked { background: #00FF00; border-color: #00FF00; }
            QCheckBox:hover { color: white; }
        """

        self.chk_forzar = QCheckBox("Forzar Captura", self.panel_control)
        self.chk_forzar.setGeometry(12, 250, 150, 20)
        self.chk_forzar.setFont(font_checkbox)
        self.chk_forzar.setStyleSheet(stylesheet_chk)
        self.chk_forzar.setChecked(self.regla_forzar_captura)
        self.chk_forzar.toggled.connect(self.actualizar_reglasbox)

        self.chk_soplado = QCheckBox("Soplado / Boba", self.panel_control)
        self.chk_soplado.setGeometry(12, 280, 150, 20)
        self.chk_soplado.setFont(font_checkbox)
        self.chk_soplado.setStyleSheet(stylesheet_chk)
        self.chk_soplado.setChecked(self.regla_soplado_automatico)
        self.chk_soplado.toggled.connect(self.actualizar_reglasbox)

        # NUEVO: Botón interactivo de Reinicio en el Panel Lateral (Instanciación primero)
        self.btn_reiniciar = QPushButton('REINICIAR', self.panel_control)
        self.btn_reiniciar.setGeometry(12, 335, 150, 40)
        self.btn_reiniciar.setFont(font_titulos)
        self.btn_reiniciar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reiniciar.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #000;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        self.btn_reiniciar.clicked.connect(self.reiniciar_partida)

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
        """Calcula movimientos simples y saltos para peones (2) y Reinas Voladoras (4) en su primer movimiento."""
        self.movimientos_validos.clear()
        tipo_pieza = self.MyBoard[fila][col]

        # 1. LOGICA DE PEÓN NORMAL (Mantiene su comportamiento estable de corto alcance)
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

        # 2. LOGICA DE REINA VOLADORA (Rayo continuo corregido para el inicio del turno)
        elif tipo_pieza == 4:
            direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for df, dc in direcciones:
                f_actual = fila + df
                c_actual = col + dc
                pieza_enemiga_detectada = None

                while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                    val_celda = self.MyBoard[f_actual][c_actual]

                    if not pieza_enemiga_detectada:
                        if val_celda == 0:
                            # Permitir el movimiento de acecho o desplazamiento libre por la diagonal
                            self.movimientos_validos.append((f_actual, c_actual))
                        elif val_celda in (1, 3):
                            pieza_enemiga_detectada = (f_actual, c_actual)
                        else:
                            break  # Bloqueado por ficha aliada
                    else:
                        if val_celda == 0:
                            # Registrar la casilla de aterrizaje como una opción de captura disponible
                            self.movimientos_validos.append((f_actual, c_actual))
                        else:
                            break  # Bloqueado por otra pieza detrás del enemigo

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

                # --- PROCESAR SOLO FICHAS DEL BOT (1: Peón, 3: Reina) ---
                if tipo_pieza in (1, 3):

                    # CASO REINA ROJA (3): RAYO VECTORIAL DE LARGO ALCANCE
                    if tipo_pieza == 3:
                        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                        for df, dc in direcciones:
                            f_actual, c_actual = fila + df, col + dc
                            pieza_enemiga_detectada = None

                            while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                                val_celda = self.MyBoard[f_actual][c_actual]

                                if not pieza_enemiga_detectada:
                                    if val_celda == 0:
                                        # Movimiento simple de largo alcance disponible
                                        movimientos_simples.append(((fila, col), (f_actual, c_actual)))
                                    elif val_celda in (2, 4):  # Enemigo (Blanco) detectado
                                        pieza_enemiga_detectada = (f_actual, c_actual)
                                    else:
                                        break  # Bloqueado por ficha aliada roja
                                else:
                                    if val_celda == 0:
                                        # Captura de largo alcance válida (guarda origen, destino e intermedia)
                                        capturas_disponibles.append(
                                            ((fila, col), (f_actual, c_actual), pieza_enemiga_detectada))
                                    else:
                                        break  # Bloqueado por otra pieza detrás del enemigo
                                f_actual += df
                                c_actual += dc

                    # CASO PEÓN ROJO (1): MOVIMIENTOS Y CAPTURAS CORTAS (SOLO HACIA ABAJO +1)
                    else:
                        f_simple = fila + 1
                        f_salto = fila + 2
                        f_intermedia = fila + 1

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

        # --- RESOLUCIÓN DEL TURNO DE LA IA ---
        if capturas_disponibles:
            origen, destino, intermedia = random.choice(capturas_disponibles)
            f_orig, c_orig = origen
            f_dest, c_dest = destino
            f_int, c_int = intermedia

            valor_bot = self.MyBoard[f_orig][c_orig]
            self.MyBoard[f_int][c_int] = 0  # Eliminar pieza humana capturada
            self.MyBoard[f_dest][c_dest] = valor_bot
            self.MyBoard[f_orig][c_orig] = 0

            self.evaluar_coronacion(f_dest, c_dest, valor_bot)
            self.status_bar.showMessage(f"🤖 El BOT te ha capturado una pieza en ({f_int}, {c_int})")
            self.actualizar_contadores_interfaz()

        elif movimientos_simples:
            origen, destino = random.choice(movimientos_simples)
            f_orig, c_orig = origen
            f_dest, c_dest = destino

            valor_bot = self.MyBoard[f_orig][c_orig]
            self.MyBoard[f_dest][c_dest] = valor_bot
            self.MyBoard[f_orig][c_orig] = 0

            self.evaluar_coronacion(f_dest, c_dest, valor_bot)
            self.status_bar.showMessage(f"🤖 El BOT movió de ({f_orig}, {c_orig}) a ({f_dest}, {c_dest})")
        else:
            self.game_active = False
            self.status_bar.showMessage("¡Felicidades! El BOT no tiene movimientos legales. ¡Ganaste!")
            return

        self.tablero.update()
        self.cambiar_turno("HUMANO")

    def calcular_saltos_continuos(self, fila, col, vector_prohibido=None):
        """
        PERFECTA: Escanea saltos de combo reales e inmediatos para peones y Reinas.
        Soporta capturas a larga distancia para Reinas, eliminando falsos positivos.
        """
        saltos_encontrados = []
        tipo_pieza = self.MyBoard[fila][col]

        if tipo_pieza == 2:  # Peón blanco: solo sube (-1)
            direcciones = [(-1, -1), (-1, 1)]
        elif tipo_pieza == 4:  # Reina blanca: las 4 direcciones
            direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            return []

        for df, dc in direcciones:
            # LÍNEA CORREGIDA: Comparación nativa de tuplas para evitar cortocircuitos en Python
            if vector_prohibido and (df, dc) == vector_prohibido:
                continue

            if tipo_pieza == 4:  # LÓGICA DE REINA VOLADORA EN COMBO (CORREGIDA)
                f_actual = fila + df
                c_actual = col + dc
                enemigo_detectado = None

                # Lanzar el rayo a larga distancia por la diagonal
                while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                    val_celda = self.MyBoard[f_actual][c_actual]

                    if not enemigo_detectado:
                        if val_celda in (1, 3):  # Encontró pieza enemiga (roja o reina)
                            enemigo_detectado = (f_actual, c_actual)
                        elif val_celda != 0:  # Chocó con pieza aliada propia
                            break
                    else:
                        # Si ya cruzó al enemigo, puede aterrizar en CUALQUIER casilla vacía continua
                        if val_celda == 0:
                            saltos_encontrados.append((f_actual, c_actual))
                        else:
                            # Bloqueado por otra pieza detrás del enemigo
                            break

                    f_actual += df
                    c_actual += dc
            else:  # LÓGICA DE PEÓN ESTABLE
                f_intermedia = fila + df
                f_salto = fila + (df * 2)
                c_intermedia = col + dc
                c_salto = col + (dc * 2)

                if 0 <= f_salto < 8 and 0 <= c_salto < 8:
                    if self.MyBoard[f_intermedia][c_intermedia] in (1, 3) and self.MyBoard[f_salto][c_salto] == 0:
                        saltos_encontrados.append((f_salto, c_salto))

        return saltos_encontrados

    def iniciar_cuenta_regresiva_combo(self, f_infractora, c_infractora, saltos_omitidos):
        """NUEVO: Inicializa el reloj de 3 segundos para continuar el combo."""
        self.interrumpir_timers_combo()

        # Configurar las piezas que van a parpadear si se agota el tiempo
        self.piezas_a_parpadear = [(f_infractora, c_infractora)]
        # Buscamos qué piezas enemigas se salvaron en las diagonales omitidas
        for f_s, c_s in saltos_omitidos:
            paso_f = 1 if f_s > f_infractora else -1
            paso_c = 1 if c_s > c_infractora else -1
            f_scan, c_scan = f_infractora + paso_f, c_infractora + paso_c
            while f_scan != f_s and c_scan != c_s:
                if self.MyBoard[f_scan][c_scan] in (1, 3):
                    self.piezas_a_parpadear.append((f_scan, c_scan))
                    break
                f_scan += paso_f
                c_scan += paso_c

        # Crear y arrancar el temporizador de cuenta regresiva de 3000ms
        self.timer_oportunidad = QTimer(self)
        self.timer_oportunidad.setSingleShot(True)
        self.timer_oportunidad.timeout.connect(self.aplicar_castigo_omision)
        self.timer_oportunidad.start(3000)

    def alternar_color_parpadeo(self):
        """NUEVO: Alterna el estado visual del color cada 200ms para simular el parpadeo."""
        self.color_parpadeo_activo = not self.color_parpadeo_activo
        self.tablero.update()

    def aplicar_castigo_omision(self):
        """NUEVO: Detona la animación de 2 segundos tras agotarse el tiempo de oportunidad."""
        self.en_penalizacion_parpadeo = True
        self.status_bar.showMessage("⚠️ ¡TIEMPO AGOTADO! Penalización por omitir captura múltiple.")

        # Temporizador rápido de 200ms para alternar colores de advertencia
        self.timer_ciclo_color = QTimer(self)
        self.timer_ciclo_color.timeout.connect(self.alternar_color_parpadeo)
        self.timer_ciclo_color.start(200)

        # Temporizador de 2 segundos que frena la animación y borra la pieza
        self.timer_parpadeo = QTimer(self)
        self.timer_parpadeo.setSingleShot(True)
        self.timer_parpadeo.timeout.connect(self.concluir_castigo_y_ceder_turno)
        self.timer_parpadeo.start(2000)

    def concluir_castigo_y_ceder_turno(self):
        """NUEVO: Borra la pieza infractora de la matriz y pasa el turno al BOT."""
        if self.piezas_a_parpadear:
            f_inf, c_inf = self.piezas_a_parpadear[0]
            # Soplado reglamentario: La ficha del jugador se elimina de la matriz
            self.MyBoard[f_inf][c_inf] = 0
            self.status_bar.showMessage(f"Ficha penalizada y eliminada en ({f_inf}, {c_inf}). Turno del BOT.")

        # Limpiar estados de animación y combo
        self.interrumpir_timers_combo()
        self.en_combo_captura = False
        self.pieza_en_combo = None
        self.pieza_seleccionada = None
        self.movimientos_validos.clear()

        self.tablero.update()
        self.cambiar_turno("BOT")

    def interrumpir_timers_combo(self):
        """NUEVO: Apaga de forma segura todos los relojes activos."""
        if hasattr(self, 'timer_oportunidad') and self.timer_oportunidad and self.timer_oportunidad.isActive():
            self.timer_oportunidad.stop()
        if hasattr(self, 'timer_ciclo_color') and self.timer_ciclo_color and self.timer_ciclo_color.isActive():
            self.timer_ciclo_color.stop()
        if hasattr(self, 'timer_parpadeo') and self.timer_parpadeo and self.timer_parpadeo.isActive():
            self.timer_parpadeo.stop()
        self.en_penalizacion_parpadeo = False
        self.color_parpadeo_activo = True

    def reiniciar_partida(self):
        """Detiene de inmediato las penalizaciones en curso y limpia el tablero a su estado inicial."""
        # 1. Seguridad: Detener todos los timers asíncronos para evitar soplados residuales
        self.interrumpir_timers_combo()

        # 2. Resetear variables de control lógico de turnos y combos
        self.game_active = True
        self.turno_actual = "HUMANO"
        self.pieza_seleccionada = None
        self.movimientos_validos.clear()
        self.en_combo_captura = False
        self.pieza_en_combo = None
        self.ultimo_vector_salto = None
        self.en_penalizacion_parpadeo = False
        self.color_parpadeo_activo = True
        self.piezas_a_parpadear.clear()

        # 3. Vaciar y regenerar la matriz de juego 8x8 con la configuración reglamentaria
        self.MyBoard = [[0 for _ in range(8)] for _ in range(8)]
        self.init_board_setup()

        # 4. Actualizar contadores visuales (0 / 12) y refrescar los lienzos
        self.actualizar_contadores_interfaz()
        self.tablero.update()

        # 5. Notificar en la barra de estado
        self.status_bar.showMessage("Partida reiniciada con éxito. Tu turno (Fichas Blancas).")

    def actualizar_reglasbox(self):
        """Sincroniza el estado de los componentes visuales con el motor de juego."""
        self.regla_forzar_captura = self.chk_forzar.isChecked()
        self.regla_soplado_automatico = self.chk_soplado.isChecked()

    def obtener_todas_las_piezas_con_captura_humano(self):
        """Escanea globalmente todo el tablero para encontrar qué fichas blancas tienen saltos obligatorios."""
        piezas_con_salto = []
        for f in range(8):
            for col in range(8):
                if self.MyBoard[f][col] in (2, 4):  # Fichas del humano
                    if self.calcular_saltos_continuos(f, col):
                        piezas_con_salto.append((f, col))
        return piezas_con_salto



if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = DamasGame()
    game.show()
    sys.exit(app.exec())
