import sys
import traceback
import faulthandler
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStatusBar, QLabel, QMenuBar, QPushButton, QCheckBox
from PyQt6.QtCore import Qt, QPoint, QTimer
# CORREGIDO: Se añade QFont a las importaciones de QtGui
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

# Habilita el manejador de fallos para imprimir la pila antes de colapsar
faulthandler.enable()

def hook_de_excepcion(tipo, valor, tb):
    """Captura errores de Qt antes del colapso del sistema."""
    mensaje = "".join(traceback.format_exception(tipo, valor, tb))
    print(mensaje)
    # Guarda el error en un archivo por si la consola se cierra muy rápido
    with open("error_critico.txt", "w") as f:
        f.write(mensaje)
    sys.__excepthook__(tipo, valor, tb)

sys.excepthook = hook_de_excepcion

class TableroDamas(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 400, 400)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """v1.8: Maneja el turno humano con Foto Pre-Movimiento y protección de matriz real."""
        if not self.main_window.game_active or self.main_window.turno_actual != "HUMANO":
            return

        if self.main_window.en_penalizacion_parpadeo:
            return

        box_size = 50
        col = int(event.position().x() // box_size)
        fila = int(event.position().y() // box_size)

        if not (0 <= fila < 8 and 0 <= col < 8):
            return

        # --- CASO A: EL JUGADOR YA SE ENCUENTRA EN MEDIO DE UN COMBO ---
        if self.main_window.en_combo_captura:
            if (fila, col) in self.main_window.movimientos_validos:
                f_origen, c_origen = self.main_window.pieza_en_combo
                valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

                df_usado = 1 if fila > f_origen else -1
                dc_usado = 1 if col > c_origen else -1

                # Limpieza de pieza comida
                f_scan, c_scan = f_origen + df_usado, c_origen + dc_usado
                while f_scan != fila and c_scan != col:
                    if self.main_window.MyBoard[f_scan][c_scan] in (1, 3):
                        self.main_window.MyBoard[f_scan][c_scan] = 0
                        break
                    f_scan += df_usado
                    c_scan += dc_usado

                self.main_window.MyBoard[fila][col] = valor_pieza
                self.main_window.MyBoard[f_origen][c_origen] = 0
                self.main_window.actualizar_contadores_interfaz()

                # Coronación inmediata en combo (Freno de turno)
                if valor_pieza == 2 and fila == 0:
                    self.main_window.MyBoard[fila][col] = 4
                    self.main_window.status_bar.showMessage(f"👑 ¡REINA coronada en ({fila}, {col})!")
                    self.main_window.interrumpir_timers_combo()
                    self.main_window.en_combo_captura = False
                    self.main_window.pieza_en_combo = None
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
                    return

                saltos_sig = self.main_window.calcular_saltos_continuos(fila, col,
                                                                        vector_prohibido=(-df_usado, -dc_usado))

                if saltos_sig:
                    self.main_window.pieza_en_combo = (fila, col)
                    self.main_window.pieza_seleccionada = (fila, col)
                    self.main_window.movimientos_validos = saltos_sig
                    self.update()
                    self.main_window.iniciar_cuenta_regresiva_combo(fila, col, saltos_sig)
                else:
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
            # 1. Foto Analítica de Peso Global ANTES de cualquier acción
            piezas_maximas, peso_max_global = self.main_window.obtener_piezas_con_maxima_captura_global("HUMANO")

            # 2. Si "Forzar Captura" está activo, bloqueamos selección de piezas subóptimas
            if self.main_window.regla_forzar_captura:
                if piezas_maximas and (fila, col) not in piezas_maximas:
                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.main_window.status_bar.showMessage(
                        f"⚠️ ¡MÁXIMA CAPTURA! Hay rutas de {peso_max_global} fichas. Elige la correcta.")
                    self.update()
                    return

            self.main_window.pieza_seleccionada = (fila, col)
            self.main_window.calcular_movimientos_validos_humano(fila, col)

            # 3. Filtrar movimientos de la ficha elegida si Forzar Captura está activo
            if self.main_window.regla_forzar_captura:
                saltos_validos = []
                for f_v, c_v in self.main_window.movimientos_validos:
                    df_u, dc_u = (1 if f_v > fila else -1), (1 if c_v > col else -1)

                    # Simulación local ultra-rápida de peso para esta rama
                    val_temp = self.main_window.MyBoard[fila][col]
                    self.main_window.MyBoard[f_v][c_v] = val_temp
                    self.main_window.MyBoard[fila][col] = 0
                    peso_rama = 1 + self.main_window.calcular_peso_maximo_captura(f_v, c_v,
                                                                                  vector_prohibido=(-df_u, -dc_u))

                    # Restauración inmediata
                    self.main_window.MyBoard[fila][col] = val_temp
                    self.main_window.MyBoard[f_v][c_v] = 0

                    if peso_rama == peso_max_global:
                        saltos_validos.append((f_v, c_v))

                if saltos_validos:
                    self.main_window.movimientos_validos = saltos_validos

            self.main_window.status_bar.showMessage(f"Ficha seleccionada en ({fila}, {col})")
            self.update()

        elif self.main_window.pieza_seleccionada and (fila, col) in self.main_window.movimientos_validos:
            f_origen, c_origen = self.main_window.pieza_seleccionada
            valor_pieza = self.main_window.MyBoard[f_origen][c_origen]

            # Tomamos foto del peso máximo para el arbitraje posterior
            _, peso_max_original = self.main_window.obtener_piezas_con_maxima_captura_global("HUMANO")
            fue_salto_captura = False
            df_usado = 1 if fila > f_origen else -1
            dc_usado = 1 if col > c_origen else -1

            # Barrido diagonal real para eliminar la pieza enemiga comida
            f_scan, c_scan = f_origen + df_usado, c_origen + dc_usado
            while f_scan != fila and c_scan != col:
                if self.main_window.MyBoard[f_scan][c_scan] in (1, 3):
                    self.main_window.MyBoard[f_scan][c_scan] = 0
                    fue_salto_captura = True
                    break
                f_scan += df_usado
                c_scan += dc_usado

            # Trasladar la pieza de forma física en la matriz real
            self.main_window.MyBoard[fila][col] = valor_pieza
            self.main_window.MyBoard[f_origen][c_origen] = 0

            if fue_salto_captura:
                self.main_window.actualizar_contadores_interfaz()

                # 1. VERIFICAR SI LA PIEZA TIENE MÁS SALTOS (Combo Continuo)
                saltos_siguientes = self.main_window.calcular_saltos_continuos(
                    fila, col, vector_prohibido=(-df_usado, -dc_usado)
                )

                if saltos_siguientes:
                    self.main_window.en_combo_captura = True
                    self.main_window.pieza_en_combo = (fila, col)
                    self.main_window.pieza_seleccionada = (fila, col)
                    self.main_window.movimientos_validos = saltos_siguientes
                    self.main_window.status_bar.showMessage("¡Combo! Tienes 3 segundos para el siguiente salto.")
                    self.update()
                    self.main_window.iniciar_cuenta_regresiva_combo(fila, col, saltos_siguientes)
                    return
                else:
                    # --- LA CADENA DE SALTOS TERMINÓ DEFINITIVAMENTE ---
                    fue_soplada_por_peso = False
                    comidas_realizadas = 1

                    if self.main_window.regla_soplado_automatico:
                        # AUDITORÍA v1.8: Comparamos contra la foto fija (peso_max_original)
                        # Solo hay infracción si lo que comiste es MENOR a lo máximo que había al inicio
                        if comidas_realizadas < peso_max_original:
                            piezas_max, _ = self.main_window.obtener_piezas_con_maxima_captura_global("HUMANO")
                            if piezas_max and isinstance(piezas_max, list) and len(piezas_max) > 0:
                                for f_inf, c_inf in piezas_max:
                                    if self.main_window.MyBoard[f_inf][c_inf] in (2, 4):
                                        self.main_window.MyBoard[f_inf][c_inf] = 0
                                        self.main_window.status_bar.showMessage(
                                            f"💨 ¡BOBA DE PESO! Soplada en ({f_inf}, {c_inf}) por omitir combo de {peso_max_original}.")
                                        if f_inf == fila and c_inf == col:
                                            fue_soplada_por_peso = True
                                self.main_window.actualizar_contadores_interfaz()

                    # 2. EVALUAR CORONACIÓN: Solo si la pieza no fue desvanecida por el arbitraje
                    if not fue_soplada_por_peso:
                        self.main_window.evaluar_coronacion(fila, col, valor_pieza)

                    self.main_window.pieza_seleccionada = None
                    self.main_window.movimientos_validos.clear()
                    self.update()
                    self.main_window.cambiar_turno("BOT")
                    return

            else:
                # --- CASO: MOVIMIENTO SIMPLE REGULAR ---
                self.main_window.status_bar.showMessage(f"Movimiento simple a ({fila}, {col})")

                fue_soplada = False
                if self.main_window.regla_soplado_automatico:
                    # Si caminaste habiendo capturas abiertas (peso_max_original > 0), es infracción
                    if peso_max_original > 0:
                        piezas_max, _ = self.main_window.obtener_piezas_con_maxima_captura_global("HUMANO")
                        if piezas_max and len(piezas_max) > 0:
                            infractor = piezas_max[0]
                            f_inf, c_inf = infractor

                            if f_inf == f_origen and c_inf == c_origen:
                                self.main_window.MyBoard[fila][col] = 0
                                self.main_window.status_bar.showMessage(
                                    f"💨 ¡BOBA! Soplada en ({fila}, {col}) por omitir captura.")
                                fue_soplada = True
                            else:
                                self.main_window.MyBoard[f_inf][c_inf] = 0
                                self.main_window.status_bar.showMessage(
                                    f"💨 ¡BOBA! Soplada en ({f_inf}, {c_inf}) por distraído.")

                            self.main_window.actualizar_contadores_interfaz()

                if not fue_soplada:
                    self.main_window.evaluar_coronacion(fila, col, valor_pieza)

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

        # NUEVA: Control de dificultad del BOT (1: Principiante, 2: Intermedio, 3: Maestro)
        self.nivel_dificultad_bot = 2

        # NUEVAS: Reglas booleanas configurables de captura y soplado
        self.regla_forzar_captura = False  # Por defecto False (Libertad estratégica)
        self.regla_soplado_automatico = True  # Por defecto True (Castigo implacable de "bobas")

        # NUEVAS: Reglas configurables para el BOT
        self.regla_bot_forzar = False  # Default: False (Permite al BOT regalar piezas por estrategia)
        self.regla_bot_soplado = True  # Default: True (El BOT también sufre soplados si omite comer)

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
        """TestScenario
        # Vaciar el tablero por completo primero
        self.MyBoard = [[0 for _ in range(8)] for _ in range(8)]

        # --- ESCENARIO DE PRUEBA DE MÁXIMA CAPTURA ---

        # 1. FICHA A (Humano, Fila inferior): Tiene un COMBO MÁXIMO DE 2 CAPTURAS
        self.MyBoard[6][1] = 2  # Tu Peón Blanco (Ficha A)
        self.MyBoard[5][2] = 1  # Peón Rojo del BOT (Primera comida)
        self.MyBoard[3][4] = 1  # Peón Rojo del BOT (Segunda comida en cadena)

        # 2. FICHA B (Humano, Fila superior): Tiene una CAPTURA SIMPLE DE 1 FICHA
        self.MyBoard[4][7] = 2  # Tu Peón Blanco (Ficha B)
        self.MyBoard[3][6] = 1  # Peón Rojo del BOT (Comida simple aislada)"""

    def init_ui(self):
        self.setWindowTitle('Damas Game - IA Laboratory Engine v1.5')
        self.setFixedSize(580, 460)
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
        self.panel_control.setGeometry(405, 0, 175, 440)
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
        font_subtitulos = QFont('MS Sans Serif', 8, QFont.Weight.Bold)
        stylesheet_chk = """
            QCheckBox { color: #BBB; border: none; }
            QCheckBox::indicator { width: 12px; height: 12px; border: 2px solid #555; border-radius: 3px; background: #222; }
            QCheckBox::indicator:checked { background: #00FF00; border-color: #00FF00; }
            QCheckBox:hover { color: white; }
        """

        # --- SECCIÓN HUMANO ---
        lbl_humano_rules = QLabel('REGLAS JUGADOR:', self.panel_control)
        lbl_humano_rules.setGeometry(12, 175, 150, 15)
        lbl_humano_rules.setFont(font_subtitulos)
        lbl_humano_rules.setStyleSheet("color: #55FF55; border: none;")

        self.chk_forzar = QCheckBox("Forzar Captura", self.panel_control)
        self.chk_forzar.setGeometry(12, 195, 150, 18)
        self.chk_forzar.setFont(font_subtitulos)
        self.chk_forzar.setStyleSheet(stylesheet_chk)
        self.chk_forzar.setChecked(self.regla_forzar_captura)
        self.chk_forzar.toggled.connect(self.actualizar_reglasbox)

        self.chk_soplado = QCheckBox("Soplado / Boba", self.panel_control)
        self.chk_soplado.setGeometry(12, 215, 150, 18)
        self.chk_soplado.setFont(font_subtitulos)
        self.chk_soplado.setStyleSheet(stylesheet_chk)
        self.chk_soplado.setChecked(self.regla_soplado_automatico)
        self.chk_soplado.toggled.connect(self.actualizar_reglasbox)

        # --- SECCIÓN BOT ---
        lbl_bot_rules = QLabel('REGLAS BOT (IA):', self.panel_control)
        lbl_bot_rules.setGeometry(12, 245, 150, 15)
        lbl_bot_rules.setFont(font_subtitulos)
        lbl_bot_rules.setStyleSheet("color: #FF5555; border: none;")

        self.chk_bot_forzar = QCheckBox("Forzar Captura", self.panel_control)
        self.chk_bot_forzar.setGeometry(12, 265, 150, 18)
        self.chk_bot_forzar.setFont(font_subtitulos)
        self.chk_bot_forzar.setStyleSheet(stylesheet_chk)
        self.chk_bot_forzar.setChecked(self.regla_bot_forzar)
        self.chk_bot_forzar.toggled.connect(self.actualizar_reglasbox)

        self.chk_bot_soplado = QCheckBox("Soplado / Boba", self.panel_control)
        self.chk_bot_soplado.setGeometry(12, 285, 150, 18)
        self.chk_bot_soplado.setFont(font_subtitulos)
        self.chk_bot_soplado.setStyleSheet(stylesheet_chk)
        self.chk_bot_soplado.setChecked(self.regla_bot_soplado)
        self.chk_bot_soplado.toggled.connect(self.actualizar_reglasbox)

        # --- PRIMERO INSTANCIAMOS EL BOTÓN DE REINICIAR REUBICADO ---
        self.btn_reiniciar = QPushButton('REINICIAR', self.panel_control)
        self.btn_reiniciar.setGeometry(12, 370, 150, 35)
        self.btn_reiniciar.setFont(font_titulos)
        self.btn_reiniciar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reiniciar.setStyleSheet("""
            QPushButton { background-color: #222; color: #00FF00; border: 2px solid #00FF00; border-radius: 5px; }
            QPushButton:hover { background-color: #00FF00; color: #000; }
            QPushButton:pressed { background-color: #009900; }
        """)
        self.btn_reiniciar.clicked.connect(self.reiniciar_partida)

        # --- SECCIÓN DE DIFICULTAD DE LA IA (AHORA EXISTE EL BOTÓN PREVIO) ---
        lbl_ia_level = QLabel('DIFICULTAD BOT:', self.panel_control)
        lbl_ia_level.setGeometry(12, 310, 150, 15)
        lbl_ia_level.setFont(font_subtitulos)
        lbl_ia_level.setStyleSheet("color: #FFA500; border: none;")

        self.btn_nv1 = QPushButton('L1', self.panel_control)
        self.btn_nv1.setGeometry(12, 330, 45, 25)
        self.btn_nv1.setCheckable(True)
        self.btn_nv1.clicked.connect(lambda: self.cambiar_dificultad_bot(1))

        self.btn_nv2 = QPushButton('L2', self.panel_control)
        self.btn_nv2.setGeometry(62, 330, 45, 25)
        self.btn_nv2.setCheckable(True)
        self.btn_nv2.clicked.connect(lambda: self.cambiar_dificultad_bot(2))

        self.btn_nv3 = QPushButton('L3', self.panel_control)
        self.btn_nv3.setGeometry(112, 330, 45, 25)
        self.btn_nv3.setCheckable(True)
        self.btn_nv3.clicked.connect(lambda: self.cambiar_dificultad_bot(3))

        style_nv = """
            QPushButton { background-color: #222; color: #888; border: 1px solid #444; font-weight: bold; border-radius: 3px; }
            QPushButton:checked { background-color: #FFA500; color: black; border-color: white; }
            QPushButton:hover { color: white; }
        """
        self.btn_nv1.setStyleSheet(style_nv)
        self.btn_nv2.setStyleSheet(style_nv)
        self.btn_nv3.setStyleSheet(style_nv)
        self.btn_nv2.setChecked(True)

        # --- BARRA DE ESTADO ---
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tu turno (Fichas Blancas). Elige una pieza.")

    def cambiar_turno(self, nuevo_turno):
        self.turno_actual = nuevo_turno
        if nuevo_turno == "BOT":
            self.status_bar.showMessage("El BOT Rojo está pensando...")

            # BLOQUEO DE SEGURIDAD: Tú ya no puedes alterar los checkboxes del BOT ni los tuyos en su turno
            self.chk_forzar.setEnabled(False)
            self.chk_soplado.setEnabled(False)
            self.chk_bot_forzar.setEnabled(False)
            self.chk_bot_soplado.setEnabled(False)

            # Inteligencia Artificial Evaluativa: El BOT decide sus checkboxes en tiempo real aquí
            self.analizar_y_calibrar_cerebro_bot()

            QTimer.singleShot(600, self.ejecutar_turno_bot)
        else:
            self.status_bar.showMessage("Tu turno (Fichas Blancas).")

            # Al regresar a tu turno, recuperas el control de tus cajas, pero las del BOT quedan bloqueadas para ti
            self.chk_forzar.setEnabled(True)
            self.chk_soplado.setEnabled(True)
            self.chk_bot_forzar.setEnabled(False)
            self.chk_bot_soplado.setEnabled(False)

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

    def calcular_peso_maximo_captura(self, fila, col, tablero_virtual=None, visitados=None, vector_prohibido=None):
        """v1.8: Calcula el peso sobre un tablero virtual para evitar borrar piezas reales por error."""
        if visitados is None: visitados = set()

        # Si es la primera llamada, creamos una copia profunda del tablero para no alterar el real
        if tablero_virtual is None:
            tablero_virtual = [fila[:] for fila in self.MyBoard]

        # Necesitamos que calcular_saltos_continuos sea capaz de leer el tablero virtual
        # Para no complicar, haremos el escaneo local manual aquí:
        saltos_inmediatos = self.obtener_saltos_desde_tablero(fila, col, tablero_virtual, vector_prohibido)

        if not saltos_inmediatos:
            return 0

        max_comidas = 0
        tipo_pieza = tablero_virtual[fila][col]

        for f_dest, c_dest in saltos_inmediatos:
            df = 1 if f_dest > fila else -1
            dc = 1 if c_dest > col else -1
            f_int, c_int = fila + df, col + dc

            # Localizar pieza intermedia (Reina o Peón)
            if tipo_pieza in (3, 4):
                while tablero_virtual[f_int][c_int] == 0:
                    f_int += df
                    c_int += dc

            if (f_int, c_int) in visitados: continue

            # SIMULACIÓN EN EL CLON
            visitados.add((f_int, c_int))
            original_int = tablero_virtual[f_int][c_int]
            tablero_virtual[f_dest][c_dest] = tipo_pieza
            tablero_virtual[fila][col] = 0
            tablero_virtual[f_int][c_int] = 0

            peso = 1 + self.calcular_peso_maximo_captura(f_dest, c_dest, tablero_virtual, visitados, (-df, -dc))
            if peso > max_comidas: max_comidas = peso

            # BACKTRACKING EN EL CLON
            tablero_virtual[fila][col] = tipo_pieza
            tablero_virtual[f_dest][c_dest] = 0
            tablero_virtual[f_int][c_int] = original_int
            visitados.remove((f_int, c_int))

        return max_comidas

    def obtener_saltos_desde_tablero(self, fila, col, tablero, vector_prohibido):
        """Ayudante que busca saltos en cualquier tablero (real o virtual)."""
        pieza = tablero[fila][col]
        enemigos = (1, 3) if pieza in (2, 4) else (2, 4)
        saltos = []

        if pieza == 2:
            dirs = [(-1, -1), (-1, 1)]
        elif pieza == 1:
            dirs = [(1, -1), (1, 1)]
        else:
            dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in dirs:
            if vector_prohibido and (df, dc) == vector_prohibido: continue

            nf, nc = fila + df, col + dc
            if pieza in (3, 4):  # Reina
                enemigo_visto = False
                while 0 <= nf < 8 and 0 <= nc < 8:
                    val = tablero[nf][nc]
                    if not enemigo_visto:
                        if val in enemigos:
                            enemigo_visto = (nf, nc)
                        elif val != 0:
                            break
                    else:
                        if val == 0:
                            saltos.append((nf, nc))
                        else:
                            break
                    nf += df;
                    nc += dc
            else:  # Peón
                sf, sc = fila + df * 2, col + dc * 2
                if 0 <= sf < 8 and 0 <= sc < 8:
                    if tablero[nf][nc] in enemigos and tablero[sf][sc] == 0:
                        saltos.append((sf, sc))
        return saltos

    def obtener_piezas_con_maxima_captura_global(self, bando):
        """
        UNIVERSAL v1.7: Devuelve una lista de tuplas [(fila, col)] con las piezas que cumplen
        estrictamente con la Ley de Máxima Captura para el bando ('HUMANO' o 'BOT').
        """
        valores_bando = (2, 4) if bando == "HUMANO" else (1, 3)
        registro_piezas = {}
        max_bajas_globales = 0

        for f in range(8):
            for c in range(8):
                if self.MyBoard[f][c] in valores_bando:
                    peso = self.calcular_peso_maximo_captura(f, c)
                    if peso > 0:
                        if peso not in registro_piezas:
                            registro_piezas[peso] = []
                        registro_piezas[peso].append((f, c))
                        if peso > max_bajas_globales:
                            max_bajas_globales = peso

        if max_bajas_globales == 0:
            return [], 0
        return registro_piezas[max_bajas_globales], max_bajas_globales

    def ejecutar_turno_bot(self):
        """
        v1.7 STABLE: Motor de la IA adaptativo con soporte de Ley de Máxima Captura.
        Audita de forma estricta los combos incompletos y las bobas globales del BOT.
        """
        if not self.game_active:
            return

        capturas_disponibles = []
        movimientos_simples = []

        # 1. ESCANEO GLOBAL DE POSIBILIDADES CON CÁLCULO DE PESO (Rutas Máximas)
        peso_max_bot = 0
        piezas_maximas_bot = []

        for fila in range(8):
            for col in range(8):
                if self.MyBoard[fila][col] in (1, 3):  # Piezas del BOT (Rojas)
                    # Calculamos el peso máximo de captura predictivo para esta pieza
                    peso = self.calcular_peso_maximo_captura(fila, col)
                    if peso > 0:
                        if peso > peso_max_bot:
                            peso_max_bot = peso
                            piezas_maximas_bot = [(fila, col)]
                        elif peso == peso_max_bot:
                            piezas_maximas_bot.append((fila, col))

                    # Escanear saltos inmediatos para la toma de acción de este turno
                    saltos = self.calcular_saltos_continuos(fila, col)
                    for s_dest in saltos:
                        f_dest, c_dest = s_dest
                        df = 1 if f_dest > fila else -1
                        dc = 1 if c_dest > col else -1
                        f_int, c_int = fila + df, col + dc
                        if self.MyBoard[fila][col] == 3:  # Reina larga
                            while self.MyBoard[f_int][c_int] == 0:
                                f_int += df
                                c_int += dc
                        capturas_disponibles.append(((fila, col), (f_dest, c_dest), (f_int, c_int)))

                    # Si no hay capturas obligatorias en esta ficha, recopila pasos simples
                    self.obtener_movimientos_simples_bot(fila, col, movimientos_simples)

        # 2. SELECCIÓN DE ACCIÓN SEGÚN REGLAS DE CHECKBOX DEL BOT
        if capturas_disponibles:
            # Filtrar capturas óptimas (Rutas de Máximo Peso) y subóptimas (Rutas cortas)
            capturas_maximas = []
            capturas_cortas = []

            for orig, dest, inter in capturas_disponibles:
                f_o, c_o = orig
                f_d, c_d = dest
                df_u = 1 if f_d > f_o else -1
                dc_u = 1 if c_d > c_o else -1

                # Simulación rápida local para saber el peso de esta rama específica del BOT
                val_orig = self.MyBoard[f_o][c_o]
                self.MyBoard[f_d][c_d] = val_orig
                self.MyBoard[f_o][c_o] = 0
                peso_rama = 1 + self.calcular_peso_maximo_captura(f_d, c_d, vector_prohibido=(-df_u, -dc_u))
                self.MyBoard[f_o][c_o] = val_orig
                self.MyBoard[f_d][c_d] = 0

                if peso_rama == peso_max_bot:
                    capturas_maximas.append((orig, dest, inter))
                else:
                    capturas_cortas.append((orig, dest, inter))

            # Elección inteligente/estrategia del BOT
            if self.regla_bot_forzar or not capturas_cortas:
                # Juega estricto o no tiene opciones cortas: toma el camino de máximo peso
                origen, destino, intermedia = random.choice(capturas_maximas)
                decision_fue_optima = True
            else:
                # Clásico: 70% va por el combo máximo, 30% elige la jugada trampa (captura corta)
                if random.random() < 0.30:
                    origen, destino, intermedia = random.choice(capturas_cortas)
                    decision_fue_optima = False
                else:
                    origen, destino, intermedia = random.choice(capturas_maximas)
                    decision_fue_optima = True

            # --- EJECUCIÓN ATÓMICA DE LA CAPTURA DEL BOT ---
            f_orig, c_orig = origen
            f_dest, c_dest = destino
            f_int, c_int = intermedia

            valor_bot = self.MyBoard[f_orig][c_orig]
            self.MyBoard[f_orig][c_orig] = 0
            self.MyBoard[f_int][c_int] = 0  # Tu ficha blanca es eliminada
            self.MyBoard[f_dest][c_dest] = valor_bot
            self.actualizar_contadores_interfaz()

            # --- EVALUAR COMBO RECURSIVO DEL BOT CORREGIDO ---
            df_u = 1 if f_dest > f_orig else -1
            dc_u = 1 if c_dest > c_orig else -1
            saltos_extras = self.calcular_saltos_continuos(f_dest, c_dest, vector_prohibido=(-df_u, -dc_u))

            if saltos_extras and decision_fue_optima:
                # El BOT va por el camino óptimo y legalmente debe continuar la cadena
                self.status_bar.showMessage("🤖 BOT en combo múltiple...")
                self.tablero.update()
                QTimer.singleShot(600, self.ejecutar_turno_bot)
                return
            else:
                # --- AUDITORÍA DE REGLAS v1.7 (CIERRE DE JUGADA) ---
                se_auto_soplo_por_combo_incompleto = False

                # REGLA CRÍTICA: Si la pieza terminó su turno pero REALMENTE aún tenía saltos extras,
                # significa que dejó el combo a medias. Castigo implacable inmediato en el aterrizaje.
                if self.regla_bot_soplado and saltos_extras:
                    self.MyBoard[f_dest][c_dest] = 0  # La pieza se desvanece por combo incompleto
                    self.status_bar.showMessage(
                        f"💨 ¡COMBO INCOMPLETO! Ficha del BOT soplada en ({f_dest}, {c_dest}) por dejar piezas vivas.")
                    self.actualizar_contadores_interfaz()
                    se_auto_soplo_por_combo_incompleto = True

                # Si no se sopló por combo incompleto, revisamos si otra pieza estática debió haber comido más
                if self.regla_bot_soplado and not decision_fue_optima and not se_auto_soplo_por_combo_incompleto:
                    for f_inf, c_inf in piezas_maximas_bot:
                        if self.MyBoard[f_inf][c_inf] in (1, 3):
                            self.MyBoard[f_inf][c_inf] = 0
                            self.status_bar.showMessage(
                                f"💨 ¡BOBA DEL BOT! Pieza de la IA soplada en ({f_inf}, {c_inf}) por omitir combo de {peso_max_bot}.")
                    self.actualizar_contadores_interfaz()

                # Cierre seguro del turno del BOT
                pieza_viva_al_final = self.MyBoard[f_dest][c_dest] in (1, 3)
                if pieza_viva_al_final:
                    self.status_bar.showMessage(f"🤖 El BOT ejecutó su jugada en ({f_dest}, {c_dest}).")
                    self.finalizar_turno_bot(f_dest, c_dest, valor_bot)
                else:
                    self.finalizar_turno_bot()

        elif movimientos_simples:
            # El BOT realiza un movimiento simple de aproximación estándar
            origen, destino = random.choice(movimientos_simples)
            f_orig, c_orig = origen
            f_dest, c_dest = destino
            valor_bot = self.MyBoard[f_orig][c_orig]

            if self.regla_bot_soplado and self.verificar_si_bot_tenia_capturas_globales():
                self.MyBoard[f_orig][c_orig] = 0  # Soplado completo por omitir captura
                self.status_bar.showMessage("💨 ¡BOBA DEL BOT! Pieza de la IA soplada por caminar en vez de capturar.")
                self.actualizar_contadores_interfaz()
                self.finalizar_turno_bot()
            else:
                self.MyBoard[f_orig][c_orig] = 0
                self.MyBoard[f_dest][c_dest] = valor_bot
                self.finalizar_turno_bot(f_dest, c_dest, valor_bot)
        else:
            self.game_active = False
            self.status_bar.showMessage("¡HAS GANADO! El BOT se ha quedado sin movimientos legales.")

            return

        self.tablero.update()
        self.cambiar_turno("HUMANO")

    def finalizar_turno_bot(self, f=None, c=None, valor=None):
        """Ejecuta coronación, refresca tablero y cambia turno al humano."""
        if f is not None and c is not None:
            self.evaluar_coronacion(f, c, valor)
        self.tablero.update()
        self.cambiar_turno("HUMANO")

    def verificar_si_bot_tenia_capturas_globales(self):
        """Escanea si el BOT tenía alguna captura obligatoria disponible en el tablero."""
        for f in range(8):
            for c in range(8):
                if self.MyBoard[f][c] in (1, 3):
                    if self.calcular_saltos_continuos(f, c):
                        return True
        return False


    def obtener_movimientos_simples_bot(self, f, c, lista_resultados):
        """Calcula pasos de aproximación para peones y reinas del BOT."""
        pieza = self.MyBoard[f][c]
        # Peón rojo (1) solo baja, Reina (3) todas direcciones
        direcciones = [(1, -1), (1, 1)] if pieza == 1 else [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in direcciones:
            nf, nc = f + df, c + dc
            if pieza == 3:  # Rayo de Reina
                while 0 <= nf < 8 and 0 <= nc < 8 and self.MyBoard[nf][nc] == 0:
                    lista_resultados.append(((f, c), (nf, nc)))
                    nf += df
                    nc += dc
            else:  # Paso de Peón
                if 0 <= nf < 8 and 0 <= nc < 8 and self.MyBoard[nf][nc] == 0:
                    lista_resultados.append(((f, c), (nf, nc)))

    def calcular_saltos_continuos(self, fila, col, vector_prohibido=None):
        """
        UNIVERSAL: Escanea saltos de combo para CUALQUIER bando (Humano o BOT).
        Detecta automáticamente quién es el enemigo según la pieza en (fila, col).
        """
        saltos_encontrados = []
        tipo_pieza = self.MyBoard[fila][col]
        if tipo_pieza == 0: return []

        # 1. Definir quién es el enemigo y las direcciones
        # Si la pieza es blanca (2, 4), el enemigo es rojo (1, 3).
        # Si la pieza es roja (1, 3), el enemigo es blanco (2, 4).
        es_blanca = tipo_pieza in (2, 4)
        enemigos = (1, 3) if es_blanca else (2, 4)

        if tipo_pieza == 2:  # Peón blanco: solo sube
            direcciones = [(-1, -1), (-1, 1)]
        elif tipo_pieza == 1:  # Peón rojo: solo baja
            direcciones = [(1, -1), (1, 1)]
        else:  # Reinas (3 o 4): todas las direcciones
            direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for df, dc in direcciones:
            # Regla de No-Retorno
            if vector_prohibido and (df, dc) == vector_prohibido:
                continue

            if tipo_pieza in (3, 4):  # LÓGICA DE REINA (Largo alcance)
                f_actual, c_actual = fila + df, col + dc
                enemigo_detectado = None
                while 0 <= f_actual < 8 and 0 <= c_actual < 8:
                    val_celda = self.MyBoard[f_actual][c_actual]
                    if not enemigo_detectado:
                        if val_celda in enemigos:
                            enemigo_detectado = (f_actual, c_actual)
                        elif val_celda != 0:  # Chocó con aliada
                            break
                    else:
                        if val_celda == 0:
                            saltos_encontrados.append((f_actual, c_actual))
                        else:  # Bloqueado tras el enemigo
                            break
                    f_actual += df
                    c_actual += dc
            else:  # LÓGICA DE PEÓN (Corto alcance)
                f_int, c_int = fila + df, col + dc
                f_s, c_s = fila + (df * 2), col + (dc * 2)
                if 0 <= f_s < 8 and 0 <= c_s < 8:
                    if self.MyBoard[f_int][c_int] in enemigos and self.MyBoard[f_s][c_s] == 0:
                        saltos_encontrados.append((f_s, c_s))

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
        self.regla_bot_forzar = self.chk_bot_forzar.isChecked()
        self.regla_bot_soplado = self.chk_bot_soplado.isChecked()

    def obtener_todas_las_piezas_con_captura_humano(self):
        """Escanea globalmente todo el tablero para encontrar qué fichas blancas tienen saltos obligatorios."""
        piezas_con_salto = []
        for f in range(8):
            for col in range(8):
                if self.MyBoard[f][col] in (2, 4):  # Fichas del humano
                    if self.calcular_saltos_continuos(f, col):
                        piezas_con_salto.append((f, col))
        return piezas_con_salto

    def analizar_y_calibrar_cerebro_bot(self):
        """
        NUEVO: Capa de Inteligencia Artificial Psicológica.
        El BOT evalúa el tablero y decide si le conviene forzar capturas o arriesgar.
        """
        vivas_rojas = 0
        vivas_blancas = 0
        for f in range(8):
            for c in range(8):
                if self.MyBoard[f][c] in (1, 3):
                    vivas_rojas += 1
                elif self.MyBoard[f][c] in (2, 4):
                    vivas_blancas += 1

        # ESTRATEGIA A: Si el BOT va perdiendo en piezas, se vuelve "agresivo y tramposo"
        if vivas_rojas < vivas_blancas:
            # Apaga 'Forzar Captura' para permitirse hacer movimientos trampa y sacrificios
            self.chk_bot_forzar.setChecked(False)
            # Mantiene el soplado activo para castigar al humano si se confía
            self.chk_bot_soplado.setChecked(True)
            self.status_bar.showMessage("🤖 El BOT nota desventaja y cambia a modo: TÁCTICA CLÁSICA.")

        # ESTRATEGIA B: Si el BOT va ganando o están empatados, juega estricto y seguro
        else:
            # Juega modo torneo estricto, no regala nada y obliga a cumplir la ley
            self.chk_bot_forzar.setChecked(True)
            self.chk_bot_soplado.setChecked(True)
            self.status_bar.showMessage("🤖 El BOT mantiene el control en modo: REGLAMENTO DE TORNEO.")

        # Sincronizamos las variables lógicas con los clicks automáticos del BOT
        self.actualizar_reglasbox()

    def cambiar_dificultad_bot(self, nivel):
        """Sincroniza el nivel elegido y commuta visualmente los botones de la UI."""
        self.nivel_dificultad_bot = nivel
        self.btn_nv1.setChecked(nivel == 1)
        self.btn_nv2.setChecked(nivel == 2)
        self.btn_nv3.setChecked(nivel == 3)

        nombres = {1: "PRINCIPIANTE", 2: "INTERMEDIO", 3: "MAESTRO 🔥"}
        self.status_bar.showMessage(f"🧠 Cerebro del BOT calibrado en modo: {nombres[nivel]}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = DamasGame()
    game.show()
    sys.exit(app.exec())

def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))
    print(text)
    # También lo guardamos en un archivo por si la consola se cierra muy rápido
    with open("crash_log.txt", "w") as f:
        f.write(text)
    sys.exit(1)

def except_hook(cls, exception, tb):
    """Captura errores de Qt antes de que la ventana colapse."""
    text = "".join(traceback.format_exception(cls, exception, tb))
    print(text)
    # Guarda el error en un archivo de texto por si la consola se cierra
    with open("crash_log.txt", "w") as f:
        f.write(text)
    sys.__excepthook__(cls, exception, tb)

#sys.excepthook = log_uncaught_exceptions

sys.excepthook = except_hook
