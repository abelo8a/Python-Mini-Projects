import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QBrush, QActionGroup


class TableroJuego(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 360, 360)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        if not self.main_window.game_active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box_size = 36
        radius = box_size / 2
        for i in range(10):
            for c in range(10):
                lados = self.main_window.MyArray[c][i]
                if lados == 0: continue

                if (c, i) in self.main_window.bloques_seleccionados_bot:
                    painter.setPen(QPen(QColor(255, 0, 50), 4, Qt.PenStyle.DashLine))
                else:
                    if lados == 3: pen_color = QColor(3, 182, 17)
                    elif lados == 4: pen_color = QColor(255, 255, 0)
                    elif lados == 5: pen_color = QColor(18, 236, 254)
                    elif lados == 6: pen_color = QColor(238, 23, 23)
                    elif lados == 7: pen_color = QColor(255, 255, 255)
                    else: pen_color = QColor(100, 100, 100)
                    painter.setPen(QPen(pen_color, 2))

                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                center_x = (c * box_size) + radius
                center_y = (i * box_size) + radius
                points = []
                for count in range(lados + 1):
                    angle = (2 * math.pi) * count / lados
                    pt_x = int(math.sin(angle) * radius + center_x)
                    pt_y = int(math.cos(angle) * radius + center_y)
                    points.append(QPoint(pt_x, pt_y))
                painter.drawPolygon(points)
        painter.end()


class BloquesGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.MyArray = [[0 for _ in range(10)] for _ in range(10)]
        self.tot_puntos = 0
        self.puntos_eliminados_ronda = 0
        self.game_active = False
        self.modo_bot = "Greedy"
        self.bloques_seleccionados_bot = set()
        self.timer_bot = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bloques Game - MONITOREO DE BLOQUES')
        self.setFixedSize(545, 385)
        self.setStyleSheet("background-color: black; color: white;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroJuego(self)

        # Panel lateral con dimensiones corregidas
        self.panel1 = QWidget(self.central_widget)
        self.panel1.setGeometry(362, 0, 183, 361)
        self.panel1.setStyleSheet("background-color: black; border-left: 1px solid #333;")

        font_labels = QFont('MS Sans Serif', 10, QFont.Weight.Bold)
        font_values = QFont('MS Sans Serif', 11, QFont.Weight.Bold)

        # 1. Indicador de Algoritmo
        self.label3 = QLabel('Algoritmo:', self.panel1)
        self.label3.setGeometry(8, 10, 85, 20)
        self.label3.setFont(font_labels)
        self.label3.setStyleSheet("color: red; border: none;")

        self.label_modo = QLabel('Greedy', self.panel1)
        self.label_modo.setGeometry(95, 10, 80, 20)
        self.label_modo.setFont(font_values)
        self.label_modo.setStyleSheet("color: cyan; border: none;")

        # 2. Indicador de Puntos Totales
        self.label1 = QLabel('Puntos:', self.panel1)
        self.label1.setGeometry(8, 45, 71, 20)
        self.label1.setFont(font_labels)
        self.label1.setStyleSheet("color: red; border: none;")

        self.label2 = QLabel('0', self.panel1)
        self.label2.setGeometry(86, 45, 80, 20)
        self.label2.setFont(font_values)
        self.label2.setStyleSheet("color: yellow; border: none;")

        # NUEVO: 3. Contador de Bloques Eliminados en la última jugada
        self.label_elim_titulo = QLabel('Eliminados:', self.panel1)
        self.label_elim_titulo.setGeometry(8, 80, 95, 20)
        self.label_elim_titulo.setFont(font_labels)
        self.label_elim_titulo.setStyleSheet("color: red; border: none;")

        self.label_elim_valor = QLabel('0', self.panel1)
        self.label_elim_valor.setGeometry(110, 80, 60, 20)
        self.label_elim_valor.setFont(font_values)
        self.label_elim_valor.setStyleSheet("color: #FF55FF; border: none;")

        # NUEVO: 4. Contador de Bloques Restantes vivos en el tablero
        self.label_rest_titulo = QLabel('Restantes:', self.panel1)
        self.label_rest_titulo.setGeometry(8, 115, 95, 20)
        self.label_rest_titulo.setFont(font_labels)
        self.label_rest_titulo.setStyleSheet("color: red; border: none;")

        self.label_rest_valor = QLabel('100', self.panel1)
        self.label_rest_valor.setGeometry(110, 115, 60, 20)
        self.label_rest_valor.setFont(font_values)
        self.label_rest_valor.setStyleSheet("color: #55FF55; border: none;")

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Elige un modo e inicia Nuevo")

        # Configuración de la Barra de Menús superiores
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu('Archivo')

        action_nuevo = QAction('Nuevo Juego', self)
        action_nuevo.triggered.connect(self.button1_click)
        menu_archivo.addAction(action_nuevo)

        action_salir = QAction('Salir', self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

        menu_modos = menu_bar.addMenu('Modo de Bot')
        grupo_modos = QActionGroup(self)

        for modo in ["Greedy", "Heurístico", "Random"]:
            act = QAction(modo, self, checkable=True)
            if modo == "Greedy": act.setChecked(True)
            act.triggered.connect(lambda checked, m=modo: self.cambiar_modo(m))
            grupo_modos.addAction(act)
            menu_modos.addAction(act)

    def cambiar_modo(self, nuevo_modo):
        self.modo_bot = nuevo_modo
        self.label_modo.setText(nuevo_modo)
        self.status_bar.showMessage(f"Modo cambiado a: {nuevo_modo}")

    def button1_click(self):
        self.label2.setText('0')
        self.label_elim_valor.setText('0')
        self.label_rest_valor.setText('100')
        self.tot_puntos = 0
        self.total_bloques_eliminados_partida = 0
        self.bloques_seleccionados_bot.clear()
        for i in range(10):
            for c in range(10):
                self.MyArray[c][i] = random.randint(3, 7)
        self.game_active = True
        self.status_bar.showMessage(f"IA en modo [{self.modo_bot}] activa...")
        self.tablero.update()
        if self.timer_bot is None:
            self.timer_bot = QTimer(self)
            self.timer_bot.timeout.connect(self.ejecutar_ciclo_bot)
        if not self.timer_bot.isActive():
            self.timer_bot.start(1000)

    def calcular_puntuaje(self):
        tabla_puntos = {2: 100, 3: 200, 4: 400, 5: 700, 6: 1100, 7: 1600,
                        8: 2200, 9: 2900, 10: 3700, 11: 4600, 12: 5600}
        puntos = tabla_puntos.get(self.puntos_eliminados_ronda, 0)
        if self.puntos_eliminados_ronda > 12:
            puntos = 5600 + (self.puntos_eliminados_ronda - 12) * 1200
        self.tot_puntos = int(self.label2.text()) + puntos
        self.label2.setText(str(self.tot_puntos))

    def eliminar_recursivo_matriz(self, matriz, w, z, target_val):
        if w < 0 or w > 9 or z < 0 or z > 9: return
        if matriz[w][z] != target_val: return
        matriz[w][z] = 0
        self.puntos_eliminados_ronda += 1
        self.eliminar_recursivo_matriz(matriz, w - 1, z, target_val)
        self.eliminar_recursivo_matriz(matriz, w + 1, z, target_val)
        self.eliminar_recursivo_matriz(matriz, w, z - 1, target_val)
        self.eliminar_recursivo_matriz(matriz, w, z + 1, target_val)

    def aplicar_fisicas_reales(self):
        # 1. Gravedad vertical
        for c in range(10):
            col_filt = [self.MyArray[c][i] for i in range(10) if self.MyArray[c][i] != 0]
            ceros_necesarios = 10 - len(col_filt)
            nueva_col = [0] * ceros_necesarios + col_filt
            self.MyArray[c] = nueva_col

        # 2. Desplazamiento horizontal de columnas
        columnas_vivas = []
        for c in range(10):
            if any(self.MyArray[c][i] != 0 for i in range(10)):
                columnas_vivas.append(self.MyArray[c])

        columnas_vaciadas = 10 - len(columnas_vivas)
        for _ in range(columnas_vaciadas):
            col_vacia = [0] * 10
            columnas_vivas.append(col_vacia)

        for c in range(10):
            self.MyArray[c] = columnas_vivas[c]

    def contar_grupo_simulado(self, w, z, target_val, visitados):
        if w < 0 or w > 9 or z < 0 or z > 9: return 0
        if (w, z) in visitados or self.MyArray[w][z] != target_val: return 0
        visitados.add((w, z))
        count = 1
        count += self.contar_grupo_simulado(w - 1, z, target_val, visitados)
        count += self.contar_grupo_simulado(w + 1, z, target_val, visitados)
        count += self.contar_grupo_simulado(w, z - 1, target_val, visitados)
        count += self.contar_grupo_simulado(w, z + 1, target_val, visitados)
        return count

    def actualizar_contadores_interfaz(self):
        vivos = 0
        for c in range(10):
            for i in range(10):
                if self.MyArray[c][i] != 0:
                    vivos += 1

        self.total_bloques_eliminados_partida += self.puntos_eliminados_ronda
        self.label_elim_valor.setText(str(self.total_bloques_eliminados_partida))
        self.label_rest_valor.setText(str(vivos))

    def finalizar_partida(self):
        self.timer_bot.stop()
        atrapadas = sum(1 for c in range(10) for i in range(10) if self.MyArray[c][i] != 0)
        self.game_active = False
        self.label_rest_valor.setText(str(atrapadas))
        self.status_bar.showMessage(f"Fin. Método: {self.modo_bot} | Quedaron: {atrapadas}")

    # LÓGICA DE SELECCIÓN RESISTENTE A BUCLES INFINITOS
    def ejecutar_ciclo_bot(self):
        if not self.game_active: return
        movimientos_validos = []

        for c in range(10):
            for i in range(10):
                val_actual = self.MyArray[c][i]
                if val_actual != 0:
                    visitados_temp = set()
                    tamano = self.contar_grupo_simulado(c, i, val_actual, visitados_temp)
                    if tamano >= 2:
                        movimientos_validos.append((tamano, i, c, visitados_temp))

        if not movimientos_validos:
            self.finalizar_partida()
            return

        # Selección segura usando max() con llaves de discriminación matemática únicas
        if self.modo_bot == "Greedy":
            mejor = max(movimientos_validos, key=lambda x: (x[0], x[1], x[2]))
        elif self.modo_bot == "Heurístico":
            mejor = max(movimientos_validos, key=lambda x: (x[1], x[0], x[2]))
        elif self.modo_bot == "Random":
            mejor = random.choice(movimientos_validos)

        tamano_g, coord_i, coord_c, celdas_grupo = mejor
        self.bloques_seleccionados_bot = celdas_grupo
        self.tablero.update()

        self.puntos_eliminados_ronda = 0
        target_val = self.MyArray[coord_c][coord_i]

        self.status_bar.showMessage(f"[{self.modo_bot}] Rompiendo grupo de {tamano_g} bloques...")
        self.eliminar_recursivo_matriz(self.MyArray, coord_c, coord_i, target_val)

        self.calcular_puntuaje()
        self.aplicar_fisicas_reales()
        self.actualizar_contadores_interfaz()

        self.bloques_seleccionados_bot.clear()
        self.tablero.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BloquesGame()
    game.show()
    sys.exit(app.exec())
