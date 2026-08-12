import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QBrush


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
                    if lados == 3:
                        pen_color = QColor(3, 182, 17)
                    elif lados == 4:
                        pen_color = QColor(255, 255, 0)
                    elif lados == 5:
                        pen_color = QColor(18, 236, 254)
                    elif lados == 6:
                        pen_color = QColor(238, 23, 23)
                    elif lados == 7:
                        pen_color = QColor(255, 255, 255)
                    else:
                        pen_color = QColor(100, 100, 100)
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
        self.bloques_seleccionados_bot = set()
        self.timer_bot = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bloques Game - BOT CON ÁRBOL DE DECISIÓN')
        self.setFixedSize(545, 385)
        self.setStyleSheet("background-color: black; color: white;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroJuego(self)
        self.panel1 = QWidget(self.central_widget)
        self.panel1.setGeometry(362, 0, 183, 361)
        self.panel1.setStyleSheet("background-color: black; border-left: 1px solid #333;")
        font_labels = QFont('MS Sans Serif', 14, QFont.Weight.Bold)
        font_values = QFont('MS Sans Serif', 12, QFont.Weight.Bold)
        self.label3 = QLabel('Nivel:', self.panel1)
        self.label3.setGeometry(8, 8, 54, 24)
        self.label3.setFont(font_labels)
        self.label3.setStyleSheet("color: red; border: none;")
        self.label9 = QLabel('BOT', self.panel1)
        self.label9.setGeometry(68, 12, 40, 20)
        self.label9.setFont(font_values)
        self.label9.setStyleSheet("color: yellow; border: none;")
        self.label1 = QLabel('Puntos:', self.panel1)
        self.label1.setGeometry(8, 48, 71, 24)
        self.label1.setFont(font_labels)
        self.label1.setStyleSheet("color: red; border: none;")
        self.label2 = QLabel('0', self.panel1)
        self.label2.setGeometry(86, 48, 80, 24)
        self.label2.setFont(font_values)
        self.label2.setStyleSheet("color: yellow; border: none;")
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Archivo -> Nuevo para iniciar")
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu('Archivo')
        action_nuevo = QAction('Nuevo', self)
        action_nuevo.triggered.connect(self.button1_click)
        menu_archivo.addAction(action_nuevo)
        action_salir = QAction('Salir', self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

    def button1_click(self):
        self.label2.setText('0')
        self.tot_puntos = 0
        self.bloques_seleccionados_bot.clear()
        self.status_bar.setStyleSheet("color: white;")
        for i in range(10):
            for c in range(10):
                self.MyArray[c][i] = random.randint(3, 7)
        self.game_active = True
        self.status_bar.showMessage("IA Predictiva activa...")
        self.tablero.update()
        if self.timer_bot is None:
            self.timer_bot = QTimer(self)
            self.timer_bot.timeout.connect(self.ejecutar_ciclo_bot)
        if not self.timer_bot.isActive():
            self.timer_bot.start(1000)

    def calcular_puntuaje(self):
        tabla_puntos = {2: 100, 3: 200, 4: 400, 5: 700, 6: 1100, 7: 1600, 8: 2200, 9: 2900, 10: 3700, 11: 4600,
                        12: 5600, 13: 6700, 14: 7900, 15: 9200}
        puntos_adicionales = tabla_puntos.get(self.puntos_eliminados_ronda, 0)
        if self.puntos_eliminados_ronda > 15:
            puntos_adicionales = 9200 + (self.puntos_eliminados_ronda - 15) * 1500
        self.tot_puntos = int(self.label2.text()) + puntos_adicionales
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
        for c in range(10):
            col_filt = []
            for i in range(10):
                if self.MyArray[c][i] != 0:
                    col_filt.append(self.MyArray[c][i])
            bloques_faltantes = 10 - len(col_filt)
            nueva_col = []
            for _ in range(bloques_faltantes):
                nueva_col.append(0)
            for val in col_filt:
                nueva_col.append(val)
            self.MyArray[c] = nueva_col

        columnas_vivas = []
        for c in range(10):
            tiene_bloques = False
            for i in range(10):
                if self.MyArray[c][i] != 0:
                    tiene_bloques = True
                    break
            if tiene_bloques:
                columnas_vivas.append(self.MyArray[c])

        columnas_vaciadas = 10 - len(columnas_vivas)
        for _ in range(columnas_vaciadas):
            col_vacia = []
            for _ in range(10):
                col_vacia.append(0)
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

    def finalizar_partida(self):
        self.timer_bot.stop()
        atrapadas = 0
        for c in range(10):
            for i in range(10):
                if self.MyArray[c][i] != 0:
                    atrapadas += 1
        self.game_active = False
        self.status_bar.showMessage(f"Partida finalizada. Bloques restantes: {atrapadas}")

    def ejecutar_ciclo_bot(self):
        if not self.game_active: return
        movimientos_validos = []
        for c in range(10):
            for i in range(10):
                val_actual = self.MyArray[c][i]
                if val_actual != 0:
                    visitados_temp = set()
                    tamano_grupo = self.contar_grupo_simulado(c, i, val_actual, visitados_temp)
                    if tamano_grupo >= 2:
                        movimientos_validos.append((tamano_grupo, c, i, visitados_temp))

        if not movimientos_validos:
            self.finalizar_partida()
            return

        movimientos_validos.sort(key=lambda x: x[0], reverse=True)
        mejor_movimiento = movimientos_validos[0]
        tamano, coord_c, coord_i, celdas_grupo = mejor_movimiento

        self.bloques_seleccionados_bot = celdas_grupo
        self.tablero.update()

        self.puntos_eliminados_ronda = 0
        target_val = self.MyArray[coord_c][coord_i]

        self.status_bar.showMessage(f"BOT eliminando grupo de {tamano} figuras...")
        self.eliminar_recursivo_matriz(self.MyArray, coord_c, coord_i, target_val)

        self.calcular_puntuaje()
        self.aplicar_fisicas_reales()

        self.bloques_seleccionados_bot.clear()
        self.tablero.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BloquesGame()
    game.show()
    sys.exit(app.exec())
