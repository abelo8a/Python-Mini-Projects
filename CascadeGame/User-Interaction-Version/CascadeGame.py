import sys
import math
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QLabel, QListWidget, QPushButton, QTextEdit,
                             QStatusBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QBrush


class TableroJuego(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 360, 360)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.main_window.mouse_click_tablero(event)

    def paintEvent(self, event):
        if not self.main_window.game_active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box_size = 36
        radius = box_size / 2

        for i in range(10):
            for c in range(10):
                lados = self.main_window.MyArray[c][i]
                if lados == 0:
                    continue

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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bloques Game')
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

        self.label9 = QLabel('1', self.panel1)
        self.label9.setGeometry(68, 12, 11, 20)
        self.label9.setFont(font_values)
        self.label9.setStyleSheet("color: yellow; border: none;")

        self.label1 = QLabel('Puntos:', self.panel1)
        self.label1.setGeometry(8, 48, 71, 24)
        self.label1.setFont(font_labels)
        self.label1.setStyleSheet("color: red; border: none;")

        self.label2 = QLabel('0', self.panel1)
        self.label2.setGeometry(86, 48, 12, 24)
        self.label2.setFont(font_values)
        self.label2.setStyleSheet("color: yellow; border: none;")

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")

        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu('Archivo')

        action_nuevo = QAction('Nuevo', self)
        action_nuevo.triggered.connect(self.button1_click)
        menu_archivo.addAction(action_nuevo)

        action_abrir = QAction('Abrir', self)
        action_abrir.triggered.connect(self.abrir1_click)
        menu_archivo.addAction(action_abrir)

        self.action_guardar = QAction('Guardar como..', self)
        self.action_guardar.setEnabled(False)
        self.action_guardar.triggered.connect(self.guardar_como1_click)
        menu_archivo.addAction(self.action_guardar)

        menu_archivo.addSeparator()

        action_salir = QAction('Salir', self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

        menu_ayuda = menu_bar.addMenu('Ayuda')
        action_acerca = QAction('Acerca de...', self)
        action_acerca.triggered.connect(self.acercade1_click)
        menu_ayuda.addAction(action_acerca)

    def button1_click(self):
        self.label2.setText('0')
        self.action_guardar.setEnabled(True)
        self.tot_puntos = 0
        for i in range(10):
            for c in range(10):
                self.MyArray[c][i] = random.randint(0, 4) + 3
        self.game_active = True
        self.tablero.update()

    def calcular_puntuaje(self):
        tabla_puntos = {
            2: 100, 3: 200, 4: 400, 5: 700, 6: 1100, 7: 1600,
            8: 2200, 9: 2900, 10: 3700, 11: 4600, 12: 5600,
            13: 6700, 14: 7900, 15: 9200
        }
        puntos_adicionales = tabla_puntos.get(self.puntos_eliminados_ronda, 0)
        self.tot_puntos = int(self.label2.text()) + puntos_adicionales
        self.label2.setText(str(self.tot_puntos))

    def eliminar_recursivo(self, w, z, target_val):
        if w < 0 or w > 9 or z < 0 or z > 9:
            return
        if self.MyArray[w][z] != target_val:
            return
        self.MyArray[w][z] = 0
        self.puntos_eliminados_ronda += 1
        self.eliminar_recursivo(w - 1, z, target_val)
        self.eliminar_recursivo(w + 1, z, target_val)
        self.eliminar_recursivo(w, z - 1, target_val)
        self.eliminar_recursivo(w, z + 1, target_val)

    def aplicar_gravedad(self):
        for c in range(10):
            columna_filtrada = [self.MyArray[c][i] for i in range(10) if self.MyArray[c][i] != 0]
            bloques_faltantes = 10 - len(columna_filtrada)
            nuevos_bloques = [random.randint(0, 4) + 3 for _ in range(bloques_faltantes)]
            nueva_columna = nuevos_bloques + columna_filtrada
            for i in range(10):
                self.MyArray[c][i] = nueva_columna[i]

    def mouse_click_tablero(self, event):
        if not self.game_active:
            return
        x, y = event.position().x(), event.position().y()
        if x >= 360 or y >= 360:
            return
        w, z = int(x // 36), int(y // 36)
        target_val = self.MyArray[w][z]
        if target_val not in (0, 1, 9):
            self.puntos_eliminados_ronda = 0
            self.eliminar_recursivo(w, z, target_val)
            if self.puntos_eliminados_ronda > 1:
                self.calcular_puntuaje()
                self.aplicar_gravedad()
                self.tablero.update()

    def abrir1_click(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivos del Juego (*.ps2)")
        if file_name: self.status_bar.showMessage(f"Partida cargada: {file_name}")

    def guardar_como1_click(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como..", "", "Archivos del Juego (*.ps2)")
        if file_name: self.status_bar.showMessage(f"Partida guardada: {file_name}")

    def acercade1_click(self):
        QMessageBox.about(self, "Acerca de", "Bloques Game\nMigrado exitosamente.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BloquesGame()
    game.show()
    sys.exit(app.exec())
